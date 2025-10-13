"""
Strategy API Schemas
"""

from datetime import datetime
from typing import Any

from pydantic import Field
from .base_schema import BaseSchema
from app.models.strategy import SignalType, StrategyType, StrategyConfigUnion


# Request Schemas
class StrategyCreate(BaseSchema):
    """Strategy creation request"""

    name: str = Field(..., description="전략 이름")
    strategy_type: StrategyType = Field(..., description="전략 타입")
    description: str | None = Field(None, description="전략 설명")
    config: StrategyConfigUnion = Field(..., description="전략 설정 (타입 안전)")
    tags: list[str] = Field(default_factory=list, description="태그")


class StrategyUpdate(BaseSchema):
    """Strategy update request"""

    name: str | None = Field(None, description="전략 이름")
    description: str | None = Field(None, description="전략 설명")
    config: StrategyConfigUnion | None = Field(None, description="전략 설정")
    is_active: bool | None = Field(None, description="활성화 상태")
    tags: list[str | None] | None = Field(None, description="태그")


class StrategyExecute(BaseSchema):
    """Strategy execution request"""

    symbol: str = Field(..., description="대상 심볼")
    market_data: dict[str, Any] = Field(..., description="시장 데이터")


class TemplateCreate(BaseSchema):
    """Template creation request"""

    name: str = Field(..., description="템플릿 이름")
    strategy_type: StrategyType = Field(..., description="전략 타입")
    description: str = Field(..., description="템플릿 설명")
    default_config: StrategyConfigUnion = Field(..., description="기본 설정 타입 안전")
    category: str = Field(..., description="카테고리")
    tags: list[str] = Field(default_factory=list, description="태그")


class TemplateUpdate(BaseSchema):
    """Template update request"""

    name: str | None = Field(None, description="템플릿 이름")
    description: str | None = Field(None, description="템플릿 설명")
    default_config: StrategyConfigUnion | None = Field(None, description="기본 설정")
    tags: list[str] | None = Field(None, description="태그")


class StrategyCreateFromTemplate(BaseSchema):
    """Create strategy from template request"""

    name: str = Field(..., description="전략 이름")
    config_overrides: StrategyConfigUnion | None = Field(None, description="설정 오버라이드")


# Response Schemas
class StrategyResponse(BaseSchema):
    """Strategy response"""

    id: str = Field(..., description="전략 ID")
    name: str = Field(..., description="전략 이름")
    strategy_type: StrategyType = Field(..., description="전략 타입")
    description: str | None = Field(None, description="전략 설명")
    config: StrategyConfigUnion = Field(..., description="전략 설정 (타입 안전)")
    is_active: bool = Field(..., description="활성화 상태")
    is_template: bool = Field(..., description="템플릿 여부")
    created_by: str | None = Field(None, description="생성자")
    created_at: datetime = Field(..., description="생성 시간")
    updated_at: datetime = Field(..., description="수정 시간")
    tags: list[str] = Field(default_factory=list, description="태그")

    class Config:
        from_attributes = True


class TemplateResponse(BaseSchema):
    """Template response"""

    id: str = Field(..., description="템플릿 ID")
    name: str = Field(..., description="템플릿 이름")
    strategy_type: StrategyType = Field(..., description="전략 타입")
    description: str = Field(..., description="템플릿 설명")
    default_config: StrategyConfigUnion = Field(..., description="기본 설정 (타입 안전)")
    category: str = Field(..., description="카테고리")
    usage_count: int = Field(..., description="사용 횟수")
    created_at: datetime = Field(..., description="생성 시간")
    updated_at: datetime = Field(..., description="수정 시간")
    tags: list[str] = Field(default_factory=list, description="태그")

    class Config:
        from_attributes = True


class ExecutionResponse(BaseSchema):
    """Execution response"""

    id: str = Field(..., description="실행 ID")
    strategy_id: str = Field(..., description="전략 ID")
    strategy_name: str = Field(..., description="전략 이름")
    symbol: str = Field(..., description="심볼")
    signal_type: SignalType = Field(..., description="신호 타입")
    signal_strength: float = Field(..., description="신호 강도")
    price: float = Field(..., description="가격")
    timestamp: datetime = Field(..., description="실행 시간")
    metadata: dict[str, Any] = Field(default_factory=dict, description="메타데이터")
    backtest_id: str | None = Field(None, description="백테스트 ID")
    created_at: datetime = Field(..., description="생성 시간")

    class Config:
        from_attributes = True


class PerformanceResponse(BaseSchema):
    """Performance response"""

    id: str = Field(..., description="성과 ID")
    strategy_id: str = Field(..., description="전략 ID")
    strategy_name: str = Field(..., description="전략 이름")
    total_signals: int = Field(..., description="총 신호 수")
    buy_signals: int = Field(..., description="매수 신호 수")
    sell_signals: int = Field(..., description="매도 신호 수")
    hold_signals: int = Field(..., description="보유 신호 수")
    total_return: float | None = Field(None, description="총 수익률")
    win_rate: float | None = Field(None, description="승률")
    avg_return_per_trade: float | None = Field(None, description="거래당 평균 수익률")
    max_drawdown: float | None = Field(None, description="최대 낙폭")
    sharpe_ratio: float | None = Field(None, description="샤프 비율")
    calmar_ratio: float | None = Field(None, description="칼마 비율")
    volatility: float | None = Field(None, description="변동성")
    start_date: datetime | None = Field(None, description="시작일")
    end_date: datetime | None = Field(None, description="종료일")
    accuracy: float | None = Field(None, description="정확도")
    avg_signal_strength: float | None = Field(None, description="평균 신호 강도")
    created_at: datetime = Field(..., description="생성 시간")
    updated_at: datetime = Field(..., description="수정 시간")

    class Config:
        from_attributes = True


# List Response Schemas
class StrategyListResponse(BaseSchema):
    """Strategy list response"""

    strategies: list[StrategyResponse] = Field(..., description="전략 목록")
    total: int = Field(..., description="총 개수")


class TemplateListResponse(BaseSchema):
    """Template list response"""

    templates: list[TemplateResponse] = Field(..., description="템플릿 목록")
    total: int = Field(..., description="총 개수")


class ExecutionListResponse(BaseSchema):
    """Execution list response"""

    executions: list[ExecutionResponse] = Field(..., description="실행 목록")
    total: int = Field(..., description="총 개수")
