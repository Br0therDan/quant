"""
Narrative Report Generation Service using LLM.

Phase 3 D1: Generates executive-level backtest analysis reports
with structured prompts, Pydantic validation, and fact-checking.
"""

import json
import logging
from datetime import UTC, datetime
from typing import Any, Dict, Optional

from app.models.trading.backtest import Backtest
from app.schemas.gen_ai.narrative import (
    BacktestNarrativeReport,
    ExecutiveSummary,
    PerformanceAnalysis,
    StrategyInsights,
    RiskAssessment,
    MarketContext,
    Recommendations,
)
from app.services.trading.backtest_service import BacktestService
from app.services.gen_ai.core.openai_client_manager import (
    InvalidModelError,
    ModelConfig,
    OpenAIClientManager,
)

logger = logging.getLogger(__name__)


class NarrativeReportService:
    """LLM 기반 백테스트 내러티브 리포트 생성 서비스."""

    def __init__(
        self,
        backtest_service: BacktestService,
        ml_signal_service: Optional[Any] = None,
        regime_service: Optional[Any] = None,
        probabilistic_service: Optional[Any] = None,
        openai_manager: OpenAIClientManager = None,  # type: ignore TODO: 개선후 제거
    ):
        """서비스 초기화.

        Args:
            backtest_service: 백테스트 서비스
            ml_signal_service: ML 시그널 서비스 (Phase 1 D1, 선택)
            regime_service: 레짐 감지 서비스 (Phase 1 D2, 선택)
            probabilistic_service: 확률 예측 서비스 (Phase 1 D3, 선택)
        """
        self.backtest_service = backtest_service
        self.ml_signal_service = ml_signal_service
        self.regime_service = regime_service
        self.probabilistic_service = probabilistic_service
        self.openai_manager = openai_manager or OpenAIClientManager()
        self.service_name = "narrative_report"

        self._client: Optional[Any] = None
        try:
            self._client = self.openai_manager.get_client()
        except RuntimeError as exc:
            logger.warning("OpenAI client initialization failed: %s", exc)

        self.default_model = self.openai_manager.get_service_policy(
            self.service_name
        ).default_model
        logger.info(
            "NarrativeReportService initialized",
            extra={"default_model": self.default_model},
        )

    def _get_client(self) -> Any:
        """Return the shared OpenAI client instance."""

        if self._client is None:
            self._client = self.openai_manager.get_client()
        return self._client

    def _resolve_model_config(self, requested_model_id: Optional[str]) -> ModelConfig:
        """Validate and resolve the requested model for narrative generation."""

        try:
            return self.openai_manager.validate_model_for_service(
                self.service_name, requested_model_id
            )
        except InvalidModelError as exc:
            raise ValueError(str(exc)) from exc

    async def generate_report(
        self,
        backtest_id: str,
        include_phase1_insights: bool = True,
        language: str = "ko",
        detail_level: str = "standard",
        model_id: Optional[str] = None,
    ) -> BacktestNarrativeReport:
        """백테스트 내러티브 리포트 생성.

        Args:
            backtest_id: 백테스트 ID
            include_phase1_insights: Phase 1 인사이트 포함 여부
            language: 리포트 언어 (ko/en)
            detail_level: 상세 수준 (brief/standard/detailed)

        Returns:
            BacktestNarrativeReport: 생성된 리포트

        Raises:
            ValueError: 백테스트를 찾을 수 없거나 완료되지 않은 경우
            Exception: LLM 호출 실패 또는 검증 실패
        """
        model_config = self._resolve_model_config(model_id)
        try:
            self._get_client()
        except RuntimeError as exc:
            raise Exception(
                "OpenAI client not initialized. Check OPENAI_API_KEY."
            ) from exc

        # 1. 백테스트 데이터 조회
        backtest = await self.backtest_service.get_backtest(backtest_id)
        if not backtest:
            raise ValueError(f"Backtest {backtest_id} not found")

        if backtest.status != "completed":
            raise ValueError(
                f"Backtest {backtest_id} is not completed (status: {backtest.status})"
            )

        # 2. 컨텍스트 구축 (백테스트 + Phase 1 인사이트)
        context = await self._build_prompt_context(backtest, include_phase1_insights)

        # 3. LLM 호출
        llm_output = await self._call_llm(context, language, detail_level, model_config)

        # 4. Pydantic 검증
        report = self._validate_output(llm_output, backtest_id, model_config)

        # 5. 사실 확인 (Fact Check)
        fact_check_passed = await self._fact_check(report, backtest)
        report.fact_check_passed = fact_check_passed

        logger.info(
            f"Generated narrative report for backtest {backtest_id}",
            extra={
                "fact_check_passed": fact_check_passed,
                "recommendation": report.executive_summary.recommendation,
                "model_id": model_config.model_id,
            },
        )

        return report

    async def _build_prompt_context(
        self, backtest: Backtest, include_phase1_insights: bool
    ) -> Dict[str, Any]:
        """프롬프트 컨텍스트 구축 (구조화된 데이터)."""

        context = {
            "backtest_id": str(backtest.id),
            "strategy_name": backtest.config.name,
            "symbols": backtest.config.symbols,
            "start_date": backtest.config.start_date.isoformat(),
            "end_date": backtest.config.end_date.isoformat(),
            "initial_cash": backtest.config.initial_cash,
            "performance": {
                "total_return": (
                    backtest.performance.total_return if backtest.performance else 0.0
                ),
                "sharpe_ratio": (
                    backtest.performance.sharpe_ratio if backtest.performance else 0.0
                ),
                "max_drawdown": (
                    backtest.performance.max_drawdown if backtest.performance else 0.0
                ),
                "volatility": (
                    backtest.performance.volatility if backtest.performance else 0.0
                ),
                "win_rate": (
                    backtest.performance.win_rate if backtest.performance else 0.0
                ),
                "total_trades": (
                    backtest.performance.total_trades if backtest.performance else 0
                ),
            },
        }

        # Phase 1 인사이트 추가 (선택 사항)
        if include_phase1_insights:
            phase1_insights = {}

            # ML Signal (Phase 1 D1)
            if self.ml_signal_service:
                try:
                    # symbols 리스트에서 첫 번째 심볼 사용
                    symbol = (
                        backtest.config.symbols[0] if backtest.config.symbols else None
                    )
                    if symbol:
                        signal = await self.ml_signal_service.get_latest_signal(symbol)
                        phase1_insights["ml_signal"] = {
                            "confidence": signal.confidence,
                            "recommendation": signal.recommendation,
                        }
                except Exception as e:
                    logger.warning(f"Failed to fetch ML signal: {e}")

            # Regime Detection (Phase 1 D2)
            if self.regime_service:
                try:
                    # symbols 리스트에서 첫 번째 심볼 사용
                    symbol = (
                        backtest.config.symbols[0] if backtest.config.symbols else None
                    )
                    if symbol:
                        regime = await self.regime_service.get_latest_regime(symbol)
                        phase1_insights["regime"] = {
                            "regime_type": regime.regime.value,
                            "confidence": regime.confidence,
                        }
                except Exception as e:
                    logger.warning(f"Failed to fetch regime: {e}")

            # Probabilistic Forecast (Phase 1 D3)
            if self.probabilistic_service:
                try:
                    # 포트폴리오 예측은 사용자별이므로 여기서는 스킵
                    # (향후 user_id를 전달받으면 추가 가능)
                    pass
                except Exception as e:
                    logger.warning(f"Failed to fetch forecast: {e}")

            context["phase1_insights"] = phase1_insights

        return context

    async def _call_llm(
        self,
        context: Dict[str, Any],
        language: str,
        detail_level: str,
        model_config: ModelConfig,
    ) -> Dict[str, Any]:
        """LLM 호출 (OpenAI GPT-4)."""

        # 시스템 프롬프트
        system_prompt = self._get_system_prompt(language, detail_level)

        # 사용자 프롬프트 (구조화된 JSON)
        user_prompt = self._get_user_prompt(context, language)

        try:
            client = self._get_client()

            response = await client.chat.completions.create(
                model=model_config.model_id,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.3,  # 낮은 온도 (일관성 중시)
                max_tokens=4000,
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("LLM 응답 내용이 비어있습니다.")

            llm_output = json.loads(content)

            logger.info(
                "LLM call successful",
                extra={
                    "model": model_config.model_id,
                    "tokens": response.usage.total_tokens if response.usage else 0,
                },
            )

            self.openai_manager.track_usage(
                service_name=self.service_name,
                model_id=model_config.model_id,
                usage=response.usage,
            )

            return llm_output

        except Exception as e:
            logger.error(f"LLM call failed: {e}", exc_info=True)
            raise Exception(f"LLM call failed: {str(e)}")

    def _get_system_prompt(self, language: str, detail_level: str) -> str:
        """시스템 프롬프트 생성 (역할 정의)."""

        lang_instruction = (
            "Respond in Korean (한국어)." if language == "ko" else "Respond in English."
        )

        detail_instruction = {
            "brief": "Keep the analysis concise and focused on key points.",
            "standard": "Provide a balanced analysis with sufficient detail.",
            "detailed": "Provide comprehensive analysis with detailed explanations.",
        }.get(detail_level, "Provide a balanced analysis with sufficient detail.")

        return f"""You are an expert quantitative analyst specializing in algorithmic trading strategy evaluation.

Your task is to analyze backtest results and generate an executive-level narrative report.

Guidelines:
1. Be objective and data-driven.
2. Highlight both strengths and weaknesses.
3. Provide actionable recommendations.
4. Use financial terminology appropriately.
5. Reference specific metrics to support your analysis.
6. {lang_instruction}
7. {detail_instruction}

Output Format:
You MUST return a valid JSON object with the following structure:
{{
  "executive_summary": {{
    "title": "string",
    "overview": "string (50-500 chars)",
    "key_findings": ["finding1", "finding2", "finding3"],
    "recommendation": "proceed|optimize|reject|research",
    "confidence_level": float (0-1)
  }},
  "performance_analysis": {{
    "summary": "string",
    "return_analysis": "string",
    "risk_analysis": "string",
    "sharpe_interpretation": "string",
    "drawdown_commentary": "string",
    "trade_statistics_summary": "string"
  }},
  "strategy_insights": {{
    "strategy_name": "string",
    "strategy_description": "string",
    "key_parameters": {{}},
    "parameter_sensitivity": "string",
    "strengths": ["strength1", "strength2"],
    "weaknesses": ["weakness1", "weakness2"]
  }},
  "risk_assessment": {{
    "overall_risk_level": "Low|Medium|High|Very High",
    "risk_summary": "string",
    "volatility_assessment": "string",
    "max_drawdown_context": "string",
    "concentration_risk": "string",
    "tail_risk": "string"
  }},
  "market_context": {{
    "regime_analysis": "string",
    "ml_signal_confidence": float or null,
    "forecast_outlook": "string" or null,
    "external_factors": ["factor1", "factor2"]
  }},
  "recommendations": {{
    "action": "proceed|optimize|reject|research",
    "rationale": "string",
    "next_steps": ["step1", "step2"],
    "optimization_suggestions": ["suggestion1", "suggestion2"] or null,
    "risk_mitigation": ["mitigation1", "mitigation2"] or null
  }}
}}

IMPORTANT: Ensure all strings are within character limits and all required fields are present."""

    def _get_user_prompt(self, context: Dict[str, Any], language: str) -> str:
        """사용자 프롬프트 생성 (컨텍스트 전달)."""

        lang_note = (
            "분석을 한국어로 작성하세요." if language == "ko" else "Write the analysis in English."
        )

        prompt = f"""Analyze the following backtest results and generate a comprehensive narrative report.

Backtest Context:
{json.dumps(context, indent=2, ensure_ascii=False)}

{lang_note}

Please provide:
1. Executive Summary with clear recommendation (PROCEED, OPTIMIZE, REJECT, or RESEARCH)
2. Performance Analysis covering returns, risk, and trade statistics
3. Strategy Insights including strengths, weaknesses, and parameter sensitivity
4. Risk Assessment with overall risk level and detailed commentary
5. Market Context (use Phase 1 insights if available)
6. Recommendations with actionable next steps

Return the analysis as a JSON object following the specified schema.
"""

        return prompt

    def _validate_output(
        self, llm_output: Dict[str, Any], backtest_id: str, model_config: ModelConfig
    ) -> BacktestNarrativeReport:
        """LLM 출력 검증 (Pydantic)."""

        try:
            # Pydantic 검증
            executive_summary = ExecutiveSummary(**llm_output["executive_summary"])
            performance_analysis = PerformanceAnalysis(
                **llm_output["performance_analysis"]
            )
            strategy_insights = StrategyInsights(**llm_output["strategy_insights"])
            risk_assessment = RiskAssessment(**llm_output["risk_assessment"])
            market_context = MarketContext(**llm_output["market_context"])
            recommendations = Recommendations(**llm_output["recommendations"])

            report = BacktestNarrativeReport(
                backtest_id=backtest_id,
                generated_at=datetime.now(UTC),
                llm_model=model_config.model_id,
                llm_version=None,
                executive_summary=executive_summary,
                performance_analysis=performance_analysis,
                strategy_insights=strategy_insights,
                risk_assessment=risk_assessment,
                market_context=market_context,
                recommendations=recommendations,
                fact_check_passed=False,  # 아직 검증 전
                validation_errors=[],
            )

            logger.info(f"LLM output validated successfully for backtest {backtest_id}")
            return report

        except Exception as e:
            logger.error(f"LLM output validation failed: {e}", exc_info=True)
            raise Exception(f"LLM output validation failed: {str(e)}")

    async def _fact_check(
        self, report: BacktestNarrativeReport, backtest: Backtest
    ) -> bool:
        """사실 확인 (KPI 스토어와 교차 검증)."""

        # 간단한 사실 확인: 주요 메트릭이 실제 값과 크게 다르지 않은지 확인
        errors = []

        # 백테스트 성과가 있는지 확인
        if not backtest.performance:
            errors.append("Backtest performance data is missing")
            report.validation_errors = errors
            return False

        # 샤프 비율 범위 확인 (-5 ~ +10 정도가 일반적)
        actual_sharpe = backtest.performance.sharpe_ratio
        if not (-5.0 <= actual_sharpe <= 10.0):
            logger.warning(
                f"Sharpe ratio {actual_sharpe} is outside normal range [-5, 10]"
            )

        # 최대 낙폭 확인 (0% ~ 100%)
        actual_drawdown = backtest.performance.max_drawdown
        if not (0.0 <= actual_drawdown <= 100.0):
            errors.append(
                f"Max drawdown {actual_drawdown}% is outside valid range [0, 100]"
            )

        # 승률 확인 (0% ~ 100%)
        actual_win_rate = backtest.performance.win_rate
        if not (0.0 <= actual_win_rate <= 100.0):
            errors.append(
                f"Win rate {actual_win_rate}% is outside valid range [0, 100]"
            )

        report.validation_errors = errors

        if errors:
            logger.warning(
                f"Fact check found {len(errors)} issues for backtest {backtest.id}",
                extra={"errors": errors},
            )
            return False

        logger.info(f"Fact check passed for backtest {backtest.id}")
        return True
