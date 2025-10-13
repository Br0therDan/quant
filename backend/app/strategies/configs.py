"""
전략 설정 클래스
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional


class StrategyConfigBase(BaseModel):
    """전략 설정 기본 클래스"""

    # 공통 설정
    lookback_period: int = Field(default=252, ge=30, description="조회 기간 (일)")
    min_data_points: int = Field(default=30, ge=10, description="최소 데이터 포인트")

    # 리스크 관리
    max_position_size: float = Field(
        default=1.0, ge=0.0, le=1.0, description="최대 포지션 크기"
    )
    stop_loss_pct: Optional[float] = Field(
        default=None, ge=0.0, le=1.0, description="손절 비율"
    )
    take_profit_pct: Optional[float] = Field(default=None, ge=0.0, description="익절 비율")


class SMACrossoverConfig(StrategyConfigBase):
    """SMA 크로스오버 전략 설정"""

    short_window: int = Field(default=10, ge=2, le=50, description="단기 이동평균 기간")
    long_window: int = Field(default=30, ge=10, le=200, description="장기 이동평균 기간")
    min_crossover_strength: float = Field(
        default=0.01, ge=0.0, le=1.0, description="최소 교차 강도"
    )

    @field_validator("long_window")
    @classmethod
    def validate_windows(cls, v, info):
        """장기 이평이 단기 이평보다 커야 함"""
        if "short_window" in info.data and v <= info.data["short_window"]:
            raise ValueError(
                f"long_window({v})는 short_window({info.data['short_window']})보다 커야 합니다"
            )
        return v


class RSIMeanReversionConfig(StrategyConfigBase):
    """RSI 평균회귀 전략 설정"""

    rsi_period: int = Field(default=14, ge=2, le=50, description="RSI 계산 기간")
    oversold_threshold: float = Field(
        default=30.0, ge=0.0, le=50.0, description="과매도 임계값"
    )
    overbought_threshold: float = Field(
        default=70.0, ge=50.0, le=100.0, description="과매수 임계값"
    )
    confirmation_periods: int = Field(default=2, ge=1, le=10, description="신호 확인 기간")

    @field_validator("overbought_threshold")
    @classmethod
    def validate_thresholds(cls, v, info):
        """과매수 임계값이 과매도 임계값보다 커야 함"""
        if "oversold_threshold" in info.data and v <= info.data["oversold_threshold"]:
            raise ValueError(
                f"overbought_threshold({v})는 oversold_threshold({info.data['oversold_threshold']})보다 커야 합니다"
            )
        return v


class MomentumConfig(StrategyConfigBase):
    """모멘텀 전략 설정"""

    momentum_period: int = Field(default=20, ge=5, le=100, description="모멘텀 계산 기간")
    buy_threshold: float = Field(default=0.02, description="매수 신호 임계값")
    sell_threshold: float = Field(default=-0.02, description="매도 신호 임계값")
    volume_filter: bool = Field(default=True, description="거래량 필터 사용 여부")
    min_volume_ratio: float = Field(default=1.5, description="최소 거래량 비율")

    # 상위 N개 종목 선택 (REFACTORING_PHASE1.md 문서 기준)
    top_n_stocks: int = Field(default=5, ge=1, le=20, description="상위 N개 종목 선택")
    rebalance_frequency: str = Field(default="monthly", description="리밸런싱 주기")

    @field_validator("rebalance_frequency")
    @classmethod
    def validate_frequency(cls, v):
        """리밸런싱 주기 검증"""
        allowed = ["daily", "weekly", "monthly", "quarterly"]
        if v not in allowed:
            raise ValueError(f"rebalance_frequency는 {allowed} 중 하나여야 합니다")
        return v


class BuyAndHoldConfig(StrategyConfigBase):
    """바이앤홀드 전략 설정"""

    allocation: dict[str, float] = Field(default_factory=dict, description="종목별 할당 비율")

    @field_validator("allocation")
    @classmethod
    def validate_allocation(cls, v):
        """할당 비율 검증"""
        if not v:
            return v

        total = sum(v.values())
        if not (0.99 <= total <= 1.01):  # 부동소수점 오차 허용
            raise ValueError(f"총 할당 비율은 1.0이어야 합니다 (현재: {total})")

        for symbol, ratio in v.items():
            if ratio < 0 or ratio > 1:
                raise ValueError(f"{symbol}의 할당 비율은 0과 1 사이여야 합니다 (현재: {ratio})")

        return v
