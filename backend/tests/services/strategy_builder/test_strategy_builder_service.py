"""Unit tests for the GenAI StrategyBuilderService."""

import json
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.schemas.enums import IntentType
from app.schemas.gen_ai.strategy_builder import (
    ConfidenceLevel,
    GeneratedStrategyConfig,
    # HumanApprovalNeeds,
    IndicatorRecommendation,
    StrategyBuilderRequest,
    ValidationStatus,
)
from app.services.gen_ai.applications.strategy_builder_service import (
    StrategyBuilderService,
)


@pytest.fixture
def mock_strategy_service():
    """Mock StrategyService"""
    service = MagicMock()
    service.get_strategy = AsyncMock()
    return service


@pytest.fixture
def strategy_builder_service(mock_strategy_service):
    """StrategyBuilderService 인스턴스 (OpenAI 없이)"""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"}):
        service = StrategyBuilderService(strategy_service=mock_strategy_service)
        return service


class TestParseIntent:
    """의도 파싱 테스트"""

    @pytest.mark.asyncio
    async def test_parse_intent_high_confidence(self, strategy_builder_service):
        """명확한 요청 → HIGH 신뢰도"""
        request = StrategyBuilderRequest(
            query="RSI가 30 이하일 때 매수하고 70 이상일 때 매도하는 전략을 만들어줘",
            context=None,
            user_preferences=None,
            existing_strategy_id=None,
        )

        # Mock OpenAI response
        mock_response = {
            "intent_type": "create_strategy",
            "confidence": 0.95,
            "extracted_entities": {
                "indicators": ["RSI"],
                "parameters": {
                    "rsi_period": 14,
                    "rsi_oversold": 30,
                    "rsi_overbought": 70,
                },
                "symbols": [],
                "goals": ["모멘텀"],
            },
            "reasoning": "사용자가 RSI 지표를 사용한 모멘텀 전략을 명확히 요청함. RSI 30 이하에서 매수, 70 이상에서 매도하는 명확한 진입/퇴출 조건을 제시했습니다.",
        }

        with patch.object(
            strategy_builder_service.client.chat.completions,
            "create",
            new=AsyncMock(
                return_value=MagicMock(
                    choices=[
                        MagicMock(message=MagicMock(content=json.dumps(mock_response)))
                    ]
                )
            ),
        ):
            parsed_intent = await strategy_builder_service._parse_intent(request)

        assert parsed_intent.intent_type == IntentType.CREATE_STRATEGY
        assert parsed_intent.confidence >= 0.8
        assert parsed_intent.confidence_level == ConfidenceLevel.HIGH
        assert "RSI" in parsed_intent.extracted_entities.get("indicators", [])

    @pytest.mark.asyncio
    async def test_parse_intent_medium_confidence(self, strategy_builder_service):
        """중간 신뢰도 요청"""
        request = StrategyBuilderRequest(
            query="추세 추종 전략을 만들어주세요 부탁합니다",
            context=None,
            user_preferences=None,
            existing_strategy_id=None,
        )

        mock_response = {
            "intent_type": "create_strategy",
            "confidence": 0.65,
            "extracted_entities": {
                "indicators": ["MACD", "EMA"],
                "goals": ["추세 추종"],
            },
            "reasoning": "추세 추종 전략이 요청되었으나 구체적인 지표가 명시되지 않았습니다. MACD와 EMA를 추천 지표로 제안합니다.",
        }

        with patch.object(
            strategy_builder_service.client.chat.completions,
            "create",
            new=AsyncMock(
                return_value=MagicMock(
                    choices=[
                        MagicMock(message=MagicMock(content=json.dumps(mock_response)))
                    ]
                )
            ),
        ):
            parsed_intent = await strategy_builder_service._parse_intent(request)

        assert 0.5 <= parsed_intent.confidence < 0.8

    @pytest.mark.asyncio
    async def test_parse_intent_low_confidence(self, strategy_builder_service):
        """불명확한 요청 → LOW 신뢰도"""
        request = StrategyBuilderRequest(
            query="뭔가 좋은 전략을 만들어주세요",
            context=None,
            user_preferences=None,
            existing_strategy_id=None,
        )

        mock_response = {
            "intent_type": "create_strategy",
            "confidence": 0.35,
            "extracted_entities": {},
            "reasoning": "요청이 너무 모호하여 의도 파악이 어렵습니다. 구체적인 지표나 목표를 명시해주시면 더 나은 전략을 제안할 수 있습니다.",
        }

        with patch.object(
            strategy_builder_service.client.chat.completions,
            "create",
            new=AsyncMock(
                return_value=MagicMock(
                    choices=[
                        MagicMock(message=MagicMock(content=json.dumps(mock_response)))
                    ]
                )
            ),
        ):
            parsed_intent = await strategy_builder_service._parse_intent(request)

        assert parsed_intent.confidence_level == ConfidenceLevel.LOW
        assert parsed_intent.confidence < 0.5

    @pytest.mark.asyncio
    async def test_parse_intent_modify_strategy(self, strategy_builder_service):
        """기존 전략 수정 의도"""
        request = StrategyBuilderRequest(
            query="RSI 기간을 21로 변경해주세요",
            context=None,
            user_preferences=None,
            existing_strategy_id="strategy_123",
        )

        mock_response = {
            "intent_type": "modify_strategy",
            "confidence": 0.88,
            "extracted_entities": {"parameters": {"rsi_period": 21}},
            "reasoning": "기존 전략의 RSI 기간 파라미터 수정 요청입니다. 기간을 14에서 21로 변경하여 신호의 민감도를 조정합니다.",
        }

        with patch.object(
            strategy_builder_service.client.chat.completions,
            "create",
            new=AsyncMock(
                return_value=MagicMock(
                    choices=[
                        MagicMock(message=MagicMock(content=json.dumps(mock_response)))
                    ]
                )
            ),
        ):
            parsed_intent = await strategy_builder_service._parse_intent(request)

        assert parsed_intent.intent_type == IntentType.MODIFY_STRATEGY


class TestValidateParameters:
    """파라미터 검증 테스트"""

    def test_validate_parameters_all_valid(self, strategy_builder_service):
        """모든 파라미터 유효"""
        parameters = {
            "rsi_period": 14,
            "rsi_oversold": 30,
            "rsi_overbought": 70,
            "macd_fast": 12,
            "macd_slow": 26,
        }

        validations = strategy_builder_service._validate_parameters(parameters)

        assert all(v.is_valid for v in validations)
        assert all(v.validation_status == ValidationStatus.VALID for v in validations)

    def test_validate_parameters_out_of_range_min(self, strategy_builder_service):
        """범위 미만 → ERROR + suggested_value"""
        parameters = {"rsi_period": 3}  # min: 5

        validations = strategy_builder_service._validate_parameters(parameters)

        assert len(validations) == 1
        assert not validations[0].is_valid
        assert validations[0].validation_status == ValidationStatus.ERROR
        assert validations[0].suggested_value == 5
        assert "값이 너무 작음" in validations[0].message

    def test_validate_parameters_out_of_range_max(self, strategy_builder_service):
        """범위 초과 → ERROR + suggested_value"""
        parameters = {"rsi_period": 100}  # max: 50

        validations = strategy_builder_service._validate_parameters(parameters)

        assert len(validations) == 1
        assert not validations[0].is_valid
        assert validations[0].validation_status == ValidationStatus.ERROR
        assert validations[0].suggested_value == 50
        assert "값이 너무 큼" in validations[0].message

    def test_validate_parameters_wrong_type(self, strategy_builder_service):
        """잘못된 타입 → ERROR"""
        parameters = {"rsi_period": "14"}  # str instead of int

        validations = strategy_builder_service._validate_parameters(parameters)

        assert len(validations) == 1
        assert not validations[0].is_valid
        assert "잘못된 타입" in validations[0].message

    def test_validate_parameters_unknown_parameter(self, strategy_builder_service):
        """알 수 없는 파라미터 → WARNING"""
        parameters = {"unknown_param": 123}

        validations = strategy_builder_service._validate_parameters(parameters)

        assert len(validations) == 1
        assert validations[0].is_valid  # 유효하지만 경고
        assert validations[0].validation_status == ValidationStatus.WARNING
        assert "알 수 없는 파라미터" in validations[0].message

    def test_validate_parameters_mixed(self, strategy_builder_service):
        """혼합: 유효 + 오류 + 경고"""
        parameters = {
            "rsi_period": 14,  # VALID
            "rsi_oversold": 5,  # ERROR (min: 10)
            "unknown_param": 999,  # WARNING
        }

        validations = strategy_builder_service._validate_parameters(parameters)

        assert len(validations) == 3
        valid_count = sum(
            1 for v in validations if v.validation_status == ValidationStatus.VALID
        )
        error_count = sum(
            1 for v in validations if v.validation_status == ValidationStatus.ERROR
        )
        warning_count = sum(
            1 for v in validations if v.validation_status == ValidationStatus.WARNING
        )

        assert valid_count == 1
        assert error_count == 1
        assert warning_count == 1


