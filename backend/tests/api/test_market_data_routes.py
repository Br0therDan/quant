"""API tests for the market data routes."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from types import SimpleNamespace
from typing import Any, Dict, List
from unittest.mock import AsyncMock

import pytest

from app.schemas.market_data.stock import QuoteData


def _make_price(day: int, *, close: float = 150.0, adjusted: float | None = None) -> SimpleNamespace:
    dt = datetime(2024, 1, day, tzinfo=UTC)
    adj = Decimal(str(adjusted if adjusted is not None else close))
    return SimpleNamespace(
        date=dt,
        open=Decimal("100"),
        high=Decimal("110"),
        low=Decimal("90"),
        close=Decimal(str(close)),
        adjusted_close=adj,
        volume=1_000,
        dividend_amount=Decimal("0"),
        split_coefficient=Decimal("1"),
    )


def _patch_stock_service(
    monkeypatch: pytest.MonkeyPatch,
    *,
    daily: List[Any] | None = None,
    weekly: List[Any] | None = None,
    monthly: List[Any] | None = None,
    quote: QuoteData | None = None,
    intraday: List[Any] | None = None,
) -> None:
    stock_service = SimpleNamespace(
        get_daily_prices=AsyncMock(return_value=daily or []),
        get_weekly_prices=AsyncMock(return_value=weekly or []),
        get_monthly_prices=AsyncMock(return_value=monthly or []),
        get_real_time_quote=AsyncMock(return_value=quote),
        get_intraday_data=AsyncMock(return_value=intraday or []),
    )

    market_service = SimpleNamespace(stock=stock_service)

    monkeypatch.setattr(
        "app.api.routes.market_data.stock.service_factory.get_market_data_service",
        lambda: market_service,
    )
    return None


def _patch_fundamental_service(
    monkeypatch: pytest.MonkeyPatch,
    *,
    overview: Any = None,
    income: List[Any] | None = None,
    balance: List[Any] | None = None,
    cash_flow: List[Any] | None = None,
    earnings: List[Any] | None = None,
) -> None:
    fundamental_service = SimpleNamespace(
        get_company_overview=AsyncMock(return_value=overview),
        get_income_statement=AsyncMock(return_value=income or []),
        get_balance_sheet=AsyncMock(return_value=balance or []),
        get_cash_flow=AsyncMock(return_value=cash_flow or []),
        get_earnings=AsyncMock(return_value=earnings or []),
    )

    market_service = SimpleNamespace(fundamental=fundamental_service)

    monkeypatch.setattr(
        "app.api.routes.market_data.fundamental.service_factory.get_fundamental_service",
        lambda: fundamental_service,
    )
    monkeypatch.setattr(
        "app.api.routes.market_data.fundamental.service_factory.get_market_data_service",
        lambda: market_service,
    )


def _patch_economic_service(
    monkeypatch: pytest.MonkeyPatch,
    *,
    gdp: List[Any] | None = None,
    inflation: List[Any] | None = None,
    interest: List[Any] | None = None,
    employment: List[Any] | None = None,
) -> None:
    economic_service = SimpleNamespace(
        get_gdp_data=AsyncMock(return_value=gdp or []),
        get_inflation_data=AsyncMock(return_value=inflation or []),
        get_interest_rates=AsyncMock(return_value=interest or []),
        get_employment_data=AsyncMock(return_value=employment or []),
    )

    market_service = SimpleNamespace(economic=economic_service)

    monkeypatch.setattr(
        "app.api.routes.market_data.economic_indicator.service_factory.get_economic_indicator_service",
        lambda: economic_service,
    )
    monkeypatch.setattr(
        "app.api.routes.market_data.economic_indicator.service_factory.get_market_data_service",
        lambda: market_service,
    )


@pytest.mark.asyncio
async def test_market_data_root_info(async_client: "AsyncClient", auth_headers: Dict[str, str]) -> None:
    response = await async_client.get("/api/v1/market-data/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Market Data API v2"
    assert "stock" in data["domains"]


@pytest.mark.asyncio
async def test_market_data_health(async_client: "AsyncClient", auth_headers: Dict[str, str]) -> None:
    response = await async_client.get("/api/v1/market-data/health", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_stock_daily_returns_data(
    async_client: "AsyncClient",
    auth_headers: Dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prices = [_make_price(1), _make_price(2)]
    _patch_stock_service(monkeypatch, daily=prices)

    response = await async_client.get(
        "/api/v1/market-data/stock/daily/AAPL",
        headers=auth_headers,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["symbol"] == "AAPL"
    assert payload["count"] == 2


@pytest.mark.asyncio
async def test_stock_daily_rejects_invalid_symbol(
    async_client: "AsyncClient",
    auth_headers: Dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_stock_service(monkeypatch)
    response = await async_client.get(
        "/api/v1/market-data/stock/daily/INVALID1",
        headers=auth_headers,
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_stock_daily_returns_404_when_missing(
    async_client: "AsyncClient",
    auth_headers: Dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_stock_service(monkeypatch, daily=[])

    response = await async_client.get(
        "/api/v1/market-data/stock/daily/AAPL",
        headers=auth_headers,
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_stock_daily_applies_date_filter(
    async_client: "AsyncClient",
    auth_headers: Dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prices = [_make_price(1), _make_price(5), _make_price(10)]
    _patch_stock_service(monkeypatch, daily=prices)

    response = await async_client.get(
        "/api/v1/market-data/stock/daily/AAPL",
        headers=auth_headers,
        params={"start_date": "2024-01-05", "end_date": "2024-01-10"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 2


@pytest.mark.asyncio
async def test_stock_weekly_returns_data(
    async_client: "AsyncClient",
    auth_headers: Dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prices = [_make_price(1), _make_price(8)]
    _patch_stock_service(monkeypatch, weekly=prices)

    response = await async_client.get(
        "/api/v1/market-data/stock/weekly/AAPL",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["count"] == 2


@pytest.mark.asyncio
async def test_stock_monthly_returns_data(
    async_client: "AsyncClient",
    auth_headers: Dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prices = [_make_price(1), _make_price(30)]
    _patch_stock_service(monkeypatch, monthly=prices)

    response = await async_client.get(
        "/api/v1/market-data/stock/monthly/AAPL",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["count"] == 2


@pytest.mark.asyncio
async def test_stock_quote_returns_payload(
    async_client: "AsyncClient",
    auth_headers: Dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    quote = QuoteData(
        symbol="AAPL",
        timestamp=datetime(2024, 1, 1, tzinfo=UTC),
        price=Decimal("123.45"),
    )
    _patch_stock_service(monkeypatch, quote=quote)

    response = await async_client.get(
        "/api/v1/market-data/stock/quote/AAPL",
        headers=auth_headers,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["symbol"] == "AAPL"


@pytest.mark.asyncio
async def test_stock_quote_returns_404_when_missing(
    async_client: "AsyncClient",
    auth_headers: Dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_stock_service(monkeypatch, quote=None)

    response = await async_client.get(
        "/api/v1/market-data/stock/quote/AAPL",
        headers=auth_headers,
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_stock_quote_handles_exception(
    async_client: "AsyncClient",
    auth_headers: Dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stock_service = SimpleNamespace(
        get_real_time_quote=AsyncMock(side_effect=RuntimeError("failure")),
    )
    monkeypatch.setattr(
        "app.api.routes.market_data.stock.service_factory.get_market_data_service",
        lambda: SimpleNamespace(stock=stock_service),
    )

    response = await async_client.get(
        "/api/v1/market-data/stock/quote/AAPL",
        headers=auth_headers,
    )

    assert response.status_code == 500


@pytest.mark.asyncio
async def test_stock_intraday_returns_data(
    async_client: "AsyncClient",
    auth_headers: Dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prices = [_make_price(1), _make_price(2)]
    _patch_stock_service(monkeypatch, intraday=prices)

    response = await async_client.get(
        "/api/v1/market-data/stock/intraday/AAPL",
        headers=auth_headers,
        params={"interval": "15min"},
    )

    assert response.status_code == 200
    assert response.json()["count"] == 2


@pytest.mark.asyncio
async def test_stock_intraday_returns_404_when_empty(
    async_client: "AsyncClient",
    auth_headers: Dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_stock_service(monkeypatch, intraday=[])

    response = await async_client.get(
        "/api/v1/market-data/stock/intraday/AAPL",
        headers=auth_headers,
        params={"interval": "15min"},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_stock_intraday_rejects_invalid_symbol(
    async_client: "AsyncClient", auth_headers: Dict[str, str]
) -> None:
    response = await async_client.get(
        "/api/v1/market-data/stock/intraday/INVALID1",
        headers=auth_headers,
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_fundamental_overview_returns_payload(
    async_client: "AsyncClient",
    auth_headers: Dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    overview = {
        "symbol": "AAPL",
        "name": "Apple",
        "exchange": "NASDAQ",
        "sector": "Technology",
        "industry": "Hardware",
        "description": "Company",
    }
    _patch_fundamental_service(monkeypatch, overview=overview)

    response = await async_client.get(
        "/api/v1/market-data/fundamental/overview/AAPL",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["data"]["symbol"] == "AAPL"


@pytest.mark.asyncio
async def test_fundamental_income_statement_returns_list(
    async_client: "AsyncClient",
    auth_headers: Dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    statements = [
        SimpleNamespace(
            model_dump=lambda: {
                "symbol": "AAPL",
                "fiscal_date_ending": "2023-12-31T00:00:00",
                "reported_currency": "USD",
            }
        )
    ]
    _patch_fundamental_service(monkeypatch, income=statements)

    response = await async_client.get(
        "/api/v1/market-data/fundamental/income-statement/AAPL",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["count"] == 1


@pytest.mark.asyncio
async def test_fundamental_income_statement_handles_exception(
    async_client: "AsyncClient",
    auth_headers: Dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def raise_error(*_args: Any, **_kwargs: Any) -> Any:
        raise RuntimeError("failure")

    fundamental_service = SimpleNamespace(get_income_statement=AsyncMock(side_effect=raise_error))
    market_service = SimpleNamespace(fundamental=fundamental_service)
    monkeypatch.setattr(
        "app.api.routes.market_data.fundamental.service_factory.get_market_data_service",
        lambda: market_service,
    )

    response = await async_client.get(
        "/api/v1/market-data/fundamental/income-statement/AAPL",
        headers=auth_headers,
    )

    assert response.status_code == 500


@pytest.mark.asyncio
async def test_fundamental_balance_sheet_returns_data(
    async_client: "AsyncClient",
    auth_headers: Dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sheets = [
        SimpleNamespace(
            model_dump=lambda: {
                "symbol": "AAPL",
                "fiscal_date_ending": "2023-12-31T00:00:00",
                "reported_currency": "USD",
            }
        )
    ]
    _patch_fundamental_service(monkeypatch, balance=sheets)

    response = await async_client.get(
        "/api/v1/market-data/fundamental/balance-sheet/AAPL",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["count"] == 1


@pytest.mark.asyncio
async def test_fundamental_cash_flow_returns_data(
    async_client: "AsyncClient",
    auth_headers: Dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    flows = [
        SimpleNamespace(
            model_dump=lambda: {
                "symbol": "AAPL",
                "fiscal_date_ending": "2023-12-31T00:00:00",
                "reported_currency": "USD",
            }
        )
    ]
    _patch_fundamental_service(monkeypatch, cash_flow=flows)

    response = await async_client.get(
        "/api/v1/market-data/fundamental/cash-flow/AAPL",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["count"] == 1


@pytest.mark.asyncio
async def test_fundamental_earnings_returns_data(
    async_client: "AsyncClient",
    auth_headers: Dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    earnings = [
        SimpleNamespace(
            model_dump=lambda: {
                "symbol": "AAPL",
                "fiscal_date_ending": "2023-12-31T00:00:00",
                "reported_eps": 1.23,
                "reported_date": "2024-01-31",
            }
        ),
        SimpleNamespace(
            model_dump=lambda: {
                "symbol": "AAPL",
                "fiscal_date_ending": "2023-09-30T00:00:00",
                "reported_eps": 1.1,
                "estimated_eps": 1.0,
                "reported_date": "2023-10-30",
            }
        ),
    ]
    _patch_fundamental_service(monkeypatch, earnings=earnings)

    response = await async_client.get(
        "/api/v1/market-data/fundamental/earnings/AAPL",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["count"] == 1


@pytest.mark.asyncio
async def test_economic_gdp_returns_payload(
    async_client: "AsyncClient",
    auth_headers: Dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_economic_service(monkeypatch, gdp=[{"date": "2023-12-31"}])

    response = await async_client.get(
        "/api/v1/market-data/economic_indicators/gdp",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.asyncio
async def test_economic_gdp_handles_exception(
    async_client: "AsyncClient",
    auth_headers: Dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    economic_service = SimpleNamespace(
        get_gdp_data=AsyncMock(side_effect=RuntimeError("failure"))
    )
    monkeypatch.setattr(
        "app.api.routes.market_data.economic_indicator.service_factory.get_economic_indicator_service",
        lambda: economic_service,
    )

    response = await async_client.get(
        "/api/v1/market-data/economic_indicators/gdp",
        headers=auth_headers,
    )

    assert response.status_code == 500


@pytest.mark.asyncio
async def test_economic_inflation_returns_payload(
    async_client: "AsyncClient",
    auth_headers: Dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_economic_service(monkeypatch, inflation=[{"date": "2023-12-31"}])

    response = await async_client.get(
        "/api/v1/market-data/economic_indicators/inflation",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.asyncio
async def test_economic_interest_rates_returns_payload(
    async_client: "AsyncClient",
    auth_headers: Dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    rates = [SimpleNamespace(model_dump=lambda: {"date": "2023-12-31"})]
    _patch_economic_service(monkeypatch, interest=rates)

    response = await async_client.get(
        "/api/v1/market-data/economic_indicators/interest-rates",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["metadata"]["count"] == 1


@pytest.mark.asyncio
async def test_economic_employment_returns_payload(
    async_client: "AsyncClient",
    auth_headers: Dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    employment = [SimpleNamespace(model_dump=lambda: {"date": "2023-12-31"})]
    _patch_economic_service(monkeypatch, employment=employment)

    response = await async_client.get(
        "/api/v1/market-data/economic_indicators/employment",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["metadata"]["count"] == 1

