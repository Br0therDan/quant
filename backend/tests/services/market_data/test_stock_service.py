"""Unit tests for :mod:`app.services.market_data.stock`.

These tests focus on the orchestration that :class:`StockService` performs
between its helper components (storage, coverage, cache) rather than the
external APIs or database implementations.  Every dependency is replaced with
async-friendly stubs so that we can exercise the decision logic in isolation.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace
from typing import Any, Iterable, List
from unittest.mock import AsyncMock, ANY

import pytest

import app.services.market_data.stock as stock_module
from app.schemas.market_data.stock import QuoteData
from app.services.market_data.stock import StockService


class _FindQuery:
    """Lightweight stand-in for Beanie's chained query helpers."""

    def __init__(self, results: Iterable[Any]) -> None:
        self._results = list(results)

    def sort(self, *_args: Any, **_kwargs: Any) -> "_FindQuery":
        return self

    async def to_list(self) -> List[Any]:
        return list(self._results)


@dataclass
class _CoverageStub:
    symbol: str
    data_type: str
    last_full_update: datetime | None = None
    last_delta_update: datetime | None = None


@pytest.fixture
def stock_service(monkeypatch: pytest.MonkeyPatch) -> StockService:
    """Return a ``StockService`` instance with dependencies patched."""

    service = StockService()

    service._fetcher = SimpleNamespace(  # type: ignore[attr-defined]
        fetch_quote=AsyncMock(name="fetch_quote"),
        fetch_intraday=AsyncMock(name="fetch_intraday"),
        fetch_historical=AsyncMock(name="fetch_historical"),
        search_symbols=AsyncMock(name="search_symbols"),
    )

    service._storage = SimpleNamespace(  # type: ignore[attr-defined]
        store_daily_prices=AsyncMock(name="store_daily_prices"),
        store_weekly_prices=AsyncMock(name="store_weekly_prices"),
        store_monthly_prices=AsyncMock(name="store_monthly_prices"),
    )

    service._coverage = SimpleNamespace(  # type: ignore[attr-defined]
        get_or_create_coverage=AsyncMock(name="get_or_create_coverage"),
        update_coverage=AsyncMock(name="update_coverage"),
    )

    service._cache = SimpleNamespace(  # type: ignore[attr-defined]
        _fetch_from_source=AsyncMock(name="_fetch_from_source"),
        _save_to_cache=AsyncMock(name="_save_to_cache"),
        _get_from_cache=AsyncMock(name="_get_from_cache"),
    )

    monkeypatch.setattr(service, "get_data_with_unified_cache", AsyncMock())
    return service


def _patch_find(monkeypatch: pytest.MonkeyPatch, attr: str, results: Iterable[Any]) -> None:
    """Patch ``DailyPrice.find``/``WeeklyPrice.find`` helpers with stub data."""

    monkeypatch.setattr(getattr(stock_module, attr), "find", lambda *_args, **_kwargs: _FindQuery(results))


def _make_price(day: int, close: float = 150.0) -> SimpleNamespace:
    dt = datetime(2024, 1, day, tzinfo=UTC)
    return SimpleNamespace(
        symbol="AAPL",
        date=dt,
        open=Decimal("100"),
        high=Decimal("110"),
        low=Decimal("90"),
        close=Decimal(str(close)),
        volume=1_000,
        adjusted_close=Decimal(str(close)),
        dividend_amount=Decimal("0"),
        split_coefficient=Decimal("1"),
    )


