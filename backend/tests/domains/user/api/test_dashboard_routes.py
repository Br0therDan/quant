"""API tests for dashboard user routes."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import ANY, AsyncMock

import pytest

from app.models.market_data.regime import MarketRegimeType
from app.schemas.ml_platform.predictive import (
    ForecastPercentileBand,
    MLSignalInsight,
    MarketRegimeSnapshot,
    PredictiveDashboardInsights,
    RegimeMetrics,
    SignalRecommendation,
    PortfolioForecastDistribution,
)
from app.schemas.user.dashboard import (
    DashboardSummary,
    DataQualityAlert,
    DataQualitySeverity,
    DataQualitySummary,
    PortfolioSummary,
    RecentActivity,
    StrategySummary,
)


@pytest.fixture
def dashboard_service_stub(monkeypatch: pytest.MonkeyPatch) -> SimpleNamespace:
    service = SimpleNamespace(
        get_dashboard_summary=AsyncMock(),
        get_portfolio_performance=AsyncMock(),
        get_strategy_comparison=AsyncMock(),
        get_recent_trades=AsyncMock(),
        get_watchlist_quotes=AsyncMock(),
        get_news_feed=AsyncMock(),
        get_economic_calendar=AsyncMock(),
        get_predictive_snapshot=AsyncMock(),
    )

    monkeypatch.setattr(
        "app.api.routes.user.dashboard.service_factory.get_dashboard_service",
        lambda: service,
    )
    return service


def _dashboard_summary(user_id: str) -> DashboardSummary:
    now = datetime.now(UTC)
    portfolio = PortfolioSummary(
        total_value=100_000.0,
        total_pnl=12_000.0,
        total_pnl_percentage=12.0,
        daily_pnl=500.0,
        daily_pnl_percentage=0.5,
    )
    strategies = StrategySummary(
        active_count=2,
        total_count=5,
        avg_success_rate=62.5,
        best_performing="alpha",
    )
    activity = RecentActivity(
        trades_count_today=3,
        backtests_count_week=1,
        last_login=now - timedelta(hours=2),
    )
    alert = DataQualityAlert(
        symbol="AAPL",
        data_type="daily",
        occurred_at=now,
        severity=DataQualitySeverity.HIGH,
        iso_score=3.2,
        prophet_score=2.1,
        price_change_pct=5.0,
        volume_z_score=1.3,
        message="Volume spike detected",
    )
    dq = DataQualitySummary(
        total_alerts=1,
        severity_breakdown={DataQualitySeverity.HIGH: 1},
        last_updated=now,
        recent_alerts=[alert],
    )
    return DashboardSummary(
        user_id=user_id,
        portfolio=portfolio,
        strategies=strategies,
        recent_activity=activity,
        data_quality=dq,
    )


def _predictive_snapshot(symbol: str) -> PredictiveDashboardInsights:
    now = datetime.now(UTC)
    insight = MLSignalInsight(
        symbol=symbol,
        as_of=now,
        lookback_days=30,
        probability=0.65,
        confidence=0.7,
        recommendation=SignalRecommendation.BUY,
        feature_contributions=[],
        top_signals=["Momentum strength"],
    )
    regime = MarketRegimeSnapshot(
        symbol=symbol,
        as_of=now,
        lookback_days=60,
        regime=MarketRegimeType.BULLISH,
        confidence=0.8,
        probabilities={MarketRegimeType.BULLISH: 0.8},
        metrics=RegimeMetrics(
            trailing_return_pct=12.0,
            volatility_pct=15.0,
            drawdown_pct=5.0,
            momentum_z=1.2,
        ),
        notes=["Breadth improving"],
    )
    forecast = PortfolioForecastDistribution(
        as_of=now,
        horizon_days=30,
        last_portfolio_value=100_000.0,
        expected_return_pct=5.0,
        expected_volatility_pct=12.0,
        percentile_bands=[
            ForecastPercentileBand(percentile=5, projected_value=95_000.0),
            ForecastPercentileBand(percentile=95, projected_value=110_000.0),
        ],
    )
    return PredictiveDashboardInsights(signal=insight, regime=regime, forecast=forecast)


@pytest.mark.asyncio
async def test_dashboard_summary_endpoint(async_client, auth_headers, dashboard_service_stub) -> None:
    summary = _dashboard_summary("user-1")
    dashboard_service_stub.get_dashboard_summary.return_value = summary

    response = await async_client.get(
        "/api/v1/dashboard/summary",
        headers=auth_headers,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["user_id"] == "user-1"
    dashboard_service_stub.get_dashboard_summary.assert_awaited_once()


@pytest.mark.asyncio
async def test_predictive_overview_endpoint(async_client, auth_headers, dashboard_service_stub) -> None:
    insights = _predictive_snapshot("AAPL")
    dashboard_service_stub.get_predictive_snapshot.return_value = insights

    response = await async_client.get(
        "/api/v1/dashboard/predictive/overview",
        headers=auth_headers,
        params={"symbol": "aapl", "horizon_days": 30},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["signal"]["symbol"] == "AAPL"
    dashboard_service_stub.get_predictive_snapshot.assert_awaited_once_with(
        ANY, "AAPL", horizon_days=30
    )
