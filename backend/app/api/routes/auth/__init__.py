from .login import router as auth_router
from .reset import router as register_router
from .verify import router as reset_router
from .register import router as verify_router

from fastapi import APIRouter

router = APIRouter()

router.include_router(auth_router)
router.include_router(register_router)
router.include_router(reset_router)
router.include_router(verify_router)
