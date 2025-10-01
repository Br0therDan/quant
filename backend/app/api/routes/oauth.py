from fastapi import APIRouter
from app.services.auth_service import (
    auth_backend,
    fastapi_users,
)
from app.services.oauth2_client import get_oauth_client
from app.core.config import settings

router = APIRouter()

google_oauth_client = get_oauth_client("google")
kakao_oauth_client = get_oauth_client("kakao")
naver_oauth_client = get_oauth_client("naver")


router.include_router(
    fastapi_users.get_oauth_router(
        google_oauth_client,
        auth_backend,  # type: ignore
        settings.SECRET_KEY,
        associate_by_email=True,
        is_verified_by_default=True,
    )
)
