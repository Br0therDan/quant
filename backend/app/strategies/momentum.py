"""모멘텀 전략

가격 모멘텀을 기반으로 한 트렌드 추종 전략
"""

from datetime import datetime

import pandas as pd

from .base_strategy import (
    BaseStrategy,
    SignalType,
    StrategySignal,
)
from .configs import MomentumConfig


class MomentumStrategy(BaseStrategy):
    """모멘텀 전략"""

    def __init__(self, config: MomentumConfig):
        super().__init__(config)
        self.config: MomentumConfig = config
        self._current_position = SignalType.HOLD

    def initialize(self, data: pd.DataFrame) -> None:
        """전략 초기화"""
        self._current_position = SignalType.HOLD

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """기술적 지표 계산"""
        df = data.copy()

        # 모멘텀 계산
        df["momentum"] = df["close"].pct_change(self.config.momentum_period)

        # 거래량 이동평균
        if self.config.volume_filter:
            df["volume_ma"] = df["volume"].rolling(window=20).mean()
            df["volume_ratio"] = df["volume"] / df["volume_ma"]

        return df

    def generate_signals(self, data: pd.DataFrame) -> list[StrategySignal]:
        """신호 생성"""
        signals = []

        for idx in range(len(data)):
            row = data.iloc[idx]
            current_date = datetime.now()
            if isinstance(data.index, pd.DatetimeIndex):
                current_date = data.index[idx]

            # 모멘텀과 거래량 확인
            momentum = row.get("momentum", 0)
            volume_ok = True

            if self.config.volume_filter:
                volume_ratio = row.get("volume_ratio", 0)
                volume_ok = volume_ratio >= self.config.min_volume_ratio

            signal_type = SignalType.HOLD
            signal_strength = abs(momentum) if not pd.isna(momentum) else 0

            # 매수 신호
            if (
                momentum > self.config.buy_threshold
                and volume_ok
                and self._current_position != SignalType.BUY
            ):
                signal_type = SignalType.BUY
                self._current_position = SignalType.BUY

            # 매도 신호
            elif (
                momentum < self.config.sell_threshold
                and self._current_position == SignalType.BUY
            ):
                signal_type = SignalType.SELL
                self._current_position = SignalType.HOLD

            if signal_type != SignalType.HOLD:
                signal = StrategySignal(
                    timestamp=current_date,
                    symbol=row.get("symbol", "UNKNOWN"),
                    signal_type=signal_type,
                    strength=min(signal_strength, 1.0),
                    price=row["close"],
                    metadata={
                        "momentum": momentum,
                        "strategy_type": "momentum",
                    },
                )
                signals.append(signal)

        return signals
