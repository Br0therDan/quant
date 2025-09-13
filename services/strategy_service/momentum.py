"""Momentum 전략

가격 모멘텀과 거래량을 기반으로 한 추세 추종 전략
- 가격 상승률과 거래량 증가를 확인하여 매수 신호
- 모멘텀 약화나 반전 시 매도 신호
- 동적 임계값 설정으로 시장 상황에 적응
"""

from datetime import datetime
from typing import Any, Optional

import numpy as np
import pandas as pd
from pydantic import Field

from .base_strategy import (
    BaseStrategy,
    SignalType,
    StrategyConfig,
    StrategySignal,
    TechnicalIndicators,
)


class MomentumConfig(StrategyConfig):
    """Momentum 전략 설정"""

    # 모멘텀 계산 파라미터
    momentum_period: int = Field(default=10, description="모멘텀 계산 기간")
    price_change_threshold: float = Field(default=0.02, description="가격 변화 임계값 (2%)")
    volume_multiplier: float = Field(default=1.5, description="평균 거래량 대비 배수")

    # 추세 필터
    use_trend_filter: bool = Field(default=True, description="추세 필터 사용 여부")
    trend_sma_period: int = Field(default=20, description="추세 확인용 SMA 기간")

    # 동적 임계값 설정
    use_dynamic_threshold: bool = Field(default=True, description="동적 임계값 사용 여부")
    volatility_period: int = Field(default=20, description="변동성 계산 기간")
    volatility_multiplier: float = Field(default=2.0, description="변동성 기반 임계값 배수")

    # 모멘텀 강도 설정
    min_momentum_strength: float = Field(default=0.3, description="최소 모멘텀 강도")
    max_position_hold_days: int = Field(default=10, description="최대 포지션 보유 기간")

    # 스탑로스/익절
    stop_loss_pct: float = Field(default=0.05, description="스탑로스 비율 (5%)")
    take_profit_pct: float = Field(default=0.10, description="익절 비율 (10%)")

    def model_post_init(self, __context: Any) -> None:
        """초기화 후 검증"""
        if self.price_change_threshold <= 0:
            raise ValueError("가격 변화 임계값은 0보다 커야 합니다")

        if self.volume_multiplier <= 1.0:
            raise ValueError("거래량 배수는 1.0보다 커야 합니다")

        if self.stop_loss_pct <= 0 or self.take_profit_pct <= 0:
            raise ValueError("스탑로스와 익절 비율은 0보다 커야 합니다")

        # min_data_points 계산
        min_required = max(
            self.momentum_period * 2,
            self.trend_sma_period if self.use_trend_filter else 0,
            self.volatility_period if self.use_dynamic_threshold else 0,
        )
        if self.min_data_points < min_required + 15:
            self.min_data_points = min_required + 15


class MomentumStrategy(BaseStrategy):
    """Momentum 전략"""

    def __init__(self, config: MomentumConfig):
        super().__init__(config)
        self.config: MomentumConfig = config

        # 전략별 상태
        self._current_position = SignalType.HOLD
        self._entry_price: Optional[float] = None
        self._entry_date: Optional[datetime] = None
        self._position_days = 0

        # 기술적 지표 저장
        self._momentum: pd.Series | None = None
        self._volume_sma: pd.Series | None = None
        self._trend_sma: pd.Series | None = None
        self._volatility: pd.Series | None = None

        # 동적 임계값
        self._dynamic_threshold: float = 0.0

    def initialize(self, data: pd.DataFrame) -> None:
        """전략 초기화"""
        self._current_position = SignalType.HOLD
        self._entry_price = None
        self._entry_date = None
        self._position_days = 0

        # 초기 지표 계산
        close_prices = data["close"]
        volume = data["volume"]

        # 모멘텀 계산 (가격 변화율)
        self._momentum = close_prices.pct_change(periods=self.config.momentum_period)

        # 거래량 이동평균
        self._volume_sma = TechnicalIndicators.sma(volume, self.config.momentum_period)

        # 추세 필터용 SMA
        if self.config.use_trend_filter:
            self._trend_sma = TechnicalIndicators.sma(
                close_prices, self.config.trend_sma_period
            )

        # 변동성 계산 (동적 임계값용)
        if self.config.use_dynamic_threshold:
            returns = close_prices.pct_change()
            self._volatility = returns.rolling(
                window=self.config.volatility_period
            ).std() * np.sqrt(
                252
            )  # 연환산 변동성

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """기술적 지표 계산"""
        df = data.copy()

        # 기본 가격 변화율
        df["price_change"] = df["close"].pct_change()
        df["price_change_n"] = df["close"].pct_change(
            periods=self.config.momentum_period
        )

        # 모멘텀 계산
        df["momentum"] = df["price_change_n"]

        # 거래량 분석
        df["volume_sma"] = TechnicalIndicators.sma(
            df["volume"], self.config.momentum_period
        )
        df["volume_ratio"] = df["volume"] / df["volume_sma"]
        df["high_volume"] = df["volume_ratio"] >= self.config.volume_multiplier

        # 추세 필터
        if self.config.use_trend_filter:
            df["trend_sma"] = TechnicalIndicators.sma(
                df["close"], self.config.trend_sma_period
            )
            df["above_trend"] = df["close"] > df["trend_sma"]
            df["trend_rising"] = df["trend_sma"] > df["trend_sma"].shift(1)
        else:
            df["above_trend"] = True
            df["trend_rising"] = True

        # 변동성 기반 동적 임계값
        if self.config.use_dynamic_threshold:
            returns = df["close"].pct_change()
            df["volatility"] = returns.rolling(
                window=self.config.volatility_period
            ).std() * np.sqrt(252)

            df["dynamic_threshold"] = (
                df["volatility"] * self.config.volatility_multiplier / 100
            ).fillna(self.config.price_change_threshold)
        else:
            df["dynamic_threshold"] = self.config.price_change_threshold

        # 모멘텀 신호 조건
        df["strong_momentum"] = df["momentum"] > df["dynamic_threshold"]
        df["weak_momentum"] = df["momentum"] < -df["dynamic_threshold"] / 2

        # 종합 매수 조건
        df["momentum_buy_signal"] = (
            df["strong_momentum"]
            & df["high_volume"]
            & df["above_trend"]
            & df["trend_rising"]
        )

        # 종합 매도 조건
        df["momentum_sell_signal"] = (
            df["weak_momentum"] | (~df["above_trend"]) | (~df["trend_rising"])
        )

        # 신호 강도 계산
        df["signal_strength"] = 0.0

        # 매수 신호 강도
        buy_condition = df["momentum_buy_signal"]
        if buy_condition.any():
            # 모멘텀, 거래량, 추세 요소를 종합
            momentum_strength = (df["momentum"] / df["dynamic_threshold"]).clip(
                0, 2
            ) / 2
            volume_strength = (df["volume_ratio"] / self.config.volume_multiplier).clip(
                0, 2
            ) / 2

            df.loc[buy_condition, "signal_strength"] = (
                ((momentum_strength + volume_strength) / 2)
                .loc[buy_condition]
                .clip(0, 1)
            )

        # 매도 신호 강도
        sell_condition = df["momentum_sell_signal"]
        if sell_condition.any():
            # 모멘텀 약화 정도에 따라 강도 결정
            momentum_weakness = (-df["momentum"] / df["dynamic_threshold"]).clip(
                0, 2
            ) / 2

            df.loc[sell_condition, "signal_strength"] = momentum_weakness.loc[
                sell_condition
            ].clip(0, 1)

        return df

    def generate_signals(self, data: pd.DataFrame) -> list[StrategySignal]:
        """신호 생성"""
        signals = []

        # 최소 데이터 요구사항 확인
        start_idx = max(
            self.config.momentum_period * 2,
            self.config.trend_sma_period if self.config.use_trend_filter else 0,
            self.config.volatility_period if self.config.use_dynamic_threshold else 0,
            len(data) - self.config.lookback_period,
        )

        for idx in range(start_idx, len(data)):
            row = data.iloc[idx]
            current_date = datetime.now()
            if isinstance(data.index, pd.DatetimeIndex):
                current_date = data.index[idx]

            # NaN 값 확인
            if pd.isna(row["momentum"]) or pd.isna(row["signal_strength"]):
                continue

            signal_type = SignalType.HOLD
            signal_strength = 0.0
            metadata = {}

            # 포지션 보유 기간 업데이트
            if self._entry_date and self._current_position != SignalType.HOLD:
                self._position_days = (current_date - self._entry_date).days

            # 스탑로스/익절 확인 (포지션 보유 중일 때)
            if (
                self._current_position == SignalType.BUY
                and self._entry_price is not None
            ):
                price_change_from_entry = (
                    row["close"] - self._entry_price
                ) / self._entry_price

                # 스탑로스
                if price_change_from_entry <= -self.config.stop_loss_pct:
                    signal_type = SignalType.SELL
                    signal_strength = 0.8
                    metadata = {
                        "signal_reason": "stop_loss",
                        "entry_price": self._entry_price,
                        "price_change": price_change_from_entry,
                        "position_days": self._position_days,
                    }

                # 익절
                elif price_change_from_entry >= self.config.take_profit_pct:
                    signal_type = SignalType.SELL
                    signal_strength = 0.9
                    metadata = {
                        "signal_reason": "take_profit",
                        "entry_price": self._entry_price,
                        "price_change": price_change_from_entry,
                        "position_days": self._position_days,
                    }

                # 최대 보유 기간 초과
                elif self._position_days >= self.config.max_position_hold_days:
                    signal_type = SignalType.SELL
                    signal_strength = 0.6
                    metadata = {
                        "signal_reason": "max_hold_period",
                        "entry_price": self._entry_price,
                        "price_change": price_change_from_entry,
                        "position_days": self._position_days,
                    }

            # 일반적인 모멘텀 신호 확인
            if signal_type == SignalType.HOLD:
                # 매수 신호
                if (
                    row["momentum_buy_signal"]
                    and row["signal_strength"] >= self.config.min_momentum_strength
                    and self._current_position != SignalType.BUY
                ):
                    signal_type = SignalType.BUY
                    signal_strength = row["signal_strength"]
                    metadata = {
                        "signal_reason": "momentum_breakout",
                        "momentum": row["momentum"],
                        "volume_ratio": row["volume_ratio"],
                        "dynamic_threshold": row["dynamic_threshold"],
                        "above_trend": row["above_trend"],
                        "trend_rising": row["trend_rising"],
                    }

                # 매도 신호
                elif (
                    row["momentum_sell_signal"]
                    and row["signal_strength"] >= self.config.min_momentum_strength
                    and self._current_position == SignalType.BUY
                ):
                    signal_type = SignalType.SELL
                    signal_strength = row["signal_strength"]
                    metadata = {
                        "signal_reason": "momentum_weakness",
                        "momentum": row["momentum"],
                        "above_trend": row["above_trend"],
                        "trend_rising": row["trend_rising"],
                    }

                    if self._entry_price:
                        price_change = (
                            row["close"] - self._entry_price
                        ) / self._entry_price
                        metadata.update(
                            {
                                "entry_price": self._entry_price,
                                "price_change": price_change,
                                "position_days": self._position_days,
                            }
                        )

            # 신호 처리 및 상태 업데이트
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

                # 상태 업데이트
                if signal_type == SignalType.BUY:
                    self._current_position = SignalType.BUY
                    self._entry_price = row["close"]
                    self._entry_date = current_date
                    self._position_days = 0
                elif signal_type == SignalType.SELL:
                    self._current_position = SignalType.HOLD
                    self._entry_price = None
                    self._entry_date = None
                    self._position_days = 0

        return signals

    def get_current_position(self) -> SignalType:
        """현재 포지션 반환"""
        return self._current_position

    def get_indicator_values(self) -> dict[str, float]:
        """현재 지표 값 반환"""
        result = {
            "momentum_period": self.config.momentum_period,
            "price_change_threshold": self.config.price_change_threshold,
            "volume_multiplier": self.config.volume_multiplier,
            "position_days": self._position_days,
        }

        if self._momentum is not None and len(self._momentum) > 0:
            result["current_momentum"] = (
                float(self._momentum.iloc[-1])
                if not pd.isna(self._momentum.iloc[-1])
                else 0.0
            )

        if self._volume_sma is not None and len(self._volume_sma) > 0:
            result["volume_sma"] = (
                float(self._volume_sma.iloc[-1])
                if not pd.isna(self._volume_sma.iloc[-1])
                else 0.0
            )

        if self._entry_price:
            result["entry_price"] = self._entry_price

        return result

    def to_dict(self) -> dict[str, Any]:
        """전략을 딕셔너리로 변환"""
        base_dict = super().to_dict()
        base_dict.update(
            {
                "strategy_type": "Momentum",
                "momentum_period": self.config.momentum_period,
                "price_change_threshold": self.config.price_change_threshold,
                "volume_multiplier": self.config.volume_multiplier,
                "use_trend_filter": self.config.use_trend_filter,
                "use_dynamic_threshold": self.config.use_dynamic_threshold,
                "current_position": self._current_position.value,
                "entry_price": self._entry_price,
                "entry_date": (
                    self._entry_date.isoformat() if self._entry_date else None
                ),
                "position_days": self._position_days,
                "indicator_values": self.get_indicator_values(),
            }
        )
        return base_dict


