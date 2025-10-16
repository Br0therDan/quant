"""Unit tests for :mod:`app.services.gen_ai.applications.narrative_report_service`."""

from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.gen_ai.applications.narrative_report_service import (
    NarrativeReportService,
)
from app.services.gen_ai.core.openai_client_manager import (
    InvalidModelError,
    ModelCapability,
    ModelConfig,
    ModelTier,
)
from app.schemas.enums import ReportRecommendation


class _DummyOpenAIManager:
    """Light-weight stand-in for :class:`OpenAIClientManager`."""

    def __init__(self, model_config: ModelConfig, *, raise_invalid: bool = False) -> None:
        self._model_config = model_config
        self._raise_invalid = raise_invalid
        self.get_client = MagicMock(return_value=MagicMock(name="AsyncOpenAI"))

    def get_service_policy(self, service_name: str) -> SimpleNamespace:
        return SimpleNamespace(default_model=self._model_config.model_id)

    def validate_model_for_service(
        self, service_name: str, requested_model_id: str | None
    ) -> ModelConfig:
        if self._raise_invalid:
            raise InvalidModelError("model not allowed")
        if requested_model_id and requested_model_id != self._model_config.model_id:
            raise InvalidModelError("model not allowed")
        return self._model_config

    def track_usage(self, *args: Any, **kwargs: Any) -> None:  # pragma: no cover - noop
        return None


@pytest.fixture
def model_config() -> ModelConfig:
    return ModelConfig(
        model_id="gpt-4o",
        tier=ModelTier.STANDARD,
        capabilities=[ModelCapability.CHAT, ModelCapability.ANALYSIS],
        input_price_per_1m=0.1,
        output_price_per_1m=0.2,
        max_tokens=128_000,
        supports_rag=True,
        description="test model",
    )


@pytest.fixture
def narrative_service(model_config: ModelConfig) -> NarrativeReportService:
    backtest_service = MagicMock(name="BacktestService")
    manager = _DummyOpenAIManager(model_config)
    return NarrativeReportService(backtest_service=backtest_service, openai_manager=manager)


def _make_backtest(performance: SimpleNamespace | None = None) -> SimpleNamespace:
    config = SimpleNamespace(
        name="Momentum Strategy",
        symbols=["AAPL", "MSFT"],
        start_date=datetime(2024, 1, 1, tzinfo=UTC),
        end_date=datetime(2024, 2, 1, tzinfo=UTC),
        initial_cash=100_000.0,
    )
    return SimpleNamespace(
        id="bt-1",
        config=config,
        performance=performance,
    )


@pytest.mark.asyncio
async def test_build_prompt_context_without_phase1(narrative_service: NarrativeReportService) -> None:
    backtest = _make_backtest(
        SimpleNamespace(
            total_return=0.12,
            sharpe_ratio=1.5,
            max_drawdown=8.0,
            volatility=0.2,
            win_rate=55.0,
            total_trades=120,
        )
    )

    context = await narrative_service._build_prompt_context(backtest, False)

    assert context["strategy_name"] == "Momentum Strategy"
    assert context["symbols"] == ["AAPL", "MSFT"]
    assert context["performance"]["total_return"] == pytest.approx(0.12)
    assert "phase1_insights" not in context


@pytest.mark.asyncio
async def test_build_prompt_context_with_phase1_insights(
    model_config: ModelConfig,
) -> None:
    ml_signal_service = SimpleNamespace(
        get_latest_signal=AsyncMock(
            return_value=SimpleNamespace(confidence=0.8, recommendation="buy")
        )
    )
    regime_service = SimpleNamespace(
        get_latest_regime=AsyncMock(
            return_value=SimpleNamespace(regime=SimpleNamespace(value="bull"), confidence=0.7)
        )
    )

    service = NarrativeReportService(
        backtest_service=MagicMock(),
        ml_signal_service=ml_signal_service,
        regime_service=regime_service,
        probabilistic_service=SimpleNamespace(),
        openai_manager=_DummyOpenAIManager(model_config),
    )

    backtest = _make_backtest(
        SimpleNamespace(
            total_return=0.05,
            sharpe_ratio=1.1,
            max_drawdown=5.0,
            volatility=0.15,
            win_rate=60.0,
            total_trades=80,
        )
    )

    context = await service._build_prompt_context(backtest, True)

    insights = context.get("phase1_insights")
    assert insights is not None
    assert insights["ml_signal"]["confidence"] == pytest.approx(0.8)
    assert insights["regime"]["regime_type"] == "bull"
    ml_signal_service.get_latest_signal.assert_awaited_once()
    regime_service.get_latest_regime.assert_awaited_once()


def test_resolve_model_config_invalid(model_config: ModelConfig) -> None:
    manager = _DummyOpenAIManager(model_config, raise_invalid=True)
    service = NarrativeReportService(backtest_service=MagicMock(), openai_manager=manager)

    with pytest.raises(ValueError):
        service._resolve_model_config("gpt-4o")


def _make_llm_payload() -> Dict[str, Dict[str, Any]]:
    long_overview = "Backtest delivered stable momentum-driven returns with controlled risk." * 2
    return {
        "executive_summary": {
            "title": "Momentum Strategy Overview",
            "overview": long_overview,
            "key_findings": ["Stable returns", "Controlled risk", "High win rate"],
            "recommendation": ReportRecommendation.PROCEED,
            "confidence_level": 0.85,
        },
        "performance_analysis": {
            "summary": "Performance remained within expectations.",
            "return_analysis": "Cumulative return beat benchmark by 12%.",
            "risk_analysis": "Volatility stayed below target band.",
            "sharpe_interpretation": "Sharpe ratio above industry median.",
            "drawdown_commentary": "Max drawdown limited to 8% during correction.",
            "trade_statistics_summary": "120 trades executed with 55% win rate.",
        },
        "strategy_insights": {
            "strategy_name": "Momentum Strategy",
            "strategy_description": "Dual moving average crossover focusing on large caps.",
            "key_parameters": {"fast": 20, "slow": 60},
            "parameter_sensitivity": "Performance remains robust across 15-25 day fast window.",
            "strengths": ["Consistent trends", "Low drawdowns"],
            "weaknesses": ["Sensitive to whipsaws", "Needs active monitoring"],
        },
        "risk_assessment": {
            "overall_risk_level": "Medium",
            "risk_summary": "Risk is balanced with moderate drawdowns.",
            "volatility_assessment": "Volatility sits near the 15% target.",
            "max_drawdown_context": "Drawdowns occurred during sector rotation phases.",
            "concentration_risk": "Positions diversified across 12 symbols.",
            "tail_risk": "Limited tail risk due to stop-loss discipline.",
        },
        "market_context": {
            "regime_analysis": "Market remained in bullish regime with strong breadth.",
            "ml_signal_confidence": 0.7,
            "forecast_outlook": "Expect continuation of trend over next quarter.",
            "external_factors": ["Fed policy support"],
        },
        "recommendations": {
            "action": ReportRecommendation.PROCEED,
            "rationale": "Risk-adjusted returns exceed mandate requirements.",
            "next_steps": ["Increase allocation", "Monitor volatility"],
            "optimization_suggestions": ["Add trailing stop"],
            "risk_mitigation": ["Maintain sector diversification"],
        },
    }


def test_validate_output_returns_report(
    narrative_service: NarrativeReportService, model_config: ModelConfig
) -> None:
    payload = _make_llm_payload()
    report = narrative_service._validate_output(payload, "bt-1", model_config)

    assert report.backtest_id == "bt-1"
    assert report.llm_model == "gpt-4o"
    assert report.executive_summary.recommendation is ReportRecommendation.PROCEED
    assert report.fact_check_passed is False
    assert report.validation_errors == []


@pytest.mark.asyncio
async def test_fact_check_detects_out_of_range_metrics(
    narrative_service: NarrativeReportService,
) -> None:
    backtest = _make_backtest(
        SimpleNamespace(
            total_return=0.2,
            sharpe_ratio=12.0,
            max_drawdown=150.0,
            volatility=0.3,
            win_rate=150.0,
            total_trades=10,
        )
    )
    report = narrative_service._validate_output(_make_llm_payload(), "bt-1", narrative_service.openai_manager.validate_model_for_service("narrative_report", None))
    # We only need a minimal report shell for fact check.
    fact_check = await narrative_service._fact_check(report, backtest)

    assert fact_check is False
    assert len(report.validation_errors) == 2
    assert any("Max drawdown" in msg for msg in report.validation_errors)
    assert any("Win rate" in msg for msg in report.validation_errors)
