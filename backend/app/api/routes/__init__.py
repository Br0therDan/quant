"""
Initialize routes package
"""

from .market_data import router as market_data_router
from .strategies import router as strategies_router
from .templates import router as templates_router
from .backtests import router as backtests_router
from .health import router as health_router
from .pipeline import router as pipeline_router
from .oauth import router as oauth_router
from .users import router as users_router

from .auth import router as auth_router

__all__ = [
    "market_data_router",
    "health_router",
    "backtests_router",
    "strategies_router",
    "templates_router",
    "pipeline_router",
    "oauth_router",
    "users_router",
    "auth_router",
]
