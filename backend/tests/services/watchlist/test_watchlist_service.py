"""Watchlist service unit tests."""

from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock

import pytest

from app.services.watchlist_service import WatchlistService


class FakeWatchlist:
    """Simple in-memory stand-in for the Watchlist document."""

    def __init__(self, **kwargs: Any) -> None:
        self.__dict__.update(kwargs)
        self.insert_called = False
        self.save_called = False
        self.delete_called = False

    async def insert(self) -> None:
        self.insert_called = True

    async def save(self) -> None:
        self.save_called = True

    async def delete(self) -> None:
        self.delete_called = True


@pytest.fixture(autouse=True)
def patch_watchlist_model(monkeypatch: pytest.MonkeyPatch) -> None:
    """Replace the Watchlist ODM model with an in-memory fake."""

    monkeypatch.setattr("app.services.watchlist_service.Watchlist", FakeWatchlist)


@pytest.fixture
def service(monkeypatch: pytest.MonkeyPatch) -> WatchlistService:
    """Create a WatchlistService with internal helpers patched."""

    svc = WatchlistService()
    monkeypatch.setattr(svc, "_trigger_data_collection", AsyncMock())
    return svc


@pytest.mark.asyncio
async def test_create_watchlist_inserts_document(service: WatchlistService, monkeypatch: pytest.MonkeyPatch) -> None:
    """`create_watchlist` should insert a new document and normalize symbols."""

    monkeypatch.setattr(service, "get_watchlist", AsyncMock(return_value=None))

    created = await service.create_watchlist(
        name="tech",
        symbols=["aapl", "msft"],
        description="Tech leaders",
        user_id="user-1",
    )

    assert isinstance(created, FakeWatchlist)
    assert created.insert_called is True
    assert created.symbols == ["AAPL", "MSFT"]
    service._trigger_data_collection.assert_awaited_once_with(["AAPL", "MSFT"])


@pytest.mark.asyncio
async def test_create_watchlist_returns_none_when_duplicate(service: WatchlistService, monkeypatch: pytest.MonkeyPatch) -> None:
    """Duplicate watchlist names should return ``None`` without inserting."""

    monkeypatch.setattr(service, "get_watchlist", AsyncMock(return_value=FakeWatchlist(name="tech")))

    result = await service.create_watchlist(
        name="tech",
        symbols=["aapl"],
        description="",
        user_id="user-1",
    )

    assert result is None
    service._trigger_data_collection.assert_not_called()


@pytest.mark.asyncio
async def test_update_watchlist_persists_changes(service: WatchlistService, monkeypatch: pytest.MonkeyPatch) -> None:
    """Updating an existing watchlist should persist updates and normalize symbols."""

    existing = FakeWatchlist(
        name="tech",
        symbols=["AAPL"],
        description="Old",
        auto_update=True,
        update_interval=3600,
        updated_at=datetime.now(timezone.utc),
    )
    monkeypatch.setattr(service, "get_watchlist", AsyncMock(return_value=existing))

    updated = await service.update_watchlist(
        name="tech",
        user_id="user-1",
        symbols=["msft"],
        description="Updated",
        update_interval=7200,
    )

    assert updated is existing
    assert existing.save_called is True
    assert existing.symbols == ["MSFT"]
    assert existing.description == "Updated"
    assert existing.update_interval == 7200
    service._trigger_data_collection.assert_awaited_once_with(["MSFT"])


@pytest.mark.asyncio
async def test_update_watchlist_returns_none_when_missing(service: WatchlistService, monkeypatch: pytest.MonkeyPatch) -> None:
    """Attempting to update a missing watchlist should return ``None``."""

    monkeypatch.setattr(service, "get_watchlist", AsyncMock(return_value=None))

    result = await service.update_watchlist(name="unknown", user_id="user-1")

    assert result is None
    service._trigger_data_collection.assert_not_called()


@pytest.mark.asyncio
async def test_delete_watchlist_deletes_document(service: WatchlistService, monkeypatch: pytest.MonkeyPatch) -> None:
    """Deleting a watchlist should call the ODM delete helper."""

    existing = FakeWatchlist(name="tech")
    monkeypatch.setattr(service, "get_watchlist", AsyncMock(return_value=existing))

    assert await service.delete_watchlist("tech", "user-1") is True
    assert existing.delete_called is True


@pytest.mark.asyncio
async def test_delete_watchlist_returns_false_when_missing(service: WatchlistService, monkeypatch: pytest.MonkeyPatch) -> None:
    """Deleting a missing watchlist should return ``False``."""

    monkeypatch.setattr(service, "get_watchlist", AsyncMock(return_value=None))

    assert await service.delete_watchlist("tech", "user-1") is False


@pytest.mark.asyncio
async def test_get_watchlist_coverage_success(service: WatchlistService, monkeypatch: pytest.MonkeyPatch) -> None:
    """Coverage information should merge results from the market data service."""

    watchlist = FakeWatchlist(
        name="tech",
        symbols=["AAPL"],
        updated_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )
    monkeypatch.setattr(service, "get_watchlist", AsyncMock(return_value=watchlist))

    fundamental = SimpleNamespace(get_company_overview=AsyncMock(return_value={"symbol": "AAPL"}))
    stock = SimpleNamespace(get_daily_prices=AsyncMock(return_value=[{"close": 1.0}]))
    market_service = SimpleNamespace(fundamental=fundamental, stock=stock)
    monkeypatch.setattr(service, "_get_market_service", AsyncMock(return_value=market_service))

    coverage = await service.get_watchlist_coverage("tech", "user-1")

    assert coverage["watchlist_name"] == "tech"
    assert coverage["total_symbols"] == 1
    assert coverage["symbols_coverage"]["AAPL"]["status"] == "complete"
    fundamental.get_company_overview.assert_awaited_once_with("AAPL")
    stock.get_daily_prices.assert_awaited_once_with("AAPL", outputsize="compact")


@pytest.mark.asyncio
async def test_get_watchlist_coverage_handles_missing(service: WatchlistService, monkeypatch: pytest.MonkeyPatch) -> None:
    """Missing watchlists should return an error payload."""

    monkeypatch.setattr(service, "get_watchlist", AsyncMock(return_value=None))

    coverage = await service.get_watchlist_coverage("tech", "user-1")

    assert coverage == {"error": "Watchlist not found"}


@pytest.mark.asyncio
async def test_setup_default_watchlist_uses_defaults(service: WatchlistService, monkeypatch: pytest.MonkeyPatch) -> None:
    """The default watchlist helper should reuse `create_watchlist` with default symbols."""

    monkeypatch.setattr(service, "get_default_symbols", AsyncMock(return_value=["AAPL", "MSFT"]))
    created = FakeWatchlist(name="default", symbols=["AAPL", "MSFT"])
    monkeypatch.setattr(service, "create_watchlist", AsyncMock(return_value=created))

    result = await service.setup_default_watchlist("user-1")

    assert result is created
    service.create_watchlist.assert_awaited_once_with(
        name="default",
        symbols=["AAPL", "MSFT"],
        description="Default watchlist with popular stocks",
        user_id="user-1",
        auto_update=True,
    )
