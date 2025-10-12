"""
Market data models package
"""

from .base import BaseMarketDataDocument, DataQualityMixin
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


__all__ = [
    # Base classes
    "BaseMarketDataDocument",
    "DataQualityMixin",
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
]
