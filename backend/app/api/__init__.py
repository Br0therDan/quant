"""
Initialize API routes package
"""

from fastapi import APIRouter
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.core.config import settings
from app.services.auth_service import (
    auth_backend,
    fastapi_users,
)
from app.services.oauth2_client import google_oauth_client
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
api_router.include_router(
    market_data_router, prefix="/market-data", tags=["Market Data"]
)
api_router.include_router(pipeline_router, prefix="/pipeline")
api_router.include_router(health_router, prefix="/health", tags=["Health"])
api_router.include_router(
    backtests_router, prefix="/backtests", tags=["Backtests", "Integrated Backtest"]
)
api_router.include_router(strategies_router, prefix="/strategies", tags=["Strategies"])
api_router.include_router(templates_router, prefix="/templates", tags=["Templates"])


# Auth and User Routes using FastAPI Users
api_router.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["Auth"]  # type: ignore
)

api_router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["Auth"],
)

api_router.include_router(
    fastapi_users.get_reset_password_router(), prefix="/auth", tags=["Auth"]
)

api_router.include_router(
    fastapi_users.get_verify_router(UserRead), prefix="/auth", tags=["Auth"]
)

api_router.include_router(
    fastapi_users.get_oauth_router(
        google_oauth_client,
        auth_backend,  # type: ignore
        settings.SECRET_KEY,
        associate_by_email=True,
        is_verified_by_default=True,
    ),
    prefix="/auth/google",
    tags=["Auth"],
)

api_router.include_router(
    fastapi_users.get_oauth_associate_router(google_oauth_client, UserRead, "SECRET"),
    prefix="/auth/associate/google",
    tags=["Auth"],
)

api_router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["Users"],
)

__all__ = ["api_router"]
