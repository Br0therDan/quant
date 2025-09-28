"""
Data Pipeline Service
Port of the original data_service pipeline functionality
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from app.services.market_data_service import MarketDataService
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class DataPipeline:
    """Data collection and processing pipeline"""

    def __init__(self):
        self.settings = get_settings()
        self.market_service = MarketDataService()
        self.symbols_to_update: List[str] = []

    async def setup_default_symbols(self) -> None:
        """Setup default watchlist symbols"""
        default_symbols = [
            "AAPL",
            "MSFT",
            "GOOGL",
            "AMZN",
            "TSLA",
            "META",
            "NVDA",
            "JPM",
            "JNJ",
            "V",
        ]

        logger.info(f"Setting up default symbols: {default_symbols}")
        self.symbols_to_update = default_symbols

    async def update_watchlist(self, symbols: List[str]) -> None:
        """Update the watchlist with new symbols"""
        self.symbols_to_update = symbols
        logger.info(f"Watchlist updated with {len(symbols)} symbols")

    async def collect_stock_info(self, symbol: str) -> bool:
        """Collect basic stock information"""
        try:
            info = await self.market_service.get_company_overview(symbol)
            if info:
                # TODO: Store company information in a separate collection
                logger.info(f"Stock info collected for {symbol}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to collect stock info for {symbol}: {e}")
            return False

    async def collect_daily_data(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> bool:
        """Collect daily price data for a symbol"""
        try:
            if not start_date:
                start_date = datetime.now() - timedelta(days=100)
            if not end_date:
                end_date = datetime.now()

            data = await self.market_service.get_market_data(
                symbol, start_date, end_date, force_refresh=True
            )

            if data:
                logger.info(f"Daily data collected for {symbol}: {len(data)} records")
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to collect daily data for {symbol}: {e}")
            return False

    async def run_full_update(
        self, symbols: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Run full data update for specified symbols"""
        target_symbols = symbols or self.symbols_to_update

        if not target_symbols:
            await self.setup_default_symbols()
            target_symbols = self.symbols_to_update

        results = {
            "total_symbols": len(target_symbols),
            "successful_updates": 0,
            "failed_updates": 0,
            "details": [],
        }

        logger.info(f"Starting full update for {len(target_symbols)} symbols")

        for symbol in target_symbols:
            try:
                # Collect basic info
                info_success = await self.collect_stock_info(symbol)

                # Collect daily data
                data_success = await self.collect_daily_data(symbol)

                if info_success and data_success:
                    results["successful_updates"] += 1
                    results["details"].append(
                        {
                            "symbol": symbol,
                            "status": "success",
                            "info_collected": info_success,
                            "data_collected": data_success,
                        }
                    )
                else:
                    results["failed_updates"] += 1
                    results["details"].append(
                        {
                            "symbol": symbol,
                            "status": "failed",
                            "info_collected": info_success,
                            "data_collected": data_success,
                        }
                    )

                # Small delay to respect rate limits
                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Update failed for {symbol}: {e}")
                results["failed_updates"] += 1
                results["details"].append(
                    {"symbol": symbol, "status": "error", "error": str(e)}
                )

        logger.info(
            f"Full update completed: {results['successful_updates']} successful, {results['failed_updates']} failed"
        )
        return results

    async def get_update_status(self) -> Dict[str, Any]:
        """Get current update status and statistics"""
        try:
            total_symbols = len(self.symbols_to_update)

            # Get data coverage for watchlist symbols
            coverage_info = []
            for symbol in self.symbols_to_update:
                coverage = await self.market_service.get_data_coverage(symbol)
                coverage_info.append(coverage)

            return {
                "watchlist_size": total_symbols,
                "symbols": self.symbols_to_update,
                "coverage": coverage_info,
                "last_check": datetime.utcnow(),
            }

        except Exception as e:
            logger.error(f"Failed to get update status: {e}")
            return {"error": str(e)}

    async def cleanup(self) -> None:
        """Cleanup pipeline resources"""
        await self.market_service.close()
