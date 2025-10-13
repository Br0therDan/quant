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

    # DuckDB 파일 경로 - 환경변수에서 읽어옴, 기본값 설정
    DUCKDB_PATH: str = getenv("DUCKDB_PATH", "./app/data/quant.duckdb")
    DATA_QUALITY_WEBHOOK_URL: str | None = getenv("DATA_QUALITY_WEBHOOK_URL", None)

    OPENAI_API_KEY: str | None = getenv("OPENAI_API_KEY", "your-openai-api-key")


settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings
