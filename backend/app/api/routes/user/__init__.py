"""
User domain API routes
"""
from .dashboard import router as dashboard_router
from .watchlists import router as watchlists_router

__all__ = [
    "dashboard_router",
    "watchlists_router",
]
