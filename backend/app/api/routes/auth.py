from fastapi import APIRouter
from app.schemas.user import UserCreate, UserRead
from app.services.auth_service import (
    auth_backend,
    fastapi_users,
)

router = APIRouter()

router.include_router(fastapi_users.get_auth_router(auth_backend))  # type: ignore
router.include_router(fastapi_users.get_register_router(UserRead, UserCreate))
router.include_router(fastapi_users.get_reset_password_router())
router.include_router(fastapi_users.get_verify_router(UserRead))
