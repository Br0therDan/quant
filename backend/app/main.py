"""
Data Service Main Application
"""

import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app import models
from app.api import api_router
from app.core.config import settings
from app.core.logging_config import setup_logging
from mysingle_quant import create_fastapi_app
from mysingle_quant.core import get_mongodb_url
from app.utils import seed_strategy_templates

# 로깅 설정 초기화
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting Quant Service...")

    try:
        from app.services.service_factory import service_factory

        logger.info("📊 Initializing DuckDB...")
        database_manager = service_factory.get_database_manager()
        logger.info(f"✅ DuckDB initialized at: {database_manager.db_path}")

        # Pre-initialize services for better performance
        logger.info("🔧 Pre-initializing services...")
        service_factory.get_market_data_service()
        service_factory.get_strategy_service()
        service_factory.get_backtest_service()
        logger.info("✅ All services pre-initialized")

        # Seed strategy templates
        logger.info("🌱 Seeding strategy templates...")
        await seed_strategy_templates()
        logger.info("✅ Strategy templates seeded")

    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

    logger.info("🎉 Quant Service startup completed successfully")

    yield

    # Shutdown
    logger.info("🛑 Shutting down Quant Service...")

    try:
        # Cleanup services
        from app.services.service_factory import service_factory

        await service_factory.cleanup()
        logger.info("✅ Services cleaned up")
    except Exception as e:
        logger.error(f"❌ Shutdown error: {e}")

    logger.info("👋 Quant Service shutdown completed")


# Create FastAPI app
app = create_fastapi_app(
    service_name=settings.SERVICE_NAME,
    service_version=settings.API_VERSION,
    description="Data Service API",
    enable_database=True,
    document_models=models.collections,
    database_name="data_service",
    enable_auth=True,
    enable_oauth=True,
    enable_metrics=True,
    enable_health_check=True,
    lifespan=lifespan,
)

# Include API routes
app.include_router(api_router, prefix=settings.API_PREFIX)


logger.info("🌱 DATABASE_URL: %s", get_mongodb_url(settings.SERVICE_NAME))
