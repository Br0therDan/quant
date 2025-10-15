"""Trading Domain Enums"""

from enum import Enum


class BacktestStatus(str, Enum):
    """백테스트 상태"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TradeType(str, Enum):
    """거래 타입"""

    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    """주문 타입"""

    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"


class SignalType(str, Enum):
    """전략 신호 타입"""

    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class StrategyType(str, Enum):
    """지원되는 전략 타입"""

    SMA_CROSSOVER = "sma_crossover"
    RSI_MEAN_REVERSION = "rsi_mean_reversion"
    MOMENTUM = "momentum"
    BUY_AND_HOLD = "buy_and_hold"
