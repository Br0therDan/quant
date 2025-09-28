"""
Strategy Service - FastAPI Application
"""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core import close_database_connection, connect_to_database, settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print(f"Starting {settings.SERVICE_NAME}...")
    await connect_to_database()
    yield
    # Shutdown
    print(f"Shutting down {settings.SERVICE_NAME}...")
    await close_database_connection()


def create_application() -> FastAPI:
    """Create and configure FastAPI application"""

    app = FastAPI(
        title=settings.SERVICE_NAME,
        description="퀀트 백테스트 전략 관리 서비스",
        version=settings.API_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API router
    app.include_router(api_router, prefix=settings.API_PREFIX)

    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "service": settings.SERVICE_NAME,
            "version": settings.API_VERSION,
            "status": "healthy",
            "docs": "/docs",
        }

    return app


# Create application instance
app = create_application()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info",
    )
