"""
Initialize routes package
"""

from app.api.routes.market_data import router as market_data_router
from app.api.routes.health import router as health_router

__all__ = ["market_data_router", "health_router"]
