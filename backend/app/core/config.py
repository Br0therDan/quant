"""
Data Service Configuration
"""

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

    # DuckDB 파일 경로 - backend 애플리케이션 내부로 통합
    DUCKDB_PATH: str = "./app/data/quant.duckdb"


settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings
