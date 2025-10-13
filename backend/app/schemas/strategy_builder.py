"""
Strategy Builder Schemas for Natural Language Strategy Creation

Phase 3 D2: Interactive Strategy Builder
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class IntentType(str, Enum):
    """사용자 의도 유형"""

    CREATE_STRATEGY = "create_strategy"  # 새 전략 생성
    MODIFY_STRATEGY = "modify_strategy"  # 기존 전략 수정
    EXPLAIN_STRATEGY = "explain_strategy"  # 전략 설명 요청
    RECOMMEND_PARAMETERS = "recommend_parameters"  # 파라미터 추천
    OPTIMIZE_STRATEGY = "optimize_strategy"  # 전략 최적화 제안


class ConfidenceLevel(str, Enum):
    """신뢰도 수준"""

    HIGH = "high"  # 0.8 이상
    MEDIUM = "medium"  # 0.5 - 0.8
    LOW = "low"  # 0.5 미만


class ValidationStatus(str, Enum):
    """검증 상태"""

    VALID = "valid"  # 검증 통과
    WARNING = "warning"  # 경고 있음 (사용 가능)
    ERROR = "error"  # 오류 (사용 불가)


class StrategyBuilderRequest(BaseModel):
    """대화형 전략 빌더 요청"""

    query: str = Field(
        ..., min_length=10, max_length=1000, description="자연어 전략 설명 또는 요청"
    )
    context: Optional[Dict[str, Any]] = Field(
        None, description="추가 컨텍스트 (심볼, 기간, 제약조건 등)"
    )
    user_preferences: Optional[Dict[str, Any]] = Field(
        None, description="사용자 선호도 (위험 선호도, 거래 빈도 등)"
    )
    existing_strategy_id: Optional[str] = Field(
        None, description="수정할 기존 전략 ID (modify intent)"
    )
    require_human_approval: bool = Field(
        default=True, description="사람 승인 필요 여부 (휴먼 인 더 루프)"
    )


class ParsedIntent(BaseModel):
    """파싱된 사용자 의도"""

    intent_type: IntentType = Field(..., description="의도 유형")
    confidence: float = Field(..., ge=0.0, le=1.0, description="의도 파싱 신뢰도")
    confidence_level: ConfidenceLevel = Field(..., description="신뢰도 수준")
    extracted_entities: Dict[str, Any] = Field(
        default_factory=dict, description="추출된 엔티티 (지표명, 파라미터 등)"
    )
    reasoning: str = Field(..., min_length=50, max_length=500, description="의도 판단 근거")


class IndicatorRecommendation(BaseModel):
    """지표 추천"""

    indicator_name: str = Field(
        ..., description="지표 이름 (예: RSI, MACD, Bollinger Bands)"
    )
    indicator_type: str = Field(
        ..., description="지표 유형 (momentum, trend, volatility 등)"
    )
    confidence: float = Field(..., ge=0.0, le=1.0, description="추천 신뢰도")
    rationale: str = Field(..., min_length=50, max_length=300, description="추천 이유")
    suggested_parameters: Dict[str, Any] = Field(
        default_factory=dict, description="제안된 기본 파라미터"
    )
    similarity_score: float = Field(
        ..., ge=0.0, le=1.0, description="쿼리와의 유사도 점수 (임베딩 기반)"
    )


class ParameterValidation(BaseModel):
    """파라미터 검증 결과"""

    parameter_name: str = Field(..., description="파라미터 이름")
    value: Any = Field(..., description="파라미터 값")
    is_valid: bool = Field(..., description="유효성 여부")
    validation_status: ValidationStatus = Field(..., description="검증 상태")
    message: Optional[str] = Field(None, description="검증 메시지 (경고/오류)")
    suggested_value: Optional[Any] = Field(None, description="제안된 값 (오류 시)")
    value_range: Optional[Dict[str, Any]] = Field(
        None, description="허용 범위 (min, max, allowed_values 등)"
    )


class GeneratedStrategyConfig(BaseModel):
    """생성된 전략 설정"""

    strategy_name: str = Field(..., min_length=3, max_length=100, description="전략 이름")
    strategy_type: str = Field(..., description="전략 타입 (기술적 지표 기반)")
    description: str = Field(..., min_length=50, max_length=500, description="전략 설명")
    indicators: List[IndicatorRecommendation] = Field(
        ..., min_length=1, max_length=5, description="사용된 지표 목록 (1-5개)"
    )
    parameters: Dict[str, Any] = Field(..., description="전략 파라미터")
    parameter_validations: List[ParameterValidation] = Field(
        ..., description="파라미터 검증 결과"
    )
    entry_conditions: str = Field(
        ..., min_length=50, max_length=300, description="진입 조건 설명"
    )
    exit_conditions: str = Field(
        ..., min_length=50, max_length=300, description="청산 조건 설명"
    )
    risk_management: Optional[str] = Field(None, description="리스크 관리 규칙")
    expected_performance: Optional[Dict[str, Any]] = Field(
        None, description="예상 성과 (과거 유사 전략 기반)"
    )


class HumanApprovalRequest(BaseModel):
    """휴먼 승인 요청"""

    requires_approval: bool = Field(..., description="승인 필요 여부")
    approval_reasons: List[str] = Field(
        default_factory=list, description="승인이 필요한 이유 (위험 요소 등)"
    )
    suggested_modifications: List[str] = Field(
        default_factory=list, description="수정 제안 사항"
    )
    approval_deadline: Optional[datetime] = Field(None, description="승인 기한")


class StrategyBuilderResponse(BaseModel):
    """대화형 전략 빌더 응답"""

    status: str = Field(..., description="처리 상태 (success/warning/error)")
    message: str = Field(..., description="응답 메시지")
    parsed_intent: ParsedIntent = Field(..., description="파싱된 사용자 의도")
    generated_strategy: Optional[GeneratedStrategyConfig] = Field(
        None, description="생성된 전략 설정"
    )
    human_approval: HumanApprovalRequest = Field(..., description="휴먼 승인 요청 정보")
    alternative_suggestions: Optional[List[str]] = Field(
        None, description="대안 제안 (의도 파싱 실패 시)"
    )
    processing_time_ms: float = Field(..., description="처리 시간 (밀리초)")
    llm_model: str = Field(..., description="사용된 LLM 모델")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="생성 시간")
    validation_errors: Optional[List[str]] = Field(None, description="검증 오류 목록")
    overall_confidence: float = Field(
        ..., ge=0.0, le=1.0, description="전체 신뢰도 (의도 + 전략 생성)"
    )


class StrategyApprovalRequest(BaseModel):
    """전략 승인 요청 (휴먼 인 더 루프)"""

    strategy_builder_response_id: str = Field(..., description="빌더 응답 ID")
    approved: bool = Field(..., description="승인 여부")
    modifications: Optional[Dict[str, Any]] = Field(None, description="수정 사항")
    approval_notes: Optional[str] = Field(None, description="승인 메모")


class StrategyApprovalResponse(BaseModel):
    """전략 승인 응답"""

    status: str = Field(..., description="승인 상태 (approved/rejected/modified)")
    message: str = Field(..., description="응답 메시지")
    strategy_id: Optional[str] = Field(None, description="생성된 전략 ID (승인 시)")
    approved_at: datetime = Field(default_factory=datetime.utcnow, description="승인 시간")


# Embedding-based Indicator Search
class IndicatorSearchRequest(BaseModel):
    """지표 검색 요청 (임베딩 기반)"""

    query: str = Field(..., min_length=3, max_length=200, description="검색 쿼리")
    top_k: int = Field(default=5, ge=1, le=10, description="상위 K개 결과")
    filters: Optional[Dict[str, Any]] = Field(None, description="필터 (유형, 카테고리 등)")


class IndicatorSearchResponse(BaseModel):
    """지표 검색 응답"""

    status: str = Field(..., description="응답 상태")
    indicators: List[IndicatorRecommendation] = Field(..., description="검색된 지표 목록")
    total: int = Field(..., description="총 검색 결과 수")
    query_embedding: Optional[List[float]] = Field(None, description="쿼리 임베딩 (디버깅용)")