@pytest.mark.asyncio
async def test_get_daily_prices_performs_full_update_when_missing_cache(
    stock_service: StockService, monkeypatch: pytest.MonkeyPatch
) -> None:
    coverage = _CoverageStub("AAPL", "daily", last_full_update=None)
    stock_service._coverage.get_or_create_coverage.return_value = coverage  # type: ignore[attr-defined]
    stock_service._storage.store_daily_prices.return_value = [_make_price(1)]  # type: ignore[attr-defined]

    _patch_find(monkeypatch, "DailyPrice", [])

    prices = await stock_service.get_daily_prices("AAPL")

    stock_service._storage.store_daily_prices.assert_awaited_once_with("AAPL", adjusted=True, is_full=True)  # type: ignore[attr-defined]
    stock_service._coverage.update_coverage.assert_awaited_once()  # type: ignore[attr-defined]
    assert prices == stock_service._storage.store_daily_prices.return_value  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_get_daily_prices_uses_cached_data_when_recent(
    stock_service: StockService, monkeypatch: pytest.MonkeyPatch
) -> None:
    last_update = datetime.now(UTC) - timedelta(days=2)
    coverage = _CoverageStub("AAPL", "daily", last_full_update=last_update)
    stock_service._coverage.get_or_create_coverage.return_value = coverage  # type: ignore[attr-defined]

    existing = [_make_price(1), _make_price(2)]
    _patch_find(monkeypatch, "DailyPrice", existing)

    prices = await stock_service.get_daily_prices("AAPL")

    stock_service._storage.store_daily_prices.assert_not_awaited()  # type: ignore[attr-defined]
    assert prices == existing


@pytest.mark.asyncio
async def test_get_daily_prices_triggers_update_for_stale_naive_timestamp(
    stock_service: StockService, monkeypatch: pytest.MonkeyPatch
) -> None:
    last_update = datetime.now() - timedelta(days=10)  # naive datetime
    coverage = _CoverageStub("AAPL", "daily", last_full_update=last_update)
    stock_service._coverage.get_or_create_coverage.return_value = coverage  # type: ignore[attr-defined]
    stock_service._storage.store_daily_prices.return_value = [_make_price(3)]  # type: ignore[attr-defined]

    _patch_find(monkeypatch, "DailyPrice", [_make_price(1)])

    await stock_service.get_daily_prices("AAPL")

    stock_service._storage.store_daily_prices.assert_awaited_once()  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_get_daily_prices_returns_empty_when_storage_yields_none(
    stock_service: StockService, monkeypatch: pytest.MonkeyPatch
) -> None:
    coverage = _CoverageStub("AAPL", "daily", last_full_update=None)
    stock_service._coverage.get_or_create_coverage.return_value = coverage  # type: ignore[attr-defined]
    stock_service._storage.store_daily_prices.return_value = None  # type: ignore[attr-defined]

    _patch_find(monkeypatch, "DailyPrice", [])

    prices = await stock_service.get_daily_prices("AAPL")

    assert prices == []
    stock_service._coverage.update_coverage.assert_not_awaited()  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_get_daily_prices_does_not_update_coverage_when_no_prices(
    stock_service: StockService, monkeypatch: pytest.MonkeyPatch
) -> None:
    coverage = _CoverageStub("AAPL", "daily", last_full_update=None)
    stock_service._coverage.get_or_create_coverage.return_value = coverage  # type: ignore[attr-defined]
    stock_service._storage.store_daily_prices.return_value = []  # type: ignore[attr-defined]

    _patch_find(monkeypatch, "DailyPrice", [])

    await stock_service.get_daily_prices("AAPL")

    stock_service._coverage.update_coverage.assert_not_awaited()  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_get_weekly_prices_performs_full_update(
    stock_service: StockService, monkeypatch: pytest.MonkeyPatch
) -> None:
    coverage = _CoverageStub("AAPL", "weekly", last_full_update=None)
    stock_service._coverage.get_or_create_coverage.return_value = coverage  # type: ignore[attr-defined]
    stock_service._storage.store_weekly_prices.return_value = [_make_price(1)]  # type: ignore[attr-defined]

    _patch_find(monkeypatch, "WeeklyPrice", [])

    prices = await stock_service.get_weekly_prices("AAPL")

    stock_service._storage.store_weekly_prices.assert_awaited_once_with("AAPL", adjusted=True)  # type: ignore[attr-defined]
    stock_service._coverage.update_coverage.assert_awaited_once()  # type: ignore[attr-defined]
    assert prices == stock_service._storage.store_weekly_prices.return_value  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_get_weekly_prices_uses_cached_data_when_recent(
    stock_service: StockService, monkeypatch: pytest.MonkeyPatch
) -> None:
    coverage = _CoverageStub("AAPL", "weekly", last_full_update=datetime.now(UTC))
    stock_service._coverage.get_or_create_coverage.return_value = coverage  # type: ignore[attr-defined]
    weekly_prices = [_make_price(1), _make_price(2)]

    _patch_find(monkeypatch, "WeeklyPrice", weekly_prices)

    prices = await stock_service.get_weekly_prices("AAPL")

    stock_service._storage.store_weekly_prices.assert_not_awaited()  # type: ignore[attr-defined]
    assert prices == weekly_prices


@pytest.mark.asyncio
async def test_get_weekly_prices_returns_empty_when_storage_none(
    stock_service: StockService, monkeypatch: pytest.MonkeyPatch
) -> None:
    coverage = _CoverageStub("AAPL", "weekly", last_full_update=None)
    stock_service._coverage.get_or_create_coverage.return_value = coverage  # type: ignore[attr-defined]
    stock_service._storage.store_weekly_prices.return_value = None  # type: ignore[attr-defined]

    _patch_find(monkeypatch, "WeeklyPrice", [])

    prices = await stock_service.get_weekly_prices("AAPL")

    assert prices == []


@pytest.mark.asyncio
async def test_get_monthly_prices_performs_full_update(
    stock_service: StockService, monkeypatch: pytest.MonkeyPatch
) -> None:
    coverage = _CoverageStub("AAPL", "monthly", last_full_update=None)
    stock_service._coverage.get_or_create_coverage.return_value = coverage  # type: ignore[attr-defined]
    stock_service._storage.store_monthly_prices.return_value = [_make_price(1)]  # type: ignore[attr-defined]

    _patch_find(monkeypatch, "MonthlyPrice", [])

    prices = await stock_service.get_monthly_prices("AAPL")

    stock_service._storage.store_monthly_prices.assert_awaited_once_with("AAPL", adjusted=True)  # type: ignore[attr-defined]
    stock_service._coverage.update_coverage.assert_awaited_once()  # type: ignore[attr-defined]
    assert prices == stock_service._storage.store_monthly_prices.return_value  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_get_monthly_prices_uses_cached_data_when_recent(
    stock_service: StockService, monkeypatch: pytest.MonkeyPatch
) -> None:
    coverage = _CoverageStub("AAPL", "monthly", last_full_update=datetime.now(UTC))
    stock_service._coverage.get_or_create_coverage.return_value = coverage  # type: ignore[attr-defined]
    monthly_prices = [_make_price(1), _make_price(5)]

    _patch_find(monkeypatch, "MonthlyPrice", monthly_prices)

    prices = await stock_service.get_monthly_prices("AAPL")

    stock_service._storage.store_monthly_prices.assert_not_awaited()  # type: ignore[attr-defined]
    assert prices == monthly_prices


@pytest.mark.asyncio
async def test_get_monthly_prices_returns_empty_when_storage_none(
    stock_service: StockService, monkeypatch: pytest.MonkeyPatch
) -> None:
    coverage = _CoverageStub("AAPL", "monthly", last_full_update=None)
    stock_service._coverage.get_or_create_coverage.return_value = coverage  # type: ignore[attr-defined]
    stock_service._storage.store_monthly_prices.return_value = None  # type: ignore[attr-defined]

    _patch_find(monkeypatch, "MonthlyPrice", [])

    prices = await stock_service.get_monthly_prices("AAPL")

    assert prices == []


