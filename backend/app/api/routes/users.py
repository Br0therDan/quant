from fastapi import APIRouter
from app.schemas.user import UserRead, UserUpdate
from app.services.auth_service import fastapi_users

router = APIRouter()

router.include_router(fastapi_users.get_users_router(UserRead, UserUpdate))
