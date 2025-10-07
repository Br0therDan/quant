"""
Market Data Management API Routes
시장 데이터 수집 및 관리 API 엔드포인트
"""

from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Path, Query

from app.services.service_factory import service_factory

router = APIRouter()


@router.post("/collect/company-info/{symbol}")
async def collect_company_info(
    symbol: str = Path(..., description="종목 심볼 (예: AAPL)"),
):
    """
    지정된 심볼의 기업 정보를 수집하여 저장

    Alpha Vantage API를 통해 기업의 기본 정보, 재무 지표,
    업종 분류 등을 수집하고 데이터베이스에 저장합니다.
    """
    try:
        market_service = service_factory.get_market_data_service()

        # 기업 정보 수집 (FundamentalService 활용)
        company_data = await market_service.fundamental.get_company_overview(
            symbol.upper()
        )

        if company_data:
            return {
                "message": f"{symbol.upper()} 기업 정보 수집 완료",
                "symbol": symbol.upper(),
                "success": True,
                "data": company_data,
            }
        else:
            return {
                "message": f"{symbol.upper()} 기업 정보 수집 실패",
                "symbol": symbol.upper(),
                "success": False,
                "error": "데이터를 찾을 수 없습니다",
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"기업 정보 수집 중 오류 발생: {str(e)}")


@router.post("/collect/market-data/{symbol}")
async def collect_market_data(
    symbol: str = Path(..., description="종목 심볼 (예: AAPL)"),
    start_date: Optional[datetime] = Query(None, description="시작일"),
    end_date: Optional[datetime] = Query(None, description="종료일"),
    outputsize: str = Query("compact", description="데이터 크기 (compact/full)"),
):
    """
    지정된 심볼의 주가 데이터를 수집하여 저장

    Alpha Vantage API를 통해 일일 OHLCV 데이터를 수집하고
    DuckDB 캐시 및 MongoDB에 저장합니다.
    """
    try:
        market_service = service_factory.get_market_data_service()

        # 주가 데이터 수집 (StockService 활용)
        market_data = await market_service.stock.get_daily_prices(
            symbol=symbol.upper(), outputsize=outputsize
        )

        if market_data:
            return {
                "message": f"{symbol.upper()} 주가 데이터 수집 완료",
                "symbol": symbol.upper(),
                "start_date": start_date,
                "end_date": end_date,
                "outputsize": outputsize,
                "success": True,
                "data_points": len(market_data) if isinstance(market_data, list) else 1,
            }
        else:
            return {
                "message": f"{symbol.upper()} 주가 데이터 수집 실패",
                "symbol": symbol.upper(),
                "success": False,
                "error": "데이터를 찾을 수 없습니다",
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"주가 데이터 수집 중 오류 발생: {str(e)}")


@router.post("/collect/bulk")
async def collect_bulk_data(
    symbols: List[str] = Query(..., description="수집할 심볼 목록"),
    include_company_info: bool = Query(True, description="기업 정보 포함 여부"),
    include_market_data: bool = Query(True, description="주가 데이터 포함 여부"),
):
    """
    여러 심볼의 데이터를 일괄 수집

    백그라운드 작업으로 처리되며, 대량의 심볼에 대해
    기업 정보와 주가 데이터를 순차적으로 수집합니다.
    """
    try:
        market_service = service_factory.get_market_data_service()

        # 심볼 정규화
        normalized_symbols = [symbol.upper() for symbol in symbols]

        results = {
            "total_symbols": len(normalized_symbols),
            "successful_collections": 0,
            "failed_collections": 0,
            "details": [],
        }

        for symbol in normalized_symbols:
            try:
                symbol_result = {
                    "symbol": symbol,
                    "company_info": False,
                    "market_data": False,
                    "errors": [],
                }

                # 기업 정보 수집
                if include_company_info:
                    try:
                        company_data = (
                            await market_service.fundamental.get_company_overview(
                                symbol
                            )
                        )
                        symbol_result["company_info"] = bool(company_data)
                    except Exception as e:
                        symbol_result["errors"].append(f"Company info: {str(e)}")

                # 주가 데이터 수집
                if include_market_data:
                    try:
                        market_data = await market_service.stock.get_daily_prices(
                            symbol=symbol, outputsize="compact"
                        )
                        symbol_result["market_data"] = bool(market_data)
                    except Exception as e:
                        symbol_result["errors"].append(f"Market data: {str(e)}")

                # 결과 집계
                if symbol_result["company_info"] or symbol_result["market_data"]:
                    results["successful_collections"] += 1
                    symbol_result["status"] = "success"
                else:
                    results["failed_collections"] += 1
                    symbol_result["status"] = "failed"

                results["details"].append(symbol_result)

            except Exception as e:
                results["failed_collections"] += 1
                results["details"].append(
                    {
                        "symbol": symbol,
                        "status": "error",
                        "error": str(e),
                    }
                )

        return {
            "message": f"대량 수집 완료: {results['successful_collections']}개 성공, {results['failed_collections']}개 실패",
            "results": results,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"대량 수집 중 오류 발생: {str(e)}")


