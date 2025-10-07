"""
Initialize models package
"""

from .backtest import Backtest, BacktestExecution, BacktestResult
from .watchlist import Watchlist
from .market_data import (
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
)
from .performance import StrategyPerformance
from .strategy import Strategy, StrategyTemplate, StrategyExecution
from mysingle_quant.auth.models import User, OAuthAccount

collections = [
    # 백테스트
    Backtest,
    BacktestExecution,
    BacktestResult,
    # Company 및 Watchlist
    Watchlist,
    # 시장 데이터
    DailyPrice,
    IntradayPrice,
    Quote,
    Dividend,
    Split,
    # 펀더멘털 데이터
    CompanyOverview,
    IncomeStatement,
    BalanceSheet,
    CashFlow,
    Earnings,
    # 경제 지표
    EconomicIndicator,
    GDP,
    Inflation,
    InterestRate,
    Employment,
    Manufacturing,
    ConsumerSentiment,
    # 인사이트 데이터
    NewsSentiment,
    NewsArticle,
    AnalystRating,
    SocialSentiment,
    MarketMood,
    OptionFlow,
    # 전략 및 성과
    Strategy,
    StrategyTemplate,
    StrategyExecution,
    # 인증
    User,
    OAuthAccount,
]

__all__ = [
    # Auth models
    "User",
    "OAuthAccount",
    # Market data models
    "DailyPrice",
    "IntradayPrice",
    "Quote",
    "Dividend",
    "Split",
    "CompanyOverview",
    "IncomeStatement",
    "BalanceSheet",
    "CashFlow",
    "Earnings",
    "EconomicIndicator",
    "GDP",
    "Inflation",
    "InterestRate",
    "Employment",
    "Manufacturing",
    "ConsumerSentiment",
    "NewsSentiment",
    "NewsArticle",
    "AnalystRating",
    "SocialSentiment",
    "MarketMood",
    "OptionFlow",
    # Other models
    "Watchlist",
    "Backtest",
    "BacktestExecution",
    "BacktestResult",
    "Strategy",
    "StrategyTemplate",
    "StrategyExecution",
    "StrategyPerformance",
]