def create_momentum_strategy(
    name: str = "Momentum Strategy",
    momentum_period: int = 10,
    price_change_threshold: float = 0.02,
    volume_multiplier: float = 1.5,
    use_trend_filter: bool = True,
    trend_sma_period: int = 20,
    use_dynamic_threshold: bool = True,
    min_momentum_strength: float = 0.3,
    stop_loss_pct: float = 0.05,
    take_profit_pct: float = 0.10,
    **kwargs: Any,
) -> MomentumStrategy:
    """Momentum 전략 생성 헬퍼 함수

    Args:
        name: 전략 이름
        momentum_period: 모멘텀 계산 기간
        price_change_threshold: 가격 변화 임계값
        volume_multiplier: 거래량 배수
        use_trend_filter: 추세 필터 사용 여부
        trend_sma_period: 추세 SMA 기간
        use_dynamic_threshold: 동적 임계값 사용
        min_momentum_strength: 최소 모멘텀 강도
        stop_loss_pct: 스탑로스 비율
        take_profit_pct: 익절 비율
        **kwargs: 추가 설정

    Returns:
        MomentumStrategy 인스턴스
    """
    config = MomentumConfig(
        name=name,
        momentum_period=momentum_period,
        price_change_threshold=price_change_threshold,
        volume_multiplier=volume_multiplier,
        use_trend_filter=use_trend_filter,
        trend_sma_period=trend_sma_period,
        use_dynamic_threshold=use_dynamic_threshold,
        min_momentum_strength=min_momentum_strength,
        stop_loss_pct=stop_loss_pct,
        take_profit_pct=take_profit_pct,
        **kwargs,
    )

    return MomentumStrategy(config)


