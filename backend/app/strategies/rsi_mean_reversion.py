"""RSI 평균회귀 전략

RSI 지표를 사용한 평균회귀 전략
"""

from datetime import datetime

import pandas as pd
from pydantic import Field

from .base_strategy import (
    BaseStrategy,
    SignalType,
    StrategyConfig,
    StrategySignal,
    TechnicalIndicators,
)


class RSIConfig(StrategyConfig):
    """RSI 전략 설정"""

    # RSI 설정
    rsi_period: int = Field(default=14, ge=2, le=50, description="RSI 계산 기간")
    oversold_threshold: float = Field(default=30.0, description="과매도 임계값")
    overbought_threshold: float = Field(default=70.0, description="과매수 임계값")

    # 확인 설정
    confirmation_periods: int = Field(default=2, description="신호 확인 기간")


class RSIMeanReversionStrategy(BaseStrategy):
    """RSI 평균회귀 전략"""

    def __init__(self, config: RSIConfig):
        super().__init__(config)
        self.config: RSIConfig = config
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
