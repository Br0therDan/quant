"""
Initialize API routes package
"""

from fastapi import APIRouter
from .routes import (
    market_data_router,  # 새로운 도메인별 구조
    backtests_router,
    strategies_router,
    watchlists_router,
    dashboard_router,
)

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(
    market_data_router, prefix="/market-data", tags=["Market Data"]
)
api_router.include_router(strategies_router, prefix="/strategies", tags=["Strategy"])
api_router.include_router(backtests_router, prefix="/backtests", tags=["Backtests"])
api_router.include_router(watchlists_router, prefix="/watchlists", tags=["Watchlists"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])


__all__ = ["api_router"]
