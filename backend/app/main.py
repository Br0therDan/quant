"""
Data Service Main Application
"""

import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app import models
from app.api import api_router
from app.core.config import settings
from mysingle_quant import create_fastapi_app
from mysingle_quant.core import get_mongodb_url
from app.utils import seed_strategy_templates

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting Quant Service...")

    try:
        # Seed strategy templates
        await seed_strategy_templates()
    except Exception as e:
        logger.error(f"Failed to seed templates: {e}")

    logger.info("✅ Quant Service startup completed")

    yield

    # Shutdown
    logger.info("🛑 Shutting down Quant Service...")

    # Cleanup services
    from app.services.service_factory import service_factory

    await service_factory.cleanup()

    logger.info("✅ Quant Service shutdown completed")


# Create FastAPI app
app = create_fastapi_app(
    service_name=settings.SERVICE_NAME,
    service_version=settings.API_VERSION,
    description="Data Service API",
    enable_database=True,
    document_models=models.collections,
    database_name="data_service",
    enable_auth=False,
    enable_metrics=True,
    enable_health_check=True,
    lifespan=lifespan,
)

# Include API routes
app.include_router(api_router, prefix=settings.API_PREFIX)

logger.info("🌱 DATABASE_URL: %s", get_mongodb_url(settings.SERVICE_NAME))
