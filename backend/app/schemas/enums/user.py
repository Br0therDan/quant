"""User Domain Enums"""

from enum import Enum


class WatchlistType(str, Enum):
    """워치리스트 타입"""

    STOCKS = "stocks"
    CRYPTO = "crypto"
    FOREX = "forex"
    COMMODITIES = "commodities"
    MIXED = "mixed"


class NotificationType(str, Enum):
    """알림 타입"""

    BACKTEST_COMPLETED = "backtest_completed"
    OPTIMIZATION_COMPLETED = "optimization_completed"
    SIGNAL_GENERATED = "signal_generated"
    DATA_QUALITY_ALERT = "data_quality_alert"
    SYSTEM_ALERT = "system_alert"
