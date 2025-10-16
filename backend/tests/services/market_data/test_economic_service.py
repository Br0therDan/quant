"""Tests for :mod:`app.services.market_data.economic_indicator`."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from typing import Any, Dict, Iterable, List
from unittest.mock import AsyncMock, ANY

import pytest

import app.services.market_data.economic_indicator as economic_module
from app.services.market_data.economic_indicator import EconomicIndicatorService


@pytest.fixture
def economic_service(monkeypatch: pytest.MonkeyPatch) -> EconomicIndicatorService:
    service = EconomicIndicatorService()
    service._alpha_vantage_client = SimpleNamespace(  # type: ignore[attr-defined]
        economic_indicators=SimpleNamespace(
            real_gdp=AsyncMock(name="real_gdp"),
            inflation=AsyncMock(name="inflation"),
            federal_funds_rate=AsyncMock(name="federal_funds_rate"),
            unemployment=AsyncMock(name="unemployment"),
        )
    )

    monkeypatch.setattr(service, "get_data_with_unified_cache", AsyncMock())
    return service


def _patch_model(monkeypatch: pytest.MonkeyPatch, name: str) -> List[Dict[str, Any]]:
    captured: List[Dict[str, Any]] = []

    class _Stub:
        def __init__(self, **payload: Any) -> None:
            captured.append(payload)

    monkeypatch.setattr(economic_module, name, _Stub)
    return captured


@pytest.mark.asyncio
async def test_get_gdp_data_invokes_cache(economic_service: EconomicIndicatorService) -> None:
    economic_service.get_data_with_unified_cache.return_value = []

    await economic_service.get_gdp_data(country="USA", period="annual")

    economic_service.get_data_with_unified_cache.assert_awaited_with(
        cache_key="gdp_data_USA_annual",
        model_class=economic_module.GDP,
        data_type="gdp",
        symbol="USA",
        refresh_callback=ANY,
        ttl_hours=168,
    )


@pytest.mark.asyncio
async def test_fetch_gdp_from_alpha_vantage_transforms_payload(
    economic_service: EconomicIndicatorService, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured = _patch_model(monkeypatch, "GDP")
    economic_service._alpha_vantage_client.economic_indicators.real_gdp.return_value = [  # type: ignore[attr-defined]
        {"data": [{"date": "2023-12-31", "value": "22.5"}]}
    ]

    records = await economic_service._fetch_gdp_from_alpha_vantage("USA", "annual")

    assert len(captured) == 1
    assert len(records) == 1
    assert isinstance(records[0], economic_module.GDP)


@pytest.mark.asyncio
async def test_fetch_gdp_from_alpha_vantage_handles_invalid_payload(
    economic_service: EconomicIndicatorService,
) -> None:
    economic_service._alpha_vantage_client.economic_indicators.real_gdp.return_value = [{}]  # type: ignore[attr-defined]

    records = await economic_service._fetch_gdp_from_alpha_vantage("USA", "annual")

    assert records == []


@pytest.mark.asyncio
async def test_get_inflation_data_invokes_cache(
    economic_service: EconomicIndicatorService,
) -> None:
    economic_service.get_data_with_unified_cache.return_value = []

    await economic_service.get_inflation_data(country="USA", indicator_type="CPI")

    economic_service.get_data_with_unified_cache.assert_awaited_with(
        cache_key="inflation_data_USA_CPI",
        model_class=economic_module.Inflation,
        data_type="inflation",
        symbol="USA",
        refresh_callback=ANY,
        ttl_hours=48,
    )


@pytest.mark.asyncio
async def test_fetch_inflation_from_alpha_vantage_transforms_payload(
    economic_service: EconomicIndicatorService, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured = _patch_model(monkeypatch, "Inflation")
    economic_service._alpha_vantage_client.economic_indicators.inflation.return_value = [  # type: ignore[attr-defined]
        {"data": [{"date": "2023-12-31", "value": "3.5"}]}
    ]

    records = await economic_service._fetch_inflation_from_alpha_vantage("USA", "CPI")

    assert len(captured) == 1
    assert len(records) == 1
    assert isinstance(records[0], economic_module.Inflation)


@pytest.mark.asyncio
async def test_get_interest_rates_invokes_cache(
    economic_service: EconomicIndicatorService,
) -> None:
    economic_service.get_data_with_unified_cache.return_value = []

    await economic_service.get_interest_rates(country="USA", rate_type="FEDERAL_FUNDS_RATE")

    economic_service.get_data_with_unified_cache.assert_awaited_with(
        cache_key="interest_rates_USA_FEDERAL_FUNDS_RATE",
        model_class=economic_module.InterestRate,
        data_type="interest_rate",
        symbol="USA",
        refresh_callback=ANY,
        ttl_hours=24,
    )


@pytest.mark.asyncio
async def test_fetch_interest_rates_from_alpha_vantage_transforms_payload(
    economic_service: EconomicIndicatorService, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured = _patch_model(monkeypatch, "InterestRate")
    economic_service._alpha_vantage_client.economic_indicators.federal_funds_rate.return_value = [  # type: ignore[attr-defined]
        {"data": [{"date": "2023-12-31", "value": "5.25"}]}
    ]

    records = await economic_service._fetch_interest_rates_from_alpha_vantage(
        "USA", "FEDERAL_FUNDS_RATE"
    )

    assert len(captured) == 1
    assert len(records) == 1
    assert isinstance(records[0], economic_module.InterestRate)


@pytest.mark.asyncio
async def test_get_employment_data_invokes_cache(
    economic_service: EconomicIndicatorService,
) -> None:
    economic_service.get_data_with_unified_cache.return_value = []

    await economic_service.get_employment_data(country="USA")

    economic_service.get_data_with_unified_cache.assert_awaited_with(
        cache_key="employment_data_USA",
        model_class=economic_module.Employment,
        data_type="employment",
        symbol="USA",
        refresh_callback=ANY,
        ttl_hours=48,
    )


@pytest.mark.asyncio
async def test_fetch_employment_from_alpha_vantage_transforms_payload(
    economic_service: EconomicIndicatorService, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured = _patch_model(monkeypatch, "Employment")
    economic_service._alpha_vantage_client.economic_indicators.unemployment.return_value = [  # type: ignore[attr-defined]
        {"data": [{"date": "2023-12-31", "value": "4.0"}]}
    ]

    records = await economic_service._fetch_employment_from_alpha_vantage("USA")

    assert len(captured) == 1
    assert len(records) == 1
    assert isinstance(records[0], economic_module.Employment)


@pytest.mark.asyncio
async def test_get_economic_calendar_filters_results(
    economic_service: EconomicIndicatorService,
) -> None:
    start = datetime(2025, 1, 1)
    end = datetime(2025, 1, 31)

    events = await economic_service.get_economic_calendar(start, end, importance="high")

    assert all(event["importance"] == "high" for event in events)
    assert all(start <= datetime.strptime(event["date"], "%Y-%m-%d") <= end for event in events)


@pytest.mark.asyncio
async def test_fetch_from_source_dispatches_to_real_gdp(
    economic_service: EconomicIndicatorService,
) -> None:
    await economic_service._fetch_from_source(method="real_gdp", interval="annual")

    economic_service._alpha_vantage_client.economic_indicators.real_gdp.assert_awaited_once()  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_fetch_from_source_raises_for_unknown_method(
    economic_service: EconomicIndicatorService,
) -> None:
    with pytest.raises(ValueError):
        await economic_service._fetch_from_source(method="unknown")


@pytest.mark.asyncio
async def test_refresh_data_from_source_returns_empty(
    economic_service: EconomicIndicatorService,
) -> None:
    assert await economic_service.refresh_data_from_source() == []


@pytest.mark.asyncio
async def test_fetch_interest_rates_handles_invalid_payload(
    economic_service: EconomicIndicatorService,
) -> None:
    economic_service._alpha_vantage_client.economic_indicators.federal_funds_rate.return_value = [{}]  # type: ignore[attr-defined]

    records = await economic_service._fetch_interest_rates_from_alpha_vantage("USA", "FEDERAL_FUNDS_RATE")

    assert records == []


@pytest.mark.asyncio
async def test_fetch_inflation_handles_invalid_payload(
    economic_service: EconomicIndicatorService,
) -> None:
    economic_service._alpha_vantage_client.economic_indicators.inflation.return_value = [{}]  # type: ignore[attr-defined]

    records = await economic_service._fetch_inflation_from_alpha_vantage("USA", "CPI")

    assert records == []

