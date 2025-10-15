"""Dashboard API routes."""

from decimal import Decimal
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from mysingle_quant.auth import get_current_active_verified_user, User
from app.services.service_factory import service_factory
from app.schemas.user.dashboard import (
    DashboardSummaryResponse,
    PortfolioPerformanceResponse,
    StrategyComparisonResponse,
    RecentTradesResponse,
    WatchlistQuotesResponse,
    NewsFeedResponse,
    EconomicCalendarResponse,
)
from app.schemas.ml_platform.predictive import (
    PredictiveInsightsResponse,
    PortfolioForecastResponse,
)


router = APIRouter()


@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(user: User = Depends(get_current_active_verified_user)):
    """대시보드 요약 데이터를 조회합니다.

    사용자의 포트폴리오, 전략, 최근 활동 요약 정보를 반환합니다.
    """
    dashboard_service = service_factory.get_dashboard_service()
    summary = await dashboard_service.get_dashboard_summary(str(user.id))
    return DashboardSummaryResponse(data=summary, message="대시보드 요약 조회 성공")


@router.get("/portfolio/performance", response_model=PortfolioPerformanceResponse)
async def get_portfolio_performance(
    period: str = Query("1M", description="조회 기간 (1D, 1W, 1M, 3M, 6M, 1Y)"),
    granularity: str = Query("day", description="데이터 간격 (hour, day, week)"),
    user: User = Depends(get_current_active_verified_user),
):
    """포트폴리오 성과 차트 데이터를 조회합니다.

    지정된 기간의 포트폴리오 성과 데이터와 요약 지표를 반환합니다.
    """
    dashboard_service = service_factory.get_dashboard_service()
    performance = await dashboard_service.get_portfolio_performance(
        str(user.id), period, granularity
    )
    return PortfolioPerformanceResponse(data=performance, message="포트폴리오 성과 조회 성공")


@router.get("/strategies/comparison", response_model=StrategyComparisonResponse)
async def get_strategy_comparison(
    limit: int = Query(10, description="조회할 전략 수"),
    sort_by: str = Query("return", description="정렬 기준 (return, sharpe, win_rate)"),
    user: User = Depends(get_current_active_verified_user),
):
    """전략 성과 비교 데이터를 조회합니다.

    사용자의 전략들을 성과별로 비교한 데이터를 반환합니다.
    """
    dashboard_service = service_factory.get_dashboard_service()
    comparison = await dashboard_service.get_strategy_comparison(
        str(user.id), limit, sort_by
    )
    return StrategyComparisonResponse(data=comparison, message="전략 비교 조회 성공")


@router.get("/trades/recent", response_model=RecentTradesResponse)
async def get_recent_trades(
    limit: int = Query(20, description="조회할 거래 수"),
    days: int = Query(7, description="조회할 일수"),
    user: User = Depends(get_current_active_verified_user),
):
    """최근 거래 내역을 조회합니다.

    지정된 기간의 최근 거래 내역과 요약 정보를 반환합니다.
    """
    dashboard_service = service_factory.get_dashboard_service()
    trades = await dashboard_service.get_recent_trades(str(user.id), limit, days)
    return RecentTradesResponse(data=trades, message="최근 거래 조회 성공")


@router.get("/watchlist/quotes", response_model=WatchlistQuotesResponse)
async def get_watchlist_quotes(user: User = Depends(get_current_active_verified_user)):
    """관심종목 현재가를 조회합니다.

    사용자의 관심종목의 현재 주가 정보를 반환합니다.
    """
    dashboard_service = service_factory.get_dashboard_service()
    quotes = await dashboard_service.get_watchlist_quotes(str(user.id))
    return WatchlistQuotesResponse(data=quotes, message="관심종목 시세 조회 성공")


