"""
Economic Indicator API Routes
경제 지표 관련 API 엔드포인트
"""

from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Query

from app.services.service_factory import service_factory

router = APIRouter()


@router.get(
    "/gdp",
    response_model=Dict[str, Any],
    description="미국 GDP 데이터를 조회합니다.",
)
async def get_gdp_data(
    interval: str = Query(default="annual", description="데이터 간격 (annual, quarterly)")
):
    """GDP 데이터 조회"""
    try:
        economic_service = service_factory.get_economic_indicator_service()

        # EconomicIndicatorService의 get_gdp_data 메서드 호출
        gdp_data = await economic_service.get_gdp_data(country="USA", period=interval)

        return {
            "success": True,
            "message": "GDP 데이터 조회 완료",
            "data": gdp_data,
            "metadata": {
                "indicator": "GDP",
                "interval": interval,
                "last_refreshed": datetime.now().isoformat(),
                "source": "Alpha Vantage",
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GDP 데이터 조회 중 오류 발생: {str(e)}")


@router.get(
    "/inflation",
    response_model=Dict[str, Any],
    description="미국 인플레이션 지표 데이터를 조회합니다.",
)
async def get_inflation_data(
    interval: str = Query(default="monthly", description="데이터 간격 (monthly, annual)")
):
    """인플레이션 데이터 조회"""
    try:
        economic_service = service_factory.get_economic_indicator_service()

        # EconomicIndicatorService의 get_inflation_data 메서드 호출
        inflation_data = await economic_service.get_inflation_data(
            country="USA", indicator_type="CPI"
        )

        return {
            "success": True,
            "message": "인플레이션 데이터 조회 완료",
            "data": inflation_data,
            "metadata": {
                "indicator": "Inflation",
                "interval": interval,
                "last_refreshed": datetime.now().isoformat(),
                "source": "Alpha Vantage",
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"인플레이션 데이터 조회 중 오류 발생: {str(e)}")


@router.get(
    "/interest-rates",
    response_model=Dict[str, Any],
    description="미국 기준금리 및 채권 수익률 데이터를 조회합니다.",
)
async def get_interest_rates(
    maturity: str = Query(
        default="10year", description="만기 (3month, 2year, 5year, 10year, 30year)"
    )
):
    """금리 데이터 조회"""
    try:
        # TODO: EconomicIndicatorService에 get_interest_rates 메서드 구현 필요
        return {
            "success": False,
            "message": "금리 데이터 조회 기능은 아직 구현되지 않았습니다.",
            "data": None,
            "metadata": {
                "indicator": "Interest Rates",
                "maturity": maturity,
                "status": "not_implemented",
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"금리 데이터 조회 중 오류 발생: {str(e)}")


@router.get(
    "/employment",
    response_model=Dict[str, Any],
    description="미국 실업률 및 고용 관련 지표를 조회합니다.",
)
async def get_employment_data():
    """고용 지표 조회"""
    try:
        # TODO: EconomicIndicatorService에 get_employment_data 메서드 구현 필요
        return {
            "success": False,
            "message": "고용 지표 조회 기능은 아직 구현되지 않았습니다.",
            "data": None,
            "metadata": {"indicator": "Employment", "status": "not_implemented"},
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"고용 지표 조회 중 오류 발생: {str(e)}")


@router.get(
    "/consumer-sentiment",
    response_model=Dict[str, Any],
    description="미국 소비자 심리 지수를 조회합니다.",
)
async def get_consumer_sentiment():
    """소비자 심리 지수 조회"""
    try:
        # TODO: EconomicIndicatorService에 get_consumer_sentiment 메서드 구현 필요
        return {
            "success": False,
            "message": "소비자 심리 지수 조회 기능은 아직 구현되지 않았습니다.",
            "data": None,
            "metadata": {
                "indicator": "Consumer Sentiment",
                "status": "not_implemented",
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"소비자 심리 지수 조회 중 오류 발생: {str(e)}")
