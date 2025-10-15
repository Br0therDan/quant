"""Market Data Domain Enums"""

from enum import Enum


class MarketRegimeType(str, Enum):
    """시장 국면 타입"""

    BULLISH = "bullish"
    BEARISH = "bearish"
    VOLATILE = "volatile"
    SIDEWAYS = "sideways"


class DataInterval(str, Enum):
    """시계열 데이터 간격"""

    # Intraday
    ONE_MIN = "1min"
    FIVE_MIN = "5min"
    FIFTEEN_MIN = "15min"
    THIRTY_MIN = "30min"
    SIXTY_MIN = "60min"

    # Daily+
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class DataQualitySeverity(str, Enum):
    """데이터 품질 이슈 심각도"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
