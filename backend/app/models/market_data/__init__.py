"""
Market data models package
"""

from .base import BaseMarketDataDocument, DataQualityMixin, MarketData
from .stock import (
    IntradayPrice,
    DailyPrice,
    WeeklyPrice,
    MonthlyPrice,
    StockDataCoverage,
)
from .crypto import (
    CryptoExchangeRate,
    CryptoIntradayPrice,
    CryptoDailyPrice,
    CryptoWeeklyPrice,
    CryptoMonthlyPrice,
)
from .fundamental import (
    CompanyOverview,
    IncomeStatement,
    BalanceSheet,
    CashFlow,
    Earnings,
)
from .economic_indicator import (
    EconomicIndicator,
    GDP,
    Inflation,
    InterestRate,
    Employment,
    Manufacturing,
)
from .intelligence import (
    NewsSentiment,
    NewsArticle,
    AnalystRating,
    SocialSentiment,
    MarketMood,
    OptionFlow,
)
from .technical_indicator import (
    TechnicalIndicator,
    IndicatorDataPoint,
)
from .regime import MarketRegime, MarketRegimeType


__all__ = [
    # Base classes
    "BaseMarketDataDocument",
    "DataQualityMixin",
    "MarketData",
    # Stock models
    "DailyPrice",
    "WeeklyPrice",
    "MonthlyPrice",
    "IntradayPrice",
    "StockDataCoverage",
    # Crypto models
    "CryptoExchangeRate",
    "CryptoIntradayPrice",
    "CryptoDailyPrice",
    "CryptoWeeklyPrice",
    "CryptoMonthlyPrice",
    # Fundamental models
    "CompanyOverview",
    "IncomeStatement",
    "BalanceSheet",
    "CashFlow",
    "Earnings",
    # Economic indicator models
    "EconomicIndicator",
    "GDP",
    "Inflation",
    "InterestRate",
    "Employment",
    "Manufacturing",
    # Intelligence models
    "NewsSentiment",
    "NewsArticle",
    "AnalystRating",
    "SocialSentiment",
    "MarketMood",
    "OptionFlow",
    # Technical indicator models
    "TechnicalIndicator",
    "IndicatorDataPoint",
    # Predictive intelligence models
    "MarketRegime",
    "MarketRegimeType",
]
