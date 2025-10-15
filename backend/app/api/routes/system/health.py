"""Health Check API Routes"""

from datetime import datetime, timezone
from fastapi import APIRouter
from pydantic import BaseModel


class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime


router = APIRouter()


@router.get("/", response_model=HealthCheckResponse)
async def service_health_check():
    """Health check endpoint"""
    return HealthCheckResponse(status="healthy", timestamp=datetime.now(timezone.utc))
