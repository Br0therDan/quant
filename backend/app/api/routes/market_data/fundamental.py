"""
Fundamental Data API Routes
기업 재무 데이터 관련 API 엔드포인트
"""

from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Query, Path

from app.services.service_factory import service_factory

router = APIRouter()


@router.get(
    "/overview/{symbol}",
    response_model=Dict[str, Any],
    summary="기업 개요 조회",
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
                "symbol": symbol.upper(),
                "last_refreshed": datetime.now().isoformat(),
                "source": "Alpha Vantage",
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"기업 개요 조회 중 오류 발생: {str(e)}")


@router.get(
    "/income-statement/{symbol}",
    response_model=Dict[str, Any],
    summary="손익계산서 조회",
    description="지정된 종목의 손익계산서를 조회합니다.",
)
async def get_income_statement(
    symbol: str = Path(..., description="종목 심볼 (예: AAPL, TSLA)"),
    period: str = Query(default="annual", description="보고 주기 (annual, quarterly)"),
):
    """손익계산서 조회"""
    try:
        # TODO: FundamentalService에 get_income_statement 메서드 구현 필요
        return {
            "success": False,
            "message": "손익계산서 조회 기능은 아직 구현되지 않았습니다.",
            "data": None,
            "metadata": {
                "symbol": symbol.upper(),
                "period": period,
                "status": "not_implemented",
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"손익계산서 조회 중 오류 발생: {str(e)}")


@router.get(
    "/balance-sheet/{symbol}",
    response_model=Dict[str, Any],
    summary="재무상태표 조회",
    description="지정된 종목의 재무상태표를 조회합니다.",
)
async def get_balance_sheet(
    symbol: str = Path(..., description="종목 심볼 (예: AAPL, TSLA)"),
    period: str = Query(default="annual", description="보고 주기 (annual, quarterly)"),
):
    """재무상태표 조회"""
    try:
        # TODO: FundamentalService에 get_balance_sheet 메서드 구현 필요
        return {
            "success": False,
            "message": "재무상태표 조회 기능은 아직 구현되지 않았습니다.",
            "data": None,
            "metadata": {
                "symbol": symbol.upper(),
                "period": period,
                "status": "not_implemented",
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"재무상태표 조회 중 오류 발생: {str(e)}")


@router.get(
    "/cash-flow/{symbol}",
    response_model=Dict[str, Any],
    summary="현금흐름표 조회",
    description="지정된 종목의 현금흐름표를 조회합니다.",
)
async def get_cash_flow(
    symbol: str = Path(..., description="종목 심볼 (예: AAPL, TSLA)"),
    period: str = Query(default="annual", description="보고 주기 (annual, quarterly)"),
):
    """현금흐름표 조회"""
    try:
        # TODO: FundamentalService에 get_cash_flow 메서드 구현 필요
        return {
            "success": False,
            "message": "현금흐름표 조회 기능은 아직 구현되지 않았습니다.",
            "data": None,
            "metadata": {
                "symbol": symbol.upper(),
                "period": period,
                "status": "not_implemented",
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"현금흐름표 조회 중 오류 발생: {str(e)}")


@router.get(
    "/earnings/{symbol}",
    response_model=Dict[str, Any],
    summary="실적 데이터 조회",
    description="지정된 종목의 실적 데이터를 조회합니다.",
)
async def get_earnings(symbol: str = Path(..., description="종목 심볼 (예: AAPL, TSLA)")):
    """실적 데이터 조회"""
    try:
        # TODO: FundamentalService에 get_earnings 메서드 구현 필요
        return {
            "success": False,
            "message": "실적 데이터 조회 기능은 아직 구현되지 않았습니다.",
            "data": None,
            "metadata": {"symbol": symbol.upper(), "status": "not_implemented"},
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"실적 데이터 조회 중 오류 발생: {str(e)}")
