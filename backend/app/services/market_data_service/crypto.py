"""
Crypto data service implementation
암호화폐 데이터 서비스 구현
"""

from typing import List, Literal, Optional, cast, Dict, Any
from datetime import datetime
from decimal import Decimal
import logging

from app.services.market_data_service.base_service import BaseMarketDataService
from app.models.market_data.crypto import (
    CryptoExchangeRate,
    CryptoIntradayPrice,
    CryptoDailyPrice,
    CryptoWeeklyPrice,
    CryptoMonthlyPrice,
)


logger = logging.getLogger(__name__)


class CryptoService(BaseMarketDataService):
    """암호화폐 데이터 서비스"""

    async def refresh_data_from_source(self, **kwargs) -> List[Dict[str, Any]]:
        """
        외부 소스에서 데이터 갱신

        Args:
            **kwargs: symbol, market, data_type 등 갱신에 필요한 매개변수

        Returns:
            갱신된 데이터 리스트
        """
        symbol = kwargs.get("symbol", "BTC")
        market = kwargs.get("market", "USD")
        data_type = kwargs.get("data_type", "daily")

        if data_type == "daily":
            results = await self._fetch_daily_prices_from_alpha_vantage(symbol, market)
        elif data_type == "weekly":
            results = await self._fetch_weekly_prices_from_alpha_vantage(symbol, market)
        elif data_type == "monthly":
            results = await self._fetch_monthly_prices_from_alpha_vantage(
                symbol, market
            )
        else:
            return []

        return results

    async def get_exchange_rate(
        self, from_currency: str, to_currency: str
    ) -> Optional[CryptoExchangeRate]:
        """암호화폐/법정화폐 환율 조회"""
        cache_key = f"crypto_exchange_rate_{from_currency}_{to_currency}"

        async def refresh_callback():
            return await self._fetch_exchange_rate_from_alpha_vantage(
                from_currency, to_currency
            )

        results = await self.get_data_with_unified_cache(
            cache_key=cache_key,
            model_class=CryptoExchangeRate,
            data_type="crypto_exchange_rate",
            symbol=f"{from_currency}_{to_currency}",
            refresh_callback=refresh_callback,
            ttl_hours=1,  # 환율은 1시간 TTL
        )

        return results[0] if results else None

    async def get_bulk_exchange_rates(
        self, crypto_symbols: List[str], target_currency: str = "USD"
    ) -> Dict[str, Optional[CryptoExchangeRate]]:
        """여러 암호화폐의 환율 일괄 조회"""
        results = {}
        for symbol in crypto_symbols:
            try:
                rate = await self.get_exchange_rate(symbol, target_currency)
                results[symbol] = rate
            except Exception as e:
                logger.error(f"Failed to get exchange rate for {symbol}: {e}")
                results[symbol] = None

        return results

    async def get_intraday_prices(
        self,
        symbol: str,
        market: str,
        interval: Literal["1min", "5min", "15min", "30min", "60min"],
        outputsize: str = "compact",
    ) -> List[CryptoIntradayPrice]:
        """암호화폐 인트라데이 가격 조회"""
        cache_key = f"crypto_intraday_{symbol}_{market}_{interval}_{outputsize}"

        async def refresh_callback():
            return await self._fetch_intraday_prices_from_alpha_vantage(
                symbol, market, interval, outputsize
            )

        results = await self.get_data_with_unified_cache(
            cache_key=cache_key,
            model_class=CryptoIntradayPrice,
            data_type="crypto_intraday",
            symbol=f"{symbol}_{market}",
            refresh_callback=refresh_callback,
            ttl_hours=1,  # 인트라데이 데이터는 1시간 TTL
        )

        return cast(List[CryptoIntradayPrice], results)

    async def get_daily_prices(
        self,
        symbol: str,
        market: str = "USD",
    ) -> List[CryptoDailyPrice]:
        """암호화폐 일일 가격 데이터 조회"""
        cache_key = f"crypto_daily_{symbol}_{market}"

        async def refresh_callback():
            return await self._fetch_daily_prices_from_alpha_vantage(symbol, market)

        results = await self.get_data_with_unified_cache(
            cache_key=cache_key,
            model_class=CryptoDailyPrice,
            data_type="crypto_daily",
            symbol=f"{symbol}_{market}",
            refresh_callback=refresh_callback,
            ttl_hours=6,  # 일일 데이터는 6시간 TTL
        )

        return cast(List[CryptoDailyPrice], results)

    async def get_weekly_prices(
        self,
        symbol: str,
        market: str = "USD",
    ) -> List[CryptoWeeklyPrice]:
        """암호화폐 주간 가격 데이터 조회"""
        cache_key = f"crypto_weekly_{symbol}_{market}"

        async def refresh_callback():
            return await self._fetch_weekly_prices_from_alpha_vantage(symbol, market)

        results = await self.get_data_with_unified_cache(
            cache_key=cache_key,
            model_class=CryptoWeeklyPrice,
            data_type="crypto_weekly",
            symbol=f"{symbol}_{market}",
            refresh_callback=refresh_callback,
            ttl_hours=24,  # 주간 데이터는 24시간 TTL
        )

        return cast(List[CryptoWeeklyPrice], results)

    async def get_monthly_prices(
        self,
        symbol: str,
        market: str = "USD",
    ) -> List[CryptoMonthlyPrice]:
        """암호화폐 월간 가격 데이터 조회"""
        cache_key = f"crypto_monthly_{symbol}_{market}"

        async def refresh_callback():
            return await self._fetch_monthly_prices_from_alpha_vantage(symbol, market)

        results = await self.get_data_with_unified_cache(
            cache_key=cache_key,
            model_class=CryptoMonthlyPrice,
            data_type="crypto_monthly",
            symbol=f"{symbol}_{market}",
            refresh_callback=refresh_callback,
            ttl_hours=168,  # 월간 데이터는 1주일(168시간) TTL
        )

        return cast(List[CryptoMonthlyPrice], results)

    # Convenience methods
    async def get_bitcoin_price(
        self,
        market: str = "USD",
        period: Literal["daily", "weekly", "monthly"] = "daily",
    ) -> List[CryptoDailyPrice] | List[CryptoWeeklyPrice] | List[CryptoMonthlyPrice]:
        """비트코인 가격 조회 편의 메서드"""
        if period == "daily":
            return await self.get_daily_prices("BTC", market)
        elif period == "weekly":
            return await self.get_weekly_prices("BTC", market)
        elif period == "monthly":
            return await self.get_monthly_prices("BTC", market)
        else:
            raise ValueError("Period must be 'daily', 'weekly', or 'monthly'")

    async def get_ethereum_price(
        self,
        market: str = "USD",
        period: Literal["daily", "weekly", "monthly"] = "daily",
    ) -> List[CryptoDailyPrice] | List[CryptoWeeklyPrice] | List[CryptoMonthlyPrice]:
        """이더리움 가격 조회 편의 메서드"""
        if period == "daily":
            return await self.get_daily_prices("ETH", market)
        elif period == "weekly":
            return await self.get_weekly_prices("ETH", market)
        elif period == "monthly":
            return await self.get_monthly_prices("ETH", market)
        else:
            raise ValueError("Period must be 'daily', 'weekly', or 'monthly'")

    # Alpha Vantage API 호출 메서드들
    async def _fetch_exchange_rate_from_alpha_vantage(
        self, from_currency: str, to_currency: str
    ) -> List[Dict[str, Any]]:
        """Alpha Vantage에서 환율 데이터 가져오기"""
        try:
            logger.info(f"Alpha Vantage API 호출 시작: {from_currency} -> {to_currency}")

            response = await self.alpha_vantage.crypto.currency_exchange_rate(
                from_currency=from_currency.upper().strip(),
                to_currency=to_currency.upper().strip(),
            )

            logger.info(f"Alpha Vantage response type: {type(response)}")

            # 응답 파싱
            if isinstance(response, dict):
                # "Realtime Currency Exchange Rate" 키 확인
                exchange_rate_data = response.get("Realtime Currency Exchange Rate", {})

                if exchange_rate_data:
                    try:
                        rate_dict = {
                            "from_currency": exchange_rate_data.get(
                                "1. From_Currency Code", from_currency
                            ),
                            "to_currency": exchange_rate_data.get(
                                "3. To_Currency Code", to_currency
                            ),
                            "timestamp": datetime.now(),
                            "exchange_rate": Decimal(
                                str(exchange_rate_data.get("5. Exchange Rate", 0))
                            ),
                            "bid_price": (
                                Decimal(str(exchange_rate_data.get("8. Bid Price", 0)))
                                if "8. Bid Price" in exchange_rate_data
                                else None
                            ),
                            "ask_price": (
                                Decimal(str(exchange_rate_data.get("9. Ask Price", 0)))
                                if "9. Ask Price" in exchange_rate_data
                                else None
                            ),
                            "data_quality_score": 95.0,
                            "source": "alpha_vantage",
                        }

                        logger.info(
                            f"Fetched exchange rate: {rate_dict['exchange_rate']}"
                        )
                        return [rate_dict]

                    except (ValueError, KeyError) as e:
                        logger.warning(f"Failed to parse exchange rate data: {e}")
                        return []

            logger.warning("No exchange rate data found in response")
            return []

        except Exception as e:
            import traceback

            logger.error(f"Failed to fetch exchange rate from Alpha Vantage: {e}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []

    async def _fetch_intraday_prices_from_alpha_vantage(
        self,
        symbol: str,
        market: str,
        interval: Literal["1min", "5min", "15min", "30min", "60min"],
        outputsize: str = "compact",
    ) -> List[Dict[str, Any]]:
        """Alpha Vantage에서 인트라데이 가격 데이터 가져오기"""
        try:
            logger.info(
                f"Alpha Vantage API 호출 시작: {symbol}/{market}, interval={interval}"
            )

            response = await self.alpha_vantage.crypto.crypto_intraday(
                symbol=symbol.upper().strip(),
                market=market.upper().strip(),
                interval=interval,
                outputsize=cast(Literal["compact", "full"], outputsize),
            )

            logger.info(f"Alpha Vantage response type: {type(response)}")

            if isinstance(response, list):
                intraday_prices = []

                for item in response:
                    if not isinstance(item, dict):
                        continue

                    try:
                        timestamp_value = item.get("timestamp") or item.get("time")
                        if isinstance(timestamp_value, str):
                            timestamp_obj = datetime.fromisoformat(timestamp_value)
                        elif isinstance(timestamp_value, datetime):
                            timestamp_obj = timestamp_value
                        else:
                            continue

                        price_dict = {
                            "symbol": symbol,
                            "market": market,
                            "timestamp": timestamp_obj,
                            "interval": interval,
                            "open_market": Decimal(
                                str(item.get("open") or item.get("1. open", 0))
                            ),
                            "high_market": Decimal(
                                str(item.get("high") or item.get("2. high", 0))
                            ),
                            "low_market": Decimal(
                                str(item.get("low") or item.get("3. low", 0))
                            ),
                            "close_market": Decimal(
                                str(item.get("close") or item.get("4. close", 0))
                            ),
                            "volume": Decimal(
                                str(item.get("volume") or item.get("5. volume", 0))
                            ),
                            "open_usd": (
                                Decimal(str(item.get("open_usd", 0)))
                                if "open_usd" in item
                                else None
                            ),
                            "high_usd": (
                                Decimal(str(item.get("high_usd", 0)))
                                if "high_usd" in item
                                else None
                            ),
                            "low_usd": (
                                Decimal(str(item.get("low_usd", 0)))
                                if "low_usd" in item
                                else None
                            ),
                            "close_usd": (
                                Decimal(str(item.get("close_usd", 0)))
                                if "close_usd" in item
                                else None
                            ),
                            "data_quality_score": 95.0,
                            "source": "alpha_vantage",
                        }
                        intraday_prices.append(price_dict)

                    except (ValueError, KeyError) as e:
                        logger.warning(f"Failed to parse intraday price data: {e}")
                        continue

                logger.info(
                    f"Fetched {len(intraday_prices)} intraday prices for {symbol}/{market}"
                )
                return intraday_prices

            return []

        except Exception as e:
            import traceback

            logger.error(f"Failed to fetch intraday prices from Alpha Vantage: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []

    async def _fetch_daily_prices_from_alpha_vantage(
        self, symbol: str, market: str
    ) -> List[Dict[str, Any]]:
        """Alpha Vantage에서 일일 가격 데이터 가져오기"""
        try:
            logger.info(f"Alpha Vantage API 호출 시작: {symbol}/{market} daily")

            response = await self.alpha_vantage.crypto.digital_currency_daily(
                symbol=symbol.upper().strip(), market=market.upper().strip()
            )

            logger.info(f"Alpha Vantage response type: {type(response)}")

            if isinstance(response, list):
                daily_prices = []

                for item in response:
                    if not isinstance(item, dict):
                        continue

                    try:
                        date_value = item.get("date")
                        if isinstance(date_value, str):
                            date_obj = datetime.strptime(date_value, "%Y-%m-%d")
                        elif isinstance(date_value, datetime):
                            date_obj = date_value
                        else:
                            continue

                        price_dict = {
                            "symbol": symbol,
                            "market": market,
                            "date": date_obj,
                            "open_market": Decimal(
                                str(item.get(f"1a. open ({market})", 0))
                            ),
                            "high_market": Decimal(
                                str(item.get(f"2a. high ({market})", 0))
                            ),
                            "low_market": Decimal(
                                str(item.get(f"3a. low ({market})", 0))
                            ),
                            "close_market": Decimal(
                                str(item.get(f"4a. close ({market})", 0))
                            ),
                            "volume": Decimal(str(item.get("5. volume", 0))),
                            "market_cap": (
                                Decimal(str(item.get(f"6. market cap ({market})", 0)))
                                if f"6. market cap ({market})" in item
                                else None
                            ),
                            "open_usd": (
                                Decimal(str(item.get("1b. open (USD)", 0)))
                                if "1b. open (USD)" in item
                                else None
                            ),
                            "high_usd": (
                                Decimal(str(item.get("2b. high (USD)", 0)))
                                if "2b. high (USD)" in item
                                else None
                            ),
                            "low_usd": (
                                Decimal(str(item.get("3b. low (USD)", 0)))
                                if "3b. low (USD)" in item
                                else None
                            ),
                            "close_usd": (
                                Decimal(str(item.get("4b. close (USD)", 0)))
                                if "4b. close (USD)" in item
                                else None
                            ),
                            "market_cap_usd": (
                                Decimal(str(item.get("6. market cap (USD)", 0)))
                                if "6. market cap (USD)" in item
                                else None
                            ),
                            "price_change": Decimal("0.0"),
                            "price_change_percent": Decimal("0.0"),
                            "data_quality_score": 95.0,
                            "source": "alpha_vantage",
                        }
                        daily_prices.append(price_dict)

                    except (ValueError, KeyError) as e:
                        logger.warning(f"Failed to parse daily price data: {e}")
                        continue

                logger.info(
                    f"Fetched {len(daily_prices)} daily prices for {symbol}/{market}"
                )
                return daily_prices

            return []

        except Exception as e:
            import traceback

            logger.error(f"Failed to fetch daily prices from Alpha Vantage: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []

    async def _fetch_weekly_prices_from_alpha_vantage(
        self, symbol: str, market: str
    ) -> List[Dict[str, Any]]:
        """Alpha Vantage에서 주간 가격 데이터 가져오기"""
        try:
            logger.info(f"Alpha Vantage API 호출 시작: {symbol}/{market} weekly")

            response = await self.alpha_vantage.crypto.digital_currency_weekly(
                symbol=symbol.upper().strip(), market=market.upper().strip()
            )

            logger.info(f"Alpha Vantage response type: {type(response)}")

            if isinstance(response, list):
                weekly_prices = []

                for item in response:
                    if not isinstance(item, dict):
                        continue

                    try:
                        date_value = item.get("date")
                        if isinstance(date_value, str):
                            date_obj = datetime.strptime(date_value, "%Y-%m-%d")
                        elif isinstance(date_value, datetime):
                            date_obj = date_value
                        else:
                            continue

                        price_dict = {
                            "symbol": symbol,
                            "market": market,
                            "date": date_obj,
                            "open_market": Decimal(
                                str(item.get(f"1a. open ({market})", 0))
                            ),
                            "high_market": Decimal(
                                str(item.get(f"2a. high ({market})", 0))
                            ),
                            "low_market": Decimal(
                                str(item.get(f"3a. low ({market})", 0))
                            ),
                            "close_market": Decimal(
                                str(item.get(f"4a. close ({market})", 0))
                            ),
                            "volume": Decimal(str(item.get("5. volume", 0))),
                            "market_cap": (
                                Decimal(str(item.get(f"6. market cap ({market})", 0)))
                                if f"6. market cap ({market})" in item
                                else None
                            ),
                            "open_usd": (
                                Decimal(str(item.get("1b. open (USD)", 0)))
                                if "1b. open (USD)" in item
                                else None
                            ),
                            "high_usd": (
                                Decimal(str(item.get("2b. high (USD)", 0)))
                                if "2b. high (USD)" in item
                                else None
                            ),
                            "low_usd": (
                                Decimal(str(item.get("3b. low (USD)", 0)))
                                if "3b. low (USD)" in item
                                else None
                            ),
                            "close_usd": (
                                Decimal(str(item.get("4b. close (USD)", 0)))
                                if "4b. close (USD)" in item
                                else None
                            ),
                            "market_cap_usd": (
                                Decimal(str(item.get("6. market cap (USD)", 0)))
                                if "6. market cap (USD)" in item
                                else None
                            ),
                            "data_quality_score": 95.0,
                            "source": "alpha_vantage",
                        }
                        weekly_prices.append(price_dict)

                    except (ValueError, KeyError) as e:
                        logger.warning(f"Failed to parse weekly price data: {e}")
                        continue

                logger.info(
                    f"Fetched {len(weekly_prices)} weekly prices for {symbol}/{market}"
                )
                return weekly_prices

            return []

        except Exception as e:
            import traceback

            logger.error(f"Failed to fetch weekly prices from Alpha Vantage: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []

    async def _fetch_monthly_prices_from_alpha_vantage(
        self, symbol: str, market: str
    ) -> List[Dict[str, Any]]:
        """Alpha Vantage에서 월간 가격 데이터 가져오기"""
        try:
            logger.info(f"Alpha Vantage API 호출 시작: {symbol}/{market} monthly")

            response = await self.alpha_vantage.crypto.digital_currency_monthly(
                symbol=symbol.upper().strip(), market=market.upper().strip()
            )

            logger.info(f"Alpha Vantage response type: {type(response)}")

            if isinstance(response, list):
                monthly_prices = []

                for item in response:
                    if not isinstance(item, dict):
                        continue

                    try:
                        date_value = item.get("date")
                        if isinstance(date_value, str):
                            date_obj = datetime.strptime(date_value, "%Y-%m-%d")
                        elif isinstance(date_value, datetime):
                            date_obj = date_value
                        else:
                            continue

                        price_dict = {
                            "symbol": symbol,
                            "market": market,
                            "date": date_obj,
                            "open_market": Decimal(
                                str(item.get(f"1a. open ({market})", 0))
                            ),
                            "high_market": Decimal(
                                str(item.get(f"2a. high ({market})", 0))
                            ),
                            "low_market": Decimal(
                                str(item.get(f"3a. low ({market})", 0))
                            ),
                            "close_market": Decimal(
                                str(item.get(f"4a. close ({market})", 0))
                            ),
                            "volume": Decimal(str(item.get("5. volume", 0))),
                            "market_cap": (
                                Decimal(str(item.get(f"6. market cap ({market})", 0)))
                                if f"6. market cap ({market})" in item
                                else None
                            ),
                            "open_usd": (
                                Decimal(str(item.get("1b. open (USD)", 0)))
                                if "1b. open (USD)" in item
                                else None
                            ),
                            "high_usd": (
                                Decimal(str(item.get("2b. high (USD)", 0)))
                                if "2b. high (USD)" in item
                                else None
                            ),
                            "low_usd": (
                                Decimal(str(item.get("3b. low (USD)", 0)))
                                if "3b. low (USD)" in item
                                else None
                            ),
                            "close_usd": (
                                Decimal(str(item.get("4b. close (USD)", 0)))
                                if "4b. close (USD)" in item
                                else None
                            ),
                            "market_cap_usd": (
                                Decimal(str(item.get("6. market cap (USD)", 0)))
                                if "6. market cap (USD)" in item
                                else None
                            ),
                            "data_quality_score": 95.0,
                            "source": "alpha_vantage",
                        }
                        monthly_prices.append(price_dict)

                    except (ValueError, KeyError) as e:
                        logger.warning(f"Failed to parse monthly price data: {e}")
                        continue

                logger.info(
                    f"Fetched {len(monthly_prices)} monthly prices for {symbol}/{market}"
                )
                return monthly_prices

            return []

        except Exception as e:
            import traceback

            logger.error(f"Failed to fetch monthly prices from Alpha Vantage: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []
