"""API tests for narrative report endpoints."""

from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.schemas.enums import ReportRecommendation
from app.schemas.gen_ai.narrative import BacktestNarrativeReport, ExecutiveSummary, MarketContext, PerformanceAnalysis, Recommendations, RiskAssessment, StrategyInsights


@pytest.fixture
def narrative_service_stub(monkeypatch: pytest.MonkeyPatch) -> SimpleNamespace:
    service = SimpleNamespace(generate_report=AsyncMock())
    monkeypatch.setattr(
        "app.api.routes.gen_ai.narrative.service_factory.get_narrative_report_service",
        lambda: service,
    )
    return service


def _sample_report() -> BacktestNarrativeReport:
    return BacktestNarrativeReport(
        backtest_id="bt-1",
        generated_at=datetime.now(UTC),
        llm_model="gpt-4o",
        llm_version=None,
        executive_summary=ExecutiveSummary(
            title="Momentum Strategy Summary",
            overview="The backtest achieved consistent returns with controlled drawdowns." * 2,
            key_findings=["Stable returns", "Controlled risk", "Robust diversification"],
            recommendation=ReportRecommendation.PROCEED,
            confidence_level=0.85,
        ),
        performance_analysis=PerformanceAnalysis(
            summary="Returns exceeded the benchmark.",
            return_analysis="Cumulative return was 12% above benchmark.",
            risk_analysis="Volatility remained within tolerance.",
            sharpe_interpretation="Sharpe ratio above target.",
            drawdown_commentary="Drawdowns limited to 8%.",
            trade_statistics_summary="Win rate averaged 55% across 120 trades.",
        ),
        strategy_insights=StrategyInsights(
            strategy_name="Momentum",
            strategy_description="Dual moving average system.",
            key_parameters={"fast": 20, "slow": 60},
            parameter_sensitivity="Stable across nearby windows.",
            strengths=["Trend capture", "Risk control"],
            weaknesses=["Choppy markets", "Latency"],
        ),
        risk_assessment=RiskAssessment(
            overall_risk_level="Medium",
            risk_summary="Risk profile is balanced.",
            volatility_assessment="Volatility near 15% target.",
            max_drawdown_context="Drawdowns occurred during market rotation.",
            concentration_risk="Portfolio diversified across sectors.",
            tail_risk="Tail risk mitigated via stops.",
        ),
        market_context=MarketContext(
            regime_analysis="Market remained in bullish regime.",
            ml_signal_confidence=0.7,
            forecast_outlook="Expect moderate continuation.",
            external_factors=["Fed policy support"],
        ),
        recommendations=Recommendations(
            action=ReportRecommendation.PROCEED,
            rationale="Risk-adjusted returns exceed mandate.",
            next_steps=["Increase allocation", "Monitor volatility"],
            optimization_suggestions=["Add trailing stop"],
            risk_mitigation=["Maintain diversification"],
        ),
        fact_check_passed=True,
        validation_errors=[],
    )


@pytest.mark.asyncio
async def test_generate_report_success(async_client, auth_headers, narrative_service_stub) -> None:
    narrative_service_stub.generate_report.return_value = _sample_report()

    response = await async_client.post(
        "/api/v1/gen-ai/narrative/backtests/bt-1/report",
        headers=auth_headers,
        params={"include_phase1_insights": True, "language": "ko", "detail_level": "standard"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["backtest_id"] == "bt-1"
    narrative_service_stub.generate_report.assert_awaited_once()


@pytest.mark.asyncio
async def test_generate_report_not_found(async_client, auth_headers, narrative_service_stub) -> None:
    narrative_service_stub.generate_report.side_effect = ValueError("Backtest bt-1 not found")

    response = await async_client.post(
        "/api/v1/gen-ai/narrative/backtests/bt-1/report",
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert "백테스트를 찾을 수 없습니다" in response.json()["detail"]


@pytest.mark.asyncio
async def test_generate_report_incomplete(async_client, auth_headers, narrative_service_stub) -> None:
    narrative_service_stub.generate_report.side_effect = ValueError("Backtest bt-1 is not completed")

    response = await async_client.post(
        "/api/v1/gen-ai/narrative/backtests/bt-1/report",
        headers=auth_headers,
    )

    assert response.status_code == 400
    assert "리포트를 생성" in response.json()["detail"]


@pytest.mark.asyncio
async def test_generate_report_unexpected_error(async_client, auth_headers, narrative_service_stub) -> None:
    narrative_service_stub.generate_report.side_effect = RuntimeError("LLM failure")

    response = await async_client.post(
        "/api/v1/gen-ai/narrative/backtests/bt-1/report",
        headers=auth_headers,
    )

    assert response.status_code == 500
    assert "오류 발생" in response.json()["detail"]
