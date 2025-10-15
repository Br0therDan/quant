"""
Strategy Builder Service

Phase 3 D2: Interactive Strategy Builder
자연어 → 전략 파라미터 변환 서비스
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.services.gen_ai.core.openai_client_manager import (
    InvalidModelError,
    ModelConfig,
    OpenAIClientManager,
)
from app.services.gen_ai.core.rag_service import RAGService
from app.schemas.gen_ai.rag import RAGAugmentedPrompt, RAGContext
from app.schemas.gen_ai.strategy_builder import (
    ConfidenceLevel,
    GeneratedStrategyConfig,
    HumanApprovalRequest,
    IndicatorRecommendation,
    IntentType,
    ParameterValidation,
    ParsedIntent,
    StrategyBuilderRAGRequest,
    StrategyBuilderRequest,
    StrategyBuilderResponse,
    ValidationStatus,
)
from app.services.trading.strategy_service import StrategyService

logger = logging.getLogger(__name__)


class StrategyBuilderService:
    """
    대화형 전략 빌더 서비스

    자연어 입력을 받아 LLM으로 의도를 파싱하고,
    전략 템플릿에 매핑하여 검증된 전략 설정을 생성합니다.

    핵심 기능:
    - 의도 파싱 (IntentType 분류)
    - 지표 추천 (임베딩 기반 유사도 매칭)
    - 파라미터 검증 (Pydantic + 범위 체크)
    - 휴먼 인 더 루프 승인 워크플로우
    """

    def __init__(
        self,
        strategy_service: StrategyService,
        openai_manager: OpenAIClientManager,
        rag_service: Optional[RAGService] = None,
    ):
        """
        Initialize Strategy Builder Service

        Args:
            strategy_service: 전략 서비스 (템플릿 조회)
            openai_api_key: OpenAI API 키 (환경변수에서 기본 로드)
        """
        self.strategy_service = strategy_service
        self.openai_manager = openai_manager
        self.service_name = "strategy_builder"
        self.rag_service = rag_service

        self._client: Optional[Any] = None
        try:
            self._client = self.openai_manager.get_client()
        except RuntimeError as exc:
            logger.warning("OpenAI client initialization failed: %s", exc)

        self.default_model = self.openai_manager.get_service_policy(
            self.service_name
        ).default_model
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.5"))
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "3000"))

        # 지표 임베딩 캐시 (향후 벡터 DB로 확장 가능)
        self._indicator_embeddings: Dict[str, List[float]] = {}
        self._initialize_indicator_knowledge()

    def _get_client(self) -> Any:
        """Return a ready-to-use OpenAI client."""

        if self._client is None:
            self._client = self.openai_manager.get_client()
        return self._client

    def _resolve_model_config(self, requested_model_id: Optional[str]) -> ModelConfig:
        """Resolve and validate the requested model for the service."""

        try:
            return self.openai_manager.validate_model_for_service(
                self.service_name, requested_model_id
            )
        except InvalidModelError as exc:
            raise ValueError(str(exc)) from exc

    def _initialize_indicator_knowledge(self):
        """지표 지식 베이스 초기화 (간소화 버전)"""
        # 향후 확장: 벡터 DB (FAISS, Pinecone 등) 통합
        self.indicator_knowledge = {
            "RSI": {
                "name": "Relative Strength Index",
                "type": "momentum",
                "description": "과매수/과매도 판단, 14일 기본",
                "parameters": {"period": 14, "overbought": 70, "oversold": 30},
                "keywords": ["모멘텀", "과매수", "과매도", "상대강도지수"],
            },
            "MACD": {
                "name": "Moving Average Convergence Divergence",
                "type": "trend",
                "description": "추세 전환 포착, 12/26/9 기본",
                "parameters": {
                    "fast_period": 12,
                    "slow_period": 26,
                    "signal_period": 9,
                },
                "keywords": ["추세", "이동평균", "다이버전스", "골든크로스"],
            },
            "Bollinger Bands": {
                "name": "Bollinger Bands",
                "type": "volatility",
                "description": "변동성 측정, 20일 SMA + 2σ",
                "parameters": {"period": 20, "std_dev": 2.0},
                "keywords": ["변동성", "볼린저밴드", "표준편차", "돌파"],
            },
            "SMA": {
                "name": "Simple Moving Average",
                "type": "trend",
                "description": "단순 이동평균, 추세 파악",
                "parameters": {"period": 20},
                "keywords": ["이동평균", "추세", "크로스오버"],
            },
            "EMA": {
                "name": "Exponential Moving Average",
                "type": "trend",
                "description": "지수 이동평균, 최근 가격 중시",
                "parameters": {"period": 12},
                "keywords": ["지수이동평균", "추세", "크로스오버"],
            },
        }

    async def build_strategy(
        self, request: StrategyBuilderRequest
    ) -> StrategyBuilderResponse:
        """
        자연어 입력으로부터 전략 생성

        Args:
            request: 전략 빌더 요청

        Returns:
            StrategyBuilderResponse: 생성된 전략 + 검증 + 승인 요청

        Raises:
            ValueError: LLM 응답 파싱 실패
            Exception: LLM API 호출 실패
        """
        model_config = self._resolve_model_config(request.model_id)
        try:
            self._get_client()
        except RuntimeError as exc:
            raise Exception(
                "OpenAI client not initialized. Check OPENAI_API_KEY."
            ) from exc

        start_time = datetime.now(timezone.utc)

        # 1. 의도 파싱 (IntentType 분류)
        parsed_intent = await self._parse_intent(request, model_config)

        # 2. 전략 생성 (의도에 따라 분기)
        generated_strategy = None
        validation_errors = []
        human_approval = HumanApprovalRequest(
            requires_approval=request.require_human_approval,
            approval_reasons=[],
            suggested_modifications=[],
            approval_deadline=None,
        )

        if parsed_intent.intent_type == IntentType.CREATE_STRATEGY:
            generated_strategy, validation_errors = await self._generate_strategy(
                request, parsed_intent, model_config
            )
            if generated_strategy:
                human_approval = self._evaluate_approval_needs(
                    generated_strategy, validation_errors
                )

        # 3. 처리 시간 계산
        processing_time_ms = (
            datetime.now(timezone.utc) - start_time
        ).total_seconds() * 1000

        # 4. 응답 구성
        status = "success" if not validation_errors else "warning"
        if parsed_intent.confidence < 0.5:
            status = "error"

        overall_confidence = (
            parsed_intent.confidence * 0.4
            + (1.0 if generated_strategy else 0.0) * 0.3
            + (
                1.0
                - len(validation_errors) / max(1, len(generated_strategy.parameters))
            )
            * 0.3
            if generated_strategy
            else parsed_intent.confidence * 0.4
        )

        response = StrategyBuilderResponse(
            status=status,
            message=self._generate_response_message(
                parsed_intent, generated_strategy, validation_errors
            ),
            parsed_intent=parsed_intent,
            generated_strategy=generated_strategy,
            human_approval=human_approval,
            alternative_suggestions=(
                self._generate_alternatives(request)
                if parsed_intent.confidence < 0.5
                else None
            ),
            processing_time_ms=processing_time_ms,
            llm_model=model_config.model_id,
            validation_errors=validation_errors if validation_errors else None,
            overall_confidence=overall_confidence,
            rag_applied=False,
            rag_contexts=None,
            rag_prompt_preview=None,
        )

        logger.info(
            "Strategy builder completed",
            extra={
                "intent": parsed_intent.intent_type,
                "confidence": overall_confidence,
                "validation_errors": len(validation_errors),
                "model_id": model_config.model_id,
            },
        )

        return response

    async def build_strategy_with_rag(
        self, request: StrategyBuilderRAGRequest
    ) -> StrategyBuilderResponse:
        """Generate a strategy with optional RAG augmentation."""

        if not request.use_rag or self.rag_service is None:
            logger.info(
                "RAG disabled or unavailable; falling back to standard strategy builder",
                extra={
                    "use_rag": request.use_rag,
                    "rag_service": bool(self.rag_service),
                },
            )
            return await self.build_strategy(request)

        contexts: List[RAGContext] = []
        augmented_prompt: Optional[RAGAugmentedPrompt] = None
        try:
            contexts = await self.rag_service.search_similar_backtests(
                user_id=request.user_id,
                query=request.query,
                top_k=request.top_k,
            )
            augmented_prompt = self.rag_service.build_augmented_prompt(
                request.query, contexts
            )
        except Exception as exc:  # pragma: no cover - network interaction
            logger.warning(
                "RAG retrieval failed; proceeding without augmentation",
                exc_info=True,
                extra={"error": str(exc)},
            )
            contexts = []
            augmented_prompt = None

        base_payload = request.model_dump()
        for field in ("user_id", "use_rag", "top_k"):
            base_payload.pop(field, None)

        context_payload = dict(base_payload.get("context") or {})
        if contexts:
            context_payload["rag_references"] = self.rag_service.serialise_contexts(
                contexts
            )
            context_payload["rag_prompt"] = augmented_prompt.prompt
        base_payload["context"] = context_payload or None

        if contexts and base_payload.get("model_id"):
            try:
                model_config = self.openai_manager.get_model_config(
                    base_payload["model_id"]
                )
                if not model_config.supports_rag:
                    logger.info(
                        "Model %s is not optimised for RAG; reverting to default %s",
                        base_payload["model_id"],
                        self.default_model,
                    )
                    base_payload["model_id"] = None
            except KeyError:
                logger.warning(
                    "Unknown model %s requested for RAG; using default",
                    base_payload.get("model_id"),
                )
                base_payload["model_id"] = None

        base_request = StrategyBuilderRequest.model_validate(base_payload)
        response = await self.build_strategy(base_request)

        return response.model_copy(
            update={
                "rag_applied": bool(contexts),
                "rag_contexts": contexts or None,
                "rag_prompt_preview": augmented_prompt.prompt
                if augmented_prompt and contexts
                else None,
            }
        )

    async def _parse_intent(
        self, request: StrategyBuilderRequest, model_config: ModelConfig
    ) -> ParsedIntent:
        """
        자연어 쿼리에서 사용자 의도 파싱

        LLM을 사용하여 IntentType 분류 + 엔티티 추출
        """
        system_prompt = """
