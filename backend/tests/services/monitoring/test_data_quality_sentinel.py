"""Unit tests for the data quality sentinel monitoring service."""

from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any, Dict, Iterable, List
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.schemas.enums import SeverityLevel
from app.services.ml_platform.infrastructure.anomaly_detector import AnomalyResult
from app.services.monitoring import data_quality_sentinel
from app.services.monitoring.data_quality_sentinel import DataQualitySentinel


class StubQuery:
    """Minimal query builder stub that mirrors Beanie's chained API."""

    def __init__(self, results: Iterable[Any]) -> None:
        self._results = results

    def sort(self, *_args: Any, **_kwargs: Any) -> "StubQuery":
        return self

    def limit(self, *_args: Any, **_kwargs: Any) -> "StubQuery":
        return self

    async def to_list(self) -> List[Any]:
        return list(self._results)


class StubDataQualityEvent:
    """In-memory stand-in for the DataQualityEvent Beanie document."""

    find_one_result: Any | None = None
    find_one_calls: List[Dict[str, Any]] = []
    find_calls: List[Dict[str, Any]] = []
    find_results: Iterable[Any] = ()
    aggregate_results: List[Dict[str, Any]] = []
    aggregate_calls: List[List[Dict[str, Any]]] = []
    inserted_instances: List["StubDataQualityEvent"] = []
    saved_instances: List[Any] = []
    init_payloads: List[Dict[str, Any]] = []

    def __init__(self, **payload: Any) -> None:
        self.__dict__.update(payload)
        if "metadata" not in self.__dict__:
            self.metadata = {}
        StubDataQualityEvent.init_payloads.append(payload)

    async def insert(self) -> None:
        StubDataQualityEvent.inserted_instances.append(self)

    async def save(self) -> None:
        StubDataQualityEvent.saved_instances.append(self)

    @classmethod
    async def find_one(cls, query: Dict[str, Any]) -> Any | None:
        cls.find_one_calls.append(query)
        return cls.find_one_result

    @classmethod
    def find(cls, query: Dict[str, Any]) -> StubQuery:
        cls.find_calls.append(query)
        return StubQuery(cls.find_results)

    @classmethod
    def aggregate(cls, pipeline: List[Dict[str, Any]]):  # type: ignore[override]
        cls.aggregate_calls.append(pipeline)

        async def iterator():
            for bucket in cls.aggregate_results:
                yield bucket

        return iterator()

    @classmethod
    def reset(cls) -> None:
        cls.find_one_result = None
        cls.find_one_calls = []
        cls.find_calls = []
        cls.find_results = []
        cls.aggregate_results = []
        cls.aggregate_calls = []
        cls.inserted_instances = []
        cls.saved_instances = []
        cls.init_payloads = []


def _make_price_point(price_date: datetime) -> SimpleNamespace:
    return SimpleNamespace(
        date=price_date,
        iso_anomaly_score=None,
        prophet_anomaly_score=None,
        volume_z_score=None,
        anomaly_severity=None,
        anomaly_reasons=None,
    )


@pytest.mark.asyncio
async def test_evaluate_daily_prices_enriches_prices_and_persists(monkeypatch: pytest.MonkeyPatch) -> None:
    dt_high = datetime(2024, 1, 5, tzinfo=UTC)
    dt_normal = datetime(2024, 1, 6, tzinfo=UTC)
    price_high = _make_price_point(dt_high)
    price_normal = _make_price_point(dt_normal)

    high_result = AnomalyResult(
        timestamp=dt_high,
        iso_score=0.92,
        prophet_score=0.35,
        price_change_pct=3.8,
        volume_z_score=2.4,
        severity=SeverityLevel.HIGH,
        anomaly_type="volume_spike",
        reasons=["volume_z > 2"],
    )
    normal_result = AnomalyResult(
        timestamp=dt_normal,
        iso_score=0.05,
        prophet_score=None,
        price_change_pct=0.2,
        volume_z_score=0.1,
        severity=SeverityLevel.NORMAL,
        anomaly_type="stable",
        reasons=[],
    )

    mock_detector = MagicMock()
    mock_detector.score_daily_prices.return_value = {
        dt_high: high_result,
        dt_normal: normal_result,
    }

    sentinel = DataQualitySentinel(anomaly_detector=mock_detector)
    persist_mock = AsyncMock()
    monkeypatch.setattr(sentinel, "_persist_event", persist_mock)

    result = await sentinel.evaluate_daily_prices("AAPL", [price_high, price_normal])

    assert result == mock_detector.score_daily_prices.return_value
    assert price_high.iso_anomaly_score == pytest.approx(high_result.iso_score)
    assert price_high.prophet_anomaly_score == high_result.prophet_score
    assert price_high.volume_z_score == pytest.approx(high_result.volume_z_score)
    assert price_high.anomaly_severity == high_result.severity
    assert price_high.anomaly_reasons == high_result.reasons

    assert price_normal.iso_anomaly_score == pytest.approx(normal_result.iso_score)
    assert price_normal.anomaly_severity == normal_result.severity

    assert persist_mock.await_count == 1
    assert persist_mock.await_args_list[0].args == ("AAPL", high_result, "alpha_vantage")


