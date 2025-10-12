"""
Technical Indicator API Routes
기술적 지표 API 엔드포인트
"""

import logging
from typing import Literal
from fastapi import APIRouter, HTTPException, Query, Path

from app.schemas.market_data.technical_indicator import (
    TechnicalIndicatorResponse,
    IndicatorListResponse,
)
from app.services.service_factory import service_factory
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/indicators",
    response_model=IndicatorListResponse,
    description="지원하는 기술적 지표 목록을 조회합니다.",
)
async def get_indicator_list():
    """지원하는 기술적 지표 목록 조회"""
    try:
        ti_service = service_factory.get_technical_indicator_service()
        indicator_list = await ti_service.get_indicator_list()

        return {
            "success": True,
            "message": "기술적 지표 목록 조회 완료",
            "data": indicator_list,
            "metadata": {
                "data_quality": {
                    "quality_score": 100.0,
                    "last_updated": datetime.now(),
                    "data_source": "Built-in",
                    "confidence_level": "high",
                },
                "cache_info": {
                    "cached": False,
                    "cache_hit": False,
                    "cache_ttl_hours": None,
                },
                "total_categories": len(indicator_list),
                "total_indicators": sum(len(v) for v in indicator_list.values()),
            },
        }
    except Exception as e:
        logger.error(f"지표 목록 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"지표 목록 조회 실패: {str(e)}")


@router.get(
    "/{symbol}/sma",
    response_model=TechnicalIndicatorResponse,
    description="단순이동평균(SMA)을 조회합니다.",
)
async def get_sma(
    symbol: str = Path(..., description="종목 심볼 (예: AAPL, TSLA)"),
    interval: Literal[
        "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
    ] = Query(default="daily", description="시간 간격"),
    time_period: int = Query(default=20, ge=1, le=200, description="이동평균 기간"),
    series_type: Literal["close", "open", "high", "low"] = Query(
        default="close", description="계산에 사용할 가격 데이터"
    ),
):
    """단순이동평균(SMA) 조회"""
    try:
        symbol = symbol.upper().strip()

        # 심볼 유효성 검사
        import re

        if not re.match(r"^[A-Z]{1,5}$", symbol):
            raise HTTPException(
                status_code=400,
                detail=f"잘못된 심볼 형식: {symbol}. 1-5자의 영문 대문자만 허용됩니다.",
            )

        ti_service = service_factory.get_technical_indicator_service()

        logger.info(f"SMA 조회 요청: {symbol}, interval={interval}, period={time_period}")

        indicator_data = await ti_service.get_sma(
            symbol=symbol,
            interval=interval,
            time_period=time_period,
            series_type=series_type,
        )

        return {
            "success": True,
            "message": f"{symbol} SMA({time_period}) 조회 완료",
            "data": indicator_data,
            "metadata": {
                "data_quality": {
                    "quality_score": 95.0,
                    "last_updated": datetime.now(),
                    "data_source": "Alpha Vantage",
                    "confidence_level": "high",
                },
                "cache_info": {
                    "cached": True,  # 실제 캐시 히트 여부는 서비스에서 결정
                    "cache_hit": indicator_data.data_points_count > 0,
                    "cache_ttl_hours": 24,
                },
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"SMA 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"SMA 조회 실패: {str(e)}")


@router.get(
    "/{symbol}/wma",
    response_model=TechnicalIndicatorResponse,
    description="가중이동평균(WMA)을 조회합니다.",
)
async def get_wma(
    symbol: str = Path(..., description="종목 심볼 (예: AAPL, TSLA)"),
    interval: Literal[
        "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
    ] = Query(default="daily", description="시간 간격"),
    time_period: int = Query(default=20, ge=1, le=200, description="이동평균 기간"),
    series_type: Literal["close", "open", "high", "low"] = Query(
        default="close", description="계산에 사용할 가격 데이터"
    ),
):
    """가중이동평균(WMA) 조회"""
    try:
        symbol = symbol.upper().strip()

        # 심볼 유효성 검사
        import re

        if not re.match(r"^[A-Z]{1,5}$", symbol):
            raise HTTPException(
                status_code=400,
                detail=f"잘못된 심볼 형식: {symbol}. 1-5자의 영문 대문자만 허용됩니다.",
            )

        ti_service = service_factory.get_technical_indicator_service()

        logger.info(f"WMA 조회 요청: {symbol}, interval={interval}, period={time_period}")

        indicator_data = await ti_service.get_wma(
            symbol=symbol,
            interval=interval,
            time_period=time_period,
            series_type=series_type,
        )

        return {
            "success": True,
            "message": f"{symbol} WMA({time_period}) 조회 완료",
            "data": indicator_data,
            "metadata": {
                "data_quality": {
                    "quality_score": 95.0,
                    "last_updated": datetime.now(),
                    "data_source": "Alpha Vantage",
                    "confidence_level": "high",
                },
                "cache_info": {
                    "cached": True,
                    "cache_hit": indicator_data.data_points_count > 0,
                    "cache_ttl_hours": 24,
                },
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"WMA 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"WMA 조회 실패: {str(e)}")


@router.get(
    "/{symbol}/dema",
    response_model=TechnicalIndicatorResponse,
    description="이중지수이동평균(DEMA)을 조회합니다.",
)
async def get_dema(
    symbol: str = Path(..., description="종목 심볼 (예: AAPL, TSLA)"),
    interval: Literal[
        "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
    ] = Query(default="daily", description="시간 간격"),
    time_period: int = Query(default=20, ge=1, le=200, description="이동평균 기간"),
    series_type: Literal["close", "open", "high", "low"] = Query(
        default="close", description="계산에 사용할 가격 데이터"
    ),
):
    """이중지수이동평균(DEMA) 조회"""
    try:
        symbol = symbol.upper().strip()

        # 심볼 유효성 검사
        import re

        if not re.match(r"^[A-Z]{1,5}$", symbol):
            raise HTTPException(
                status_code=400,
                detail=f"잘못된 심볼 형식: {symbol}. 1-5자의 영문 대문자만 허용됩니다.",
            )

        ti_service = service_factory.get_technical_indicator_service()

        logger.info(f"DEMA 조회 요청: {symbol}, interval={interval}, period={time_period}")

        indicator_data = await ti_service.get_dema(
            symbol=symbol,
            interval=interval,
            time_period=time_period,
            series_type=series_type,
        )

        return {
            "success": True,
            "message": f"{symbol} DEMA({time_period}) 조회 완료",
            "data": indicator_data,
            "metadata": {
                "data_quality": {
                    "quality_score": 95.0,
                    "last_updated": datetime.now(),
                    "data_source": "Alpha Vantage",
                    "confidence_level": "high",
                },
                "cache_info": {
                    "cached": True,
                    "cache_hit": indicator_data.data_points_count > 0,
                    "cache_ttl_hours": 24,
                },
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"DEMA 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"DEMA 조회 실패: {str(e)}")


@router.get(
    "/{symbol}/tema",
    response_model=TechnicalIndicatorResponse,
    description="삼중지수이동평균(TEMA)을 조회합니다.",
)
async def get_tema(
    symbol: str = Path(..., description="종목 심볼 (예: AAPL, TSLA)"),
    interval: Literal[
        "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
    ] = Query(default="daily", description="시간 간격"),
    time_period: int = Query(default=20, ge=1, le=200, description="이동평균 기간"),
    series_type: Literal["close", "open", "high", "low"] = Query(
        default="close", description="계산에 사용할 가격 데이터"
    ),
):
    """삼중지수이동평균(TEMA) 조회"""
    try:
        symbol = symbol.upper().strip()

        # 심볼 유효성 검사
        import re

        if not re.match(r"^[A-Z]{1,5}$", symbol):
            raise HTTPException(
                status_code=400,
                detail=f"잘못된 심볼 형식: {symbol}. 1-5자의 영문 대문자만 허용됩니다.",
            )

        ti_service = service_factory.get_technical_indicator_service()

        logger.info(f"TEMA 조회 요청: {symbol}, interval={interval}, period={time_period}")

        indicator_data = await ti_service.get_tema(
            symbol=symbol,
            interval=interval,
            time_period=time_period,
            series_type=series_type,
        )

        return {
            "success": True,
            "message": f"{symbol} TEMA({time_period}) 조회 완료",
            "data": indicator_data,
            "metadata": {
                "data_quality": {
                    "quality_score": 95.0,
                    "last_updated": datetime.now(),
                    "data_source": "Alpha Vantage",
                    "confidence_level": "high",
                },
                "cache_info": {
                    "cached": True,
                    "cache_hit": indicator_data.data_points_count > 0,
                    "cache_ttl_hours": 24,
                },
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TEMA 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"TEMA 조회 실패: {str(e)}")


@router.get(
    "/{symbol}/ema",
    response_model=TechnicalIndicatorResponse,
    description="지수이동평균(EMA)을 조회합니다.",
)
async def get_ema(
    symbol: str = Path(..., description="종목 심볼 (예: AAPL, TSLA)"),
    interval: Literal[
        "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
    ] = Query(default="daily", description="시간 간격"),
    time_period: int = Query(default=20, ge=1, le=200, description="이동평균 기간"),
    series_type: Literal["close", "open", "high", "low"] = Query(
        default="close", description="계산에 사용할 가격 데이터"
    ),
):
    """지수이동평균(EMA) 조회"""
    try:
        symbol = symbol.upper().strip()

        # 심볼 유효성 검사
        import re

        if not re.match(r"^[A-Z]{1,5}$", symbol):
            raise HTTPException(
                status_code=400,
                detail=f"잘못된 심볼 형식: {symbol}. 1-5자의 영문 대문자만 허용됩니다.",
            )

        ti_service = service_factory.get_technical_indicator_service()

        logger.info(f"EMA 조회 요청: {symbol}, interval={interval}, period={time_period}")

        indicator_data = await ti_service.get_ema(
            symbol=symbol,
            interval=interval,
            time_period=time_period,
            series_type=series_type,
        )

        return {
            "success": True,
            "message": f"{symbol} EMA({time_period}) 조회 완료",
            "data": indicator_data,
            "metadata": {
                "data_quality": {
                    "quality_score": 95.0,
                    "last_updated": datetime.now(),
                    "data_source": "Alpha Vantage",
                    "confidence_level": "high",
                },
                "cache_info": {
                    "cached": True,
                    "cache_hit": indicator_data.data_points_count > 0,
                    "cache_ttl_hours": 24,
                },
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"EMA 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"EMA 조회 실패: {str(e)}")


@router.get(
    "/{symbol}/rsi",
    response_model=TechnicalIndicatorResponse,
    description="상대강도지수(RSI)를 조회합니다.",
)
async def get_rsi(
    symbol: str = Path(..., description="종목 심볼 (예: AAPL, TSLA)"),
    interval: Literal[
        "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
    ] = Query(default="daily", description="시간 간격"),
    time_period: int = Query(default=14, ge=2, le=200, description="RSI 계산 기간"),
    series_type: Literal["close", "open", "high", "low"] = Query(
        default="close", description="계산에 사용할 가격 데이터"
    ),
):
    """상대강도지수(RSI) 조회"""
    try:
        symbol = symbol.upper().strip()

        # 심볼 유효성 검사
        import re

        if not re.match(r"^[A-Z]{1,5}$", symbol):
            raise HTTPException(
                status_code=400,
                detail=f"잘못된 심볼 형식: {symbol}. 1-5자의 영문 대문자만 허용됩니다.",
            )

        ti_service = service_factory.get_technical_indicator_service()

        logger.info(f"RSI 조회 요청: {symbol}, interval={interval}, period={time_period}")

        indicator_data = await ti_service.get_rsi(
            symbol=symbol,
            interval=interval,
            time_period=time_period,
            series_type=series_type,
        )

        return {
            "success": True,
            "message": f"{symbol} RSI({time_period}) 조회 완료",
            "data": indicator_data,
            "metadata": {
                "data_quality": {
                    "quality_score": 95.0,
                    "last_updated": datetime.now(),
                    "data_source": "Alpha Vantage",
                    "confidence_level": "high",
                },
                "cache_info": {
                    "cached": True,
                    "cache_hit": indicator_data.data_points_count > 0,
                    "cache_ttl_hours": 24,
                },
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"RSI 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"RSI 조회 실패: {str(e)}")


@router.get(
    "/{symbol}/macd",
    response_model=TechnicalIndicatorResponse,
    description="MACD를 조회합니다.",
)
async def get_macd(
    symbol: str = Path(..., description="종목 심볼 (예: AAPL, TSLA)"),
    interval: Literal[
        "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
    ] = Query(default="daily", description="시간 간격"),
    series_type: Literal["close", "open", "high", "low"] = Query(
        default="close", description="계산에 사용할 가격 데이터"
    ),
    fastperiod: int = Query(default=12, ge=2, le=200, description="빠른 이동평균 기간"),
    slowperiod: int = Query(default=26, ge=2, le=200, description="느린 이동평균 기간"),
    signalperiod: int = Query(default=9, ge=1, le=200, description="시그널 라인 기간"),
):
    """MACD 조회"""
    try:
        symbol = symbol.upper().strip()

        # 심볼 유효성 검사
        import re

        if not re.match(r"^[A-Z]{1,5}$", symbol):
            raise HTTPException(
                status_code=400,
                detail=f"잘못된 심볼 형식: {symbol}. 1-5자의 영문 대문자만 허용됩니다.",
            )

        ti_service = service_factory.get_technical_indicator_service()

        logger.info(f"MACD 조회 요청: {symbol}, interval={interval}")

        indicator_data = await ti_service.get_macd(
            symbol=symbol,
            interval=interval,
            series_type=series_type,
            fastperiod=fastperiod,
            slowperiod=slowperiod,
            signalperiod=signalperiod,
        )

        return {
            "success": True,
            "message": f"{symbol} MACD 조회 완료",
            "data": indicator_data,
            "metadata": {
                "data_quality": {
                    "quality_score": 95.0,
                    "last_updated": datetime.now(),
                    "data_source": "Alpha Vantage",
                    "confidence_level": "high",
                },
                "cache_info": {
                    "cached": True,
                    "cache_hit": indicator_data.data_points_count > 0,
                    "cache_ttl_hours": 24,
                },
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MACD 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"MACD 조회 실패: {str(e)}")


@router.get(
    "/{symbol}/bbands",
    response_model=TechnicalIndicatorResponse,
    description="볼린저밴드(BBANDS)를 조회합니다.",
)
async def get_bbands(
    symbol: str = Path(..., description="종목 심볼 (예: AAPL, TSLA)"),
    interval: Literal[
        "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
    ] = Query(default="daily", description="시간 간격"),
    time_period: int = Query(default=20, ge=2, le=200, description="이동평균 기간"),
    series_type: Literal["close", "open", "high", "low"] = Query(
        default="close", description="계산에 사용할 가격 데이터"
    ),
    nbdevup: int = Query(default=2, ge=1, le=5, description="상단 밴드 표준편차 배수"),
    nbdevdn: int = Query(default=2, ge=1, le=5, description="하단 밴드 표준편차 배수"),
):
    """볼린저밴드(BBANDS) 조회"""
    try:
        symbol = symbol.upper().strip()

        # 심볼 유효성 검사
        import re

        if not re.match(r"^[A-Z]{1,5}$", symbol):
            raise HTTPException(
                status_code=400,
                detail=f"잘못된 심볼 형식: {symbol}. 1-5자의 영문 대문자만 허용됩니다.",
            )

        ti_service = service_factory.get_technical_indicator_service()

        logger.info(
            f"BBANDS 조회 요청: {symbol}, interval={interval}, period={time_period}"
        )

        indicator_data = await ti_service.get_bbands(
            symbol=symbol,
            interval=interval,
            time_period=time_period,
            series_type=series_type,
            nbdevup=nbdevup,
            nbdevdn=nbdevdn,
        )

        return {
            "success": True,
            "message": f"{symbol} BBANDS({time_period}) 조회 완료",
            "data": indicator_data,
            "metadata": {
                "data_quality": {
                    "quality_score": 95.0,
                    "last_updated": datetime.now(),
                    "data_source": "Alpha Vantage",
                    "confidence_level": "high",
                },
                "cache_info": {
                    "cached": True,
                    "cache_hit": indicator_data.data_points_count > 0,
                    "cache_ttl_hours": 24,
                },
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"BBANDS 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"BBANDS 조회 실패: {str(e)}")


@router.get(
    "/{symbol}/adx",
    response_model=TechnicalIndicatorResponse,
    description="평균방향지수(ADX)를 조회합니다.",
)
async def get_adx(
    symbol: str = Path(..., description="종목 심볼 (예: AAPL, TSLA)"),
    interval: Literal[
        "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
    ] = Query(default="daily", description="시간 간격"),
    time_period: int = Query(default=14, ge=2, le=100, description="ADX 계산 기간"),
):
    """평균방향지수(ADX) 조회"""
    try:
        symbol = symbol.upper().strip()

        # 심볼 유효성 검사
        import re

        if not re.match(r"^[A-Z]{1,5}$", symbol):
            raise HTTPException(
                status_code=400,
                detail=f"잘못된 심볼 형식: {symbol}. 1-5자의 영문 대문자만 허용됩니다.",
            )

        ti_service = service_factory.get_technical_indicator_service()

        logger.info(f"ADX 조회 요청: {symbol}, interval={interval}, period={time_period}")

        indicator_data = await ti_service.get_adx(
            symbol=symbol,
            interval=interval,
            time_period=time_period,
        )

        return {
            "success": True,
            "message": f"{symbol} ADX({time_period}) 조회 완료",
            "data": indicator_data,
            "metadata": {
                "data_quality": {
                    "quality_score": 95.0,
                    "last_updated": datetime.now(),
                    "data_source": "Alpha Vantage",
                    "confidence_level": "high",
                },
                "cache_info": {
                    "cached": True,
                    "cache_hit": indicator_data.data_points_count > 0,
                    "cache_ttl_hours": 24,
                },
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ADX 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"ADX 조회 실패: {str(e)}")


@router.get(
    "/{symbol}/atr",
    response_model=TechnicalIndicatorResponse,
    description="평균진폭(ATR)을 조회합니다.",
)
async def get_atr(
    symbol: str = Path(..., description="종목 심볼 (예: AAPL, TSLA)"),
    interval: Literal[
        "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
    ] = Query(default="daily", description="시간 간격"),
    time_period: int = Query(default=14, ge=2, le=100, description="ATR 계산 기간"),
):
    """평균진폭(ATR) 조회"""
    try:
        symbol = symbol.upper().strip()

        # 심볼 유효성 검사
        import re

        if not re.match(r"^[A-Z]{1,5}$", symbol):
            raise HTTPException(
                status_code=400,
                detail=f"잘못된 심볼 형식: {symbol}. 1-5자의 영문 대문자만 허용됩니다.",
            )

        ti_service = service_factory.get_technical_indicator_service()

        logger.info(f"ATR 조회 요청: {symbol}, interval={interval}, period={time_period}")

        indicator_data = await ti_service.get_atr(
            symbol=symbol,
            interval=interval,
            time_period=time_period,
        )

        return {
            "success": True,
            "message": f"{symbol} ATR({time_period}) 조회 완료",
            "data": indicator_data,
            "metadata": {
                "data_quality": {
                    "quality_score": 95.0,
                    "last_updated": datetime.now(),
                    "data_source": "Alpha Vantage",
                    "confidence_level": "high",
                },
                "cache_info": {
                    "cached": True,
                    "cache_hit": indicator_data.data_points_count > 0,
                    "cache_ttl_hours": 24,
                },
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ATR 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"ATR 조회 실패: {str(e)}")


@router.get(
    "/{symbol}/stoch",
    response_model=TechnicalIndicatorResponse,
    description="스토캐스틱 오실레이터(STOCH)를 조회합니다.",
)
async def get_stoch(
    symbol: str = Path(..., description="종목 심볼 (예: AAPL, TSLA)"),
    interval: Literal[
        "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
    ] = Query(default="daily", description="시간 간격"),
    fastkperiod: int = Query(default=5, ge=1, le=100, description="Fast K 기간"),
    slowkperiod: int = Query(default=3, ge=1, le=100, description="Slow K 기간"),
    slowdperiod: int = Query(default=3, ge=1, le=100, description="Slow D 기간"),
    slowkmatype: int = Query(default=0, ge=0, le=8, description="Slow K MA 타입"),
    slowdmatype: int = Query(default=0, ge=0, le=8, description="Slow D MA 타입"),
):
    """스토캐스틱 오실레이터(STOCH) 조회"""
    try:
        symbol = symbol.upper().strip()

        # 심볼 유효성 검사
        import re

        if not re.match(r"^[A-Z]{1,5}$", symbol):
            raise HTTPException(
                status_code=400,
                detail=f"잘못된 심볼 형식: {symbol}. 1-5자의 영문 대문자만 허용됩니다.",
            )

        ti_service = service_factory.get_technical_indicator_service()

        logger.info(f"STOCH 조회 요청: {symbol}, interval={interval}")

        indicator_data = await ti_service.get_stoch(
            symbol=symbol,
            interval=interval,
            fastkperiod=fastkperiod,
            slowkperiod=slowkperiod,
            slowdperiod=slowdperiod,
            slowkmatype=slowkmatype,
            slowdmatype=slowdmatype,
        )

        return {
            "success": True,
            "message": f"{symbol} STOCH 조회 완료",
            "data": indicator_data,
            "metadata": {
                "data_quality": {
                    "quality_score": 95.0,
                    "last_updated": datetime.now(),
                    "data_source": "Alpha Vantage",
                    "confidence_level": "high",
                },
                "cache_info": {
                    "cached": True,
                    "cache_hit": indicator_data.data_points_count > 0,
                    "cache_ttl_hours": 24,
                },
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"STOCH 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"STOCH 조회 실패: {str(e)}")
