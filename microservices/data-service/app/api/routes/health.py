"""
Health Check API Routes
"""

from datetime import datetime
from fastapi import APIRouter

from app.schemas.market_data import HealthCheckResponse
from app.core.config import get_settings
from app.models.market_data import MarketData

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""

    settings = get_settings()

    # Check database connection
    database_connected = True
    total_symbols = 0
    last_update = None

    try:
        # Simple aggregation to check DB connection and get stats
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "unique_symbols": {"$addToSet": "$symbol"},
                    "latest_date": {"$max": "$updated_at"},
                }
            }
        ]

        result = await MarketData.aggregate(pipeline).to_list()
        if result:
            total_symbols = len(result[0].get("unique_symbols", []))
            last_update = result[0].get("latest_date")

    except Exception:
        database_connected = False

    # Check Alpha Vantage API (simple check)
    alpha_vantage_available = bool(settings.alpha_vantage_api_key)

    status = "healthy" if database_connected else "unhealthy"

    return HealthCheckResponse(
        status=status,
        timestamp=datetime.utcnow(),
        database_connected=database_connected,
        alpha_vantage_available=alpha_vantage_available,
        total_symbols=total_symbols,
        last_update=last_update,
    )
