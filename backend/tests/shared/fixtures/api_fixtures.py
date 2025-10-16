"""API level fixtures shared across backend tests."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict

import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock

from mysingle_quant.auth.authenticate import generate_jwt
from mysingle_quant.core.config import settings as core_settings

from app.main import app


@dataclass
class StubUser:
    """Lightweight stand-in for the auth user model used in tests."""

    id: str = "507f1f77bcf86cd799439011"
    email: str = "dev-superuser@mysingle.io"
    full_name: str = "Dev Test Superuser"
    is_active: bool = True
    is_superuser: bool = True
    is_verified: bool = True


class FakeUserManager:
    """Minimal user manager emulating the behaviour required by the API."""

    def __init__(self, user: StubUser, password: str = "dev-superuser-password") -> None:
        self.user = user
        self.password = password

    async def authenticate(self, username: str, password: str):
        if username != self.user.email or password != self.password:
            return None
        return self.user

    async def get(self, *_args, **_kwargs):
        return self.user

    async def on_after_logout(self, *_args, **_kwargs):
        return None


@pytest.fixture
def stub_user() -> StubUser:
    """Provide a fresh stub user for each test case."""

    return StubUser()


@pytest.fixture
async def async_client(
    monkeypatch: pytest.MonkeyPatch, stub_user: StubUser
) -> AsyncClient:
    """FastAPI test client with external dependencies patched for isolation."""

    async def fake_init_mongo(*_args, **_kwargs):
        class _Client:
            def close(self) -> None:
                return None

        return _Client()

    async def fake_create_first_super_admin() -> None:
        return None

    async def fake_ensure_dev_test_superuser():
        payload = {
            "sub": stub_user.id,
            "email": stub_user.email,
            "is_active": stub_user.is_active,
            "is_superuser": stub_user.is_superuser,
            "is_verified": stub_user.is_verified,
            "aud": core_settings.DEFAULT_AUDIENCE,
            "iat": int(datetime.now(timezone.utc).timestamp()),
        }
        token = generate_jwt(payload=payload)
        return stub_user, token

    fake_user_manager = FakeUserManager(stub_user)

    monkeypatch.setattr(
        "mysingle_quant.core.app_factory.init_mongo", fake_init_mongo
    )
    monkeypatch.setattr(
        "mysingle_quant.core.app_factory.create_first_super_admin",
        fake_create_first_super_admin,
    )
    monkeypatch.setattr(
        "app.core.init_test_user.ensure_dev_test_superuser",
        fake_ensure_dev_test_superuser,
    )
    monkeypatch.setattr(
        "app.main.ensure_dev_test_superuser", fake_ensure_dev_test_superuser
    )
    monkeypatch.setattr(core_settings, "MOCK_DATABASE", True)

    # Patch user manager instances used by auth routes and dependencies
    monkeypatch.setattr(
        "mysingle_quant.auth.router.auth.user_manager", fake_user_manager
    )
    monkeypatch.setattr(
        "mysingle_quant.auth.deps.user_manager", fake_user_manager
    )

    # Guard against other user manager helpers invoked during startup
    monkeypatch.setattr(
        "mysingle_quant.auth.user_manager.UserManager.authenticate",
        AsyncMock(return_value=stub_user),
    )

    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client


@pytest.fixture
def test_user_token(async_client: AsyncClient) -> str:
    """Return the development test user token exposed by the app state."""

    _ = async_client
    token = getattr(app.state, "dev_test_user_token", None)
    if not token:
        raise RuntimeError("Development test user token is not initialized.")
    return token


@pytest.fixture
def test_superuser_token(async_client: AsyncClient) -> str:
    """Return the development test superuser token exposed by the app state."""

    _ = async_client
    token = getattr(app.state, "dev_test_superuser_token", None)
    if not token:
        raise RuntimeError("Development test superuser token is not initialized.")
    return token


@pytest.fixture
def auth_headers(test_user_token: str) -> Dict[str, str]:
    """Default bearer token header for authenticated requests."""

    return {"Authorization": f"Bearer {test_user_token}"}


@pytest.fixture
def superuser_headers(test_superuser_token: str) -> Dict[str, str]:
    """Bearer token header for superuser requests."""

    return {"Authorization": f"Bearer {test_superuser_token}"}
