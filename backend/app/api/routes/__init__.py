"""
Initialize routes package
"""

# System routes
from .system.health import router as health_router
from .system.tasks import router as tasks_router

# Trading routes
from .trading.backtests import router as backtests_router
from .trading.strategies import router as strategies_router
from .trading.signals import router as signals_router

# Market data routes
from .market_data import router as market_data_router

# ML Platform routes
from .ml_platform.feature_store import router as feature_store_router
from .ml_platform.ml import router as ml_router

# Gen AI routes
from .gen_ai import router as gen_ai_router

# User routes
from .user.watchlists import router as watchlists_router
from .user.dashboard import router as dashboard_router


__all__ = [
    # System
    "health_router",
    "tasks_router",
    # Trading
    "backtests_router",
    "strategies_router",
    "signals_router",
    # Market data
    "market_data_router",
    # ML Platform
    "feature_store_router",
    "ml_router",
    # Gen AI
    "gen_ai_router",
    # User
    "watchlists_router",
    "dashboard_router",
]
