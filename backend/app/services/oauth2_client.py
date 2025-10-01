from httpx_oauth.clients.google import GoogleOAuth2
from httpx_oauth.clients.kakao import KakaoOAuth2
from httpx_oauth.clients.naver import NaverOAuth2
from httpx_oauth.oauth2 import BaseOAuth2
from app.core.config import settings

oauth_clients = {
    "google": GoogleOAuth2(
        settings.GOOGLE_CLIENT_ID,
        settings.GOOGLE_CLIENT_SECRET,
    ),
    "kakao": KakaoOAuth2(
        settings.KAKAO_CLIENT_ID,
        settings.KAKAO_CLIENT_SECRET,
    ),
    "naver": NaverOAuth2(
        settings.NAVER_CLIENT_ID,
        settings.NAVER_CLIENT_SECRET,
    ),
}


def get_oauth_client(provider_name: str) -> BaseOAuth2:
    client = oauth_clients.get(provider_name)
    if client is None:
        raise ValueError(f"Unsupported OAuth provider: {provider_name}")
    return client
