"""
Market data models package
"""

from .base import BaseMarketDataDocument, DataQualityMixin
from .stock import DailyPrice, IntradayPrice, Quote, Dividend, Split
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
    ConsumerSentiment,
)
from .intelligence import (
    NewsSentiment,
    NewsArticle,
    AnalystRating,
    SocialSentiment,
    MarketMood,
    OptionFlow,
)

# 전체 컬렉션 리스트 (Beanie 초기화용)
market_data_collections = [
    # Stock data
    DailyPrice,
    IntradayPrice,
    Quote,
    Dividend,
    Split,
    # Fundamental data
    CompanyOverview,
    IncomeStatement,
    BalanceSheet,
    CashFlow,
    Earnings,
    # Economic indicators
    EconomicIndicator,
    GDP,
    Inflation,
    InterestRate,
    Employment,
    Manufacturing,
    ConsumerSentiment,
    # Intelligence data
    NewsSentiment,
    NewsArticle,
    AnalystRating,
    SocialSentiment,
    MarketMood,
    OptionFlow,
]

__all__ = [
    # Base classes
    "BaseMarketDataDocument",
    "DataQualityMixin",
    # Stock models
    "DailyPrice",
    "IntradayPrice",
    "Quote",
    "Dividend",
    "Split",
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
    "ConsumerSentiment",
    # Intelligence models
    "NewsSentiment",
    "NewsArticle",
    "AnalystRating",
    "SocialSentiment",
    "MarketMood",
    "OptionFlow",
    # Collections list
    "market_data_collections",
]
