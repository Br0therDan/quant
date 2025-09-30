"""
Data Service Configuration
"""

from os import getenv
from mysingle_quant.core import CommonSettings
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


settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings
