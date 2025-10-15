"""API level fixtures shared across backend tests."""

from __future__ import annotations

from typing import Dict

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def async_client() -> AsyncClient:
    """FastAPI test client that respects the application lifespan."""

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
