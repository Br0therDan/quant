"""
Strategy Models using Beanie (MongoDB ODM)
"""

from datetime import datetime, UTC
from typing import Union, Any

from app.models.base_model import BaseDocument
from pydantic import Field
from app.schemas.enums import StrategyType, SignalType
from app.strategies.configs import (
    SMACrossoverConfig,
    RSIMeanReversionConfig,
    MomentumConfig,
    BuyAndHoldConfig,
)


# Config 타입 Union with discriminator
StrategyConfigUnion = Union[
    SMACrossoverConfig,
    RSIMeanReversionConfig,
    MomentumConfig,
    BuyAndHoldConfig,
]


class Strategy(BaseDocument):
    """전략 정의 문서 모델"""

    name: str = Field(..., description="전략 이름")
    strategy_type: StrategyType = Field(..., description="전략 타입")
    description: str | None = Field(None, description="전략 설명")

    # ✅ 타입 안전한 설정 (discriminator 필드 사용)
    config: StrategyConfigUnion = Field(
        ..., description="전략 설정", discriminator="config_type"
    )

    # 상태 정보
    is_active: bool = Field(default=True, description="활성화 상태")
    is_template: bool = Field(default=False, description="템플릿 여부")

    # 메타데이터
    created_by: str | None = Field(None, description="생성자")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
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

    # ✅ 타입 안전한 기본 설정 (discriminator 필드 사용)
    default_config: StrategyConfigUnion = Field(
        ..., description="기본 설정", discriminator="config_type"
    )

    # 사용 통계
    usage_count: int = Field(default=0, description="사용 횟수")

    # 메타데이터
    category: str = Field(..., description="카테고리")
    difficulty: str = Field(default="intermediate", description="난이도")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
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
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "strategy_executions"
        indexes = [
            [("strategy_id", 1), ("timestamp", -1)],
            "symbol",
            "signal_type",
            "timestamp",
            "backtest_id",
        ]
