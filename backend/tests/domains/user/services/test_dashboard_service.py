"""Tests for :mod:`app.services.user.dashboard_service`."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from typing import Any, Dict, Tuple

import pytest
from unittest.mock import AsyncMock, Mock

from app.schemas.user.dashboard import (
    DashboardSummary,
    DataQualityAlert,
    DataQualitySeverity,
    DataQualitySummary,
    PortfolioPerformance,
    PortfolioPerformanceSummary,
    PortfolioSummary,
    RecentActivity,
    RecentTrades,
    StrategyComparison,
    StrategyPerformanceItem,
    StrategyStatus,
    StrategySummary,
    SentimentType,
    ImportanceLevel,
    TradeItem,
    TradeSide,
    TradesSummary,
    NewsFeed,
    EconomicCalendar,
)
from app.schemas.ml_platform.predictive import (
    ForecastPercentileBand,
    MLSignalInsight,
    MarketRegimeSnapshot,
    PredictiveDashboardInsights,
    PortfolioForecastDistribution,
    RegimeMetrics,
    SignalRecommendation,
)
from app.services.monitoring.data_quality_sentinel import (
    AlertPayload,
    DataQualitySummaryPayload,
)
from app.services.user.dashboard_service import DashboardService
from app.schemas.enums.system import SeverityLevel
from app.models.market_data.regime import MarketRegimeType


@pytest.fixture
def service_with_mocks() -> Tuple[DashboardService, Dict[str, Any]]:
    """Create a :class:`DashboardService` with async dependencies patched."""

    portfolio_service = SimpleNamespace(
        get_portfolio_summary=AsyncMock(),
        get_recent_trades=AsyncMock(),
        get_portfolio_performance=AsyncMock(),
        get_probabilistic_forecast=AsyncMock(),
    )
    strategy_service = SimpleNamespace()
    backtest_service = SimpleNamespace()
    market_data_service = SimpleNamespace()
    watchlist_service = SimpleNamespace()
    ml_signal_service = SimpleNamespace(score_symbol=AsyncMock())
    regime_service = SimpleNamespace(
        get_latest_regime=AsyncMock(), refresh_regime=AsyncMock()
    )
    probabilistic_service = SimpleNamespace(forecast_from_history=AsyncMock())
    data_quality_sentinel = SimpleNamespace(get_recent_summary=AsyncMock())

    service = DashboardService(
        database_manager=Mock(),
        portfolio_service=portfolio_service,
        strategy_service=strategy_service,
        backtest_service=backtest_service,
        market_data_service=market_data_service,
        watchlist_service=watchlist_service,
        ml_signal_service=ml_signal_service,
        regime_service=regime_service,
        probabilistic_service=probabilistic_service,
        data_quality_sentinel=data_quality_sentinel,
    )

    return service, {
        "portfolio": portfolio_service,
        "ml_signal": ml_signal_service,
        "regime": regime_service,
        "probabilistic": probabilistic_service,
        "data_quality": data_quality_sentinel,
    }


@pytest.mark.asyncio
async def test_get_dashboard_summary_combines_sections(
    service_with_mocks: Tuple[DashboardService, Dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The dashboard summary should aggregate data from collaborating services."""

    service, deps = service_with_mocks

    portfolio_summary = PortfolioSummary(
        total_value=100_000,
        total_pnl=12_000,
        total_pnl_percentage=12.0,
        daily_pnl=500,
        daily_pnl_percentage=0.5,
    )
    deps["portfolio"].get_portfolio_summary.return_value = portfolio_summary

    strategy_summary = StrategySummary(
        active_count=2,
        total_count=5,
        avg_success_rate=62.5,
        best_performing="s-1",
    )
    monkeypatch.setattr(
        service,
        "_get_strategies_summary",
        AsyncMock(return_value=strategy_summary),
    )

    activity = RecentActivity(
        trades_count_today=3,
        backtests_count_week=1,
        last_login=datetime.now() - timedelta(hours=1),
    )
    monkeypatch.setattr(
        service,
        "_get_recent_activity",
        AsyncMock(return_value=activity),
    )

    alert = DataQualityAlert(
        symbol="AAPL",
        data_type="daily",
        occurred_at=datetime.now(UTC),
        severity=DataQualitySeverity.HIGH,
        iso_score=3.1,
        prophet_score=2.4,
        price_change_pct=5.5,
        volume_z_score=1.2,
        message="High variance",
    )
    dq_summary = DataQualitySummary(
        total_alerts=1,
        severity_breakdown={DataQualitySeverity.HIGH: 1},
        last_updated=datetime.now(UTC),
        recent_alerts=[alert],
    )
    monkeypatch.setattr(
        service,
        "_get_data_quality_summary",
        AsyncMock(return_value=dq_summary),
    )

    summary = await service.get_dashboard_summary("user-123")

    assert isinstance(summary, DashboardSummary)
    assert summary.user_id == "user-123"
    assert summary.portfolio == portfolio_summary
    assert summary.strategies == strategy_summary
    assert summary.recent_activity == activity
    assert summary.data_quality == dq_summary
    deps["portfolio"].get_portfolio_summary.assert_awaited_once_with("user-123")


@pytest.mark.asyncio
async def test_get_dashboard_summary_wraps_errors(
    service_with_mocks: Tuple[DashboardService, Dict[str, Any]]
) -> None:
    """Errors from dependencies should be wrapped with a descriptive message."""

    service, deps = service_with_mocks
    deps["portfolio"].get_portfolio_summary.side_effect = RuntimeError("boom")

    with pytest.raises(Exception) as exc:
        await service.get_dashboard_summary("user-1")

    assert "대시보드 요약 조회 실패" in str(exc.value)


@pytest.mark.asyncio
async def test_get_recent_trades_summarises_metrics(
    service_with_mocks: Tuple[DashboardService, Dict[str, Any]]
) -> None:
    """`get_recent_trades` should compute totals from the portfolio service payload."""

    service, deps = service_with_mocks

    trades = [
        TradeItem(
            trade_id="t1",
            symbol="AAPL",
            side=TradeSide.BUY,
            quantity=10,
            price=180.0,
            value=1_800.0,
            pnl=25.5,
            strategy_name="Alpha",
            timestamp=datetime.now(),
        ),
        TradeItem(
            trade_id="t2",
            symbol="MSFT",
            side=TradeSide.SELL,
            quantity=5,
            price=300.0,
            value=1_500.0,
            pnl=-10.0,
            strategy_name="Beta",
            timestamp=datetime.now(),
        ),
    ]
    deps["portfolio"].get_recent_trades.return_value = trades

    result = await service.get_recent_trades("user-42", limit=5, days=3)

    assert isinstance(result, RecentTrades)
    assert result.trades == trades
    assert result.summary.model_dump() == {
        "total_trades": 2,
        "winning_trades": 1,
        "total_pnl": 15.5,
    }
    deps["portfolio"].get_recent_trades.assert_awaited_once_with("user-42", 5, 3)


@pytest.mark.asyncio
async def test_get_recent_trades_wraps_errors(
    service_with_mocks: Tuple[DashboardService, Dict[str, Any]]
) -> None:
    """Exceptions are wrapped when the underlying service fails."""

    service, deps = service_with_mocks
    deps["portfolio"].get_recent_trades.side_effect = ValueError("offline")

    with pytest.raises(Exception) as exc:
        await service.get_recent_trades("user-1")

    assert "최근 거래 조회 실패" in str(exc.value)


def _build_data_quality_payload() -> DataQualitySummaryPayload:
    """Helper creating a deterministic sentinel payload for tests."""

    alert = AlertPayload(
        symbol="AAPL",
        data_type="daily",
        occurred_at=datetime.now(UTC),
        severity=SeverityLevel.HIGH,
        iso_score=1.4,
        prophet_score=0.8,
        price_change_pct=4.2,
        volume_z_score=1.1,
        message="Price spike",
    )
    return DataQualitySummaryPayload(
        total_alerts=2,
        severity_breakdown={SeverityLevel.HIGH: 2},
        last_updated=datetime.now(UTC),
        recent_alerts=[alert],
    )


