"""
Stock data update tasks
주식 데이터 자동 업데이트 작업

이 모듈은 스케줄러를 통해 주기적으로 실행되는 주식 데이터 업데이트 작업을 포함합니다.
"""

import logging
from datetime import datetime

from app.models.market_data.stock import StockDataCoverage
from app.services.service_factory import service_factory


logger = logging.getLogger(__name__)


async def update_stock_data_coverage() -> dict:
    """
    StockDataCoverage를 기반으로 만료된 데이터를 자동 업데이트

    Returns:
        업데이트 결과 딕셔너리
    """
    logger.info("🔄 Starting stock data coverage update task...")

    try:
        market_service = service_factory.get_market_data_service()

        # 업데이트가 필요한 Coverage 찾기 (next_update_due가 현재 시간보다 이전)
        now = datetime.utcnow()
        expired_coverages = await StockDataCoverage.find(
            {"is_active": True, "next_update_due": {"$lte": now}}
        ).to_list()

        logger.info(f"📊 Found {len(expired_coverages)} expired coverages to update")

        results = {
            "total": len(expired_coverages),
            "success": 0,
            "failed": 0,
            "errors": [],
        }

        for coverage in expired_coverages:
            try:
                symbol = coverage.symbol
                data_type = coverage.data_type

                logger.info(f"🔄 Updating {data_type} data for {symbol}...")

                # 데이터 타입별로 업데이트 수행
                if data_type == "daily":
                    await market_service.stock.get_daily_prices(
                        symbol=symbol,
                        outputsize="compact",  # Delta update
                        adjusted=True,
                    )
                elif data_type == "weekly":
                    await market_service.stock.get_weekly_prices(
                        symbol=symbol, outputsize="full", adjusted=True
                    )
                elif data_type == "monthly":
                    await market_service.stock.get_monthly_prices(
                        symbol=symbol, outputsize="full", adjusted=True
                    )

                results["success"] += 1
                logger.info(f"✅ Successfully updated {data_type} data for {symbol}")

            except Exception as e:
                results["failed"] += 1
                error_msg = f"Failed to update {coverage.data_type} for {coverage.symbol}: {str(e)}"
                results["errors"].append(error_msg)
                logger.error(f"❌ {error_msg}")

        logger.info(
            f"✅ Stock data coverage update completed: "
            f"{results['success']} success, {results['failed']} failed"
        )

        return results

    except Exception as e:
        logger.error(f"❌ Stock data coverage update task failed: {e}", exc_info=True)
        return {"total": 0, "success": 0, "failed": 0, "errors": [str(e)]}


async def force_update_all_active_symbols() -> dict:
    """
    모든 활성 심볼의 데이터를 강제 업데이트 (Full update)

    주의: 이 작업은 많은 Alpha Vantage API 호출을 발생시킬 수 있습니다.
    일일 API 한도를 고려하여 사용해야 합니다.

    Returns:
        업데이트 결과 딕셔너리
    """
    logger.info("🔄 Starting forced full update for all active symbols...")

    try:
        market_service = service_factory.get_market_data_service()

        # 모든 활성 Coverage 찾기
        all_coverages = await StockDataCoverage.find({"is_active": True}).to_list()

        # 심볼별로 그룹화 (중복 제거)
        symbols_by_type = {}
        for coverage in all_coverages:
            symbol = coverage.symbol
            data_type = coverage.data_type

            if symbol not in symbols_by_type:
                symbols_by_type[symbol] = []
            symbols_by_type[symbol].append(data_type)

        logger.info(f"📊 Found {len(symbols_by_type)} unique symbols to update")

        results = {
            "total_symbols": len(symbols_by_type),
            "success": 0,
            "failed": 0,
            "errors": [],
        }

        for symbol, data_types in symbols_by_type.items():
            try:
                logger.info(f"🔄 Force updating all data for {symbol}...")

                # Daily, Weekly, Monthly 모두 Full update
                if "daily" in data_types:
                    await market_service.stock.get_daily_prices(
                        symbol=symbol, outputsize="full", adjusted=True
                    )

                if "weekly" in data_types:
                    await market_service.stock.get_weekly_prices(
                        symbol=symbol, outputsize="full", adjusted=True
                    )

                if "monthly" in data_types:
                    await market_service.stock.get_monthly_prices(
                        symbol=symbol, outputsize="full", adjusted=True
                    )

                results["success"] += 1
                logger.info(f"✅ Successfully force updated all data for {symbol}")

            except Exception as e:
                results["failed"] += 1
                error_msg = f"Failed to force update {symbol}: {str(e)}"
                results["errors"].append(error_msg)
                logger.error(f"❌ {error_msg}")

        logger.info(
            f"✅ Forced full update completed: "
            f"{results['success']} success, {results['failed']} failed"
        )

        return results

    except Exception as e:
        logger.error(f"❌ Forced full update task failed: {e}", exc_info=True)
        return {"total_symbols": 0, "success": 0, "failed": 0, "errors": [str(e)]}
