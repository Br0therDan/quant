"""Market regime API routes."""

from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from mysingle_quant.auth import get_current_active_verified_user, User

from app.schemas.market_data.base import CacheInfo, DataQualityInfo, MetadataInfo
from app.schemas.predictive import MarketRegimeResponse
from app.services.service_factory import service_factory


router = APIRouter(tags=["Market Regime"])


@router.get("/", response_model=MarketRegimeResponse)
async def get_market_regime(
    symbol: str = Query(..., description="Symbol to retrieve regime for"),
    refresh: bool = Query(False, description="Force refresh from raw features"),
    lookback_days: int = Query(
        90, ge=30, le=240, description="Lookback window in days"
    ),
    user: User = Depends(get_current_active_verified_user),
):
    """Return the latest market regime snapshot."""

    regime_service = service_factory.get_regime_detection_service()

    if refresh:
        snapshot = await regime_service.refresh_regime(symbol.upper(), lookback_days)
    else:
        snapshot = await regime_service.get_latest_regime(symbol.upper())
        if snapshot is None:
            snapshot = await regime_service.refresh_regime(
                symbol.upper(), lookback_days
            )

    metadata = MetadataInfo(
        data_quality=DataQualityInfo(
            quality_score=Decimal(str(round(snapshot.confidence * 100, 2))),
            last_updated=snapshot.as_of,
            data_source="duckdb_features",
            confidence_level="classification",
        ),
        cache_info=CacheInfo(
            cached=not refresh,
            cache_hit=snapshot is not None and not refresh,
            cache_timestamp=snapshot.as_of if not refresh else None,
            cache_ttl=None,
        ),
        processing_time_ms=None,
    )

    return MarketRegimeResponse(
        success=True,
        data=snapshot,
        metadata=metadata,
        message="Market regime snapshot retrieved",
    )
