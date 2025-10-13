"""
Strategy implementations for the strategy service
"""

from .base_strategy import BaseStrategy, SignalType, StrategyConfig, StrategySignal
from .buy_and_hold import BuyAndHoldStrategy
from .momentum import MomentumStrategy
from .rsi_mean_reversion import RSIMeanReversionStrategy
from .sma_crossover import SMACrossoverStrategy
from .configs import (
    SMACrossoverConfig,
    RSIMeanReversionConfig,
    MomentumConfig,
    BuyAndHoldConfig,
)

__all__ = [
    "BaseStrategy",
    "StrategyConfig",
    "StrategySignal",
    "SignalType",
    "BuyAndHoldStrategy",
    "MomentumStrategy",
    "RSIMeanReversionStrategy",
    "SMACrossoverStrategy",
    "SMACrossoverConfig",
    "RSIMeanReversionConfig",
    "MomentumConfig",
    "BuyAndHoldConfig",
]
