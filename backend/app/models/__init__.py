"""
Initialize models package
"""

from .market_data import MarketData, DataRequest, DataQuality
from .company import Company, Watchlist
from .backtest import Backtest, BacktestExecution, BacktestResult
from .strategy import Strategy, StrategyTemplate, StrategyExecution

collections = [
    MarketData,
    DataRequest,
    DataQuality,
    Company,
    Watchlist,
    # 전략
    Strategy,
    StrategyTemplate,
    StrategyExecution,
    # 백테스트
    Backtest,
    BacktestExecution,
    BacktestResult,
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
]
