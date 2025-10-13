"""RSI 평균회귀 전략

RSI 지표를 사용한 평균회귀 전략
"""

from datetime import datetime

import pandas as pd

from .base_strategy import (
    BaseStrategy,
    SignalType,
    StrategySignal,
    TechnicalIndicators,
)
from .configs import RSIMeanReversionConfig


class RSIMeanReversionStrategy(BaseStrategy):
    """RSI 평균회귀 전략"""

    def __init__(self, config: RSIMeanReversionConfig):
        super().__init__(config)
        self.config: RSIMeanReversionConfig = config
        self._current_position = SignalType.HOLD

    def initialize(self, data: pd.DataFrame) -> None:
        """전략 초기화"""
        self._current_position = SignalType.HOLD

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """기술적 지표 계산"""
        df = data.copy()

        # RSI 계산
        df["rsi"] = TechnicalIndicators.rsi(df["close"], self.config.rsi_period)

        return df

    def generate_signals(self, data: pd.DataFrame) -> list[StrategySignal]:
        """신호 생성"""
        signals = []

        for idx in range(len(data)):
            row = data.iloc[idx]
            current_date = datetime.now()
            if isinstance(data.index, pd.DatetimeIndex):
                current_date = data.index[idx]

            rsi = row.get("rsi", 50)
            signal_type = SignalType.HOLD
            signal_strength = 0.5

            # 과매도 상태에서 매수 신호
            if (
                rsi < self.config.oversold_threshold
                and self._current_position != SignalType.BUY
            ):
                signal_type = SignalType.BUY
                signal_strength = (self.config.oversold_threshold - rsi) / 30.0
                self._current_position = SignalType.BUY

            # 과매수 상태에서 매도 신호
            elif (
                rsi > self.config.overbought_threshold
                and self._current_position == SignalType.BUY
            ):
                signal_type = SignalType.SELL
                signal_strength = (rsi - self.config.overbought_threshold) / 30.0
                self._current_position = SignalType.HOLD

            if signal_type != SignalType.HOLD:
                signal = StrategySignal(
                    timestamp=current_date,
                    symbol=row.get("symbol", "UNKNOWN"),
                    signal_type=signal_type,
                    strength=min(signal_strength, 1.0),
                    price=row["close"],
                    metadata={
                        "rsi": rsi,
                        "strategy_type": "rsi_mean_reversion",
                    },
                )
                signals.append(signal)

        return signals
