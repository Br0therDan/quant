import logging
from typing import Optional

from beanie import PydanticObjectId
from fastapi import Depends, Request
from fastapi_users import BaseUserManager
from fastapi_users_db_beanie import BeanieUserDatabase, ObjectIDIDMixin

from app.models.user import User, OAuthAccount
from app.core.config import settings
from app.utils.email.email_gen import (
    generate_verification_email,
    generate_reset_password_email,
)
from app.utils.email.email_sending import send_email

# 로거 설정
logger = logging.getLogger(__name__)


async def get_user_db():
    yield BeanieUserDatabase(User, OAuthAccount)  # type: ignore


SECRET = settings.SECRET_KEY


class UserManager(ObjectIDIDMixin, BaseUserManager[User, PydanticObjectId]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        """신규 가입 후 이메일 인증 발송"""
        logger.info(f"New user registered: {user.email} (ID: {user.id})")

        if not user.is_verified and settings.emails_enabled:
            try:
                # 인증 이메일 발송
                origin = (
                    str(request.base_url).rstrip("/")
                    if request
                    else settings.FRONTEND_URL
                )
                email_data = generate_verification_email(user.email, origin)

                send_email(
                    email_to=user.email,
                    subject=email_data.subject,
                    html_content=email_data.html_content,
                )

                logger.info(f"Verification email sent to {user.email}")
            except Exception as e:
                logger.error(f"Failed to send verification email to {user.email}: {e}")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """패스워드 복구 요청 후 이메일 발송"""
        logger.info(f"Password reset requested for user: {user.email} (ID: {user.id})")

        if settings.emails_enabled:
            try:
                origin = (
                    str(request.base_url).rstrip("/")
                    if request
                    else settings.FRONTEND_URL
                )
                email_data = generate_reset_password_email(
                    email_to=user.email,
                    email=user.email,
                    token=token,
                    origin=origin,
                )

                send_email(
                    email_to=user.email,
                    subject=email_data.subject,
                    html_content=email_data.html_content,
                )

                logger.info(f"Password reset email sent to {user.email}")
            except Exception as e:
                logger.error(
                    f"Failed to send password reset email to {user.email}: {e}"
                )

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """인증 이메일 재요청 후 발송"""
        logger.info(
            f"Email verification re-requested for user: {user.email} (ID: {user.id})"
        )

        if settings.emails_enabled:
            try:
                origin = (
                    str(request.base_url).rstrip("/")
                    if request
                    else settings.FRONTEND_URL
                )
                email_data = generate_verification_email(user.email, origin)

                send_email(
                    email_to=user.email,
                    subject=email_data.subject,
                    html_content=email_data.html_content,
                )

                logger.info(f"Verification email re-sent to {user.email}")
            except Exception as e:
                logger.error(
                    f"Failed to re-send verification email to {user.email}: {e}"
                )

    async def on_after_verify(self, user: User, request: Optional[Request] = None):
        """이메일 인증 완료 후"""
        logger.info(f"User email verified successfully: {user.email} (ID: {user.id})")

    async def on_after_update(
        self, user: User, update_dict: dict, request: Optional[Request] = None
    ):
        """사용자 정보 업데이트 후"""
        logger.info(
            f"User updated: {user.email} (ID: {user.id}), fields: {list(update_dict.keys())}"
        )


async def get_user_manager(user_db: BeanieUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)
