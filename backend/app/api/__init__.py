"""
Initialize API routes package
"""

from fastapi import APIRouter
from .routes import (
    market_data_router,
    pipeline_router,
    backtests_router,
    strategies_router,
)

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(
    market_data_router, prefix="/market-data", tags=["Market Data"]
)
api_router.include_router(pipeline_router, prefix="/pipeline", tags=["Pipeline"])
api_router.include_router(strategies_router, prefix="/strategies", tags=["Strategy"])
api_router.include_router(backtests_router, prefix="/backtests", tags=["Backtests"])


__all__ = ["api_router"]
