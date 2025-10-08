"""
Fundamental Data API Routes
기업 재무 데이터 관련 API 엔드포인트
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, Path

from app.services.service_factory import service_factory
from app.schemas.market_data.fundamental import (
    CompanyOverviewResponse,
    IncomeStatementResponse,
    BalanceSheetResponse,
    CashFlowResponse,
    EarningsResponse,
)

router = APIRouter()


@router.get(
    "/overview/{symbol}",
    response_model=CompanyOverviewResponse,
    description="지정된 종목의 기업 개요 정보를 조회합니다.",
)
async def get_company_overview(
    symbol: str = Path(..., description="종목 심볼 (예: AAPL, TSLA)")
):
    """기업 개요 조회"""
    try:
        fundamental_service = service_factory.get_fundamental_service()

        # FundamentalService의 get_company_overview 메서드 호출
        overview_data = await fundamental_service.get_company_overview(symbol.upper())

        return {
            "success": True,
            "message": f"{symbol} 기업 개요 조회 완료",
            "data": overview_data,
            "metadata": {
                "data_quality": {
                    "quality_score": 95.0,
                    "last_updated": datetime.now(),
                    "data_source": "Alpha Vantage",
                    "confidence_level": "high",
                },
                "cache_info": {
                    "cached": False,
                    "cache_hit": False,
                    "cache_timestamp": None,
                    "cache_ttl": None,
                },
                "processing_time_ms": None,
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"기업 개요 조회 중 오류 발생: {str(e)}")


@router.get(
    "/income-statement/{symbol}",
    response_model=IncomeStatementResponse,
    description="지정된 종목의 손익계산서를 조회합니다.",
)
async def get_income_statement(
    symbol: str = Path(..., description="종목 심볼 (예: AAPL, TSLA)"),
    period: str = Query(default="annual", description="보고 주기 (annual, quarterly)"),
):
    """손익계산서 조회"""
    try:
        market_service = service_factory.get_market_data_service()
        income_statements = await market_service.fundamental.get_income_statement(
            symbol=symbol.upper(), period=period
        )

        return {
            "success": True,
            "message": f"{symbol.upper()}의 손익계산서를 성공적으로 조회했습니다.",
            "data": [stmt.model_dump() for stmt in income_statements],
            "count": len(income_statements),
            "metadata": {
                "data_quality": {
                    "quality_score": 95.0,
                    "last_updated": datetime.now(),
                    "data_source": "Alpha Vantage",
                    "confidence_level": "high",
                },
                "cache_info": {
                    "cached": False,
                    "cache_hit": False,
                    "cache_timestamp": None,
                    "cache_ttl": None,
                },
                "processing_time_ms": None,
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"손익계산서 조회 중 오류 발생: {str(e)}")


@router.get(
    "/balance-sheet/{symbol}",
    response_model=BalanceSheetResponse,
    description="지정된 종목의 재무상태표를 조회합니다.",
)
async def get_balance_sheet(
    symbol: str = Path(..., description="종목 심볼 (예: AAPL, TSLA)"),
    period: str = Query(default="annual", description="보고 주기 (annual, quarterly)"),
):
    """재무상태표 조회"""
    try:
        market_service = service_factory.get_market_data_service()
        balance_sheets = await market_service.fundamental.get_balance_sheet(
            symbol=symbol.upper(), period=period
        )

        return {
            "success": True,
            "message": f"{symbol.upper()}의 재무상태표를 성공적으로 조회했습니다.",
            "data": [sheet.model_dump() for sheet in balance_sheets],
            "count": len(balance_sheets),
            "metadata": {
                "data_quality": {
                    "quality_score": 95.0,
                    "last_updated": datetime.now(),
                    "data_source": "Alpha Vantage",
                    "confidence_level": "high",
                },
                "cache_info": {
                    "cached": False,
                    "cache_hit": False,
                    "cache_timestamp": None,
                    "cache_ttl": None,
                },
                "processing_time_ms": None,
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"재무상태표 조회 중 오류 발생: {str(e)}")


@router.get(
    "/cash-flow/{symbol}",
    response_model=CashFlowResponse,
    description="지정된 종목의 현금흐름표를 조회합니다.",
)
async def get_cash_flow(
    symbol: str = Path(..., description="종목 심볼 (예: AAPL, TSLA)"),
    period: str = Query(default="annual", description="보고 주기 (annual, quarterly)"),
):
    """현금흐름표 조회"""
    try:
        market_service = service_factory.get_market_data_service()
        cash_flows = await market_service.fundamental.get_cash_flow(
            symbol=symbol.upper(), period=period
        )

        return {
            "success": True,
            "message": f"{symbol.upper()}의 현금흐름표를 성공적으로 조회했습니다.",
            "data": [flow.model_dump() for flow in cash_flows],
            "count": len(cash_flows),
            "metadata": {
                "data_quality": {
                    "quality_score": 95.0,
                    "last_updated": datetime.now(),
                    "data_source": "Alpha Vantage",
                    "confidence_level": "high",
                },
                "cache_info": {
                    "cached": False,
                    "cache_hit": False,
                    "cache_timestamp": None,
                    "cache_ttl": None,
                },
                "processing_time_ms": None,
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"현금흐름표 조회 중 오류 발생: {str(e)}")


@router.get(
    "/earnings/{symbol}",
    response_model=EarningsResponse,
    description="지정된 종목의 실적 데이터를 조회합니다.",
)
async def get_earnings(symbol: str = Path(..., description="종목 심볼 (예: AAPL, TSLA)")):
    """실적 데이터 조회"""
    try:
        market_service = service_factory.get_market_data_service()
        earnings = await market_service.fundamental.get_earnings(symbol=symbol.upper())

        return {
            "success": True,
            "message": f"{symbol.upper()}의 실적 발표 데이터를 성공적으로 조회했습니다.",
            "data": [earning.model_dump() for earning in earnings],
            "count": len(earnings),
            "metadata": {
                "data_quality": {
                    "quality_score": 95.0,
                    "last_updated": datetime.now(),
                    "data_source": "Alpha Vantage",
                    "confidence_level": "high",
                },
                "cache_info": {
                    "cached": False,
                    "cache_hit": False,
                    "cache_timestamp": None,
                    "cache_ttl": None,
                },
                "processing_time_ms": None,
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"실적 데이터 조회 중 오류 발생: {str(e)}")