@pytest.mark.asyncio
async def test_evaluate_daily_prices_returns_empty_when_no_prices(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_detector = MagicMock()
    sentinel = DataQualitySentinel(anomaly_detector=mock_detector)
    persist_mock = AsyncMock()
    monkeypatch.setattr(sentinel, "_persist_event", persist_mock)

    result = await sentinel.evaluate_daily_prices("AAPL", [])

    assert result == {}
    mock_detector.score_daily_prices.assert_not_called()
    assert persist_mock.await_count == 0


@pytest.mark.asyncio
async def test_get_recent_summary_builds_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    StubDataQualityEvent.reset()
    events = [
        SimpleNamespace(
            symbol="AAPL",
            data_type="daily",
            occurred_at=datetime(2024, 1, 8, tzinfo=UTC),
            severity=SeverityLevel.HIGH,
            iso_score=0.91,
            prophet_score=0.41,
            price_change_pct=4.2,
            volume_z_score=2.5,
            message="Volume spike detected",
            metadata={"reasons": ["volume"]},
        ),
        SimpleNamespace(
            symbol="MSFT",
            data_type="daily",
            occurred_at=datetime(2024, 1, 7, tzinfo=UTC),
            severity=SeverityLevel.CRITICAL,
            iso_score=0.97,
            prophet_score=0.55,
            price_change_pct=5.8,
            volume_z_score=3.1,
            message="Severe anomaly",
            metadata={"reasons": ["iso", "prophet"]},
        ),
    ]
    StubDataQualityEvent.find_results = events
    StubDataQualityEvent.aggregate_results = [
        {"_id": SeverityLevel.HIGH.value, "count": 1},
        {"_id": SeverityLevel.CRITICAL.value, "count": 1},
    ]
    monkeypatch.setattr(data_quality_sentinel, "DataQualityEvent", StubDataQualityEvent)

    fixed_now = datetime(2024, 1, 9, tzinfo=UTC)

    class FixedDateTime(datetime):
        @classmethod
        def now(cls, tz=None):  # type: ignore[override]
            if tz:
                return fixed_now
            return fixed_now.replace(tzinfo=None)

    monkeypatch.setattr(data_quality_sentinel, "datetime", FixedDateTime)

    sentinel = DataQualitySentinel()
    summary = await sentinel.get_recent_summary(lookback_hours=48, limit=2)

    assert summary.total_alerts == 2
    assert summary.severity_breakdown[SeverityLevel.HIGH] == 1
    assert summary.severity_breakdown[SeverityLevel.CRITICAL] == 1
    assert summary.last_updated == fixed_now
    assert [alert.symbol for alert in summary.recent_alerts] == ["AAPL", "MSFT"]
    assert summary.recent_alerts[0].iso_score == pytest.approx(events[0].iso_score)
    assert summary.recent_alerts[1].message == events[1].message


@pytest.mark.asyncio
async def test_persist_event_updates_existing_event(monkeypatch: pytest.MonkeyPatch) -> None:
    StubDataQualityEvent.reset()

    class ExistingEvent:
        def __init__(self) -> None:
            self.symbol = "AAPL"
            self.data_type = "daily"
            self.occurred_at = datetime(2024, 1, 1, tzinfo=UTC)
            self.severity = SeverityLevel.LOW
            self.anomaly_type = "volume_spike"
            self.iso_score = 0.1
            self.prophet_score = None
            self.price_change_pct = 0.5
            self.volume_z_score = 0.2
            self.source = "alpha_vantage"
            self.message = "Old message"
            self.metadata = {"reasons": []}
            self._saved = 0

        async def save(self) -> None:
            self._saved += 1

    existing_event = ExistingEvent()
    StubDataQualityEvent.find_one_result = existing_event
    monkeypatch.setattr(data_quality_sentinel, "DataQualityEvent", StubDataQualityEvent)

    sentinel = DataQualitySentinel()
    dispatch_mock = AsyncMock()
    monkeypatch.setattr(sentinel, "_dispatch_webhook", dispatch_mock)

    result = AnomalyResult(
        timestamp=datetime(2024, 1, 2, tzinfo=UTC),
        iso_score=0.81,
        prophet_score=0.43,
        price_change_pct=2.6,
        volume_z_score=1.3,
        severity=SeverityLevel.MEDIUM,
        anomaly_type="price_spike",
        reasons=["iso > 0.8"],
    )

    await sentinel._persist_event("AAPL", result, source="alpha_vantage")

    assert existing_event.severity == result.severity
    assert existing_event.iso_score == result.iso_score
    assert existing_event.prophet_score == result.prophet_score
    assert existing_event.price_change_pct == result.price_change_pct
    assert existing_event.volume_z_score == result.volume_z_score
    assert existing_event.message == sentinel._build_message("AAPL", result)
    assert existing_event.metadata == {"reasons": result.reasons}
    assert existing_event._saved == 1
    dispatch_mock.assert_not_called()


@pytest.mark.asyncio
async def test_persist_event_inserts_new_event_and_dispatches_webhook(monkeypatch: pytest.MonkeyPatch) -> None:
    StubDataQualityEvent.reset()
    StubDataQualityEvent.find_one_result = None
    monkeypatch.setattr(data_quality_sentinel, "DataQualityEvent", StubDataQualityEvent)

    sentinel = DataQualitySentinel()
    dispatch_mock = AsyncMock()
    monkeypatch.setattr(sentinel, "_dispatch_webhook", dispatch_mock)

    result = AnomalyResult(
        timestamp=datetime(2024, 1, 3, tzinfo=UTC),
        iso_score=0.95,
        prophet_score=0.52,
        price_change_pct=4.7,
        volume_z_score=3.2,
        severity=SeverityLevel.CRITICAL,
        anomaly_type="volume_spike",
        reasons=["volume_z > 3"],
    )

    await sentinel._persist_event("MSFT", result, source="ingestion")

    assert len(StubDataQualityEvent.inserted_instances) == 1
    inserted_event = StubDataQualityEvent.inserted_instances[0]
    assert inserted_event.symbol == "MSFT"
    assert inserted_event.data_type == sentinel.data_type
    assert inserted_event.iso_score == result.iso_score
    assert inserted_event.price_change_pct == result.price_change_pct
    assert inserted_event.source == "ingestion"
    assert inserted_event.message == sentinel._build_message("MSFT", result)
    assert inserted_event.metadata == {"reasons": result.reasons}

    assert dispatch_mock.await_count == 1
    assert dispatch_mock.await_args_list[0].args == (inserted_event,)


@pytest.mark.asyncio
async def test_dispatch_webhook_sends_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    sentinel = DataQualitySentinel()
    monkeypatch.setattr(data_quality_sentinel.settings, "DATA_QUALITY_WEBHOOK_URL", "https://example.com/webhook")

    captured: Dict[str, Any] = {}

    class DummyResponse:
        def raise_for_status(self) -> None:
            captured["raised"] = True

    class DummyClient:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            captured["timeout"] = kwargs.get("timeout")

        async def __aenter__(self) -> "DummyClient":
            return self

        async def __aexit__(self, _exc_type, _exc, _tb) -> None:
            return None

        async def post(self, url: str, json: Dict[str, Any]) -> DummyResponse:
            captured["url"] = url
            captured["json"] = json
            return DummyResponse()

    monkeypatch.setattr(data_quality_sentinel.httpx, "AsyncClient", DummyClient)

    event = SimpleNamespace(
        symbol="AAPL",
        severity=SeverityLevel.HIGH,
        occurred_at=datetime(2024, 1, 4, tzinfo=UTC),
        data_type="daily",
        message="Alert triggered",
        iso_score=0.93,
        prophet_score=None,
        price_change_pct=3.1,
        volume_z_score=2.0,
        metadata={"reasons": ["volume"]},
    )

    await sentinel._dispatch_webhook(event)

    assert captured["url"] == "https://example.com/webhook"
    assert captured["json"]["symbol"] == "AAPL"
    assert captured["json"]["severity"] == SeverityLevel.HIGH.value
    assert captured["json"]["metadata"] == event.metadata
    assert captured["timeout"] == 5
    assert captured["raised"] is True


@pytest.mark.asyncio
async def test_dispatch_webhook_noop_when_url_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    sentinel = DataQualitySentinel()
    monkeypatch.setattr(data_quality_sentinel.settings, "DATA_QUALITY_WEBHOOK_URL", None)

    called = False

    class FailingClient:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            nonlocal called
            called = True

    monkeypatch.setattr(data_quality_sentinel.httpx, "AsyncClient", FailingClient)

    event = SimpleNamespace(
        symbol="AAPL",
        severity=SeverityLevel.HIGH,
        occurred_at=datetime(2024, 1, 4, tzinfo=UTC),
        data_type="daily",
        message="Alert",
        iso_score=0.93,
        prophet_score=None,
        price_change_pct=3.1,
        volume_z_score=2.0,
        metadata={},
    )

    await sentinel._dispatch_webhook(event)

    assert called is False
