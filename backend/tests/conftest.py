"""공통 테스트 픽스처 및 설정."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def async_client():
    """FastAPI lifespan을 포함한 비동기 HTTP 클라이언트."""
    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client


@pytest.fixture
def test_user_token(async_client):
    """개발 환경용 테스트 사용자 토큰."""
    _ = async_client
    token = getattr(app.state, "dev_test_user_token", None)
    if not token:
        raise RuntimeError("Development test user token is not initialized.")
    return token


@pytest.fixture
def test_superuser_token(async_client):
    """개발 환경용 테스트 슈퍼유저 토큰."""
    _ = async_client
    token = getattr(app.state, "dev_test_superuser_token", None)
    if not token:
        raise RuntimeError("Development test superuser token is not initialized.")
    return token


# E2E 테스트용 마크 정의 (이미 pyproject.toml에 등록됨)
# pytest.mark.e2e
# pytest.mark.slow
