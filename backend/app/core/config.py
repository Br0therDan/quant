"""
Data Service Configuration
"""

from os import getenv
from typing import Self
from mysingle_quant.core import CommonSettings
from pydantic import computed_field, model_validator
from pydantic_settings import SettingsConfigDict


class Settings(CommonSettings):
    """Application settings extending CommonSettings."""

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    SERVICE_NAME: str = "quant-service"
    API_PREFIX: str = "/api/v1"
    API_VERSION: str = "v1"

    SUPERUSER_EMAIL: str = "your_email@example.com"
    SUPERUSER_PASSWORD: str = "change-this-admin-password"
    SUPERUSER_FULLNAME: str = "Admin User"

    # DuckDB 파일 경로 - 환경변수에서 읽어옴, 기본값 설정
    DUCKDB_PATH: str = getenv("DUCKDB_PATH", "./app/data/quant.duckdb")

    EMAIL_TOKEN_EXPIRE_HOURS: int = 48  # 이메일 토큰 만료 시간 (시간 단위)

    GOOGLE_CLIENT_ID: str = "your-google-client-id"
    GOOGLE_CLIENT_SECRET: str = "your-google-client-secret"

    OKTA_CLIENT_ID: str = "your-okta-client-id"
    OKTA_CLIENT_SECRET: str = "your-okta-client-secret"
    OKTA_DOMAIN: str = "your-okta-domain"

    KAKAO_CLIENT_ID: str = "your-kakao-client-id"
    KAKAO_CLIENT_SECRET: str = "your-kakao-client-secret"

    NAVER_CLIENT_ID: str = "your-naver-client-id"
    NAVER_CLIENT_SECRET: str = "your-naver-client-secret"

    # Frontend URL for email links
    FRONTEND_URL: str = "http://localhost:3000"

    # 메일링 설정 (Mailtrap)
    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str = "your_smtp_host"
    SMTP_USER: str = "your_smtp_user"
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: str = "your_email@example.com"
    EMAILS_FROM_NAME: str = "Admin Name"

    @model_validator(mode="after")
    def _set_default_emails_from(self) -> Self:
        if not self.EMAILS_FROM_NAME:
            self.EMAILS_FROM_NAME = self.PROJECT_NAME
        return self

    @computed_field
    @property
    def emails_enabled(self) -> bool:
        return bool(self.SMTP_HOST == "your_smtp_host")


settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings
