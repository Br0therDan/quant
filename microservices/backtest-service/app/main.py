"""
Data Service Main Application
"""


import logging

from mysingle_quant import create_fastapi_app
from mysingle_quant.core import get_mongodb_url

from app import models
from app.api import api_router
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = create_fastapi_app(
    service_name=settings.SERVICE_NAME,
    service_version=settings.API_VERSION,
    description="Backtest Service API",
    enable_database=True,
    document_models=models.collections,
    database_name="data_service",
    enable_auth=False,
    enable_metrics=True,
    enable_health_check=True,
)

# Include API routes
app.include_router(api_router, prefix=settings.API_PREFIX)

logger.info("🌱 DATABASE_URL: %s", get_mongodb_url(settings.SERVICE_NAME))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8501, reload=True)
