"""
Crypto data service implementation
암호화폐 데이터 서비스 구현
"""

from typing import List, Literal, Optional, cast, Dict, Any
from datetime import datetime
from decimal import Decimal
import logging

from app.services.market_data.base_service import BaseMarketDataService
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

            if isinstance(response, dict):
                logger.debug(f"Response keys: {response.keys()}")
                # Crypto intraday는 "Time Series Crypto (5min)" 같은 키를 사용
                time_series_key = f"Time Series Crypto ({interval})"
                time_series = response.get(time_series_key, {})

                if not time_series:
                    logger.warning(
                        f"No time series data found in response for {symbol}/{market} intraday ({interval})"
                    )
                    return []

                intraday_prices = []

                for timestamp_str, price_data in time_series.items():
                    if not isinstance(price_data, dict):
                        continue

                    try:
                        # Alpha Vantage intraday는 "YYYY-MM-DD HH:MM:SS" 형식
                        timestamp_obj = datetime.strptime(
                            timestamp_str, "%Y-%m-%d %H:%M:%S"
                        )

                        # Alpha Vantage crypto API는 단순히 "1. open", "2. high" 형식 사용
                        price_dict = {
                            "symbol": symbol,
                            "market": market,
                            "timestamp": timestamp_obj,
                            "interval": interval,
                            "open_market": Decimal(str(price_data.get("1. open", "0"))),
                            "high_market": Decimal(str(price_data.get("2. high", "0"))),
                            "low_market": Decimal(str(price_data.get("3. low", "0"))),
                            "close_market": Decimal(
                                str(price_data.get("4. close", "0"))
                            ),
                            "volume": Decimal(str(price_data.get("5. volume", "0"))),
                            "open_usd": None,
                            "high_usd": None,
                            "low_usd": None,
                            "close_usd": None,
                            "data_quality_score": 95.0,
                            "source": "alpha_vantage",
                        }
                        intraday_prices.append(price_dict)

                    except (ValueError, KeyError) as e:
                        logger.warning(
                            f"Failed to parse intraday price data for {timestamp_str}: {e}"
                        )
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
            logger.debug(
                f"Response keys: {response.keys() if isinstance(response, dict) else 'Not a dict'}"
            )

            if isinstance(response, dict):
                # Alpha Vantage는 "Time Series (Digital Currency Daily)" 키로 데이터를 반환
                time_series_key = "Time Series (Digital Currency Daily)"
                time_series = response.get(time_series_key, {})

                if not time_series:
                    logger.warning(
                        f"No time series data found in response for {symbol}/{market}"
                    )
                    logger.debug(f"Available keys: {list(response.keys())}")
                    return []

                daily_prices = []

                for date_str, price_data in time_series.items():
                    if not isinstance(price_data, dict):
                        continue

                    try:
                        # 첫 번째 항목만 로깅 (디버그용)
                        if len(daily_prices) == 0:
                            logger.debug(
                                f"First daily price_data keys: {list(price_data.keys())}"
                            )
                            logger.debug(f"Sample daily price_data: {price_data}")

                        date_obj = datetime.strptime(date_str, "%Y-%m-%d")

                        # Alpha Vantage crypto API는 단순히 "1. open", "2. high" 형식 사용
                        price_dict = {
                            "symbol": symbol,
                            "market": market,
                            "date": date_obj,
                            "open_market": Decimal(str(price_data.get("1. open", "0"))),
                            "high_market": Decimal(str(price_data.get("2. high", "0"))),
                            "low_market": Decimal(str(price_data.get("3. low", "0"))),
                            "close_market": Decimal(
                                str(price_data.get("4. close", "0"))
                            ),
                            "volume": Decimal(str(price_data.get("5. volume", "0"))),
                            "market_cap": None,  # Crypto API doesn't provide market cap in time series
                            "open_usd": None,
                            "high_usd": None,
                            "low_usd": None,
                            "close_usd": None,
                            "market_cap_usd": (
                                Decimal(str(price_data.get("6. market cap (USD)", "0")))
                                if "6. market cap (USD)" in price_data
                                else None
                            ),
                            "price_change": Decimal("0.0"),
                            "price_change_percent": Decimal("0.0"),
                            "data_quality_score": 95.0,
                            "source": "alpha_vantage",
                        }
                        daily_prices.append(price_dict)

                    except (ValueError, KeyError) as e:
                        logger.warning(
                            f"Failed to parse daily price data for {date_str}: {e}"
                        )
                        continue

                logger.info(
                    f"Fetched {len(daily_prices)} daily prices for {symbol}/{market}"
                )
                return daily_prices

            logger.warning(f"Unexpected response type: {type(response)}")
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

            if isinstance(response, dict):
                logger.debug(f"Response keys: {response.keys()}")
                time_series_key = "Time Series (Digital Currency Weekly)"
                time_series = response.get(time_series_key, {})

                if not time_series:
                    logger.warning(
                        f"No time series data found in response for {symbol}/{market} weekly"
                    )
                    return []

                weekly_prices = []

                for date_str, price_data in time_series.items():
                    if not isinstance(price_data, dict):
                        continue

                    try:
                        # 첫 번째 항목만 로깅 (디버그용)
                        if len(weekly_prices) == 0:
                            logger.debug(
                                f"First weekly price_data keys: {list(price_data.keys())}"
                            )
                            logger.debug(f"Sample weekly price_data: {price_data}")

                        date_obj = datetime.strptime(date_str, "%Y-%m-%d")

                        # Alpha Vantage crypto API는 단순히 "1. open", "2. high" 형식 사용
                        price_dict = {
                            "symbol": symbol,
                            "market": market,
                            "date": date_obj,
                            "open_market": Decimal(str(price_data.get("1. open", "0"))),
                            "high_market": Decimal(str(price_data.get("2. high", "0"))),
                            "low_market": Decimal(str(price_data.get("3. low", "0"))),
                            "close_market": Decimal(
                                str(price_data.get("4. close", "0"))
                            ),
                            "volume": Decimal(str(price_data.get("5. volume", "0"))),
                            "market_cap": None,
                            "open_usd": None,
                            "high_usd": None,
                            "low_usd": None,
                            "close_usd": None,
                            "market_cap_usd": None,
                            "data_quality_score": 95.0,
                            "source": "alpha_vantage",
                        }
                        weekly_prices.append(price_dict)

                    except (ValueError, KeyError) as e:
                        logger.warning(
                            f"Failed to parse weekly price data for {date_str}: {e}"
                        )
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

            if isinstance(response, dict):
                logger.debug(f"Response keys: {response.keys()}")
                time_series_key = "Time Series (Digital Currency Monthly)"
                time_series = response.get(time_series_key, {})

                if not time_series:
                    logger.warning(
                        f"No time series data found in response for {symbol}/{market} monthly"
                    )
                    return []

                monthly_prices = []

                for date_str, price_data in time_series.items():
                    if not isinstance(price_data, dict):
                        continue

                    try:
                        # 첫 번째 항목만 로깅 (디버그용)
                        if len(monthly_prices) == 0:
                            logger.debug(
                                f"First monthly price_data keys: {list(price_data.keys())}"
                            )
                            logger.debug(f"Sample monthly price_data: {price_data}")

                        date_obj = datetime.strptime(date_str, "%Y-%m-%d")

                        # Alpha Vantage crypto API는 단순히 "1. open", "2. high" 형식 사용
                        price_dict = {
                            "symbol": symbol,
                            "market": market,
                            "date": date_obj,
                            "open_market": Decimal(str(price_data.get("1. open", "0"))),
                            "high_market": Decimal(str(price_data.get("2. high", "0"))),
                            "low_market": Decimal(str(price_data.get("3. low", "0"))),
                            "close_market": Decimal(
                                str(price_data.get("4. close", "0"))
                            ),
                            "volume": Decimal(str(price_data.get("5. volume", "0"))),
                            "market_cap": None,
                            "open_usd": None,
                            "high_usd": None,
                            "low_usd": None,
                            "close_usd": None,
                            "market_cap_usd": None,
                            "data_quality_score": 95.0,
                            "source": "alpha_vantage",
                        }
                        monthly_prices.append(price_dict)

                    except (ValueError, KeyError) as e:
                        logger.warning(
                            f"Failed to parse monthly price data for {date_str}: {e}"
                        )
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
