"""
Market Data API Routes - Main Router
도메인별 마켓 데이터 API 라우터 통합
"""

from fastapi import APIRouter, Depends
from mysingle_quant.auth import get_current_active_verified_user

from .stock import router as stock_router
from .crypto import router as crypto_router
from .fundamental import router as fundamental_router
from .economic_indicator import router as economic_indicator_router
from .intelligence import router as intelligence_router
from .management import router as management_router
from .technical_indicators import router as technical_indicators_router

# 메인 마켓 데이터 라우터
router = APIRouter(dependencies=[Depends(get_current_active_verified_user)])

# 도메인별 라우터 포함
router.include_router(stock_router, prefix="/stock", tags=["Stock"])
router.include_router(crypto_router, prefix="/crypto", tags=["Crypto"])
router.include_router(fundamental_router, prefix="/fundamental", tags=["Fundamental"])
router.include_router(economic_indicator_router, prefix="/economic", tags=["Economic"])
router.include_router(
    intelligence_router, prefix="/intelligence", tags=["Intelligence"]
)
router.include_router(management_router, prefix="/management", tags=["Market Data"])
router.include_router(
    technical_indicators_router,
    prefix="/technical-indicators",
    tags=["Technical Indicator"],
)


@router.get("/", tags=["Market Data"])
async def get_market_data_info():
    """마켓 데이터 API 정보 및 사용 가능한 엔드포인트 목록"""
    return {
        "name": "Market Data API v2",
        "version": "2.0.0",
        "description": "도메인별 분리된 마켓 데이터 API",
        "domains": {
            "stock": {
                "description": "주식 데이터 (일일 가격, 실시간 호가 등)",
                "endpoints": [
                    "/daily/{symbol}",
                    "/quote/{symbol}",
                    "/historical/{symbol}",
                ],
            },
            "crypto": {
                "description": "암호화폐 데이터 (일일/주간/월간 가격, 환율 등)",
                "endpoints": [
                    "/exchange-rate/{from_currency}/{to_currency}",
                    "/daily/{symbol}",
                    "/weekly/{symbol}",
                    "/monthly/{symbol}",
                    "/bitcoin/{period}",
                    "/ethereum/{period}",
                ],
            },
            "fundamental": {
                "description": "기업 재무 데이터 (재무제표, 기업 개요 등)",
                "endpoints": [
                    "/overview/{symbol}",
                    "/income-statement/{symbol}",
                    "/balance-sheet/{symbol}",
                ],
            },
            "economic": {
                "description": "경제 지표 (GDP, 인플레이션, 고용률 등)",
                "endpoints": ["/gdp", "/inflation", "/employment", "/interest-rates"],
            },
            "intelligence": {
                "description": "시장 인텔리전스 (뉴스, 감정 분석, 분석가 추천)",
                "endpoints": [
                    "/news/{symbol}",
                    "/sentiment/{symbol}",
                    "/analyst-recommendations/{symbol}",
                ],
            },
            "management": {
                "description": "데이터 수집 및 관리 (기업 정보, 주가 데이터 수집)",
                "endpoints": [
                    "/collect/company-info/{symbol}",
                    "/collect/market-data/{symbol}",
                    "/collect/bulk",
                    "/coverage/{symbol}",
                    "/status",
                ],
            },
            "technical-indicators": {
                "description": "기술적 지표 (SMA, EMA, RSI, MACD, Bollinger Bands 등)",
                "endpoints": [
                    "/indicators",
                    "/{symbol}/sma",
                    "/{symbol}/ema",
                    "/{symbol}/rsi",
                    "/{symbol}/macd",
                    "/{symbol}/bbands",
                ],
            },
        },
    }


@router.get("/health", tags=["Market Data"])
async def health_check():
    """마켓 데이터 서비스 상태 확인"""
    return {
        "status": "healthy",
        "services": {
            "stock_service": "operational",
            "crypto_service": "operational",
            "fundamental_service": "operational",
            "economic_indicator_service": "operational",
            "intelligence_service": "operational",
            "technical_indicator_service": "operational",
        },
        "cache_status": {"duckdb": "connected", "mongodb": "connected"},
    }
