"""
Intelligence Data API Routes
시장 인텔리전스 데이터 관련 API 엔드포인트
"""

from datetime import datetime, date
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Path

from app.services.service_factory import service_factory

router = APIRouter()


@router.get(
    "/news/{symbol}",
    response_model=Dict[str, Any],
    description="지정된 종목 관련 뉴스를 조회합니다.",
)
async def get_news(
    symbol: str = Path(..., description="종목 심볼 (예: AAPL, TSLA)"),
    topics: Optional[str] = Query(default=None, description="관심 주제 (쉼표로 구분)"),
    time_from: Optional[date] = Query(default=None, description="시작 날짜 (YYYY-MM-DD)"),
    time_to: Optional[date] = Query(default=None, description="종료 날짜 (YYYY-MM-DD)"),
    limit: int = Query(default=50, description="결과 개수 제한", ge=1, le=1000),
):
    """종목 뉴스 조회"""
    try:
        intelligence_service = service_factory.get_intelligence_service()

        # topics를 리스트로 변환
        topics_list = topics.split(",") if topics else None

        # date를 datetime으로 변환
        start_datetime = (
            datetime.combine(time_from, datetime.min.time()) if time_from else None
        )
        end_datetime = (
            datetime.combine(time_to, datetime.min.time()) if time_to else None
        )

        # IntelligenceService의 get_news 메서드 호출
        news_data = await intelligence_service.get_news(
            symbol=symbol.upper(),
            topics=topics_list,
            start_date=start_datetime,
            end_date=end_datetime,
            limit=limit,
        )

        return {
            "success": True,
            "message": f"{symbol} 뉴스 데이터 조회 완료",
            "data": news_data,
            "metadata": {
                "symbol": symbol.upper(),
                "topics": topics_list,
                "time_from": time_from.isoformat() if time_from else None,
                "time_to": time_to.isoformat() if time_to else None,
                "limit": limit,
                "last_refreshed": datetime.now().isoformat(),
                "source": "Alpha Vantage",
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"뉴스 데이터 조회 중 오류 발생: {str(e)}")


@router.get(
    "/sentiment/{symbol}",
    response_model=Dict[str, Any],
    description="지정된 종목의 감정 분석 결과를 조회합니다.",
)
async def get_sentiment_analysis(
    symbol: str = Path(..., description="종목 심볼 (예: AAPL, TSLA)"),
    time_range: str = Query(
        default="1month", description="시간 범위 (1week, 1month, 3months, 6months)"
    ),
    sources: Optional[str] = Query(default=None, description="분석 소스 (쉼표로 구분)"),
):
    """감정 분석 조회"""
    try:
        intelligence_service = service_factory.get_intelligence_service()

        # sources를 리스트로 변환
        sources_list = sources.split(",") if sources else None

        # IntelligenceService의 get_sentiment_analysis 메서드 호출
        sentiment_data = await intelligence_service.get_sentiment_analysis(
            symbol=symbol.upper(), timeframe=time_range
        )

        return {
            "success": True,
            "message": f"{symbol} 감정 분석 조회 완료",
            "data": sentiment_data,
            "metadata": {
                "symbol": symbol.upper(),
                "time_range": time_range,
                "sources": sources_list,
                "last_refreshed": datetime.now().isoformat(),
                "source": "Alpha Vantage",
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"감정 분석 조회 중 오류 발생: {str(e)}")


@router.get(
    "/analyst-recommendations/{symbol}",
    response_model=Dict[str, Any],
    description="지정된 종목의 분석가 추천 정보를 조회합니다.",
)
async def get_analyst_recommendations(
    symbol: str = Path(..., description="종목 심볼 (예: AAPL, TSLA)"),
    time_range: str = Query(
        default="3months", description="시간 범위 (1month, 3months, 6months, 1year)"
    ),
    brokers: Optional[str] = Query(default=None, description="증권사 리스트 (쉼표로 구분)"),
):
    """분석가 추천 조회"""
    try:
        intelligence_service = service_factory.get_intelligence_service()

        # brokers를 리스트로 변환
        brokers_list = brokers.split(",") if brokers else None

        # IntelligenceService의 get_analyst_recommendations 메서드 호출
        recommendations_data = await intelligence_service.get_analyst_recommendations(
            symbol=symbol.upper()
        )

        return {
            "success": True,
            "message": f"{symbol} 분석가 추천 조회 완료",
            "data": recommendations_data,
            "metadata": {
                "symbol": symbol.upper(),
                "time_range": time_range,
                "brokers": brokers_list,
                "last_refreshed": datetime.now().isoformat(),
                "source": "Alpha Vantage",
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석가 추천 조회 중 오류 발생: {str(e)}")


@router.get(
    "/social-sentiment/{symbol}",
    response_model=Dict[str, Any],
    description="지정된 종목의 소셜 미디어 감정 분석을 조회합니다.",
)
async def get_social_sentiment(
    symbol: str = Path(..., description="종목 심볼 (예: AAPL, TSLA)"),
    platforms: Optional[str] = Query(
        default=None, description="소셜 미디어 플랫폼 (twitter,reddit,stocktwits)"
    ),
    time_range: str = Query(default="1week", description="시간 범위 (1day, 1week, 1month)"),
):
    """소셜 미디어 감정 분석 조회"""
    try:
        intelligence_service = service_factory.get_intelligence_service()

        # platforms를 리스트로 변환
        platforms_list = platforms.split(",") if platforms else None

        # IntelligenceService의 get_social_sentiment 메서드 호출
        social_sentiment_data = await intelligence_service.get_social_sentiment(
            symbol=symbol.upper(),
            platforms=platforms_list or ["twitter", "reddit", "stocktwits"],
        )

        return {
            "success": True,
            "message": f"{symbol} 소셜 감정 분석 조회 완료",
            "data": social_sentiment_data,
            "metadata": {
                "symbol": symbol.upper(),
                "platforms": platforms_list,
                "time_range": time_range,
                "last_refreshed": datetime.now().isoformat(),
                "source": "Social Media Analytics",
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"소셜 감정 분석 조회 중 오류 발생: {str(e)}")