if __name__ == "__main__":
    # 사용 예시
    import numpy as np

    # 테스트 데이터 생성 (추세가 있는 데이터)
    dates = pd.date_range("2023-01-01", periods=150, freq="D")
    np.random.seed(42)

    # 모멘텀이 있는 가격 데이터 생성
    prices = []
    volumes = []
    price = 100

    for i in range(150):
        # 추세 + 노이즈
        if i < 50:  # 상승 추세
            trend = 0.005
        elif i < 100:  # 횡보
            trend = 0.0
        else:  # 강한 상승
            trend = 0.01

        daily_return = trend + np.random.randn() * 0.02
        price *= 1 + daily_return
        prices.append(price)

        # 거래량 (가격 상승시 증가 경향)
        base_volume = 1000
        if daily_return > 0.01:  # 강한 상승시 거래량 증가
            volume = base_volume * (1.5 + np.random.rand())
        else:
            volume = base_volume * (0.8 + np.random.rand() * 0.4)
        volumes.append(int(volume))

    test_data = pd.DataFrame(
        {
            "date": dates,
            "open": prices,
            "high": [p * (1 + abs(np.random.randn()) * 0.01) for p in prices],
            "low": [p * (1 - abs(np.random.randn()) * 0.01) for p in prices],
            "close": prices,
            "volume": volumes,
            "symbol": "TEST",
        }
    ).set_index("date")

    # 전략 생성 및 실행
    strategy = create_momentum_strategy(
        name="테스트 모멘텀 전략",
        momentum_period=8,
        price_change_threshold=0.015,
        volume_multiplier=1.3,
        use_dynamic_threshold=True,
        min_momentum_strength=0.4,
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

    # 신호별 수익률 계산
    if len(signals) >= 2:
        trades = []
        for i in range(0, len(signals) - 1, 2):
            if (
                i + 1 < len(signals)
                and signals[i].signal_type == SignalType.BUY
                and signals[i + 1].signal_type == SignalType.SELL
            ):
                buy_price = signals[i].price
                sell_price = signals[i + 1].price
                return_pct = (sell_price - buy_price) / buy_price * 100
                trades.append(return_pct)

                print(
                    f"거래: {buy_price:.2f} -> {sell_price:.2f} "
                    f"(수익률: {return_pct:.2f}%)"
                )

        if trades:
            avg_return = sum(trades) / len(trades)
            print(f"평균 거래 수익률: {avg_return:.2f}%")

    # 최근 신호 출력
    for signal in signals[-3:]:
        reason = signal.metadata.get("signal_reason", "unknown")
        print(
            f"신호: {signal.signal_type.value} at {signal.price:.2f} "
            f"(강도: {signal.strength:.2f}, 사유: {reason})"
        )