@pytest.mark.asyncio
async def test_get_data_quality_summary_transforms_payload(
    service_with_mocks: Tuple[DashboardService, Dict[str, Any]]
) -> None:
    """The private helper should convert sentinel payloads into schema objects."""

    service, deps = service_with_mocks
    deps["data_quality"].get_recent_summary.return_value = _build_data_quality_payload()

    summary = await service._get_data_quality_summary()

    assert isinstance(summary, DataQualitySummary)
    assert summary.total_alerts == 2
    assert summary.severity_breakdown == {DataQualitySeverity.HIGH: 2}
    assert summary.recent_alerts[0].severity == DataQualitySeverity.HIGH


@pytest.mark.asyncio
async def test_get_data_quality_summary_returns_none_without_sentinel(
    service_with_mocks: Tuple[DashboardService, Dict[str, Any]]
) -> None:
    """When no sentinel is configured the helper should return ``None``."""

    service, _ = service_with_mocks
    service.data_quality_sentinel = None

    assert await service._get_data_quality_summary() is None


@pytest.mark.asyncio
async def test_get_data_quality_summary_logs_and_returns_none_on_error(
    service_with_mocks: Tuple[DashboardService, Dict[str, Any]]
) -> None:
    """Failures from the sentinel should be swallowed to keep the dashboard resilient."""

    service, deps = service_with_mocks
    deps["data_quality"].get_recent_summary.side_effect = RuntimeError("timeout")

    assert await service._get_data_quality_summary() is None


@pytest.mark.asyncio
async def test_get_portfolio_performance_delegates_to_portfolio_service(
    service_with_mocks: Tuple[DashboardService, Dict[str, Any]]
) -> None:
    """Portfolio performance lookups are delegated to :class:`PortfolioService`."""

    service, deps = service_with_mocks
    performance = PortfolioPerformance(
        period="1M",
        data_points=[],
        summary=PortfolioPerformanceSummary(
            total_return=5.0, volatility=3.0, sharpe_ratio=1.1, max_drawdown=-2.5
        ),
    )
    deps["portfolio"].get_portfolio_performance.return_value = performance

    result = await service.get_portfolio_performance("user", period="1M", granularity="day")

    assert result is performance
    deps["portfolio"].get_portfolio_performance.assert_awaited_once_with(
        "user", "1M", "day"
    )


@pytest.mark.asyncio
async def test_get_predictive_snapshot_refreshes_stale_regime(
    service_with_mocks: Tuple[DashboardService, Dict[str, Any]]
) -> None:
    """Stale regime snapshots should trigger a refresh before returning data."""

    service, deps = service_with_mocks

    signal = MLSignalInsight(
        symbol="AAPL",
        as_of=datetime.now(UTC),
        lookback_days=30,
        probability=0.7,
        confidence=0.6,
        recommendation=SignalRecommendation.BUY,
        feature_contributions=[],
        top_signals=[],
    )
    deps["ml_signal"].score_symbol.return_value = signal

    stale_regime = MarketRegimeSnapshot(
        symbol="AAPL",
        as_of=datetime.now(UTC) - timedelta(days=2),
        lookback_days=30,
        regime=MarketRegimeType.BULLISH,
        confidence=0.5,
        probabilities={MarketRegimeType.BULLISH: 0.6},
        metrics=RegimeMetrics(
            trailing_return_pct=5.0,
            volatility_pct=10.0,
            drawdown_pct=2.0,
            momentum_z=1.0,
        ),
        notes=[],
    )
    fresh_regime = stale_regime.model_copy(update={"as_of": datetime.now(UTC)})
    deps["regime"].get_latest_regime.return_value = stale_regime
    deps["regime"].refresh_regime.return_value = fresh_regime

    forecast = PortfolioForecastDistribution(
        as_of=datetime.now(UTC),
        horizon_days=30,
        last_portfolio_value=120_000,
        expected_return_pct=6.5,
        expected_volatility_pct=12.0,
        percentile_bands=[
            ForecastPercentileBand(percentile=5, projected_value=100_000),
            ForecastPercentileBand(percentile=95, projected_value=145_000),
        ],
    )
    deps["portfolio"].get_probabilistic_forecast.return_value = forecast

    snapshot = await service.get_predictive_snapshot("user", symbol="AAPL", horizon_days=30)

    assert isinstance(snapshot, PredictiveDashboardInsights)
    assert snapshot.signal == signal
    assert snapshot.regime == fresh_regime
    assert snapshot.forecast == forecast
    deps["regime"].get_latest_regime.assert_awaited_once_with("AAPL")
    deps["regime"].refresh_regime.assert_awaited_once_with("AAPL")
    deps["portfolio"].get_probabilistic_forecast.assert_awaited_once_with(
        "user", horizon_days=30
    )


