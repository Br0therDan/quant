"""
Initialize API routes package
"""

from fastapi import APIRouter
from .routes import (
    market_data_router,
    pipeline_router,
    health_router,
    backtests_router,
    strategies_router,
    templates_router,
)

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(
    market_data_router, prefix="/market-data", tags=["Market Data"]
)
api_router.include_router(pipeline_router, prefix="/pipeline")
api_router.include_router(health_router, prefix="/health", tags=["Health"])
api_router.include_router(
    backtests_router, prefix="/backtests", tags=["Backtests", "Integrated Backtest"]
)
api_router.include_router(strategies_router, prefix="/strategies", tags=["Strategies"])
api_router.include_router(templates_router, prefix="/templates", tags=["Templates"])

__all__ = ["api_router"]
