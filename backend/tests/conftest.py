"""
pytest conftest.py

테스트 공통 픽스처 및 설정
"""

import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient, ASGITransport
import jwt
import os

from app.main import app


@pytest.fixture
async def async_client():
    """비동기 HTTP 클라이언트"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def test_user_token():
    """테스트 사용자 JWT 토큰 생성

    실제 JWT 형식으로 생성하여 인증 미들웨어를 통과하도록 함
    """
    # JWT 시크릿 키 (환경변수 또는 기본값)
    secret_key = os.getenv("SECRET_KEY", "test-secret-key-change-in-production")

    # 테스트 사용자 페이로드
    payload = {
        "sub": "test-user-id-123",  # Subject (user ID)
        "email": "test@example.com",
        "is_active": True,
        "is_superuser": False,
        "is_verified": True,
        "exp": datetime.utcnow() + timedelta(hours=1),  # 만료 시간
        "iat": datetime.utcnow(),  # 발급 시간
    }

    # JWT 토큰 생성
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token


@pytest.fixture
def test_superuser_token():
    """테스트 슈퍼유저 JWT 토큰 생성"""
    secret_key = os.getenv("SECRET_KEY", "test-secret-key-change-in-production")

    payload = {
        "sub": "test-superuser-id-456",
        "email": "admin@example.com",
        "is_active": True,
        "is_superuser": True,
        "is_verified": True,
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow(),
    }

    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token


# E2E 테스트용 마크 정의 (이미 pyproject.toml에 등록됨)
# pytest.mark.e2e
# pytest.mark.slow