당신은 퀀트 트레이딩 전략 어시스턴트입니다.
사용자의 자연어 요청을 분석하여 의도를 파악하고 핵심 정보를 추출하세요.

의도 유형:
- create_strategy: 새 전략을 만들고 싶음
- modify_strategy: 기존 전략을 수정하고 싶음
- explain_strategy: 전략에 대한 설명을 원함
- recommend_parameters: 파라미터 추천을 원함
- optimize_strategy: 전략 최적화 제안을 원함

추출할 정보:
- 지표명 (RSI, MACD, Bollinger Bands 등)
- 파라미터 (기간, 임계값 등)
- 심볼 (AAPL, TSLA 등)
- 목표 (고수익, 저위험, 단타 등)

JSON 형식으로 응답하세요:
{
    "intent_type": "create_strategy",
    "confidence": 0.85,
    "extracted_entities": {
        "indicators": ["RSI", "MACD"],
        "parameters": {"rsi_period": 14},
        "symbols": ["AAPL"],
        "goals": ["고수익"]
    },
    "reasoning": "사용자가 RSI와 MACD를 사용한 새 전략을 만들고 싶어 함"
}
"""

        user_prompt = f"""
사용자 요청: {request.query}

추가 컨텍스트: {json.dumps(request.context or {}, ensure_ascii=False)}
사용자 선호도: {json.dumps(request.user_preferences or {}, ensure_ascii=False)}
"""

        try:
            client = self._get_client()
            response = await client.chat.completions.create(
                model=model_config.model_id,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=self.temperature,
                max_tokens=1000,
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("LLM 응답이 비어있습니다.")

            llm_output = json.loads(content)

            self.openai_manager.track_usage(
                service_name=self.service_name,
                model_id=model_config.model_id,
                usage=response.usage,
            )

            # IntentType 검증
            intent_type_str = llm_output.get("intent_type", "create_strategy")
            try:
                intent_type = IntentType(intent_type_str)
            except ValueError:
                logger.warning(
                    f"Unknown intent type: {intent_type_str}, defaulting to CREATE_STRATEGY"
                )
                intent_type = IntentType.CREATE_STRATEGY

            confidence = float(llm_output.get("confidence", 0.5))
            confidence_level = (
                ConfidenceLevel.HIGH
                if confidence >= 0.8
                else (
                    ConfidenceLevel.MEDIUM if confidence >= 0.5 else ConfidenceLevel.LOW
                )
            )

            return ParsedIntent(
                intent_type=intent_type,
                confidence=confidence,
                confidence_level=confidence_level,
                extracted_entities=llm_output.get("extracted_entities", {}),
                reasoning=llm_output.get("reasoning", "LLM 의도 파싱 결과"),
            )

        except Exception as e:
            logger.error(f"Intent parsing failed: {e}", exc_info=True)
            # 기본값 반환 (CREATE_STRATEGY)
            return ParsedIntent(
                intent_type=IntentType.CREATE_STRATEGY,
                confidence=0.3,
                confidence_level=ConfidenceLevel.LOW,
                extracted_entities={},
                reasoning=f"의도 파싱 실패: {str(e)}",
            )

    async def _generate_strategy(
        self,
        request: StrategyBuilderRequest,
        parsed_intent: ParsedIntent,
        model_config: ModelConfig,
    ) -> tuple[Optional[GeneratedStrategyConfig], List[str]]:
        """
        파싱된 의도로부터 전략 설정 생성

        Returns:
            (GeneratedStrategyConfig or None, validation_errors)
        """
        system_prompt = """