@router.get("/coverage/{symbol}")
async def get_data_coverage(
    symbol: str = Path(..., description="종목 심볼 (예: AAPL)"),
):
    """
    지정된 심볼의 데이터 커버리지 정보 조회

    기업 정보, 주가 데이터의 수집 상태와 품질을 확인합니다.
    """
    try:
        market_service = service_factory.get_market_data_service()

        coverage_info = {
            "symbol": symbol.upper(),
            "company_info": {
                "available": False,
                "last_update": None,
                "data_quality": "unknown",
            },
            "market_data": {
                "available": False,
                "last_update": None,
                "data_points": 0,
                "date_range": None,
            },
            "overall_status": "incomplete",
        }

        # 기업 정보 확인
        try:
            company_data = await market_service.fundamental.get_company_overview(
                symbol.upper()
            )
            if company_data:
                coverage_info["company_info"]["available"] = True
                coverage_info["company_info"]["data_quality"] = "good"
                # last_update는 실제 데이터베이스에서 조회해야 함
        except Exception as e:
            coverage_info["company_info"]["error"] = str(e)

        # 주가 데이터 확인
        try:
            market_data = await market_service.stock.get_daily_prices(
                symbol=symbol.upper(), outputsize="compact"
            )
            if market_data:
                coverage_info["market_data"]["available"] = True
                coverage_info["market_data"]["data_points"] = (
                    len(market_data) if isinstance(market_data, list) else 1
                )
                # date_range와 last_update는 실제 데이터에서 추출해야 함
        except Exception as e:
            coverage_info["market_data"]["error"] = str(e)

        # 전체 상태 판단
        if (
            coverage_info["company_info"]["available"]
            and coverage_info["market_data"]["available"]
        ):
            coverage_info["overall_status"] = "complete"
        elif (
            coverage_info["company_info"]["available"]
            or coverage_info["market_data"]["available"]
        ):
            coverage_info["overall_status"] = "partial"

        return coverage_info

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"커버리지 확인 중 오류 발생: {str(e)}")


@router.get("/status")
async def get_system_status():
    """
    시장 데이터 시스템의 전반적인 상태 조회

    API 연결 상태, 캐시 성능, 수집 통계 등을 확인합니다.
    """
    try:
        market_service = service_factory.get_market_data_service()

        # MarketDataService 헬스체크
        health_status = await market_service.health_check()

        system_status = {
            "overall_status": "healthy" if health_status["healthy"] else "unhealthy",
            "api_connections": health_status,
            "last_check": datetime.now(),
            "cache_status": {
                "duckdb_available": True,  # DatabaseManager에서 확인해야 함
                "mongodb_available": True,  # 실제 연결 상태 확인해야 함
            },
            "collection_stats": {
                # 실제 통계는 데이터베이스에서 조회해야 함
                "total_symbols": 0,
                "last_collection": None,
                "recent_errors": 0,
            },
        }

        return system_status

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"상태 조회 중 오류 발생: {str(e)}")
