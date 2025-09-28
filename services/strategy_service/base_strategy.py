"""전략 기본 클래스

모든 거래 전략의 기본 인터페이스를 정의합니다.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any

import pandas as pd
from pydantic import BaseModel, Field


class SignalType(str, Enum):
    """신호 타입"""

    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class StrategyConfig(BaseModel):
    """전략 설정 기본 모델"""

    model_config = {"extra": "allow"}  # 추가 필드 허용

    name: str
    description: str = ""
    parameters: dict[str, Any] = Field(default_factory=dict)

    # 공통 설정
    lookback_period: int = 252  # 기본 조회 기간 (일 단위)
    min_data_points: int = 30  # 최소 데이터 포인트 수

    # 리스크 관리
    max_position_size: float = 1.0  # 최대 포지션 크기 (0-1)
    stop_loss_pct: float | None = None  # 손절 비율 (예: 0.05 = 5%)
    take_profit_pct: float | None = None  # 익절 비율 (예: 0.1 = 10%)


class StrategySignal(BaseModel):
    """전략 신호"""

    timestamp: datetime
    symbol: str
    signal_type: SignalType
    strength: float = Field(ge=0.0, le=1.0, description="신호 강도 (0-1)")
    price: float = Field(gt=0, description="신호 생성 시점 가격")
    metadata: dict[str, Any] = Field(default_factory=dict, description="추가 정보")


class StrategyMetrics(BaseModel):
    """전략 성과 지표"""

    total_signals: int
    buy_signals: int
    sell_signals: int
    hold_signals: int

    accuracy: float | None = None  # 정확도 (실제 백테스트 후 계산)
    avg_signal_strength: float

    # 기술적 지표 관련
    indicator_values: dict[str, float] = Field(default_factory=dict)


class BaseStrategy(ABC):
    """기본 전략 클래스

    모든 전략은 이 클래스를 상속받아 구현해야 합니다.
    """

    def __init__(self, config: StrategyConfig):
        self.config = config
        self.name = config.name
        self.description = config.description
        self.parameters = config.parameters

        # 내부 상태
        self._is_initialized = False
        self._signals: list[StrategySignal] = []
        self._last_signal: StrategySignal | None = None

    @property
    def is_initialized(self) -> bool:
        """전략 초기화 상태"""
        return self._is_initialized

    @property
    def signals(self) -> list[StrategySignal]:
        """생성된 신호 목록"""
        return self._signals.copy()

    @property
    def last_signal(self) -> StrategySignal | None:
        """마지막 신호"""
        return self._last_signal

    @abstractmethod
    def initialize(self, data: pd.DataFrame) -> None:
        """전략 초기화

        Args:
            data: 주가 데이터 (OHLCV)
        """
        pass

    @abstractmethod
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """기술적 지표 계산

        Args:
            data: 주가 데이터

        Returns:
            지표가 추가된 데이터프레임
        """
        pass

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> list[StrategySignal]:
        """신호 생성

        Args:
            data: 지표가 계산된 주가 데이터

        Returns:
            생성된 신호 목록
        """
        pass

    def validate_data(self, data: pd.DataFrame) -> bool:
        """데이터 유효성 검증

        Args:
            data: 검증할 데이터

        Returns:
            데이터 유효성 여부
        """
        if data.empty:
            return False

        required_columns = ["open", "high", "low", "close", "volume"]
        if not all(col in data.columns for col in required_columns):
            return False

        if len(data) < self.config.min_data_points:
            return False

        return True

    def run(self, data: pd.DataFrame) -> list[StrategySignal]:
        """전략 실행

        Args:
            data: 주가 데이터

        Returns:
            생성된 신호 목록
        """
        if not self.validate_data(data):
            raise ValueError(
                f"데이터가 유효하지 않습니다. 최소 {self.config.min_data_points}개 데이터 포인트가 필요합니다."
            )

        # 1. 전략 초기화
        if not self._is_initialized:
            self.initialize(data)
            self._is_initialized = True

        # 2. 기술적 지표 계산
        data_with_indicators = self.calculate_indicators(data)

        # 3. 신호 생성
        signals = self.generate_signals(data_with_indicators)

        # 4. 신호 저장
        self._signals.extend(signals)
        if signals:
            self._last_signal = signals[-1]

        return signals

    def get_metrics(self) -> StrategyMetrics:
        """전략 성과 지표 계산

        Returns:
            성과 지표
        """
        if not self._signals:
            return StrategyMetrics(
                total_signals=0,
                buy_signals=0,
                sell_signals=0,
                hold_signals=0,
                avg_signal_strength=0.0,
            )

        total_signals = len(self._signals)
        buy_signals = sum(1 for s in self._signals if s.signal_type == SignalType.BUY)
        sell_signals = sum(1 for s in self._signals if s.signal_type == SignalType.SELL)
        hold_signals = sum(1 for s in self._signals if s.signal_type == SignalType.HOLD)

        avg_strength = sum(s.strength for s in self._signals) / total_signals

        return StrategyMetrics(
            total_signals=total_signals,
            buy_signals=buy_signals,
            sell_signals=sell_signals,
            hold_signals=hold_signals,
            avg_signal_strength=avg_strength,
        )

    def reset(self) -> None:
        """전략 상태 초기화"""
        self._is_initialized = False
        self._signals.clear()
        self._last_signal = None

    def to_dict(self) -> dict[str, Any]:
        """전략을 딕셔너리로 변환"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "config": self.config.model_dump(),
            "is_initialized": self._is_initialized,
            "total_signals": len(self._signals),
        }

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"signals={len(self._signals)}, "
            f"initialized={self._is_initialized})"
        )


# 기술적 지표 계산 유틸리티
class TechnicalIndicators:
    """기술적 지표 계산 유틸리티"""

    @staticmethod
    def sma(data: pd.Series, window: int) -> pd.Series:
        """단순 이동평균"""
        return data.rolling(window=window).mean()

    @staticmethod
    def ema(data: pd.Series, window: int) -> pd.Series:
        """지수 이동평균"""
        return data.ewm(span=window).mean()

    @staticmethod
    def rsi(data: pd.Series, window: int = 14) -> pd.Series:
        """RSI (Relative Strength Index)"""
        delta = data.diff()
        # 타입 체크 무시하고 계산
        gain = delta.where(delta > 0, 0.0).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0.0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def bollinger_bands(
        data: pd.Series, window: int = 20, std_dev: float = 2
    ) -> dict[str, pd.Series]:
        """볼린저 밴드"""
        sma = data.rolling(window=window).mean()
        std = data.rolling(window=window).std()

        return {
            "middle": sma,
            "upper": sma + (std * std_dev),
            "lower": sma - (std * std_dev),
        }

    @staticmethod
    def macd(
        data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
    ) -> dict[str, pd.Series]:
        """MACD"""
        ema_fast = data.ewm(span=fast).mean()
        ema_slow = data.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line

        return {"macd": macd_line, "signal": signal_line, "histogram": histogram}


if __name__ == "__main__":
    # 사용 예시
    config = StrategyConfig(name="테스트 전략")

    # 실제 구현은 상속받은 클래스에서
    print(f"전략 설정: {config}")
    print(f"기술적 지표 유틸리티: {TechnicalIndicators.__name__}")
