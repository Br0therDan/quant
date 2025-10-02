"""
Initialize models package
"""

from .backtest import Backtest, BacktestExecution, BacktestResult
from .company import Company, Watchlist
from .market_data import MarketData, DataRequest, DataQuality
from .performance import StrategyPerformance
from .strategy import Strategy, StrategyTemplate, StrategyExecution
from mysingle_quant.auth.models import User, OAuthAccount

collections = [
    # 백테스트
    Backtest,
    BacktestExecution,
    BacktestResult,
    # Company 및 Watchlist
    Company,
    Watchlist,
    # 시장 데이터
    MarketData,
    DataRequest,
    DataQuality,
    # 성과
    StrategyPerformance,
    # 전략
    Strategy,
    StrategyTemplate,
    StrategyExecution,
    # 인증
    User,
    OAuthAccount,
]

__all__ = [
    "MarketData",
    "DataRequest",
    "DataQuality",
    "Company",
    "Watchlist",
    "Backtest",
    "BacktestExecution",
    "BacktestResult",
    "Strategy",
    "StrategyTemplate",
    "StrategyExecution",
    "StrategyPerformance",
]
