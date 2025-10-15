"""
Trading domain API routes
"""

from .backtests import router as backtests_router
from .strategies import router as strategies_router
from .signals import router as signals_router

__all__ = [
    "backtests_router",
    "strategies_router",
    "signals_router",
]