@pytest.mark.asyncio
async def test_get_strategy_comparison_sorts_by_return(
    service_with_mocks: Tuple[DashboardService, Dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Strategies should be sorted by total return when requested."""

    service, _ = service_with_mocks

    choice_values = iter(
        [
            "RSI",
            "Momentum",
            StrategyStatus.ACTIVE,
            "MACD",
            "RSI",
            StrategyStatus.PAUSED,
            "Bollinger",
            "SMA",
            StrategyStatus.ACTIVE,
        ]
    )
    uniform_values = iter([5.11, 60.0, 1.0, 10.22, 65.0, 1.2, 2.33, 70.0, 1.4])
    randint_values = iter([150, 10, 200, 20, 250, 30])

    monkeypatch.setattr(
        "app.services.user.dashboard_service.random.choice", lambda seq: next(choice_values)
    )
    monkeypatch.setattr(
        "app.services.user.dashboard_service.random.uniform",
        lambda a, b: next(uniform_values),
    )
    monkeypatch.setattr(
        "app.services.user.dashboard_service.random.randint",
        lambda a, b: next(randint_values),
    )

    comparison = await service.get_strategy_comparison("user", limit=3, sort_by="return")

    assert isinstance(comparison, StrategyComparison)
    returns = [item.total_return for item in comparison.strategies]
    assert returns == [10.22, 5.11, 2.33]


@pytest.mark.asyncio
async def test_get_strategy_comparison_sorts_by_sharpe(
    service_with_mocks: Tuple[DashboardService, Dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The sorting logic should also work for the Sharpe ratio ordering."""

    service, _ = service_with_mocks

    choice_values = iter(
        [
            "RSI",
            "Momentum",
            StrategyStatus.ACTIVE,
            "MACD",
            "RSI",
            StrategyStatus.PAUSED,
            "Bollinger",
            "SMA",
            StrategyStatus.ACTIVE,
        ]
    )
    # Sharpe ratios are the 3rd value in each trio of uniform calls
    uniform_values = iter([5.11, 60.0, 0.8, 4.22, 65.0, 1.5, 3.33, 70.0, 1.1])
    randint_values = iter([150, 10, 200, 20, 250, 30])

    monkeypatch.setattr(
        "app.services.user.dashboard_service.random.choice", lambda seq: next(choice_values)
    )
    monkeypatch.setattr(
        "app.services.user.dashboard_service.random.uniform",
        lambda a, b: next(uniform_values),
    )
    monkeypatch.setattr(
        "app.services.user.dashboard_service.random.randint",
        lambda a, b: next(randint_values),
    )

    comparison = await service.get_strategy_comparison("user", limit=3, sort_by="sharpe")

    sharpes = [item.sharpe_ratio for item in comparison.strategies]
    assert sharpes == [1.5, 1.1, 0.8]


@pytest.mark.asyncio
async def test_get_watchlist_quotes_generates_deterministic_payload(
    service_with_mocks: Tuple[DashboardService, Dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Watchlist quotes should expose consistent market data snapshots."""

    service, _ = service_with_mocks

    change_values = iter([5.0, -2.5, 3.0, 0.0, 1.5])
    volume_values = iter([1_000_000, 2_000_000, 3_000_000, 4_000_000, 5_000_000])
    market_cap_values = iter([100, 200, 150, 180, 220])

    monkeypatch.setattr(
        "app.services.user.dashboard_service.random.uniform",
        lambda a, b: next(change_values),
    )

    def _deterministic_randint(a: int, b: int) -> int:
        if b == 50_000_000:
            return next(volume_values)
        return next(market_cap_values)

    monkeypatch.setattr(
        "app.services.user.dashboard_service.random.randint", _deterministic_randint
    )

    quotes = await service.get_watchlist_quotes("user-1")

    assert isinstance(quotes.symbols, list)
    assert len(quotes.symbols) == 5
    first = quotes.symbols[0]
    assert first.symbol == "AAPL"
    assert first.change == 5.0
    assert first.volume == 1_000_000
    assert first.market_cap == 100 * 1e9


@pytest.mark.asyncio
async def test_get_news_feed_respects_filters(
    service_with_mocks: Tuple[DashboardService, Dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The generated news feed should honour supplied filters and randomness."""

    service, _ = service_with_mocks

    sentiment_cycle = iter(
        [
            SentimentType.POSITIVE,
            SentimentType.NEUTRAL,
            SentimentType.NEGATIVE,
            SentimentType.POSITIVE,
            SentimentType.NEUTRAL,
        ]
    )
    relevance_values = iter([0.9, 0.8, 0.7, 0.6, 0.5])

    monkeypatch.setattr(
        "app.services.user.dashboard_service.random.choice",
        lambda seq: next(sentiment_cycle),
    )
    monkeypatch.setattr(
        "app.services.user.dashboard_service.random.uniform",
        lambda a, b: next(relevance_values),
    )

    feed = await service.get_news_feed(
        "user-1", limit=3, symbols=["AAPL"], categories=["tech"]
    )

    assert len(feed.articles) == 3
    assert all("AAPL" in article.symbols for article in feed.articles)
    assert feed.articles[0].sentiment == SentimentType.POSITIVE
    assert feed.articles[-1].relevance_score == 0.7


@pytest.mark.asyncio
async def test_get_economic_calendar_generates_events(
    service_with_mocks: Tuple[DashboardService, Dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Economic calendar helper should produce mock events with importance values."""

    service, _ = service_with_mocks

    importance_cycle = iter(
        [
            ImportanceLevel.HIGH,
            ImportanceLevel.MEDIUM,
            ImportanceLevel.LOW,
            ImportanceLevel.HIGH,
            ImportanceLevel.MEDIUM,
        ]
    )

    def _importance_choice(seq):
        first = seq[0]
        if isinstance(first, ImportanceLevel):
            return next(importance_cycle)
        return first

    monkeypatch.setattr(
        "app.services.user.dashboard_service.random.choice",
        _importance_choice,
    )

    calendar = await service.get_economic_calendar("user-1", days=3)

    assert len(calendar.events) == 5
    assert calendar.events[0].importance == ImportanceLevel.HIGH
    assert calendar.events[2].importance == ImportanceLevel.LOW


@pytest.mark.asyncio
async def test_get_recent_activity_returns_recent_snapshot(
    service_with_mocks: Tuple[DashboardService, Dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The recent activity generator should reference a predictable timestamp."""

    service, _ = service_with_mocks

    class _FixedDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2024, 1, 1, tzinfo=UTC if tz else None)

    monkeypatch.setattr("app.services.user.dashboard_service.datetime", _FixedDateTime)

    activity = await service._get_recent_activity("user-1")

    assert activity.trades_count_today == 15
    assert activity.backtests_count_week == 3
    assert activity.last_login.year == 2023

