"""
Data Pipeline API Routes (Consolidated)

This module serves as the main entry point for all pipeline-related operations.
Individual route groups are split across separate modules for better organization:
- status.py: Pipeline status and monitoring
- companies.py: Company data collection and retrieval
- watchlists.py: Watchlist management operations

This file imports and combines all route groups for the main API router.
"""

from fastapi import APIRouter

# Import sub-routers from organized modules
from .status import router as status_router
from .companies import router as companies_router
from .watchlists import router as watchlists_router

# Create main pipeline router that combines all sub-routers
router = APIRouter()

# Include all sub-routers
router.include_router(status_router)
router.include_router(companies_router)
router.include_router(watchlists_router)
