"""
Initialize models package
"""

from .backtest import Backtest, BacktestExecution, BacktestResult
from .watchlist import Watchlist
from .market_data import (
    DailyPrice,
    WeeklyPrice,
    MonthlyPrice,
    IntradayPrice,
    StockDataCoverage,
    MarketRegime,
    MarketData,
    # Crypto data
    CryptoExchangeRate,
    CryptoIntradayPrice,
    CryptoDailyPrice,
    CryptoWeeklyPrice,
    CryptoMonthlyPrice,
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
    # Intelligence data
    NewsSentiment,
    NewsArticle,
    AnalystRating,
    SocialSentiment,
    MarketMood,
    OptionFlow,
    # Technical indicators
    TechnicalIndicator,
    IndicatorDataPoint,
)
from .performance import StrategyPerformance
from .strategy import Strategy, StrategyTemplate, StrategyExecution
from .data_quality import DataQualityEvent
from .optimization import OptimizationStudy, OptimizationTrial
from mysingle_quant.auth.models import User, OAuthAccount

collections = [
    # 백테스트
    Backtest,
    BacktestExecution,
    BacktestResult,
    # Company 및 Watchlist
    Watchlist,
    # 시장 데이터 - 주식
    DailyPrice,
    WeeklyPrice,
    MonthlyPrice,
    IntradayPrice,
    StockDataCoverage,
    MarketData,
    # 시장 데이터 - 암호화폐
    CryptoExchangeRate,
    CryptoIntradayPrice,
    CryptoDailyPrice,
    CryptoWeeklyPrice,
    CryptoMonthlyPrice,
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
    # 인사이트 데이터 (Beanie ODM 모델만)
    NewsSentiment,
    # NewsArticle,  # Pydantic 모델이므로 컬렉션에서 제외
    AnalystRating,
    SocialSentiment,
    MarketMood,
    OptionFlow,
    # 기술적 지표
    TechnicalIndicator,
    IndicatorDataPoint,
    # 예측 인텔리전스
    MarketRegime,
    # 모니터링
    DataQualityEvent,
    # 최적화
    OptimizationStudy,
    OptimizationTrial,
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
    # Market data models - Stock
    "DailyPrice",
    "WeeklyPrice",
    "MonthlyPrice",
    "IntradayPrice",
    "StockDataCoverage",
    "MarketData",
    "MarketRegime",
    # Monitoring
    "DataQualityEvent",
    # Optimization
    "OptimizationStudy",
    "OptimizationTrial",
    # Market data models - Crypto
    "CryptoExchangeRate",
    "CryptoIntradayPrice",
    "CryptoDailyPrice",
    "CryptoWeeklyPrice",
    "CryptoMonthlyPrice",
    # Fundamental data
    "CompanyOverview",
    "IncomeStatement",
    "BalanceSheet",
    "CashFlow",
    "Earnings",
    # Economic indicators
    "EconomicIndicator",
    "GDP",
    "Inflation",
    "InterestRate",
    "Employment",
    "Manufacturing",
    # Intelligence data
    "NewsSentiment",
    "NewsArticle",
    "AnalystRating",
    "SocialSentiment",
    "MarketMood",
    "OptionFlow",
    # Technical indicators
    "TechnicalIndicator",
    "IndicatorDataPoint",
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