class TestEvaluateApprovalNeeds:
    """휴먼 승인 필요성 평가 테스트"""

    def test_approval_needed_validation_errors(self, strategy_builder_service):
        """검증 오류 → 승인 필요"""
        strategy = GeneratedStrategyConfig(
            strategy_name="Test Strategy",
            strategy_type="technical",
            description="테스트 전략입니다. " * 10,  # 50자 이상
            indicators=[
                IndicatorRecommendation(
                    indicator_name="RSI",
                    indicator_type="momentum",
                    confidence=0.9,
                    rationale="과매수/과매도 판단에 유용합니다. " * 5,  # 50자 이상
                    similarity_score=0.95,
                )
            ],
            parameters={"rsi_period": 14},
            parameter_validations=[],
            entry_conditions="RSI < 30 (과매도 구간에서 매수 시그널 생성하는 기술적 지표 전략입니다. RSI 지표로 과매도 구간 감지합니다)",
            exit_conditions="RSI > 70 (과매수 구간에서 매도 시그널 생성하는 기술적 지표 전략입니다. RSI 지표로 과매수 구간 감지합니다)",
            risk_management=None,
            expected_performance=None,
        )
        validation_errors = ["rsi_period 범위 초과", "macd_fast 타입 오류"]

        approval = strategy_builder_service._evaluate_approval_needs(
            strategy, validation_errors
        )

        assert approval.requires_approval
        assert len(approval.approval_reasons) > 0
        assert any("검증 오류" in reason for reason in approval.approval_reasons)

        strategy = GeneratedStrategyConfig(
            strategy_name="Test Strategy",
            strategy_type="technical",
            description="테스트 전략입니다. " * 10,
            indicators=[
                IndicatorRecommendation(
                    indicator_name="Stochastic",
                    indicator_type="momentum",
                    confidence=0.55,  # 낮은 신뢰도
                    rationale="스토캐스틱 오실레이터를 사용한 과매수 과매도 판단 지표입니다. 모멘텀 전환점을 효과적으로 포착합니다.",
                    similarity_score=0.60,
                )
            ],
            parameters={},
            parameter_validations=[],
            entry_conditions="Stochastic < 20에서 매수 시그널 생성합니다 (과매도 구간). K선과 D선 교차시 진입합니다.",
            exit_conditions="Stochastic > 80에서 매도 시그널 생성합니다 (과매수 구간). K선과 D선 교차시 청산합니다.",
            risk_management=None,
            expected_performance=None,
        )

        validation_errors = []

        approval = strategy_builder_service._evaluate_approval_needs(
            strategy, validation_errors
        )

        assert approval.requires_approval
        strategy = GeneratedStrategyConfig(
            strategy_name="Test Strategy",
            strategy_type="technical",
            description="테스트 전략입니다. " * 10,
            indicators=[
                IndicatorRecommendation(
                    indicator_name="RSI",
                    indicator_type="momentum",
                    confidence=0.9,
                    rationale="과매수/과매도 판단에 유용합니다. " * 5,
                    similarity_score=0.95,
                )
            ],
            parameters={"rsi_period": 14},
            parameter_validations=[],
            entry_conditions="RSI < 30 (과매도 구간에서 매수 시그널 생성합니다. RSI 지표로 진입 조건을 판단합니다)",
            exit_conditions="RSI > 70 (과매수 구간에서 매도 시그널 생성합니다. RSI 지표로 청산 조건을 판단합니다)",
            risk_management=None,  # 리스크 관리 없음
            expected_performance=None,
        )

        validation_errors = []

        approval = strategy_builder_service._evaluate_approval_needs(
            strategy, validation_errors
        )

        assert approval.requires_approval
        strategy = GeneratedStrategyConfig(
            strategy_name="Test Strategy",
            strategy_type="technical",
            description="테스트 전략입니다. " * 10,
            indicators=[
                IndicatorRecommendation(
                    indicator_name="RSI",
                    indicator_type="momentum",
                    confidence=0.9,
                    rationale="과매수/과매도 판단에 유용합니다. " * 5,
                    similarity_score=0.95,
                )
            ],
            parameters={"rsi_period": 14},
            parameter_validations=[],
            entry_conditions="RSI < 30 (과매도 구간에서 매수 시그널 생성합니다. RSI 지표로 진입 조건을 판단합니다)",
            exit_conditions="RSI > 70 (과매수 구간에서 매도 시그널 생성합니다. RSI 지표로 청산 조건을 판단합니다)",
            risk_management="손절: -5%, 익절: +10%",
            expected_performance=None,
        )

        validation_errors = []

        approval = strategy_builder_service._evaluate_approval_needs(
            strategy, validation_errors
        )

        # risk_management가 있어도 기본 정책상 항상 수동 검토 권장
        assert approval.requires_approval

    def test_approval_needed_user_request(self, strategy_builder_service):
        """사용자 명시 요청 → 승인 필요"""
        strategy = GeneratedStrategyConfig(
            strategy_name="Test Strategy",
            strategy_type="technical",
            description="테스트 전략입니다. " * 10,
            indicators=[
                IndicatorRecommendation(
                    indicator_name="RSI",
                    indicator_type="momentum",
                    confidence=0.9,
                    rationale="과매수/과매도 판단에 유용합니다. " * 5,
                    similarity_score=0.95,
                )
            ],
            parameters={"rsi_period": 14},
            parameter_validations=[],
            entry_conditions="RSI < 30 (과매도 구간에서 매수 시그널 생성하는 모멘텀 전략입니다. RSI 지표로 판단합니다)",
            exit_conditions="RSI > 70 (과매수 구간에서 매도 시그널 생성하는 모멘텀 전략입니다. RSI 지표로 판단합니다)",
            risk_management="손절: -5%, 익절: +10%",
            expected_performance=None,
        )

        validation_errors = []

        # _evaluate_approval_needs는 기본적으로 항상 승인 필요(안전한 기본값)
        approval = strategy_builder_service._evaluate_approval_needs(
            strategy, validation_errors
        )

        # 검증 오류가 없어도 수동 검토 권장 (기본 정책)
        assert approval.requires_approval
        assert len(approval.approval_reasons) > 0
        # 검증을 통과했으나 수동 검토가 필요함
        assert "검증을 통과" in approval.approval_reasons[0]


