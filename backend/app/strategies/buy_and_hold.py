"""Buy & Hold 벤치마크 전략

단순 매수 후 보유 전략으로 다른 활성 전략들의 성과 비교 기준점 제공
"""

from datetime import datetime
from typing import Any

import pandas as pd
from pydantic import Field

from .base_strategy import (
    BaseStrategy,
    SignalType,
    StrategyConfig,
    StrategySignal,
)


class BuyAndHoldConfig(StrategyConfig):
    """Buy & Hold 전략 설정"""

    # 보유 기간 설정
    hold_period_days: int | None = Field(
        default=None, description="보유 기간 (일, None이면 무제한)"
    )
    auto_sell_at_end: bool = Field(default=True, description="데이터 종료시 자동 매도 여부")

    # 리밸런싱 설정
    enable_rebalancing: bool = Field(default=False, description="정기 리밸런싱 활성화")
    rebalancing_frequency_days: int = Field(default=30, description="리밸런싱 주기 (일)")

    # 분할 매수 설정
    enable_dca: bool = Field(default=False, description="분할 매수 (DCA) 활성화")
    dca_frequency_days: int = Field(default=7, description="분할 매수 주기 (일)")
    dca_periods: int = Field(default=4, description="분할 매수 횟수")

    # 성과 추적
    track_performance: bool = Field(default=True, description="성과 추적 여부")
    benchmark_symbol: str = Field(default="SPY", description="벤치마크 심볼")

    def model_post_init(self, __context: Any) -> None:
        """초기화 후 검증"""
        if self.hold_period_days is not None and self.hold_period_days <= 0:
            raise ValueError("보유 기간은 0보다 커야 합니다")

        if self.enable_rebalancing and self.rebalancing_frequency_days <= 0:
            raise ValueError("리밸런싱 주기는 0보다 커야 합니다")

        if self.enable_dca:
            if self.dca_frequency_days <= 0:
                raise ValueError("분할 매수 주기는 0보다 커야 합니다")
            if self.dca_periods <= 0:
                raise ValueError("분할 매수 횟수는 0보다 커야 합니다")

        # Buy & Hold는 최소 데이터 요구사항이 낮음
        if self.min_data_points < 2:
            self.min_data_points = 2


class BuyAndHoldStrategy(BaseStrategy):
    """Buy & Hold 벤치마크 전략"""

    def __init__(self, config: BuyAndHoldConfig):
        super().__init__(config)
        self.config: BuyAndHoldConfig = config

        # 전략별 상태
        self._initial_buy_made = False
        self._buy_date: datetime | None = None
        self._buy_price: float | None = None
        self._current_position = SignalType.HOLD

    def initialize(self, data: pd.DataFrame) -> None:
        """전략 초기화"""
        self._initial_buy_made = False
        self._buy_date = None
        self._buy_price = None
        self._current_position = SignalType.HOLD

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """기술적 지표 계산 (Buy & Hold는 단순함)"""
        df = data.copy()

        # 단순한 가격 변화율만 계산
        df["price_change"] = df["close"].pct_change()
        df["cumulative_return"] = (1 + df["price_change"]).cumprod() - 1

        return df

    def generate_signals(self, data: pd.DataFrame) -> list[StrategySignal]:
        """신호 생성"""
        signals = []

        for idx in range(len(data)):
            row = data.iloc[idx]
            current_date = datetime.now()
            if isinstance(data.index, pd.DatetimeIndex):
                current_date = data.index[idx]

            signal_type = SignalType.HOLD
            signal_strength = 1.0
            metadata = {}

            # 첫 번째 매수 신호
            if not self._initial_buy_made:
                signal_type = SignalType.BUY
                metadata = {
                    "signal_reason": "initial_buy",
                    "strategy_type": "buy_and_hold",
                }

                self._initial_buy_made = True
                self._buy_date = current_date
                self._buy_price = row["close"]
                self._current_position = SignalType.BUY

            # 데이터 종료시 자동 매도
            elif (
                self.config.auto_sell_at_end
                and idx == len(data) - 1
                and self._current_position == SignalType.BUY
            ):
                signal_type = SignalType.SELL
                signal_strength = 1.0
                metadata = {
                    "signal_reason": "end_of_data",
                    "strategy_type": "buy_and_hold",
                }

                if self._buy_price:
                    price_change = (row["close"] - self._buy_price) / self._buy_price
                    metadata["price_change"] = price_change
                    metadata["total_return"] = price_change

                self._current_position = SignalType.HOLD

            # 신호가 있는 경우에만 추가
            if signal_type != SignalType.HOLD:
                signal = StrategySignal(
                    timestamp=current_date,
                    symbol=row.get("symbol", "UNKNOWN"),
                    signal_type=signal_type,
                    strength=signal_strength,
                    price=row["close"],
                    metadata=metadata,
                )
                signals.append(signal)

        return signals

    def get_current_position(self) -> SignalType:
        """현재 포지션 반환"""
        return self._current_position


def create_buy_and_hold_strategy(
    name: str = "Buy & Hold",
    hold_period_days: int | None = None,
    auto_sell_at_end: bool = True,
    **kwargs: Any,
) -> BuyAndHoldStrategy:
    """Buy & Hold 전략 생성 헬퍼 함수"""
    config = BuyAndHoldConfig(
        name=name,
        hold_period_days=hold_period_days,
        auto_sell_at_end=auto_sell_at_end,
        **kwargs,
    )

    return BuyAndHoldStrategy(config)
