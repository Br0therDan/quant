"""
API Router Configuration
"""

from fastapi import APIRouter

from .routes import health, strategies, templates

api_router = APIRouter()

# Include all route modules
api_router.include_router(strategies.router)
api_router.include_router(templates.router)
api_router.include_router(health.router)

__all__ = ["api_router"]
