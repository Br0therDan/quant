"""SMA Crossover 전략

단순 이동평균선 교차 전략 구현
- 단기 SMA가 장기 SMA를 상향 돌파 시 매수 신호
- 단기 SMA가 장기 SMA를 하향 돌파 시 매도 신호
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
    TechnicalIndicators,
)


class SMAConfig(StrategyConfig):
    """SMA Crossover 전략 설정"""

    # SMA 파라미터
    short_window: int = Field(default=20, description="단기 SMA 기간")
    long_window: int = Field(default=50, description="장기 SMA 기간")

    # 신호 강도 설정
    min_signal_strength: float = Field(default=0.6, description="최소 신호 강도")

    def model_post_init(self, __context: Any) -> None:
        """초기화 후 검증"""
        if self.short_window >= self.long_window:
            raise ValueError("단기 기간은 장기 기간보다 작아야 합니다")

        # min_data_points를 장기 기간에 맞춰 설정
        if self.min_data_points < self.long_window + 10:
            self.min_data_points = self.long_window + 10


class SMACrossoverStrategy(BaseStrategy):
    """SMA Crossover 전략"""

    def __init__(self, config: SMAConfig):
        super().__init__(config)
        self.config: SMAConfig = config

        # 전략별 상태
        self._current_position = SignalType.HOLD
        self._last_crossover_date: datetime | None = None

        # 기술적 지표 저장
        self._sma_short: pd.Series | None = None
        self._sma_long: pd.Series | None = None

    def initialize(self, data: pd.DataFrame) -> None:
        """전략 초기화"""
        self._current_position = SignalType.HOLD
        self._last_crossover_date = None
        self._sma_short = None
        self._sma_long = None

        # 초기 지표 계산
        close_prices = data["close"]
        self._sma_short = TechnicalIndicators.sma(
            close_prices, self.config.short_window
        )
        self._sma_long = TechnicalIndicators.sma(close_prices, self.config.long_window)

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """기술적 지표 계산"""
        df = data.copy()

        # SMA 계산
        df["sma_short"] = TechnicalIndicators.sma(df["close"], self.config.short_window)
        df["sma_long"] = TechnicalIndicators.sma(df["close"], self.config.long_window)

        # 교차 지점 확인
        df["sma_diff"] = df["sma_short"] - df["sma_long"]
        df["sma_diff_prev"] = df["sma_diff"].shift(1)

        # 골든 크로스 (상향 돌파)
        df["golden_cross"] = (df["sma_diff"] > 0) & (df["sma_diff_prev"] <= 0)

        # 데드 크로스 (하향 돌파)
        df["dead_cross"] = (df["sma_diff"] < 0) & (df["sma_diff_prev"] >= 0)

        # 신호 강도 계산 (차이의 크기를 정규화)
        max_diff = abs(df["sma_diff"]).rolling(window=self.config.long_window).max()
        df["signal_strength"] = abs(df["sma_diff"]) / (max_diff + 1e-8)  # 0으로 나누기 방지
        df["signal_strength"] = df["signal_strength"].fillna(0).clip(0, 1)

        return df

    def generate_signals(self, data: pd.DataFrame) -> list[StrategySignal]:
        """신호 생성"""
        signals = []

        # 최소 데이터 요구사항 확인
        start_idx = max(
            self.config.long_window, len(data) - self.config.lookback_period
        )

        for idx in range(start_idx, len(data)):
            row = data.iloc[idx]

            # NaN 값 확인
            if pd.isna(row["sma_short"]) or pd.isna(row["sma_long"]):
                continue

            signal_type = SignalType.HOLD
            signal_strength = 0.0
            metadata = {}

            # 골든 크로스 확인
            if (
                row["golden_cross"]
                and row["signal_strength"] >= self.config.min_signal_strength
            ):
                signal_type = SignalType.BUY
                signal_strength = row["signal_strength"]
                metadata = {
                    "crossover_type": "golden_cross",
                    "sma_short": row["sma_short"],
                    "sma_long": row["sma_long"],
                    "sma_diff": row["sma_diff"],
                }
                self._current_position = SignalType.BUY
                # 인덱스가 datetime인 경우에만 설정
                if isinstance(data.index, pd.DatetimeIndex):
                    self._last_crossover_date = data.index[idx]

            # 데드 크로스 확인
            elif (
                row["dead_cross"]
                and row["signal_strength"] >= self.config.min_signal_strength
            ):
                signal_type = SignalType.SELL
                signal_strength = row["signal_strength"]
                metadata = {
                    "crossover_type": "dead_cross",
                    "sma_short": row["sma_short"],
                    "sma_long": row["sma_long"],
                    "sma_diff": row["sma_diff"],
                }
                self._current_position = SignalType.SELL
                # 인덱스가 datetime인 경우에만 설정
                if isinstance(data.index, pd.DatetimeIndex):
                    self._last_crossover_date = data.index[idx]

            # 신호가 있는 경우에만 추가
            if signal_type != SignalType.HOLD:
                # timestamp 설정
                timestamp = datetime.now()
                if isinstance(data.index, pd.DatetimeIndex):
                    timestamp = data.index[idx]

                signal = StrategySignal(
                    timestamp=timestamp,
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

    def get_indicator_values(self) -> dict[str, float]:
        """현재 지표 값 반환"""
        if self._sma_short is None or self._sma_long is None:
            return {}

        return {
            "sma_short": (
                float(self._sma_short.iloc[-1])
                if not pd.isna(self._sma_short.iloc[-1])
                else 0.0
            ),
            "sma_long": (
                float(self._sma_long.iloc[-1])
                if not pd.isna(self._sma_long.iloc[-1])
                else 0.0
            ),
            "sma_diff": (
                float(self._sma_short.iloc[-1] - self._sma_long.iloc[-1])
                if not pd.isna(self._sma_short.iloc[-1])
                and not pd.isna(self._sma_long.iloc[-1])
                else 0.0
            ),
        }

    def to_dict(self) -> dict[str, Any]:
        """전략을 딕셔너리로 변환"""
        base_dict = super().to_dict()
        base_dict.update(
            {
                "strategy_type": "SMA_Crossover",
                "short_window": self.config.short_window,
                "long_window": self.config.long_window,
                "current_position": self._current_position.value,
                "last_crossover_date": (
                    self._last_crossover_date.isoformat()
                    if self._last_crossover_date
                    else None
                ),
                "indicator_values": self.get_indicator_values(),
            }
        )
        return base_dict


def create_sma_strategy(
    name: str = "SMA Crossover",
    short_window: int = 20,
    long_window: int = 50,
    min_signal_strength: float = 0.6,
    **kwargs: Any,
) -> SMACrossoverStrategy:
    """SMA Crossover 전략 생성 헬퍼 함수

    Args:
        name: 전략 이름
        short_window: 단기 SMA 기간
        long_window: 장기 SMA 기간
        min_signal_strength: 최소 신호 강도
        **kwargs: 추가 설정

    Returns:
        SMACrossoverStrategy 인스턴스
    """
    config = SMAConfig(
        name=name,
        short_window=short_window,
        long_window=long_window,
        min_signal_strength=min_signal_strength,
        **kwargs,
    )

    return SMACrossoverStrategy(config)


# 호환성을 위한 별칭
create_sma_crossover_strategy = create_sma_strategy


if __name__ == "__main__":
    # 사용 예시
    import numpy as np

    # 테스트 데이터 생성
    dates = pd.date_range("2023-01-01", periods=100, freq="D")
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(100) * 0.5)

    test_data = pd.DataFrame(
        {
            "date": dates,
            "open": prices * 0.99,
            "high": prices * 1.01,
            "low": prices * 0.98,
            "close": prices,
            "volume": np.random.randint(1000, 10000, 100),
            "symbol": "TEST",
        }
    ).set_index("date")

    # 전략 생성 및 실행
    strategy = create_sma_strategy(name="테스트 SMA 전략", short_window=10, long_window=20)

    # 전략 실행
    signals = strategy.run(test_data)

    print(f"전략: {strategy}")
    print(f"생성된 신호 수: {len(signals)}")
    print(f"현재 포지션: {strategy.get_current_position()}")
    print(f"지표 값: {strategy.get_indicator_values()}")

    # 신호 출력
    for signal in signals[-3:]:  # 마지막 3개 신호
        print(
            f"신호: {signal.signal_type.value} at {signal.price:.2f} (강도: {signal.strength:.2f})"
        )
