"""Buy & Hold 벤치마크 전략

단순 매수 후 보유 전략으로 다른 활성 전략들의 성과 비교 기준점 제공
- 시작 시점에 매수 신호 한 번 생성
- 종료 시점까지 보유 (매도 신호 없음)
- 또는 설정된 보유 기간 후 매도
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

        # DCA 관련 상태
        self._dca_count = 0
        self._last_dca_date: datetime | None = None
        self._dca_prices: list[float] = []

        # 리밸런싱 관련
        self._last_rebalance_date: datetime | None = None

        # 성과 추적
        self._total_invested = 0.0
        self._position_size = 0.0

    def initialize(self, data: pd.DataFrame) -> None:
        """전략 초기화"""
        self._initial_buy_made = False
        self._buy_date = None
        self._buy_price = None
        self._current_position = SignalType.HOLD

        self._dca_count = 0
        self._last_dca_date = None
        self._dca_prices = []

        self._last_rebalance_date = None

        self._total_invested = 0.0
        self._position_size = 0.0

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """기술적 지표 계산 (Buy & Hold는 단순함)"""
        df = data.copy()

        # 단순한 가격 변화율만 계산
        df["price_change"] = df["close"].pct_change()
        df["cumulative_return"] = (1 + df["price_change"]).cumprod() - 1

        # 보유 기간 확인
        if self._buy_date is not None:
            if isinstance(data.index, pd.DatetimeIndex):
                df["days_held"] = (data.index - self._buy_date).days
            else:
                df["days_held"] = 0
        else:
            df["days_held"] = 0

        # 매도 시점 확인
        df["should_sell"] = False
        if self.config.hold_period_days is not None:
            df["should_sell"] = df["days_held"] >= self.config.hold_period_days

        # DCA 시점 확인
        df["dca_signal"] = False
        if self.config.enable_dca and self._dca_count < self.config.dca_periods:
            if self._last_dca_date is None:
                df["dca_signal"].iloc[0] = True  # 첫 번째 DCA
            elif isinstance(data.index, pd.DatetimeIndex):
                days_since_dca = (data.index - self._last_dca_date).days
                df["dca_signal"] = days_since_dca >= self.config.dca_frequency_days

        # 리밸런싱 시점 확인
        df["rebalance_signal"] = False
        if self.config.enable_rebalancing:
            if self._last_rebalance_date is None:
                df["rebalance_signal"].iloc[0] = True  # 첫 번째 리밸런싱
            elif isinstance(data.index, pd.DatetimeIndex):
                days_since_rebalance = (data.index - self._last_rebalance_date).days
                df["rebalance_signal"] = (
                    days_since_rebalance >= self.config.rebalancing_frequency_days
                )

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
            signal_strength = 1.0  # Buy & Hold는 확신이 강함
            metadata = {}

            # 첫 번째 매수 신호 (DCA가 아닌 경우)
            if not self._initial_buy_made and not self.config.enable_dca:
                signal_type = SignalType.BUY
                metadata = {
                    "signal_reason": "initial_buy",
                    "strategy_type": "buy_and_hold",
                }

                self._initial_buy_made = True
                self._buy_date = current_date
                self._buy_price = row["close"]
                self._current_position = SignalType.BUY
                self._total_invested = row["close"]
                self._position_size = 1.0

            # DCA 매수 신호
            elif (
                self.config.enable_dca
                and row["dca_signal"]
                and self._dca_count < self.config.dca_periods
            ):
                signal_type = SignalType.BUY
                signal_strength = 1.0 / self.config.dca_periods  # 분할 매수 비중
                metadata = {
                    "signal_reason": "dca_buy",
                    "dca_count": self._dca_count + 1,
                    "total_dca_periods": self.config.dca_periods,
                    "strategy_type": "buy_and_hold_dca",
                }

                if not self._initial_buy_made:
                    self._initial_buy_made = True
                    self._buy_date = current_date
                    self._buy_price = row["close"]
                    self._current_position = SignalType.BUY

                self._dca_count += 1
                self._last_dca_date = current_date
                self._dca_prices.append(row["close"])

                # 평균 매수가 업데이트
                self._total_invested += row["close"] * signal_strength
                self._position_size += signal_strength

                if self._position_size > 0:
                    self._buy_price = self._total_invested / self._position_size

            # 리밸런싱 신호
            elif (
                self.config.enable_rebalancing
                and row["rebalance_signal"]
                and self._current_position == SignalType.BUY
            ):
                # 리밸런싱은 매도 후 재매수로 구현
                signal_type = SignalType.SELL
                signal_strength = 0.5  # 리밸런싱 신호 강도는 중간
                metadata = {
                    "signal_reason": "rebalancing_sell",
                    "days_held": row.get("days_held", 0),
                    "strategy_type": "buy_and_hold_rebalance",
                }

                if self._buy_price:
                    price_change = (row["close"] - self._buy_price) / self._buy_price
                    metadata["price_change"] = price_change

                self._last_rebalance_date = current_date
                # 리밸런싱 매도 후에는 다음 주기에 재매수 예정

            # 보유 기간 만료로 인한 매도
            elif (
                self.config.hold_period_days is not None
                and row["should_sell"]
                and self._current_position == SignalType.BUY
            ):
                signal_type = SignalType.SELL
                signal_strength = 1.0
                metadata = {
                    "signal_reason": "hold_period_expired",
                    "days_held": row.get("days_held", 0),
                    "planned_hold_days": self.config.hold_period_days,
                    "strategy_type": "buy_and_hold",
                }

                if self._buy_price:
                    price_change = (row["close"] - self._buy_price) / self._buy_price
                    metadata["price_change"] = price_change
                    metadata["total_return"] = price_change

                self._current_position = SignalType.HOLD

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
                    "days_held": row.get("days_held", 0),
                    "strategy_type": "buy_and_hold",
                }

                if self._buy_price:
                    price_change = (row["close"] - self._buy_price) / self._buy_price
                    metadata["price_change"] = price_change
                    metadata["total_return"] = price_change

                    if self.config.enable_dca and self._dca_prices:
                        avg_buy_price = sum(self._dca_prices) / len(self._dca_prices)
                        dca_return = (row["close"] - avg_buy_price) / avg_buy_price
                        metadata["dca_return"] = dca_return
                        metadata["dca_buy_prices"] = self._dca_prices

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

    def get_indicator_values(self) -> dict[str, float]:
        """현재 지표 값 반환"""
        result = {
            "initial_buy_made": float(self._initial_buy_made),
            "total_invested": self._total_invested,
            "position_size": self._position_size,
        }

        if self._buy_price:
            result["average_buy_price"] = self._buy_price

        if self.config.enable_dca:
            result["dca_count"] = float(self._dca_count)
            result["dca_remaining"] = float(self.config.dca_periods - self._dca_count)

        if self._buy_date:
            days_held = (datetime.now() - self._buy_date).days
            result["days_held"] = float(days_held)

        return result

    def to_dict(self) -> dict[str, Any]:
        """전략을 딕셔너리로 변환"""
        base_dict = super().to_dict()
        base_dict.update(
            {
                "strategy_type": "Buy_And_Hold",
                "hold_period_days": self.config.hold_period_days,
                "enable_dca": self.config.enable_dca,
                "enable_rebalancing": self.config.enable_rebalancing,
                "auto_sell_at_end": self.config.auto_sell_at_end,
                "current_position": self._current_position.value,
                "buy_date": self._buy_date.isoformat() if self._buy_date else None,
                "buy_price": self._buy_price,
                "dca_count": self._dca_count,
                "dca_prices": self._dca_prices,
                "total_invested": self._total_invested,
                "indicator_values": self.get_indicator_values(),
            }
        )
        return base_dict


def create_buy_and_hold_strategy(
    name: str = "Buy & Hold",
    hold_period_days: int | None = None,
    auto_sell_at_end: bool = True,
    enable_dca: bool = False,
    dca_frequency_days: int = 7,
    dca_periods: int = 4,
    enable_rebalancing: bool = False,
    rebalancing_frequency_days: int = 30,
    **kwargs: Any,
) -> BuyAndHoldStrategy:
    """Buy & Hold 전략 생성 헬퍼 함수

    Args:
        name: 전략 이름
        hold_period_days: 보유 기간 (일, None이면 무제한)
        auto_sell_at_end: 데이터 종료시 자동 매도
        enable_dca: 분할 매수 활성화
        dca_frequency_days: 분할 매수 주기
        dca_periods: 분할 매수 횟수
        enable_rebalancing: 리밸런싱 활성화
        rebalancing_frequency_days: 리밸런싱 주기
        **kwargs: 추가 설정

    Returns:
        BuyAndHoldStrategy 인스턴스
    """
    config = BuyAndHoldConfig(
        name=name,
        hold_period_days=hold_period_days,
        auto_sell_at_end=auto_sell_at_end,
        enable_dca=enable_dca,
        dca_frequency_days=dca_frequency_days,
        dca_periods=dca_periods,
        enable_rebalancing=enable_rebalancing,
        rebalancing_frequency_days=rebalancing_frequency_days,
        **kwargs,
    )

    return BuyAndHoldStrategy(config)


if __name__ == "__main__":
    # 사용 예시
    import numpy as np

    # 테스트 데이터 생성 (장기 상승 추세)
    dates = pd.date_range("2023-01-01", periods=365, freq="D")
    np.random.seed(42)

    # 장기적으로 상승하는 가격 데이터
    prices = []
    price = 100
    daily_returns = np.random.normal(0.0005, 0.02, 365)  # 연 12% 상승, 20% 변동성

    for daily_return in daily_returns:
        price *= 1 + daily_return
        prices.append(price)

    volumes = np.random.randint(1000, 5000, 365)

    test_data = pd.DataFrame(
        {
            "date": dates,
            "open": prices,
            "high": [p * 1.01 for p in prices],
            "low": [p * 0.99 for p in prices],
            "close": prices,
            "volume": volumes,
            "symbol": "TEST",
        }
    ).set_index("date")

    print("=== 기본 Buy & Hold 전략 ===")
    strategy1 = create_buy_and_hold_strategy(
        name="기본 Buy & Hold",
        hold_period_days=None,  # 무제한 보유
        auto_sell_at_end=True,
    )

    signals1 = strategy1.run(test_data)
    print(f"전략: {strategy1}")
    print(f"생성된 신호 수: {len(signals1)}")
    print(f"현재 포지션: {strategy1.get_current_position()}")

    if len(signals1) >= 2:
        buy_signal = next(s for s in signals1 if s.signal_type == SignalType.BUY)
        sell_signal = next(s for s in signals1 if s.signal_type == SignalType.SELL)
        total_return = (sell_signal.price - buy_signal.price) / buy_signal.price * 100
        days_held = (sell_signal.timestamp - buy_signal.timestamp).days
        print(f"총 수익률: {total_return:.2f}% ({days_held}일 보유)")

    print("\\n=== DCA Buy & Hold 전략 ===")
    strategy2 = create_buy_and_hold_strategy(
        name="DCA Buy & Hold",
        enable_dca=True,
        dca_frequency_days=30,  # 월별 분할 매수
        dca_periods=12,  # 12개월
        auto_sell_at_end=True,
    )

    signals2 = strategy2.run(test_data)
    print(f"전략: {strategy2}")
    print(f"생성된 신호 수: {len(signals2)}")
    print(f"지표 값: {strategy2.get_indicator_values()}")

    # DCA 신호들 출력
    buy_signals = [s for s in signals2 if s.signal_type == SignalType.BUY]
    sell_signals = [s for s in signals2 if s.signal_type == SignalType.SELL]

    print(f"DCA 매수 신호: {len(buy_signals)}개")
    for i, signal in enumerate(buy_signals[:5], 1):
        print(f"  {i}차 매수: {signal.price:.2f} (강도: {signal.strength:.2f})")

    if sell_signals:
        sell_signal = sell_signals[0]
        if "dca_return" in sell_signal.metadata:
            print(f"DCA 총 수익률: {sell_signal.metadata['dca_return']*100:.2f}%")

    print("\\n=== 제한된 보유 기간 전략 ===")
    strategy3 = create_buy_and_hold_strategy(
        name="90일 Hold", hold_period_days=90, auto_sell_at_end=False
    )

    signals3 = strategy3.run(test_data)
    print(f"전략: {strategy3}")
    print(f"생성된 신호 수: {len(signals3)}")

    if len(signals3) >= 2:
        buy_signal = signals3[0]
        sell_signal = signals3[1]
        period_return = (sell_signal.price - buy_signal.price) / buy_signal.price * 100
        print(f"90일 수익률: {period_return:.2f}%")
