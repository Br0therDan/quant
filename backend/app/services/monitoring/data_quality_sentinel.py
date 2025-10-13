"""Co-ordinates anomaly scoring, persistence and alerting."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Dict, Iterable, List, MutableMapping, Optional

import httpx

from app.core.config import settings
from app.models.data_quality import DataQualityEvent, SeverityLevel
from app.models.market_data.stock import DailyPrice
from app.services.ml.anomaly_detector import AnomalyDetectionService, AnomalyResult


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class AlertPayload:
    """Lightweight serialisable structure for dashboard summaries."""

    symbol: str
    data_type: str
    occurred_at: datetime
    severity: SeverityLevel
    iso_score: float
    prophet_score: Optional[float]
    price_change_pct: float
    volume_z_score: float
    message: str


@dataclass(slots=True)
class DataQualitySummaryPayload:
    """Aggregated snapshot returned to higher level services."""

    total_alerts: int
    severity_breakdown: Dict[SeverityLevel, int]
    last_updated: datetime
    recent_alerts: List[AlertPayload]


class DataQualitySentinel:
    """Runs anomaly detection and persists resulting events."""

    def __init__(
        self,
        anomaly_detector: Optional[AnomalyDetectionService] = None,
        data_type: str = "daily",
    ) -> None:
        self.detector = anomaly_detector or AnomalyDetectionService()
        self.data_type = data_type

    async def evaluate_daily_prices(
        self, symbol: str, prices: Iterable[DailyPrice], source: str = "alpha_vantage"
    ) -> MutableMapping[datetime, AnomalyResult]:
        price_list = list(prices)
        if not price_list:
            return {}

        analysis = self.detector.score_daily_prices(symbol, price_list)

        await asyncio.gather(
            *[
                self._persist_event(symbol, result, source)
                for result in analysis.values()
                if result.severity is not SeverityLevel.NORMAL
            ]
        )

        for price in price_list:
            result = analysis.get(price.date)
            if not result:
                continue
            price.iso_anomaly_score = result.iso_score
            price.prophet_anomaly_score = result.prophet_score
            price.volume_z_score = result.volume_z_score
            price.anomaly_severity = result.severity
            price.anomaly_reasons = result.reasons or None

        return analysis

    async def get_recent_summary(
        self, lookback_hours: int = 24, limit: int = 5
    ) -> DataQualitySummaryPayload:
        window_start = datetime.now(UTC) - timedelta(hours=lookback_hours)

        filter_query = {
            "data_type": self.data_type,
            "occurred_at": {"$gte": window_start},
        }

        recent_events = (
            await DataQualityEvent.find(filter_query)
            .sort("-occurred_at")
            .limit(limit)
            .to_list()
        )

        severity_breakdown: Dict[SeverityLevel, int] = {
            level: 0 for level in SeverityLevel
        }

        # Count total events per severity within the window
        async for bucket in DataQualityEvent.aggregate(
            [
                {"$match": filter_query},
                {"$group": {"_id": "$severity", "count": {"$sum": 1}}},
            ]
        ):
            try:
                level = SeverityLevel(bucket["_id"])
            except ValueError:
                continue
            severity_breakdown[level] = int(bucket.get("count", 0))

        recent_alerts = [
            AlertPayload(
                symbol=event.symbol,
                data_type=event.data_type,
                occurred_at=event.occurred_at,
                severity=event.severity,
                iso_score=event.iso_score or 0.0,
                prophet_score=event.prophet_score,
                price_change_pct=event.price_change_pct or 0.0,
                volume_z_score=event.volume_z_score or 0.0,
                message=event.message,
            )
            for event in recent_events
        ]

        return DataQualitySummaryPayload(
            total_alerts=sum(severity_breakdown.values()),
            severity_breakdown=severity_breakdown,
            last_updated=datetime.now(UTC),
            recent_alerts=recent_alerts,
        )

    async def _persist_event(
        self, symbol: str, result: AnomalyResult, source: str
    ) -> None:
        existing = await DataQualityEvent.find_one(
            {
                "symbol": symbol,
                "data_type": self.data_type,
                "occurred_at": result.timestamp,
                "anomaly_type": result.anomaly_type,
            }
        )

        payload = {
            "symbol": symbol,
            "data_type": self.data_type,
            "occurred_at": result.timestamp,
            "severity": result.severity,
            "anomaly_type": result.anomaly_type,
            "iso_score": result.iso_score,
            "prophet_score": result.prophet_score,
            "price_change_pct": result.price_change_pct,
            "volume_z_score": result.volume_z_score,
            "source": source,
            "message": self._build_message(symbol, result),
            "metadata": {"reasons": result.reasons},
        }

        if existing:
            for key, value in payload.items():
                setattr(existing, key, value)
            await existing.save()
            event = existing
        else:
            event = DataQualityEvent(**payload)
            await event.insert()

        if event.severity in {SeverityLevel.HIGH, SeverityLevel.CRITICAL}:
            await self._dispatch_webhook(event)

    async def _dispatch_webhook(self, event: DataQualityEvent) -> None:
        webhook_url = getattr(settings, "DATA_QUALITY_WEBHOOK_URL", None)
        if not webhook_url:
            return

        payload = {
            "symbol": event.symbol,
            "severity": event.severity.value,
            "occurred_at": event.occurred_at.isoformat(),
            "data_type": event.data_type,
            "message": event.message,
            "iso_score": event.iso_score,
            "prophet_score": event.prophet_score,
            "price_change_pct": event.price_change_pct,
            "volume_z_score": event.volume_z_score,
            "metadata": event.metadata,
        }

        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.post(webhook_url, json=payload)
                response.raise_for_status()
        except Exception as exc:  # pragma: no cover - network interaction
            logger.warning("Failed to dispatch data quality webhook: %s", exc)

    def _build_message(self, symbol: str, result: AnomalyResult) -> str:
        return (
            f"{symbol} {self.data_type} anomaly – severity {result.severity.value} "
            f"({result.anomaly_type}) | price_change={result.price_change_pct:.2f}% "
            f"volume_z={result.volume_z_score:.2f} iso={result.iso_score:.2f}"
        )


__all__ = [
    "DataQualitySentinel",
    "AlertPayload",
    "DataQualitySummaryPayload",
]
