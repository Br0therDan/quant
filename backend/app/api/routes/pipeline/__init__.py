from .watchlists import router as watchlists_router
from .companies import router as companies_router
from .status import router as status_router

from fastapi import APIRouter

router = APIRouter()
router.include_router(watchlists_router, prefix="/watchlists")
router.include_router(companies_router, prefix="/companies")
router.include_router(status_router, prefix="/status")
