"""
API Router Configuration
"""

from fastapi import APIRouter

from .routes import backtests, health

api_router = APIRouter()

# Include all route modules
api_router.include_router(backtests.router)
api_router.include_router(health.router)

__all__ = ["api_router"]