@pytest.mark.asyncio
async def test_get_real_time_quote_force_refresh_bypasses_cache(
    stock_service: StockService
) -> None:
    stock_service._fetcher.fetch_quote.return_value = QuoteData(  # type: ignore[attr-defined]
        symbol="AAPL",
        timestamp=datetime.now(UTC),
        price=Decimal("123.45"),
    )

    quote = await stock_service.get_real_time_quote("AAPL", force_refresh=True)

    stock_service.get_data_with_unified_cache.assert_not_awaited()
    stock_service._fetcher.fetch_quote.assert_awaited_once_with("AAPL")  # type: ignore[attr-defined]
    assert isinstance(quote, QuoteData)


@pytest.mark.asyncio
async def test_get_real_time_quote_returns_cached_instance(stock_service: StockService) -> None:
    cached_quote = QuoteData(symbol="AAPL", timestamp=datetime.now(UTC), price=Decimal("150.0"))
    stock_service.get_data_with_unified_cache.return_value = [cached_quote]

    quote = await stock_service.get_real_time_quote("AAPL")

    assert quote is cached_quote
    stock_service._fetcher.fetch_quote.assert_not_awaited()  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_get_real_time_quote_converts_dict(stock_service: StockService) -> None:
    stock_service.get_data_with_unified_cache.return_value = [
        {"symbol": "AAPL", "timestamp": datetime.now(UTC), "price": Decimal("99.5")}
    ]

    quote = await stock_service.get_real_time_quote("AAPL")

    assert isinstance(quote, QuoteData)
    assert quote.symbol == "AAPL"


@pytest.mark.asyncio
async def test_get_real_time_quote_falls_back_on_cache_error(stock_service: StockService) -> None:
    stock_service.get_data_with_unified_cache.side_effect = RuntimeError("cache error")
    fallback = QuoteData(symbol="AAPL", timestamp=datetime.now(UTC), price=Decimal("88.1"))
    stock_service._fetcher.fetch_quote.return_value = fallback  # type: ignore[attr-defined]

    quote = await stock_service.get_real_time_quote("AAPL")

    assert quote is fallback


@pytest.mark.asyncio
async def test_get_intraday_data_uses_interval_specific_ttl(stock_service: StockService) -> None:
    stock_service.get_data_with_unified_cache.return_value = []

    await stock_service.get_intraday_data("AAPL", interval="1min")

    stock_service.get_data_with_unified_cache.assert_awaited_with(
        cache_key="intraday_AAPL_1min_False_False_full_latest",
        model_class=stock_module.DailyPrice,
        data_type="stock_intraday",
        symbol="AAPL",
        refresh_callback=ANY,
        ttl_hours=1,
    )


@pytest.mark.asyncio
async def test_get_intraday_data_defaults_to_four_hour_ttl(stock_service: StockService) -> None:
    stock_service.get_data_with_unified_cache.reset_mock()
    stock_service.get_data_with_unified_cache.return_value = []

    await stock_service.get_intraday_data("AAPL", interval="custom")

    assert stock_service.get_data_with_unified_cache.call_args.kwargs["ttl_hours"] == 4


@pytest.mark.asyncio
async def test_get_intraday_data_returns_cached_list(stock_service: StockService) -> None:
    sample = [_make_price(1)]
    stock_service.get_data_with_unified_cache.return_value = sample

    data = await stock_service.get_intraday_data("AAPL")

    assert data == sample


@pytest.mark.asyncio
async def test_get_historical_data_delegates_to_fetcher(stock_service: StockService) -> None:
    stock_service._fetcher.fetch_historical.return_value = {"prices": []}  # type: ignore[attr-defined]

    result = await stock_service.get_historical_data("AAPL")

    stock_service._fetcher.fetch_historical.assert_awaited_once_with("AAPL", None, None)  # type: ignore[attr-defined]
    assert result == {"prices": []}


@pytest.mark.asyncio
async def test_search_symbols_delegates_to_fetcher(stock_service: StockService) -> None:
    stock_service._fetcher.search_symbols.return_value = {"bestMatches": []}  # type: ignore[attr-defined]

    result = await stock_service.search_symbols("apple")

    stock_service._fetcher.search_symbols.assert_awaited_once_with("apple")  # type: ignore[attr-defined]
    assert result == {"bestMatches": []}