당신은 전문 퀀트 전략 설계자입니다.
사용자 요청을 기반으로 기술적 지표 기반 트레이딩 전략을 설계하세요.

사용 가능한 지표:
- RSI (Relative Strength Index): 모멘텀 지표, 과매수/과매도 판단
- MACD (Moving Average Convergence Divergence): 추세 지표, 크로스오버
- Bollinger Bands: 변동성 지표, 밴드 돌파
- SMA (Simple Moving Average): 추세 지표, 이동평균
- EMA (Exponential Moving Average): 추세 지표, 지수이동평균

JSON 형식으로 응답하세요:
{
    "strategy_name": "RSI + MACD 모멘텀 전략",
    "strategy_type": "technical",
    "description": "RSI로 과매도 포착, MACD로 추세 전환 확인",
    "indicators": [
        {
            "indicator_name": "RSI",
            "indicator_type": "momentum",
            "confidence": 0.9,
            "rationale": "과매도 구간에서 매수 시그널 생성",
            "suggested_parameters": {"period": 14, "overbought": 70, "oversold": 30},
            "similarity_score": 0.95
        }
    ],
    "parameters": {
        "rsi_period": 14,
        "rsi_oversold": 30,
        "macd_fast": 12,
        "macd_slow": 26
    },
    "entry_conditions": "RSI < 30 (과매도) AND MACD 골든크로스",
    "exit_conditions": "RSI > 70 (과매수) OR MACD 데드크로스",
    "risk_management": "손절: -5%, 익절: +10%"
}
"""

        user_prompt = f"""
