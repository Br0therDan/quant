"""SMA 크로스오버 전략

단순 이동평균선 교차를 이용한 트렌드 추종 전략
"""

from datetime import datetime

import pandas as pd

from .base_strategy import (
    BaseStrategy,
    SignalType,
    StrategySignal,
    TechnicalIndicators,
)
from .configs import SMACrossoverConfig


class SMACrossoverStrategy(BaseStrategy):
    """SMA 크로스오버 전략"""

    def __init__(self, config: SMACrossoverConfig):
        super().__init__(config)
        self.config: SMACrossoverConfig = config
        self._current_position = SignalType.HOLD

        # 설정은 이미 Pydantic에 의해 검증됨

    def initialize(self, data: pd.DataFrame) -> None:
        """전략 초기화"""
        self._current_position = SignalType.HOLD

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """기술적 지표 계산"""
        df = data.copy()

        # 이동평균 계산
        df["sma_short"] = TechnicalIndicators.sma(df["close"], self.config.short_window)
        df["sma_long"] = TechnicalIndicators.sma(df["close"], self.config.long_window)

        # 교차 신호
        df["sma_diff"] = df["sma_short"] - df["sma_long"]
        df["crossover_strength"] = df["sma_diff"] / df["sma_long"]

        return df

    def generate_signals(self, data: pd.DataFrame) -> list[StrategySignal]:
        """신호 생성"""
        signals = []
        prev_diff = 0

        for idx in range(len(data)):
            row = data.iloc[idx]
            current_date = datetime.now()
            if isinstance(data.index, pd.DatetimeIndex):
                current_date = data.index[idx]

            sma_diff = row.get("sma_diff", 0)
            crossover_strength = row.get("crossover_strength", 0)

            signal_type = SignalType.HOLD
            signal_strength = abs(crossover_strength)

            # 골든 크로스 (단기 이평이 장기 이평을 위로 돌파)
            if (
                prev_diff <= 0
                and sma_diff > 0
                and abs(crossover_strength) >= self.config.min_crossover_strength
                and self._current_position != SignalType.BUY
            ):
                signal_type = SignalType.BUY
                self._current_position = SignalType.BUY

            # 데드 크로스 (단기 이평이 장기 이평을 아래로 돌파)
            elif (
                prev_diff >= 0
                and sma_diff < 0
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
                        "sma_short": row.get("sma_short"),
                        "sma_long": row.get("sma_long"),
                        "crossover_strength": crossover_strength,
                        "strategy_type": "sma_crossover",
                    },
                )
                signals.append(signal)

            prev_diff = sma_diff

        return signals
