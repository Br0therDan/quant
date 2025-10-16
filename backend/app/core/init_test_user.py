"""Utilities for creating development test users."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Optional, Tuple

from mysingle_quant.auth.models import User
from mysingle_quant.auth.security.jwt import generate_jwt
from mysingle_quant.auth.security.password import password_helper
from mysingle_quant.core.config import settings as core_settings

logger = logging.getLogger(__name__)

_DEFAULT_EMAIL = "dev-superuser@mysingle.io"
_DEFAULT_PASSWORD = "dev-superuser-password"
_DEFAULT_FULL_NAME = "Dev Test Superuser"


def _is_development_environment() -> bool:
    """Return True when the application runs in a development context."""
    return core_settings.DEV_MODE or core_settings.ENVIRONMENT.lower() in {
        "development",
        "dev",
        "local",
        "testing",
    }


def _get_credentials() -> tuple[str, str, str]:
    """Load test superuser credentials from the environment."""
    email = os.getenv("DEV_TEST_SUPERUSER_EMAIL", _DEFAULT_EMAIL)
    password = os.getenv("DEV_TEST_SUPERUSER_PASSWORD", _DEFAULT_PASSWORD)
    full_name = os.getenv("DEV_TEST_SUPERUSER_NAME", _DEFAULT_FULL_NAME)
    return email, password, full_name


def _build_token_payload(user: User) -> dict[str, object]:
    """Create a JWT payload for the development test user."""
    return {
        "sub": str(user.id),
        "email": user.email,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "is_verified": user.is_verified,
        "aud": core_settings.DEFAULT_AUDIENCE,
        "iat": int(datetime.now(timezone.utc).timestamp()),
    }


async def ensure_dev_test_superuser() -> Tuple[Optional[User], Optional[str]]:
    """Ensure a development-only superuser exists and return its token.

    Returns
    -------
    tuple
        A tuple of the persisted ``User`` instance and a non-expiring JWT token.
        ``(None, None)`` is returned when the environment is not a development one
        or when user creation fails.
    """

    if not _is_development_environment():
        return None, None

    email, password, full_name = _get_credentials()

    try:
        user = await User.find_one({"email": email})

        if user is None:
            hashed_password = password_helper.hash(password)
            user = User(
                email=email,
                hashed_password=hashed_password,
                full_name=full_name,
                is_active=True,
                is_superuser=True,
                is_verified=True,
            )
            user = await User.create(user)
            logger.info("Created development test superuser: %s", email)
        else:
            updated = False

            if user.full_name != full_name:
                user.full_name = full_name
                updated = True

            if not user.is_active:
                user.is_active = True
                updated = True

            if not user.is_superuser:
                user.is_superuser = True
                updated = True

            if not user.is_verified:
                user.is_verified = True
                updated = True

            verified, upgraded_hash = password_helper.verify_and_update(
                password, user.hashed_password
            )
            if not verified:
                user.hashed_password = password_helper.hash(password)
                updated = True
            elif upgraded_hash is not None:
                user.hashed_password = upgraded_hash
                updated = True

            if updated:
                await user.save()
                logger.info("Updated development test superuser profile: %s", email)

        token_payload = _build_token_payload(user)
        token = generate_jwt(token_payload)
        return user, token

    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Failed to ensure development test superuser: %s", exc)
        return None, None
