"""ChatOps agent orchestrating operational diagnostics for Phase 3."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime, time
from typing import Dict, Iterable, List, Optional, Sequence

from app.models.trading.backtest import Backtest
from app.models.ml_platform.data_quality import DataQualityEvent
from app.schemas.enums import BacktestStatus, SeverityLevel
from app.schemas.gen_ai.chatops import CacheStatusSnapshot, FailureInsight
from app.schemas.user.dashboard import (
    DataQualityAlert,
    DataQualitySeverity,
    DataQualitySummary,
)
from app.services.database_manager import DatabaseManager
from app.services.market_data import MarketDataService
from app.services.monitoring.data_quality_sentinel import (
    AlertPayload,
    DataQualitySentinel,
    DataQualitySummaryPayload,
)

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ChatOpsAgentResult:
    """Container returned by the ChatOps agent."""

    answer: str
    used_tools: List[str] = field(default_factory=list)
    denied_tools: List[str] = field(default_factory=list)
    cache_status: Optional[CacheStatusSnapshot] = None
    data_quality: Optional[DataQualitySummary] = None
    recent_failures: List[FailureInsight] = field(default_factory=list)
    external_services: Dict[str, Dict[str, str]] = field(default_factory=dict)


class ChatOpsAgent:
    """Phase 3 ChatOps agent providing operational diagnostics."""

    _TOOL_PERMISSIONS: Dict[str, set[str]] = {
        "get_cache_status": {"admin", "devops", "engineer", "viewer"},
        "get_data_quality_summary": {
            "admin",
            "devops",
            "engineer",
            "analyst",
            "viewer",
        },
        "list_recent_failures": {"admin", "devops", "engineer"},
        "check_alpha_vantage": {"admin", "devops", "engineer", "analyst"},
    }

    def __init__(
        self,
        market_data_service: MarketDataService,
        database_manager: DatabaseManager,
        data_quality_sentinel: DataQualitySentinel,
    ) -> None:
        self.market_data_service = market_data_service
        self.database_manager = database_manager
        self.data_quality_sentinel = data_quality_sentinel

    async def run(
        self, question: str, user_roles: Optional[Sequence[str]] = None
    ) -> ChatOpsAgentResult:
        """Process a natural language question and return diagnostics."""

        normalized = question.lower()
        tools = self._select_tools(normalized)
        roles = self._normalise_roles(user_roles)

        logger.info("ChatOpsAgent invoked", extra={"tools": tools, "roles": roles})

        answer_lines: List[str] = []
        result = ChatOpsAgentResult(answer="")

        for tool in tools:
            if not self._is_authorised(tool, roles):
                logger.warning(
                    "ChatOps tool denied", extra={"tool": tool, "roles": roles}
                )
                result.denied_tools.append(tool)
                continue

            if tool == "get_cache_status":
                cache_status = await self._gather_cache_status()
                result.cache_status = cache_status
                result.used_tools.append(tool)
                answer_lines.append(self._format_cache_status(cache_status))
            elif tool == "get_data_quality_summary":
                data_quality = await self._gather_data_quality_summary()
                result.data_quality = data_quality
                result.used_tools.append(tool)
                answer_lines.append(self._format_data_quality(data_quality))
            elif tool == "list_recent_failures":
                failures = await self._gather_recent_failures()
                result.recent_failures = failures
                result.used_tools.append(tool)
                if failures:
                    answer_lines.append(self._format_failures(failures))
                else:
                    answer_lines.append("최근 48시간 내 실패 이벤트가 기록되지 않았습니다.")
            elif tool == "check_alpha_vantage":
                external_status = await self._check_alpha_vantage()
                result.external_services.update(external_status)
                result.used_tools.append(tool)
                answer_lines.append(self._format_external_services(external_status))

        if not answer_lines:
            answer_lines.append("요청하신 항목에 대해 실행 가능한 ChatOps 툴이 없거나 모두 권한에 의해 차단되었습니다.")

        if result.denied_tools:
            answer_lines.append(
                "권한 부족으로 실행되지 않은 툴: " + ", ".join(sorted(result.denied_tools))
            )

        result.answer = "\n".join(answer_lines)
        return result

    def _select_tools(self, normalized_question: str) -> List[str]:
        """Infer tool list from the natural language question."""

        tools: List[str] = []

        if any(
            keyword in normalized_question
            for keyword in ["캐시", "cache", "duckdb", "mongodb"]
        ):
            tools.append("get_cache_status")

        if any(
            keyword in normalized_question
            for keyword in ["데이터 품질", "data quality", "sentinel", "센티널"]
        ):
            tools.append("get_data_quality_summary")

        if any(
            keyword in normalized_question
            for keyword in ["실패", "에러", "오류", "failure", "incident"]
        ):
            tools.append("list_recent_failures")

        if any(
            keyword in normalized_question
            for keyword in ["alpha vantage", "외부 api", "api 상태", "alpha"]
        ):
            tools.append("check_alpha_vantage")

        if not tools:
            tools.append("get_data_quality_summary")

        return tools

    def _normalise_roles(self, roles: Optional[Sequence[str]]) -> set[str]:
        if not roles:
            return {"viewer"}
        return {role.lower() for role in roles}

    def _is_authorised(self, tool: str, roles: Iterable[str]) -> bool:
        allowed = self._TOOL_PERMISSIONS.get(tool, {"admin"})
        return any(role in allowed for role in roles)

    async def _gather_cache_status(self) -> CacheStatusSnapshot:
        notes: List[str] = []
        duckdb_status = "connected"
        duckdb_row_count: Optional[int] = None
        duckdb_last_updated: Optional[datetime] = None

        try:
            self.database_manager.connect()

            def _query_duckdb() -> tuple[int, Optional[datetime]]:
                conn = self.database_manager.duckdb_conn
                result = conn.execute(
                    "SELECT COUNT(*) AS cnt, MAX(date) AS last_date FROM daily_prices"
                ).fetchone()
                if result is None:
                    return 0, None
                total_count, last_date = result
                if last_date is not None:
                    last_dt = datetime.combine(last_date, time.min, tzinfo=UTC)
                else:
                    last_dt = None
                return int(total_count or 0), last_dt

            duckdb_row_count, duckdb_last_updated = await asyncio.to_thread(
                _query_duckdb
            )
        except Exception as exc:  # pragma: no cover - database connectivity
            duckdb_status = "error"
            notes.append(f"DuckDB 조회 중 오류: {exc}")

        mongodb_status = "unknown"
        mongodb_last_event_at: Optional[datetime] = None
        try:
            latest_events = (
                await DataQualityEvent.find_all()
                .sort("-occurred_at")
                .limit(1)
                .to_list()
            )
            if latest_events:
                mongodb_status = "connected"
                mongodb_last_event_at = latest_events[0].occurred_at
            else:
                mongodb_status = "no_events"
        except Exception as exc:  # pragma: no cover - database connectivity
            mongodb_status = "error"
            notes.append(f"MongoDB 조회 중 오류: {exc}")

        return CacheStatusSnapshot(
            duckdb_status=duckdb_status,
            duckdb_row_count=duckdb_row_count,
            duckdb_last_updated=duckdb_last_updated,
            mongodb_status=mongodb_status,
            mongodb_last_event_at=mongodb_last_event_at,
            notes=notes,
        )

    async def _gather_data_quality_summary(self) -> DataQualitySummary:
        payload = await self.data_quality_sentinel.get_recent_summary()
        return self._convert_summary(payload)

    async def _gather_recent_failures(self, limit: int = 5) -> List[FailureInsight]:
        failures: List[FailureInsight] = []

        try:
            from beanie.operators import In

            dq_events = (
                await DataQualityEvent.find(
                    In(
                        DataQualityEvent.severity,
                        [SeverityLevel.HIGH, SeverityLevel.CRITICAL],
                    )
                )
                .sort("-occurred_at")
                .limit(limit)
                .to_list()
            )
            for event in dq_events:
                failures.append(
                    FailureInsight(
                        source="data_quality",
                        identifier=f"{event.symbol}:{event.anomaly_type}",
                        occurred_at=event.occurred_at,
                        severity=DataQualitySeverity(event.severity.value),
                        message=event.message,
                        metadata={
                            "iso_score": event.iso_score,
                            "prophet_score": event.prophet_score,
                            "price_change_pct": event.price_change_pct,
                            "volume_z_score": event.volume_z_score,
                        },
                    )
                )
        except Exception as exc:  # pragma: no cover - database connectivity
            logger.warning("Failed to fetch data quality events", exc_info=exc)

        try:
            backtest_failures = (
                await Backtest.find(Backtest.status == BacktestStatus.FAILED)
                .sort("-updated_at")
                .limit(limit)
                .to_list()
            )
            for backtest in backtest_failures:
                occurred_at = (
                    backtest.updated_at or backtest.created_at or datetime.now(UTC)
                )
                message = backtest.error_message or "백테스트 실패 (상세 메시지 없음)"
                failures.append(
                    FailureInsight(
                        source="backtest",
                        identifier=str(backtest.id) if backtest.id else backtest.name,
                        occurred_at=occurred_at,
                        severity=None,
                        message=message,
                        metadata={
                            "name": backtest.name,
                            "symbols": (
                                backtest.config.symbols if backtest.config else []
                            ),
                        },
                    )
                )
        except Exception as exc:  # pragma: no cover - database connectivity
            logger.warning("Failed to fetch backtest failures", exc_info=exc)

        failures.sort(key=lambda item: item.occurred_at, reverse=True)
        return failures[:limit]

    async def _check_alpha_vantage(self) -> Dict[str, Dict[str, str]]:
        health = await self.market_data_service.health_check()
        external = health.get("external_apis") or {}
        return {"external_apis": external, "cache": health.get("cache", {})}

    def _convert_summary(
        self, payload: DataQualitySummaryPayload
    ) -> DataQualitySummary:
        severity_breakdown = {
            DataQualitySeverity(level.value): count
            for level, count in payload.severity_breakdown.items()
        }
        recent_alerts = [self._convert_alert(alert) for alert in payload.recent_alerts]

        return DataQualitySummary(
            total_alerts=payload.total_alerts,
            severity_breakdown=severity_breakdown,
            last_updated=payload.last_updated,
            recent_alerts=recent_alerts,
        )

    def _convert_alert(self, alert: AlertPayload) -> DataQualityAlert:
        return DataQualityAlert(
            symbol=alert.symbol,
            data_type=alert.data_type,
            occurred_at=alert.occurred_at,
            severity=DataQualitySeverity(alert.severity.value),
            iso_score=alert.iso_score,
            prophet_score=alert.prophet_score,
            price_change_pct=alert.price_change_pct,
            volume_z_score=alert.volume_z_score,
            message=alert.message,
        )

    def _format_cache_status(self, snapshot: CacheStatusSnapshot) -> str:
        duckdb_info = (
            f"DuckDB: {snapshot.duckdb_status}"
            f" (행 수 {snapshot.duckdb_row_count or 0:,}"
        )
        if snapshot.duckdb_last_updated:
            duckdb_info += f", 최신 {snapshot.duckdb_last_updated.isoformat()}"
        duckdb_info += ")"

        mongodb_info = f"MongoDB: {snapshot.mongodb_status}"
        if snapshot.mongodb_last_event_at:
            mongodb_info += f" (최근 이벤트 {snapshot.mongodb_last_event_at.isoformat()})"

        notes = f" 경고: {'; '.join(snapshot.notes)}" if snapshot.notes else ""
        return f"캐시 상태 — {duckdb_info}, {mongodb_info}.{notes}"

    def _format_data_quality(self, summary: DataQualitySummary) -> str:
        critical = summary.severity_breakdown.get(DataQualitySeverity.CRITICAL, 0)
        high = summary.severity_breakdown.get(DataQualitySeverity.HIGH, 0)
        latest = summary.recent_alerts[0] if summary.recent_alerts else None

        if latest:
            latest_msg = (
                f"최근 경보: {latest.symbol} {latest.data_type} {latest.severity.value}"
                f" ({latest.price_change_pct:.2f}% 변동)"
            )
        else:
            latest_msg = "최근 경보 없음"

        return (
            "데이터 품질 요약 — 총 {total}건, "
            "심각도 CRITICAL {critical}건, HIGH {high}건. {latest_msg}."
        ).format(
            total=summary.total_alerts,
            critical=critical,
            high=high,
            latest_msg=latest_msg,
        )

    def _format_failures(self, failures: List[FailureInsight]) -> str:
        items = []
        for failure in failures[:3]:
            severity = failure.severity.value if failure.severity else "n/a"
            items.append(
                f"- {failure.source}: {failure.identifier} @ {failure.occurred_at.isoformat()}"
                f" (severity={severity}) — {failure.message}"
            )
        return "최근 실패 요약:\n" + "\n".join(items)

    def _format_external_services(self, status: Dict[str, Dict[str, str]]) -> str:
        external = status.get("external_apis", {})
        alpha_status = external.get("alpha_vantage", "unknown")
        cache = status.get("cache", {})
        duckdb = cache.get("duckdb", "unknown")
        mongodb = cache.get("mongodb", "unknown")
        return (
            "외부 서비스 상태 — Alpha Vantage: {alpha}, DuckDB 캐시: {duckdb}, "
            "MongoDB: {mongodb}."
        ).format(alpha=alpha_status, duckdb=duckdb, mongodb=mongodb)


__all__ = ["ChatOpsAgent", "ChatOpsAgentResult"]