@router.get("/news/feed", response_model=NewsFeedResponse)
async def get_news_feed(
    limit: int = Query(10, description="조회할 뉴스 수"),
    symbols: Optional[List[str]] = Query(None, description="관련 심볼 필터"),
    categories: Optional[List[str]] = Query(None, description="카테고리 필터"),
    user: User = Depends(get_current_active_verified_user),
):
    """뉴스 피드를 조회합니다.

    사용자와 관련된 뉴스 피드를 반환합니다.
    """
    dashboard_service = service_factory.get_dashboard_service()
    news = await dashboard_service.get_news_feed(
        str(user.id), limit, symbols, categories
    )
    return NewsFeedResponse(data=news, message="뉴스 피드 조회 성공")


@router.get("/economic/calendar", response_model=EconomicCalendarResponse)
async def get_economic_calendar(
    days: int = Query(7, description="조회할 일수"),
    importance: Optional[List[str]] = Query(
        None, description="중요도 필터 (high, medium, low)"
    ),
    user: User = Depends(get_current_active_verified_user),
):
    """경제 캘린더를 조회합니다.

    예정된 경제 지표 발표 일정을 반환합니다.
    """
    dashboard_service = service_factory.get_dashboard_service()
    calendar = await dashboard_service.get_economic_calendar(
        str(user.id), days, importance
    )
    return EconomicCalendarResponse(data=calendar, message="경제 캘린더 조회 성공")


@router.get(
    "/predictive/overview",
    response_model=PredictiveInsightsResponse,
)
async def get_predictive_overview(
    symbol: str = Query(..., description="예측 인텔리전스를 요청할 심볼"),
    horizon_days: int = Query(30, ge=7, le=120, description="예측 기간 (일)"),
    user: User = Depends(get_current_active_verified_user),
):
    """Predictive intelligence bundle combining signal, regime, and forecast."""

    dashboard_service = service_factory.get_dashboard_service()
    insights = await dashboard_service.get_predictive_snapshot(
        str(user.id), symbol.upper(), horizon_days=horizon_days
    )

    response = PredictiveInsightsResponse(
        success=True,
        data=insights,
        message="Predictive insights retrieved",
    )
    response.metadata.data_quality.quality_score = Decimal(
        str(round(insights.signal.confidence * 100, 2))
    )
    response.metadata.data_quality.last_updated = insights.signal.as_of
    response.metadata.cache_info.cache_hit = False
    response.metadata.cache_info.cached = False
    response.metadata.cache_info.cache_timestamp = insights.regime.as_of
    response.metadata.processing_time_ms = None
    return response


@router.get(
    "/portfolio/forecast",
    response_model=PortfolioForecastResponse,
)
async def get_portfolio_forecast(
    horizon_days: int = Query(30, ge=7, le=120, description="예측 기간 (일, 7-120일)"),
    user: User = Depends(get_current_active_verified_user),
):
    """포트폴리오 확률적 예측을 조회합니다.

    히스토리 기반 Gaussian projection으로 5/50/95 백분위 예측을 생성합니다.

    Args:
        horizon_days: 예측 기간 (일)
        user: 인증된 사용자

    Returns:
        백분위 예측 분포 (5th, 50th, 95th percentiles)

    Raises:
        400: 포트폴리오 히스토리가 없는 경우
        500: 예측 생성 실패
    """
    portfolio_service = service_factory.get_portfolio_service()

    try:
        forecast = await portfolio_service.get_portfolio_forecast(
            user_id=str(user.id), horizon_days=horizon_days
        )

        from app.schemas.market_data.base import (
            MetadataInfo,
            DataQualityInfo,
            CacheInfo,
        )

        response = PortfolioForecastResponse(
            success=True,
            message=f"{horizon_days}일 포트폴리오 예측 생성 완료",
            data=forecast,
            metadata=MetadataInfo(
                data_quality=DataQualityInfo(
                    quality_score=Decimal("95.0"),
                    last_updated=forecast.as_of,
                    data_source="probabilistic_kpi",
                    confidence_level="model_based",
                ),
                cache_info=CacheInfo(
                    cached=False,
                    cache_hit=False,
                    cache_timestamp=None,
                    cache_ttl=None,
                ),
                processing_time_ms=0.0,
            ),
        )
        return response

    except ValueError as ve:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        from fastapi import HTTPException

        raise HTTPException(status_code=500, detail=f"예측 생성 실패: {str(e)}")
