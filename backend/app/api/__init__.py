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
api_router.include_router(market_data_router)
api_router.include_router(pipeline_router)
api_router.include_router(health_router)
api_router.include_router(backtests_router)
api_router.include_router(strategies_router)
api_router.include_router(templates_router)

__all__ = ["api_router"]
