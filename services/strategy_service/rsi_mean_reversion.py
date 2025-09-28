"""RSI Mean Reversion 전략

RSI 지표를 이용한 평균회귀 전략
- RSI가 과매도 구간(30 이하)에서 상승 시 매수 신호
- RSI가 과매수 구간(70 이상)에서 하락 시 매도 신호
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


class RSIConfig(StrategyConfig):
    """RSI Mean Reversion 전략 설정"""

    # RSI 파라미터
    rsi_period: int = Field(default=14, description="RSI 계산 기간")
    oversold_threshold: float = Field(default=30.0, description="과매도 임계값")
    overbought_threshold: float = Field(default=70.0, description="과매수 임계값")

    # 추가 필터
    use_sma_filter: bool = Field(default=True, description="SMA 필터 사용 여부")
    sma_period: int = Field(default=50, description="SMA 필터 기간")

    # 신호 강도 설정
    min_signal_strength: float = Field(default=0.5, description="최소 신호 강도")

    def model_post_init(self, __context: Any) -> None:
        """초기화 후 검증"""
        if self.oversold_threshold >= self.overbought_threshold:
            raise ValueError("과매도 임계값은 과매수 임계값보다 작아야 합니다")

        if not (0 <= self.oversold_threshold <= 100):
            raise ValueError("과매도 임계값은 0-100 사이여야 합니다")

        if not (0 <= self.overbought_threshold <= 100):
            raise ValueError("과매수 임계값은 0-100 사이여야 합니다")

        # min_data_points를 RSI 기간에 맞춰 설정
        min_required = max(
            self.rsi_period * 2, self.sma_period if self.use_sma_filter else 0
        )
        if self.min_data_points < min_required + 10:
            self.min_data_points = min_required + 10


class RSIMeanReversionStrategy(BaseStrategy):
    """RSI Mean Reversion 전략"""

    def __init__(self, config: RSIConfig):
        super().__init__(config)
        self.config: RSIConfig = config

        # 전략별 상태
        self._current_position = SignalType.HOLD
        self._last_rsi_signal_date: datetime | None = None

        # 기술적 지표 저장
        self._rsi: pd.Series | None = None
        self._sma: pd.Series | None = None

        # RSI 상태 추적
        self._in_oversold = False
        self._in_overbought = False

    def initialize(self, data: pd.DataFrame) -> None:
        """전략 초기화"""
        self._current_position = SignalType.HOLD
        self._last_rsi_signal_date = None
        self._rsi = None
        self._sma = None
        self._in_oversold = False
        self._in_overbought = False

        # 초기 지표 계산
        close_prices = data["close"]
        self._rsi = TechnicalIndicators.rsi(close_prices, self.config.rsi_period)
        if self.config.use_sma_filter:
            self._sma = TechnicalIndicators.sma(close_prices, self.config.sma_period)

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """기술적 지표 계산"""
        df = data.copy()

        # RSI 계산
        df["rsi"] = TechnicalIndicators.rsi(df["close"], self.config.rsi_period)

        # SMA 필터 (선택적)
        if self.config.use_sma_filter:
            df["sma"] = TechnicalIndicators.sma(df["close"], self.config.sma_period)
            df["price_above_sma"] = df["close"] > df["sma"]
        else:
            df["price_above_sma"] = True  # 필터 비활성화 시 항상 True

        # RSI 상태 확인
        df["rsi_oversold"] = df["rsi"] <= self.config.oversold_threshold
        df["rsi_overbought"] = df["rsi"] >= self.config.overbought_threshold
        df["rsi_neutral"] = (df["rsi"] > self.config.oversold_threshold) & (
            df["rsi"] < self.config.overbought_threshold
        )

        # RSI 이전 값
        df["rsi_prev"] = df["rsi"].shift(1)

        # RSI 변화량
        df["rsi_change"] = df["rsi"] - df["rsi_prev"]

        # 과매도에서 상승 (매수 신호)
        df["rsi_oversold_rising"] = (
            (df["rsi_prev"] <= self.config.oversold_threshold)
            & (df["rsi"] > df["rsi_prev"])
            & (df["rsi_change"] > 0)
        )

        # 과매수에서 하락 (매도 신호)
        df["rsi_overbought_falling"] = (
            (df["rsi_prev"] >= self.config.overbought_threshold)
            & (df["rsi"] < df["rsi_prev"])
            & (df["rsi_change"] < 0)
        )

        # 신호 강도 계산
        # 과매도/과매수 영역에서 얼마나 멀리 있는지에 따라 강도 결정
        df["signal_strength"] = 0.0

        # 매수 신호 강도 (RSI가 낮을수록 강함)
        buy_condition = df["rsi_oversold_rising"]
        df.loc[buy_condition, "signal_strength"] = (
            (self.config.oversold_threshold - df.loc[buy_condition, "rsi_prev"])
            / self.config.oversold_threshold
        ).clip(0, 1)

        # 매도 신호 강도 (RSI가 높을수록 강함)
        sell_condition = df["rsi_overbought_falling"]
        df.loc[sell_condition, "signal_strength"] = (
            (df.loc[sell_condition, "rsi_prev"] - self.config.overbought_threshold)
            / (100 - self.config.overbought_threshold)
        ).clip(0, 1)

        return df

    def generate_signals(self, data: pd.DataFrame) -> list[StrategySignal]:
        """신호 생성"""
        signals = []

        # 최소 데이터 요구사항 확인
        start_idx = max(
            self.config.rsi_period * 2,
            self.config.sma_period if self.config.use_sma_filter else 0,
            len(data) - self.config.lookback_period,
        )

        for idx in range(start_idx, len(data)):
            row = data.iloc[idx]

            # NaN 값 확인
            if pd.isna(row["rsi"]) or pd.isna(row["rsi_prev"]):
                continue

            signal_type = SignalType.HOLD
            signal_strength = 0.0
            metadata = {}

            # 매수 신호: 과매도에서 RSI 상승 + SMA 필터
            if (
                row["rsi_oversold_rising"]
                and row["price_above_sma"]
                and row["signal_strength"] >= self.config.min_signal_strength
            ):
                signal_type = SignalType.BUY
                signal_strength = row["signal_strength"]
                metadata = {
                    "signal_reason": "rsi_oversold_rising",
                    "rsi_current": row["rsi"],
                    "rsi_previous": row["rsi_prev"],
                    "rsi_change": row["rsi_change"],
                    "price_above_sma": row["price_above_sma"],
                }
                self._current_position = SignalType.BUY
                if isinstance(data.index, pd.DatetimeIndex):
                    self._last_rsi_signal_date = data.index[idx]

            # 매도 신호: 과매수에서 RSI 하락
            elif (
                row["rsi_overbought_falling"]
                and row["signal_strength"] >= self.config.min_signal_strength
            ):
                signal_type = SignalType.SELL
                signal_strength = row["signal_strength"]
                metadata = {
                    "signal_reason": "rsi_overbought_falling",
                    "rsi_current": row["rsi"],
                    "rsi_previous": row["rsi_prev"],
                    "rsi_change": row["rsi_change"],
                    "price_above_sma": row["price_above_sma"],
                }
                self._current_position = SignalType.SELL
                if isinstance(data.index, pd.DatetimeIndex):
                    self._last_rsi_signal_date = data.index[idx]

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
        if self._rsi is None:
            return {}

        result = {
            "rsi": (
                float(self._rsi.iloc[-1]) if not pd.isna(self._rsi.iloc[-1]) else 0.0
            ),
            "oversold_threshold": self.config.oversold_threshold,
            "overbought_threshold": self.config.overbought_threshold,
        }

        if self._sma is not None:
            result["sma"] = (
                float(self._sma.iloc[-1]) if not pd.isna(self._sma.iloc[-1]) else 0.0
            )

        return result

    def to_dict(self) -> dict[str, Any]:
        """전략을 딕셔너리로 변환"""
        base_dict = super().to_dict()
        base_dict.update(
            {
                "strategy_type": "RSI_Mean_Reversion",
                "rsi_period": self.config.rsi_period,
                "oversold_threshold": self.config.oversold_threshold,
                "overbought_threshold": self.config.overbought_threshold,
                "use_sma_filter": self.config.use_sma_filter,
                "current_position": self._current_position.value,
                "last_rsi_signal_date": (
                    self._last_rsi_signal_date.isoformat()
                    if self._last_rsi_signal_date
                    else None
                ),
                "indicator_values": self.get_indicator_values(),
            }
        )
        return base_dict


def create_rsi_strategy(
    name: str = "RSI Mean Reversion",
    rsi_period: int = 14,
    oversold_threshold: float = 30.0,
    overbought_threshold: float = 70.0,
    use_sma_filter: bool = True,
    sma_period: int = 50,
    min_signal_strength: float = 0.5,
    **kwargs: Any,
) -> RSIMeanReversionStrategy:
    """RSI Mean Reversion 전략 생성 헬퍼 함수

    Args:
        name: 전략 이름
        rsi_period: RSI 계산 기간
        oversold_threshold: 과매도 임계값
        overbought_threshold: 과매수 임계값
        use_sma_filter: SMA 필터 사용 여부
        sma_period: SMA 기간
        min_signal_strength: 최소 신호 강도
        **kwargs: 추가 설정

    Returns:
        RSIMeanReversionStrategy 인스턴스
    """
    config = RSIConfig(
        name=name,
        rsi_period=rsi_period,
        oversold_threshold=oversold_threshold,
        overbought_threshold=overbought_threshold,
        use_sma_filter=use_sma_filter,
        sma_period=sma_period,
        min_signal_strength=min_signal_strength,
        **kwargs,
    )

    return RSIMeanReversionStrategy(config)


if __name__ == "__main__":
    # 사용 예시
    import numpy as np

    # 테스트 데이터 생성 (변동성이 큰 데이터)
    dates = pd.date_range("2023-01-01", periods=200, freq="D")
    np.random.seed(42)

    # 평균회귀 특성을 가진 가격 데이터 생성
    prices = []
    price = 100
    for _i in range(200):
        # 평균으로의 회귀 + 랜덤 노이즈
        mean_reversion = (100 - price) * 0.02
        random_change = np.random.randn() * 2
        price += mean_reversion + random_change
        prices.append(max(price, 50))  # 최소값 제한

    test_data = pd.DataFrame(
        {
            "date": dates,
            "open": prices,
            "high": [p * 1.02 for p in prices],
            "low": [p * 0.98 for p in prices],
            "close": prices,
            "volume": np.random.randint(1000, 10000, 200),
            "symbol": "TEST",
        }
    ).set_index("date")

    # 전략 생성 및 실행
    strategy = create_rsi_strategy(
        name="테스트 RSI 전략",
        rsi_period=14,
        oversold_threshold=25,
        overbought_threshold=75,
        use_sma_filter=False,  # 테스트에서는 필터 비활성화
    )

    # 전략 실행
    signals = strategy.run(test_data)

    print(f"전략: {strategy}")
    print(f"생성된 신호 수: {len(signals)}")
    print(f"현재 포지션: {strategy.get_current_position()}")
    print(f"지표 값: {strategy.get_indicator_values()}")

    # 신호 타입별 개수
    buy_signals = sum(1 for s in signals if s.signal_type == SignalType.BUY)
    sell_signals = sum(1 for s in signals if s.signal_type == SignalType.SELL)
    print(f"매수 신호: {buy_signals}, 매도 신호: {sell_signals}")

    # 최근 신호 출력
    for signal in signals[-5:]:
        print(
            f"신호: {signal.signal_type.value} at {signal.price:.2f} (강도: {signal.strength:.2f})"
        )