사용자 요청: {request.query}

파싱된 의도:
- 의도 유형: {parsed_intent.intent_type.value}
- 추출된 엔티티: {json.dumps(parsed_intent.extracted_entities, ensure_ascii=False)}

추가 컨텍스트: {json.dumps(request.context or {}, ensure_ascii=False)}

위 정보를 기반으로 구체적인 트레이딩 전략을 JSON 형식으로 설계하세요.
"""

        try:
            client = self._get_client()
            response = await client.chat.completions.create(
                model=model_config.model_id,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("LLM 응답이 비어있습니다.")

            llm_output = json.loads(content)

            self.openai_manager.track_usage(
                service_name=self.service_name,
                model_id=model_config.model_id,
                usage=response.usage,
            )

            # Indicators 변환
            indicators = [
                IndicatorRecommendation(**ind)
                for ind in llm_output.get("indicators", [])
            ]

            # Parameters 검증
            parameters = llm_output.get("parameters", {})
            parameter_validations = self._validate_parameters(parameters)
            validation_errors = [
                f"{pv.parameter_name}: {pv.message}"
                for pv in parameter_validations
                if pv.validation_status == ValidationStatus.ERROR
            ]

            strategy_config = GeneratedStrategyConfig(
                strategy_name=llm_output.get("strategy_name", "생성된 전략"),
                strategy_type=llm_output.get("strategy_type", "technical"),
                description=llm_output.get("description", "LLM 생성 전략"),
                indicators=indicators,
                parameters=parameters,
                parameter_validations=parameter_validations,
                entry_conditions=llm_output.get("entry_conditions", "조건 없음"),
                exit_conditions=llm_output.get("exit_conditions", "조건 없음"),
                risk_management=llm_output.get("risk_management"),
                expected_performance=llm_output.get("expected_performance"),
            )

            return strategy_config, validation_errors

        except Exception as e:
            logger.error(f"Strategy generation failed: {e}", exc_info=True)
            return None, [f"전략 생성 실패: {str(e)}"]

    def _validate_parameters(
        self, parameters: Dict[str, Any]
    ) -> List[ParameterValidation]:
        """
        파라미터 검증 (범위, 타입 체크)

        간소화 버전: 기본 범위 체크만 수행
        향후 확장: Pydantic 모델 기반 상세 검증
        """
        validations = []

        # 기본 검증 규칙
        validation_rules = {
            "rsi_period": {"min": 5, "max": 50, "type": int},
            "rsi_oversold": {"min": 10, "max": 40, "type": int},
            "rsi_overbought": {"min": 60, "max": 90, "type": int},
            "macd_fast": {"min": 5, "max": 20, "type": int},
            "macd_slow": {"min": 20, "max": 50, "type": int},
            "macd_signal": {"min": 5, "max": 15, "type": int},
            "bb_period": {"min": 10, "max": 50, "type": int},
            "bb_std_dev": {"min": 1.0, "max": 3.0, "type": float},
        }

        for param_name, param_value in parameters.items():
            if param_name in validation_rules:
                rule = validation_rules[param_name]
                is_valid = True
                message = None
                suggested_value = None

                # 타입 체크
                if not isinstance(param_value, rule["type"]):
                    is_valid = False
                    message = f"잘못된 타입: {type(param_value).__name__}, 예상: {rule['type'].__name__}"
                    suggested_value = (
                        rule["type"](param_value) if rule["type"] is int else None
                    )

                # 범위 체크
                elif "min" in rule and param_value < rule["min"]:
                    is_valid = False
                    message = f"값이 너무 작음: {param_value} < {rule['min']}"
                    suggested_value = rule["min"]

                elif "max" in rule and param_value > rule["max"]:
                    is_valid = False
                    message = f"값이 너무 큼: {param_value} > {rule['max']}"
                    suggested_value = rule["max"]

                validations.append(
                    ParameterValidation(
                        parameter_name=param_name,
                        value=param_value,
                        is_valid=is_valid,
                        validation_status=(
                            ValidationStatus.VALID
                            if is_valid
                            else ValidationStatus.ERROR
                        ),
                        message=message,
                        suggested_value=suggested_value,
                        value_range={
                            "min": rule.get("min"),
                            "max": rule.get("max"),
                            "type": rule["type"].__name__,
                        },
                    )
                )
            else:
                # 알 수 없는 파라미터 (경고)
                validations.append(
                    ParameterValidation(
                        parameter_name=param_name,
                        value=param_value,
                        is_valid=True,
                        validation_status=ValidationStatus.WARNING,
                        message="알 수 없는 파라미터 (검증 규칙 없음)",
                        suggested_value=None,
                        value_range=None,
                    )
                )

        return validations

    def _evaluate_approval_needs(
        self, strategy: GeneratedStrategyConfig, validation_errors: List[str]
    ) -> HumanApprovalRequest:
        """
        휴먼 승인 필요성 평가
        """
        requires_approval = True  # 기본적으로 승인 필요
        approval_reasons = []
        suggested_modifications = []

        # 검증 오류가 있는 경우
        if validation_errors:
            approval_reasons.append(
                f"{len(validation_errors)}개 파라미터 검증 오류 발견"
            )
            suggested_modifications.extend(
                [f"파라미터 수정: {err}" for err in validation_errors]
            )

        # 낮은 신뢰도 지표
        low_confidence_indicators = [
            ind.indicator_name for ind in strategy.indicators if ind.confidence < 0.7
        ]
        if low_confidence_indicators:
            approval_reasons.append(
                f"낮은 신뢰도 지표: {', '.join(low_confidence_indicators)}"
            )

        # 리스크 관리 규칙 없음
        if not strategy.risk_management:
            approval_reasons.append("리스크 관리 규칙이 정의되지 않음")
            suggested_modifications.append("손절/익절 규칙 추가 권장")

        # 승인 이유가 없으면 자동 승인 가능 (단, 기본은 승인 필요)
        if not approval_reasons:
            approval_reasons.append("전략이 기본 검증을 통과했으나 수동 검토 권장")

        return HumanApprovalRequest(
            requires_approval=requires_approval,
            approval_reasons=approval_reasons,
            suggested_modifications=suggested_modifications,
            approval_deadline=None,
        )

    def _generate_response_message(
        self,
        parsed_intent: ParsedIntent,
        strategy: Optional[GeneratedStrategyConfig],
        validation_errors: List[str],
    ) -> str:
        """응답 메시지 생성"""
        if parsed_intent.confidence < 0.5:
            return f"요청을 이해하지 못했습니다 (신뢰도: {parsed_intent.confidence:.2f}). 더 구체적인 설명을 부탁드립니다."

        if not strategy:
            return "전략 생성에 실패했습니다. 다시 시도해주세요."

        if validation_errors:
            return f"전략이 생성되었으나 {len(validation_errors)}개 검증 오류가 있습니다. 승인 후 수정이 필요합니다."

        return f"'{strategy.strategy_name}' 전략이 성공적으로 생성되었습니다. 승인을 기다리고 있습니다."

    def _generate_alternatives(self, request: StrategyBuilderRequest) -> List[str]:
        """대안 제안 생성 (의도 파싱 실패 시)"""
        return [
            "RSI와 MACD를 사용한 모멘텀 전략을 만들고 싶어요",
            "Bollinger Bands 돌파 전략을 테스트하고 싶어요",
            "단기 매매를 위한 EMA 크로스오버 전략을 추천해주세요",
        ]
