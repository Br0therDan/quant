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
        economic_service = service_factory.get_market_data_service().economic
        interest_rates = await economic_service.get_interest_rates(
            country="USA", rate_type="FEDERAL_FUNDS_RATE"
        )

        return {
            "success": True,
            "message": f"금리 데이터(만기: {maturity})를 성공적으로 조회했습니다.",
            "data": [rate.model_dump() for rate in interest_rates],
            "metadata": {
                "indicator": "Interest Rates",
                "maturity": maturity,
                "count": len(interest_rates),
                "status": "success",
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
        economic_service = service_factory.get_market_data_service().economic
        employment_data = await economic_service.get_employment_data(country="USA")

        return {
            "success": True,
            "message": "고용 지표를 성공적으로 조회했습니다.",
            "data": [emp.model_dump() for emp in employment_data],
            "metadata": {
                "indicator": "Employment",
                "count": len(employment_data),
                "status": "success",
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"고용 지표 조회 중 오류 발생: {str(e)}")


# @router.get(
#     "/consumer-sentiment",
#     response_model=Dict[str, Any],
#     description="미국 소비자 심리 지수를 조회합니다.",
# )
# async def get_consumer_sentiment():
#     """소비자 심리 지수 조회"""
#     try:
#         # Note: Alpha Vantage에서 소비자 심리 지수를 직접 제공하지 않음
#         # 기본적인 소비자 심리 데이터 샘플 반환
#         sample_data = [
#             {
#                 "date": "2024-12-01",
#                 "index_value": 75.2,
#                 "change_monthly": 1.5,
#                 "change_yearly": -2.3,
#                 "category": "Michigan Consumer Sentiment Index",
#                 "note": "샘플 데이터 - 실제 API 연동 필요",
#             },
#             {
#                 "date": "2024-11-01",
#                 "index_value": 74.1,
#                 "change_monthly": -0.8,
#                 "change_yearly": -1.9,
#                 "category": "Michigan Consumer Sentiment Index",
#                 "note": "샘플 데이터 - 실제 API 연동 필요",
#             },
#         ]

#         return {
#             "success": True,
#             "message": "소비자 심리 지수 조회 완료 (샘플 데이터)",
#             "data": sample_data,
#             "metadata": {
#                 "indicator": "Consumer Sentiment",
#                 "count": len(sample_data),
#                 "status": "sample_data",
#                 "note": "Alpha Vantage에서 소비자 심리 지수를 직접 제공하지 않음",
#             },
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"소비자 심리 지수 조회 중 오류 발생: {str(e)}")
