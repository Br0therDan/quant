"""
Strategy Models using Beanie (MongoDB ODM)
"""

from datetime import datetime
from enum import Enum
from typing import Any

from .base_model import BaseDocument
from pydantic import Field


class StrategyType(str, Enum):
    """지원되는 전략 타입"""

    SMA_CROSSOVER = "sma_crossover"
    RSI_MEAN_REVERSION = "rsi_mean_reversion"
    MOMENTUM = "momentum"
    BUY_AND_HOLD = "buy_and_hold"


class SignalType(str, Enum):
    """신호 타입"""

    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class Strategy(BaseDocument):
    """전략 정의 문서 모델"""

    name: str = Field(..., description="전략 이름")
    strategy_type: StrategyType = Field(..., description="전략 타입")
    description: str | None = Field(None, description="전략 설명")

    # 전략 파라미터
    parameters: dict[str, Any] = Field(default_factory=dict, description="전략 파라미터")

    # 상태 정보
    is_active: bool = Field(default=True, description="활성화 상태")
    is_template: bool = Field(default=False, description="템플릿 여부")

    # 메타데이터
    created_by: str | None = Field(None, description="생성자")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    tags: list[str] = Field(default_factory=list, description="태그")

    class Settings:
        name = "strategies"
        indexes = [
            "name",
            "strategy_type",
            "is_active",
            "is_template",
            "created_at",
        ]


class StrategyTemplate(BaseDocument):
    """전략 템플릿 문서 모델"""

    name: str = Field(..., description="템플릿 이름")
    strategy_type: StrategyType = Field(..., description="전략 타입")
    description: str = Field(..., description="템플릿 설명")

    # 템플릿 설정
    default_parameters: dict[str, Any] = Field(
        default_factory=dict, description="기본 파라미터"
    )
    parameter_schema: dict[str, Any] | None = Field(None, description="파라미터 스키마")

    # 사용 통계
    usage_count: int = Field(default=0, description="사용 횟수")

    # 메타데이터
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    tags: list[str] = Field(default_factory=list, description="태그")

    class Settings:
        name = "strategy_templates"
        indexes = [
            "name",
            "strategy_type",
            "created_at",
        ]


class StrategyExecution(BaseDocument):
    """전략 실행 기록 문서 모델"""

    strategy_id: str = Field(..., description="전략 ID")
    strategy_name: str = Field(..., description="전략 이름")

    # 실행 정보
    symbol: str = Field(..., description="실행 대상 심볼")
    signal_type: SignalType = Field(..., description="생성된 신호")
    signal_strength: float = Field(..., ge=0.0, le=1.0, description="신호 강도")

    # 가격 정보
    price: float = Field(..., gt=0, description="신호 생성 시점 가격")
    timestamp: datetime = Field(..., description="신호 생성 시간")

    # 추가 정보
    metadata: dict[str, Any] = Field(default_factory=dict, description="추가 메타데이터")

    # 백테스트 정보 (선택적)
    backtest_id: str | None = Field(None, description="백테스트 ID")

    # 메타데이터
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "strategy_executions"
        indexes = [
            [("strategy_id", 1), ("timestamp", -1)],
            "symbol",
            "signal_type",
            "timestamp",
            "backtest_id",
        ]
