"""Tests for :mod:`app.services.market_data.fundamental`."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace
from typing import Any, Dict, List
from unittest.mock import AsyncMock, ANY

import pytest

import app.services.market_data.fundamental as fundamental_module
from app.services.market_data.fundamental import FundamentalService


@pytest.fixture
def fundamental_service(monkeypatch: pytest.MonkeyPatch) -> FundamentalService:
    service = FundamentalService()

    service._alpha_vantage_client = SimpleNamespace(  # type: ignore[attr-defined]
        fundamental=SimpleNamespace(
            overview=AsyncMock(name="overview"),
            income_statement=AsyncMock(name="income_statement"),
            balance_sheet=AsyncMock(name="balance_sheet"),
            cash_flow=AsyncMock(name="cash_flow"),
            earnings=AsyncMock(name="earnings"),
        )
    )

    monkeypatch.setattr(service, "get_data_with_unified_cache", AsyncMock())
    monkeypatch.setattr(service, "_store_to_duckdb_cache", AsyncMock(return_value=True))
    service._db_manager = SimpleNamespace(  # type: ignore[attr-defined]
        store_cache_data=AsyncMock(return_value=True)
    )
    return service


def _patch_model(monkeypatch: pytest.MonkeyPatch, name: str) -> List[Dict[str, Any]]:
    captured: List[Dict[str, Any]] = []

    class _Stub:
        def __init__(self, **payload: Any) -> None:
            captured.append(payload)

    monkeypatch.setattr(fundamental_module, name, _Stub)
    return captured


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("123.45", Decimal("123.45")),
        (None, None),
        ("N/A", None),
        ("bad", None),
    ],
)
def test_to_decimal_handles_various_inputs(
    fundamental_service: FundamentalService, value: Any, expected: Any
) -> None:
    assert fundamental_service._to_decimal(value) == expected


@pytest.mark.asyncio
async def test_get_company_overview_returns_first_cached_entry(
    fundamental_service: FundamentalService, monkeypatch: pytest.MonkeyPatch
) -> None:
    class StubOverview:
        def __init__(self, **payload: Any) -> None:
            self.__dict__.update(payload)

    monkeypatch.setattr(fundamental_module, "CompanyOverview", StubOverview)
    overview = StubOverview(symbol="AAPL")
    fundamental_service.get_data_with_unified_cache.return_value = [overview]

    result = await fundamental_service.get_company_overview("AAPL")

    assert isinstance(result, StubOverview)


@pytest.mark.asyncio
async def test_get_company_overview_returns_none_for_invalid_cache(
    fundamental_service: FundamentalService,
) -> None:
    fundamental_service.get_data_with_unified_cache.return_value = ["unexpected"]

    result = await fundamental_service.get_company_overview("AAPL")

    assert result is None


@pytest.mark.asyncio
async def test_fetch_overview_from_alpha_vantage_builds_model(
    fundamental_service: FundamentalService, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured = _patch_model(monkeypatch, "CompanyOverview")
    payload = {
        "symbol": "AAPL",
        "name": "Apple",
        "description": "Tech",
        "market_capitalization": "150000000000",
    }
    fundamental_service._alpha_vantage_client.fundamental.overview.return_value = [  # type: ignore[attr-defined]
        payload
    ]

    result = await fundamental_service._fetch_overview_from_alpha_vantage("AAPL")

    assert captured[0]["symbol"] == "AAPL"
    assert isinstance(result, fundamental_module.CompanyOverview)


@pytest.mark.asyncio
async def test_fetch_overview_from_alpha_vantage_returns_none_when_empty(
    fundamental_service: FundamentalService,
) -> None:
    fundamental_service._alpha_vantage_client.fundamental.overview.return_value = [{}]  # type: ignore[attr-defined]

    result = await fundamental_service._fetch_overview_from_alpha_vantage("AAPL")

    assert result is None


@pytest.mark.asyncio
async def test_get_income_statement_invokes_cache(
    fundamental_service: FundamentalService,
) -> None:
    fundamental_service.get_data_with_unified_cache.return_value = []

    await fundamental_service.get_income_statement("AAPL", period="quarterly")

    fundamental_service.get_data_with_unified_cache.assert_awaited_with(
        cache_key="income_statement_AAPL_quarterly",
        model_class=fundamental_module.IncomeStatement,
        data_type="fundamental_income",
        symbol="AAPL",
        refresh_callback=ANY,
        ttl_hours=72,
    )


@pytest.mark.asyncio
async def test_fetch_income_statement_transforms_reports(
    fundamental_service: FundamentalService, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured = _patch_model(monkeypatch, "IncomeStatement")
    fundamental_service._alpha_vantage_client.fundamental.income_statement.return_value = [  # type: ignore[attr-defined]
        {
            "annual_reports": [
                {
                    "fiscalDateEnding": "2023-12-31",
                    "reportedCurrency": "USD",
                    "totalRevenue": "100",
                    "costOfRevenue": "50",
                    "grossProfit": "50",
                    "operatingExpenses": "10",
                    "operatingIncome": "40",
                    "interestIncome": "1",
                    "interestExpense": "2",
                    "incomeBeforeTax": "38",
                    "incomeTaxExpense": "8",
                    "netIncome": "30",
                    "eps": "1.50",
                    "dilutedEPS": "1.40",
                    "researchAndDevelopment": "5",
                }
            ]
        }
    ]

    statements = await fundamental_service._fetch_income_statement_from_alpha_vantage(
        "AAPL"
    )

    assert len(captured) == 1
    assert len(statements) == 1
    assert isinstance(statements[0], fundamental_module.IncomeStatement)


@pytest.mark.asyncio
async def test_fetch_balance_sheet_transforms_reports(
    fundamental_service: FundamentalService, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured = _patch_model(monkeypatch, "BalanceSheet")
    fundamental_service._alpha_vantage_client.fundamental.balance_sheet.return_value = [  # type: ignore[attr-defined]
        {
            "annual_reports": [
                {
                    "fiscalDateEnding": "2023-12-31",
                    "totalAssets": "100",
                    "totalLiabilities": "60",
                    "totalShareholderEquity": "40",
                    "commonStockSharesOutstanding": "100",
                }
            ]
        }
    ]

    sheets = await fundamental_service._fetch_balance_sheet_from_alpha_vantage("AAPL")

    assert len(captured) == 1
    assert len(sheets) == 1
    assert isinstance(sheets[0], fundamental_module.BalanceSheet)


@pytest.mark.asyncio
async def test_fetch_cash_flow_transforms_reports(
    fundamental_service: FundamentalService, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured = _patch_model(monkeypatch, "CashFlow")
    fundamental_service._alpha_vantage_client.fundamental.cash_flow.return_value = [  # type: ignore[attr-defined]
        {
            "annual_reports": [
                {
                    "fiscalDateEnding": "2023-12-31",
                    "operatingCashflow": "10",
                    "capitalExpenditures": "-3",
                }
            ]
        }
    ]

    flows = await fundamental_service._fetch_cash_flow_from_alpha_vantage("AAPL")

    assert len(captured) == 1
    assert len(flows) == 1
    assert isinstance(flows[0], fundamental_module.CashFlow)


@pytest.mark.asyncio
async def test_fetch_earnings_combines_annual_and_quarterly(
    fundamental_service: FundamentalService, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured = _patch_model(monkeypatch, "Earnings")
    fundamental_service._alpha_vantage_client.fundamental.earnings.return_value = [  # type: ignore[attr-defined]
        {
            "annual_earnings": [
                {"fiscalDateEnding": "2023-12-31", "reportedEPS": "5.0"}
            ],
            "quarterly_earnings": [
                {
                    "fiscalDateEnding": "2023-09-30",
                    "reportedEPS": "1.2",
                    "estimatedEPS": "1.0",
                    "surprise": "0.2",
                    "surprisePercentage": "5.0",
                    "reportedDate": "2023-10-25",
                }
            ],
        }
    ]

    earnings = await fundamental_service._fetch_earnings_from_alpha_vantage("AAPL")

    assert len(captured) == 2
    assert len(earnings) == 2
    for item in earnings:
        assert isinstance(item, fundamental_module.Earnings)


@pytest.mark.asyncio
async def test_calculate_financial_ratios_returns_metrics(
    fundamental_service: FundamentalService,
) -> None:
    @dataclass
    class StubOverview:
        pe_ratio: Decimal | None = Decimal("20")
        peg_ratio: Decimal | None = Decimal("1.5")
        book_value: Decimal | None = Decimal("4")
        dividend_yield: Decimal | None = Decimal("0.02")
        eps: Decimal | None = Decimal("5")
        profit_margin: Decimal | None = Decimal("0.3")
        operating_margin_ttm: Decimal | None = Decimal("0.25")
        return_on_assets_ttm: Decimal | None = Decimal("0.1")
        return_on_equity_ttm: Decimal | None = Decimal("0.2")
        revenue_per_share_ttm: Decimal | None = Decimal("12")
        beta: Decimal | None = Decimal("1.1")
        market_capitalization: Decimal | None = Decimal("200")
        revenue_ttm: Decimal | None = Decimal("100")
        shares_outstanding: int | None = 50
        fty: Decimal | None = Decimal("4")
        book_value_total: Decimal | None = Decimal("4")
        book_value_ratio: Decimal | None = Decimal("4")

    fundamental_service.get_company_overview = AsyncMock(return_value=StubOverview())  # type: ignore[assignment]

    ratios = await fundamental_service.calculate_financial_ratios("AAPL")

    assert "pe_ratio" in ratios
    assert ratios["price_to_sales"] == pytest.approx(2.0)


@pytest.mark.asyncio
async def test_calculate_financial_ratios_returns_empty_when_overview_missing(
    fundamental_service: FundamentalService,
) -> None:
    fundamental_service.get_company_overview = AsyncMock(return_value=None)  # type: ignore[assignment]

    ratios = await fundamental_service.calculate_financial_ratios("AAPL")

    assert ratios == {}


@pytest.mark.asyncio
async def test_fetch_from_source_dispatches_correct_method(
    fundamental_service: FundamentalService,
) -> None:
    await fundamental_service._fetch_from_source(method="balance_sheet", symbol="AAPL")

    fundamental_service._alpha_vantage_client.fundamental.balance_sheet.assert_awaited_once()  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_fetch_from_source_raises_for_unknown_method(
    fundamental_service: FundamentalService,
) -> None:
    with pytest.raises(ValueError):
        await fundamental_service._fetch_from_source(method="unknown", symbol="AAPL")


@pytest.mark.asyncio
async def test_save_to_cache_uses_duckdb_cache(
    fundamental_service: FundamentalService, monkeypatch: pytest.MonkeyPatch
) -> None:
    payload = {"Name": "Apple", "MarketCapitalization": "100"}
    fundamental_service._db_manager = SimpleNamespace(  # type: ignore[attr-defined]
        store_cache_data=lambda **_kwargs: True
    )
    _patch_model(monkeypatch, "CompanyOverview")
    monkeypatch.setattr(
        "app.models.market_data.fundamental.CompanyOverview",
        lambda **payload: SimpleNamespace(**payload),
    )

    success = await fundamental_service._save_to_cache(payload, cache_key="overview", symbol="AAPL")

    assert success is True
    fundamental_service._store_to_duckdb_cache.assert_awaited_once()  # type: ignore[attr-defined]

