"""
Initialize API routes package
"""

from fastapi import APIRouter
from app.api.routes.market_data import router as market_data_router
from app.api.routes.pipeline import router as pipeline_router
from app.api.routes.health import router as health_router

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(market_data_router)
api_router.include_router(pipeline_router)
api_router.include_router(health_router)

__all__ = ["api_router"]
