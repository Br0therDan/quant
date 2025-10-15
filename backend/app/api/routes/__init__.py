"""
Initialize routes package
"""

# System routes
from .system import router as system_router

# Trading routes
from .trading import backtests_router, strategies_router, signals_router

# Market data routes
from .market_data import router as market_data_router

# ML Platform routes
from .ml_platform import router as ml_router

# Gen AI routes
from .gen_ai import router as gen_ai_router

# User routes
from .user import watchlists_router, dashboard_router


__all__ = [
    # System
    "system_router",
    # Trading
    "backtests_router",
    "strategies_router",
    "signals_router",
    # Market data
    "market_data_router",
    # ML Platform
    "ml_router",
    # Gen AI
    "gen_ai_router",
    # User
    "watchlists_router",
    "dashboard_router",
]
