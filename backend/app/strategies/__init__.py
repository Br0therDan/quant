"""
Strategy implementations for the strategy service
"""

from .base_strategy import BaseStrategy, SignalType, StrategyConfig, StrategySignal
from .buy_and_hold import BuyAndHoldConfig, BuyAndHoldStrategy
from .momentum import MomentumConfig, MomentumStrategy
from .rsi_mean_reversion import RSIConfig, RSIMeanReversionStrategy
from .sma_crossover import SMAConfig, SMACrossoverStrategy

__all__ = [
    "BaseStrategy",
    "StrategyConfig",
    "StrategySignal",
    "SignalType",
    "BuyAndHoldStrategy",
    "BuyAndHoldConfig",
    "MomentumStrategy",
    "MomentumConfig",
    "RSIMeanReversionStrategy",
    "RSIConfig",
    "SMACrossoverStrategy",
    "SMAConfig",
]