class TestBuildStrategy:
    """전략 생성 통합 테스트"""

    @pytest.mark.asyncio
    async def test_build_strategy_success(self, strategy_builder_service):
        """전략 생성 성공 (E2E)"""
        request = StrategyBuilderRequest(
            query="RSI 모멘텀 전략을 만들어줘. 과매도/과매수 구간을 활용하고 싶습니다.",
            require_human_approval=True,
            context=None,
            user_preferences=None,
            existing_strategy_id=None,
        )

        # Mock 의도 파싱
        mock_intent_response = {
            "intent_type": "create_strategy",
            "confidence": 0.92,
            "extracted_entities": {"indicators": ["RSI"]},
            "reasoning": "사용자가 RSI 모멘텀 전략 생성을 요청했습니다. 과매도/과매수 구간 활용을 원하며 기술적 지표 기반 전략입니다.",
        }

        # Mock 전략 생성
        mock_strategy_response = {
            "strategy_name": "RSI 모멘텀 전략",
            "strategy_type": "technical",
            "description": "RSI 지표를 사용한 모멘텀 기반 트레이딩 전략입니다. " * 5,
            "indicators": [
                {
                    "indicator_name": "RSI",
                    "indicator_type": "momentum",
                    "confidence": 0.95,
                    "rationale": "과매도 구간에서 매수 시그널을 생성하는 효과적인 지표입니다. " * 3,
                    "suggested_parameters": {
                        "period": 14,
                        "overbought": 70,
                        "oversold": 30,
                    },
                    "similarity_score": 0.98,
                }
            ],
            "parameters": {"rsi_period": 14, "rsi_oversold": 30, "rsi_overbought": 70},
            "entry_conditions": "RSI < 30 (과매도) 구간에서 매수 시그널을 생성합니다. RSI 지표가 30 이하로 떨어질 때 진입합니다.",
            "exit_conditions": "RSI > 70 (과매수) 구간에서 매도 시그널을 생성합니다. RSI 지표가 70 이상으로 상승할 때 청산합니다.",
            "risk_management": "손절: -5%, 익절: +10%",
        }

        with patch.object(
            strategy_builder_service.client.chat.completions,
            "create",
            new=AsyncMock(
                side_effect=[
                    # 첫 번째 호출: 의도 파싱
                    MagicMock(
                        choices=[
                            MagicMock(
                                message=MagicMock(
                                    content=json.dumps(mock_intent_response)
                                )
                            )
                        ]
                    ),
                    # 두 번째 호출: 전략 생성
                    MagicMock(
                        choices=[
                            MagicMock(
                                message=MagicMock(
                                    content=json.dumps(mock_strategy_response)
                                )
                            )
                        ]
                    ),
                ]
            ),
        ):
            response = await strategy_builder_service.build_strategy(request)

        assert response.status == "success"
        assert response.parsed_intent.intent_type == IntentType.CREATE_STRATEGY
        assert response.parsed_intent.confidence >= 0.8
        assert response.generated_strategy is not None
        assert response.generated_strategy.strategy_name == "RSI 모멘텀 전략"
        assert response.human_approval.requires_approval
        assert response.overall_confidence > 0.7

    @pytest.mark.asyncio
    async def test_build_strategy_low_confidence_fallback(
        self, strategy_builder_service
    ):
        """낮은 신뢰도 → 대안 제안"""
        request = StrategyBuilderRequest(
            query="뭔가 좋은 전략을 만들어줘. 수익률 높은 걸로 부탁해",
            context=None,
            user_preferences=None,
            existing_strategy_id=None,
        )

        mock_intent_response = {
            "intent_type": "create_strategy",
            "confidence": 0.35,
            "extracted_entities": {},
            "reasoning": "요청이 너무 모호함",
        }

        with patch.object(
            strategy_builder_service.client.chat.completions,
            "create",
            new=AsyncMock(
                return_value=MagicMock(
                    choices=[
                        MagicMock(
                            message=MagicMock(content=json.dumps(mock_intent_response))
                        )
                    ]
                )
            ),
        ):
            response = await strategy_builder_service.build_strategy(request)

        assert response.status == "error"
        assert response.overall_confidence < 0.5
        assert response.alternative_suggestions is not None
        assert len(response.alternative_suggestions) > 0

    @pytest.mark.asyncio
    async def test_build_strategy_no_openai_client(self, mock_strategy_service):
        """OpenAI 클라이언트 없음 → 오류 또는 정상 처리 (환경에 따라)"""
        # OPENAI_API_KEY 환경변수 제거
        with patch.dict("os.environ", {}, clear=True):
            service = StrategyBuilderService(strategy_service=mock_strategy_service)

        request = StrategyBuilderRequest(
            query="RSI 전략을 만들어줘. 모멘텀 기반으로 부탁해",
            context=None,
            user_preferences=None,
            existing_strategy_id=None,
        )

        # OpenAI 클라이언트가 초기화되지 않으면 오류, 초기화되면 API 오류
        response = await service.build_strategy(request)

        # 결과는 error 상태여야 함 (API 키 없음 또는 모델 접근 불가)
        assert response.status == "error"
        assert response.parsed_intent is None or response.parsed_intent.confidence < 0.5


class TestIndicatorKnowledge:
    """지표 지식 베이스 테스트"""

    def test_indicator_knowledge_initialized(self, strategy_builder_service):
        """지표 지식 베이스가 초기화됨"""
        assert hasattr(strategy_builder_service, "indicator_knowledge")
        assert len(strategy_builder_service.indicator_knowledge) >= 5

        # 기본 지표 확인
        assert "RSI" in strategy_builder_service.indicator_knowledge
        assert "MACD" in strategy_builder_service.indicator_knowledge
        assert "Bollinger Bands" in strategy_builder_service.indicator_knowledge

    def test_indicator_knowledge_structure(self, strategy_builder_service):
        """지표 정보 구조 확인"""
        rsi_info = strategy_builder_service.indicator_knowledge["RSI"]

        assert "name" in rsi_info
        assert "type" in rsi_info
        assert "description" in rsi_info
        assert "parameters" in rsi_info
        assert "keywords" in rsi_info

        assert rsi_info["type"] == "momentum"
        assert isinstance(rsi_info["parameters"], dict)
        assert isinstance(rsi_info["keywords"], list)
