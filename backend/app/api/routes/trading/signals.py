"""Routes exposing machine learning signal insights."""

from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from mysingle_quant.auth import get_current_active_verified_user, User

from app.schemas.market_data.base import CacheInfo, DataQualityInfo, MetadataInfo
from app.schemas.ml_platform.predictive import MLSignalResponse
from app.services.service_factory import service_factory


router = APIRouter(tags=["Signals"])


@router.get("/{symbol}", response_model=MLSignalResponse)
async def get_ml_signal(
    symbol: str,
    lookback_days: int = Query(
        60, ge=20, le=180, description="Feature lookback window"
    ),
    user: User = Depends(get_current_active_verified_user),
):
    """Return ML signal inference for the requested symbol."""

    signal_service = service_factory.get_ml_signal_service()
    insight = await signal_service.score_symbol(
        symbol.upper(), lookback_days=lookback_days
    )

    metadata = MetadataInfo(
        data_quality=DataQualityInfo(
            quality_score=Decimal(str(round(insight.confidence * 100, 2))),
            last_updated=insight.as_of,
            data_source="duckdb_features",
            confidence_level="model_based",
        ),
        cache_info=CacheInfo(
            cached=False,
            cache_hit=False,
            cache_timestamp=None,
            cache_ttl=None,
        ),
        processing_time_ms=None,
    )

    return MLSignalResponse(
        success=True,
        data=insight,
        metadata=metadata,
        message="Signal inference generated",
    )
