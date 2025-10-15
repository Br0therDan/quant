"""
Stock data service implementation
주식 데이터 서비스 구현
"""

from typing import List, Literal, Optional, cast
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import logging

from app.services.market_data.base_service import (
    BaseMarketDataService,
    DataQualityValidator,
)
from app.services.database_manager import DatabaseManager
from app.services.monitoring.data_quality_sentinel import DataQualitySentinel
from app.models.market_data.stock import (
    DailyPrice,
    WeeklyPrice,
    MonthlyPrice,
    StockDataCoverage,
)
from app.schemas.market_data.stock import QuoteData


logger = logging.getLogger(__name__)


class StockService(BaseMarketDataService):
    """주식 데이터 서비스"""

    def __init__(
        self,
        database_manager: Optional[DatabaseManager] = None,
        data_quality_sentinel: Optional[DataQualitySentinel] = None,
    ) -> None:
        super().__init__(database_manager)
        self.data_quality_sentinel = data_quality_sentinel

    async def get_daily_prices(
        self,
        symbol: str,
        outputsize: str = "compact",
        adjusted: bool = True,
    ) -> List[DailyPrice]:
        """
        일일 주가 데이터 조회 (Coverage 기반 캐싱)

        Args:
            symbol: 종목 심볼
            outputsize: 'compact' (최근 100개) 또는 'full' (전체 데이터)
            adjusted: True면 adjusted prices, False면 raw prices
        """
        # Coverage 확인
        coverage = await self._get_or_create_coverage(symbol, "daily")

        # Full update가 필요한지 확인 (최초 또는 7일 이상 경과)
        needs_full_update = (
            coverage.last_full_update is None
            or (datetime.now(timezone.utc) - coverage.last_full_update).days >= 7
        )

        # MongoDB에서 기존 데이터 조회
        existing_prices = (
            await DailyPrice.find({"symbol": symbol}).sort("-date").to_list()
        )

        # 데이터가 없거나 Full update가 필요한 경우만 API 호출
        if not existing_prices or needs_full_update:
            # Full update: Alpha Vantage에서 전체 데이터 가져와서 MongoDB에 저장
            logger.info(
                f"🔄 Performing full update for {symbol} daily prices (existing: {len(existing_prices)}, needs_full: {needs_full_update})"
            )
            prices = await self._fetch_and_store_daily_prices(
                symbol, adjusted=adjusted, is_full=True
            )

            # Coverage 업데이트
            if prices:
                await self._update_coverage(
                    coverage=coverage, data_records=prices, update_type="full"
                )
            return prices or []
        else:
            # 캐시된 데이터 사용 (Alpha Vantage API 호출 없음)
            logger.info(
                f"✅ Using cached data for {symbol} daily prices ({len(existing_prices)} records, last_update: {coverage.last_full_update})"
            )
            return existing_prices

    async def get_weekly_prices(
        self,
        symbol: str,
        outputsize: str = "full",
        adjusted: bool = True,
    ) -> List[WeeklyPrice]:
        """
        주간 주가 데이터 조회 (Coverage 기반 캐싱)

        Weekly는 항상 full로 요청하여 MongoDB에 저장
        """
        # Coverage 확인
        coverage = await self._get_or_create_coverage(symbol, "weekly")

        # Full update가 필요한지 확인 (최초 또는 30일 이상 경과)
        needs_full_update = (
            coverage.last_full_update is None
            or (datetime.now(timezone.utc) - coverage.last_full_update).days >= 30
        )

        if needs_full_update:
            logger.info(f"🔄 Performing full update for {symbol} weekly prices")
            prices = await self._fetch_and_store_weekly_prices(
                symbol, adjusted=adjusted
            )

            if prices:
                await self._update_coverage(coverage, prices, "full")
        else:
            # MongoDB에서 조회
            logger.info(
                f"✅ Using cached data for {symbol} weekly prices (last_update: {coverage.last_full_update})"
            )
            prices = await WeeklyPrice.find({"symbol": symbol}).sort("-date").to_list()

        return prices or []

    async def get_monthly_prices(
        self,
        symbol: str,
        outputsize: str = "full",
        adjusted: bool = True,
    ) -> List[MonthlyPrice]:
        """
        월간 주가 데이터 조회 (Coverage 기반 캐싱)

        Monthly는 항상 full로 요청하여 MongoDB에 저장
        """
        # Coverage 확인
        coverage = await self._get_or_create_coverage(symbol, "monthly")

        # Full update가 필요한지 확인 (최초 또는 60일 이상 경과)
        needs_full_update = (
            coverage.last_full_update is None
            or (datetime.now(timezone.utc) - coverage.last_full_update).days >= 60
        )

        if needs_full_update:
            logger.info(f"🔄 Performing full update for {symbol} monthly prices")
            prices = await self._fetch_and_store_monthly_prices(
                symbol, adjusted=adjusted
            )

            if prices:
                await self._update_coverage(coverage, prices, "full")
        else:
            # MongoDB에서 조회
            logger.info(
                f"✅ Using cached data for {symbol} monthly prices (last_update: {coverage.last_full_update})"
            )
            prices = await MonthlyPrice.find({"symbol": symbol}).sort("-date").to_list()

        return prices or []

    # Alpha Vantage API 호출 메서드들
    async def _fetch_daily_prices_from_alpha_vantage(
        self, symbol: str, outputsize: str = "compact"
    ) -> List[DailyPrice]:
        """Alpha Vantage에서 일일 주가 데이터 가져오기"""
        try:
            # 심볼 유효성 검사
            if not symbol or not symbol.strip():
                raise ValueError("유효한 심볼이 필요합니다")

            # mysingle_quant의 AlphaVantageClient 사용
            if outputsize not in ["compact", "full"]:
                outputsize = "compact"

            logger.info(f"Alpha Vantage API 호출 시작: {symbol}, outputsize={outputsize}")

            response = await self.alpha_vantage.stock.daily_adjusted(
                symbol=symbol.upper().strip(),
                outputsize=outputsize,  # type: ignore
            )

            # 응답 데이터 구조 로깅
            logger.info(f"Alpha Vantage response type: {type(response)}")

            # mysingle_quant 클라이언트가 이미 파싱된 리스트를 반환하는 경우
            if isinstance(response, list):
                logger.info(f"Response is list with {len(response)} items")
                daily_prices = []

                for item in response:
                    if not isinstance(item, dict):
                        continue

                    try:
                        # 데이터 품질 확인 (간단한 검증)
                        required_fields = [
                            "date",
                            "open",
                            "high",
                            "low",
                            "close",
                            "volume",
                        ]
                        if not all(field in item for field in required_fields):
                            logger.warning(
                                f"Missing required fields in item: {item.keys()}"
                            )
                            continue

                        # date 처리 - 문자열 또는 datetime 객체 모두 처리
                        date_value = item["date"]
                        if isinstance(date_value, str):
                            date_obj = datetime.strptime(date_value, "%Y-%m-%d")
                        elif isinstance(date_value, datetime):
                            date_obj = date_value
                        else:
                            logger.warning(f"Unexpected date type: {type(date_value)}")
                            continue

                        # dict로 저장 (Beanie 모델 초기화 문제 회피)
                        daily_price_dict = {
                            "symbol": symbol,
                            "date": date_obj,
                            "open": Decimal(str(item["open"])),
                            "high": Decimal(str(item["high"])),
                            "low": Decimal(str(item["low"])),
                            "close": Decimal(str(item["close"])),
                            "volume": int(item["volume"]),
                            "adjusted_close": Decimal(
                                str(item.get("adjusted_close", item["close"]))
                            ),
                            "dividend_amount": Decimal(
                                str(item.get("dividend_amount", 0))
                            ),
                            "split_coefficient": Decimal(
                                str(item.get("split_coefficient", 1))
                            ),
                            "data_quality_score": 95.0,
                            "source": "alpha_vantage",
                            "price_change": Decimal("0.0"),
                            "price_change_percent": Decimal("0.0"),
                        }
                        daily_prices.append(daily_price_dict)

                    except (ValueError, KeyError) as e:
                        logger.warning(f"Failed to parse daily price data: {e}")
                        continue

                logger.info(f"Fetched {len(daily_prices)} daily prices for {symbol}")
                return daily_prices

            # 기존 딕셔너리 구조 처리 (fallback)
            elif isinstance(response, dict):
                logger.info(f"Response is dict with keys: {list(response.keys())}")

                # Time Series 키를 확인
                available_keys = list(response.keys())
                time_series_key = None
                for key in available_keys:
                    if "time series" in key.lower() or "daily" in key.lower():
                        time_series_key = key
                        break

                if not time_series_key:
                    logger.warning(
                        f"No time series data found for {symbol}. Available keys: {available_keys}"
                    )
                    return []

                time_series = response.get(time_series_key, {})
                if not isinstance(time_series, dict):
                    logger.warning(
                        f"Invalid time series data type: {type(time_series)}"
                    )
                    return []

                daily_prices = []

                # 타입 캐스팅을 통해 타입 체크 우회
                time_series_dict = cast(dict, time_series)
                for date_str, price_data in time_series_dict.items():
                    try:
                        # 데이터 품질 확인
                        quality_score = DataQualityValidator.validate_price_data(
                            price_data
                        )

                        # date 객체를 datetime으로 변환
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d")

                        daily_price = DailyPrice(
                            symbol=symbol,
                            date=date_obj,
                            open=Decimal(str(price_data["1. open"])),
                            high=Decimal(str(price_data["2. high"])),
                            low=Decimal(str(price_data["3. low"])),
                            close=Decimal(str(price_data["4. close"])),
                            volume=int(price_data["6. volume"]),
                            adjusted_close=Decimal(
                                str(price_data["5. adjusted close"])
                            ),
                            dividend_amount=Decimal(
                                str(price_data.get("7. dividend amount", 0))
                            ),
                            split_coefficient=Decimal(
                                str(price_data.get("8. split coefficient", 1))
                            ),
                            data_quality_score=quality_score.overall_score,
                            source="alpha_vantage",
                            price_change=Decimal("0.0"),
                            price_change_percent=Decimal("0.0"),
                            # Provide default anomaly-related fields required by the model
                            iso_anomaly_score=0.0,
                            prophet_anomaly_score=0.0,
                            volume_z_score=0.0,
                            anomaly_severity=None,
                            anomaly_reasons=[],
                        )
                        daily_prices.append(daily_price)
                    except (ValueError, KeyError) as e:
                        logger.warning(
                            f"Failed to parse daily price data for {date_str}: {e}"
                        )
                        continue

                logger.info(f"Fetched {len(daily_prices)} daily prices for {symbol}")
                return daily_prices

            else:
                logger.warning(
                    f"Unexpected response type for {symbol}: {type(response)}"
                )
                return []

        except Exception as e:
            import traceback

            logger.error(f"Failed to fetch daily prices from Alpha Vantage: {e}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []

    async def _fetch_weekly_prices_from_alpha_vantage(
        self, symbol: str, outputsize: str = "full"
    ) -> List[WeeklyPrice]:
        """Alpha Vantage에서 주간 주가 데이터 가져오기"""
        try:
            if outputsize not in ["compact", "full"]:
                outputsize = "full"

            response = await self.alpha_vantage.stock.weekly_adjusted(
                symbol=symbol, outputsize=cast(Literal["compact", "full"], outputsize)
            )

            if isinstance(response, list):
                logger.info(f"Response is list with {len(response)} items")
                weekly_prices = []

                for item in response:
                    if not isinstance(item, dict):
                        continue

                    try:
                        required_fields = [
                            "date",
                            "open",
                            "high",
                            "low",
                            "close",
                            "volume",
                        ]
                        if not all(field in item for field in required_fields):
                            continue

                        # date 처리
                        date_value = item["date"]
                        if isinstance(date_value, str):
                            date_obj = datetime.strptime(date_value, "%Y-%m-%d")
                        elif isinstance(date_value, datetime):
                            date_obj = date_value
                        else:
                            continue

                        weekly_price = WeeklyPrice(
                            symbol=symbol,
                            date=date_obj,
                            open=Decimal(str(item["open"])),
                            high=Decimal(str(item["high"])),
                            low=Decimal(str(item["low"])),
                            close=Decimal(str(item["close"])),
                            volume=int(item["volume"]),
                            adjusted_close=Decimal(
                                str(item.get("adjusted_close", item["close"]))
                            ),
                            dividend_amount=Decimal(
                                str(item.get("dividend_amount", 0))
                            ),
                            split_coefficient=Decimal(
                                str(item.get("split_coefficient", 1))
                            ),
                            data_quality_score=95.0,
                            source="alpha_vantage",
                        )
                        weekly_prices.append(weekly_price)

                    except (ValueError, KeyError) as e:
                        logger.warning(f"Failed to parse weekly price data: {e}")
                        continue

                logger.info(f"Fetched {len(weekly_prices)} weekly prices for {symbol}")
                return weekly_prices

            else:
                logger.warning(
                    f"Unexpected response type for {symbol}: {type(response)}"
                )
                return []

        except Exception as e:
            logger.error(f"Failed to fetch weekly prices from Alpha Vantage: {e}")
            return []

    async def _fetch_monthly_prices_from_alpha_vantage(
        self, symbol: str, outputsize: str = "full"
    ) -> List[MonthlyPrice]:
        """Alpha Vantage에서 월간 주가 데이터 가져오기"""
        try:
            if outputsize not in ["compact", "full"]:
                outputsize = "full"

            response = await self.alpha_vantage.stock.monthly_adjusted(
                symbol=symbol, outputsize=cast(Literal["compact", "full"], outputsize)
            )

            if isinstance(response, list):
                logger.info(f"Response is list with {len(response)} items")
                monthly_prices = []

                for item in response:
                    if not isinstance(item, dict):
                        continue

                    try:
                        required_fields = [
                            "date",
                            "open",
                            "high",
                            "low",
                            "close",
                            "volume",
                        ]
                        if not all(field in item for field in required_fields):
                            continue

                        # date 처리
                        date_value = item["date"]
                        if isinstance(date_value, str):
                            date_obj = datetime.strptime(date_value, "%Y-%m-%d")
                        elif isinstance(date_value, datetime):
                            date_obj = date_value
                        else:
                            continue

                        monthly_price = MonthlyPrice(
                            symbol=symbol,
                            date=date_obj,
                            open=Decimal(str(item["open"])),
                            high=Decimal(str(item["high"])),
                            low=Decimal(str(item["low"])),
                            close=Decimal(str(item["close"])),
                            volume=int(item["volume"]),
                            adjusted_close=Decimal(
                                str(item.get("adjusted_close", item["close"]))
                            ),
                            dividend_amount=Decimal(
                                str(item.get("dividend_amount", 0))
                            ),
                            split_coefficient=Decimal(
                                str(item.get("split_coefficient", 1))
                            ),
                            data_quality_score=95.0,
                            source="alpha_vantage",
                        )
                        monthly_prices.append(monthly_price)

                    except (ValueError, KeyError) as e:
                        logger.warning(f"Failed to parse monthly price data: {e}")
                        continue

                logger.info(
                    f"Fetched {len(monthly_prices)} monthly prices for {symbol}"
                )
                return monthly_prices

            else:
                logger.warning(
                    f"Unexpected response type for {symbol}: {type(response)}"
                )
                return []

        except Exception as e:
            logger.error(f"Failed to fetch monthly prices from Alpha Vantage: {e}")
            return []

    async def refresh_data_from_source(self, **kwargs) -> List[DailyPrice]:
        """베이스 클래스의 추상 메서드 구현"""
        # 이 메서드는 더 이상 직접 사용되지 않으므로 빈 구현
        return []

    # BaseMarketDataService 추상 메서드 구현
    async def _fetch_from_source(self, **kwargs):
        """Alpha Vantage에서 주식 데이터 가져오기"""
        try:
            method = kwargs.get("method", "daily")
            symbol = kwargs.get("symbol")

            if not symbol:
                raise ValueError("Symbol is required for stock data")

            if method == "daily":
                outputsize = kwargs.get("outputsize", "compact")
                return await self.alpha_vantage.stock.daily_adjusted(
                    symbol=symbol, outputsize=outputsize
                )
            elif method == "quote":
                return await self.alpha_vantage.stock.quote(symbol=symbol)
            elif method == "intraday":
                interval = kwargs.get("interval", "5min")
                outputsize = kwargs.get("outputsize", "compact")
                return await self.alpha_vantage.stock.intraday(
                    symbol=symbol, interval=interval, outputsize=outputsize
                )
            else:
                raise ValueError(f"Unknown stock method: {method}")

        except Exception as e:
            logger.error(f"Error fetching stock data from source: {e}")
            raise

    async def _save_to_cache(self, data, **kwargs) -> bool:
        """주식 데이터를 캐시에 저장"""
        try:
            cache_key = kwargs.get("cache_key", "stock_data")
            method = kwargs.get("method", "daily")
            symbol = kwargs.get("symbol", "UNKNOWN")

            # 데이터를 DailyPrice 모델로 변환
            if isinstance(data, dict) and method == "daily":
                try:
                    # Alpha Vantage 응답에서 Time Series 추출
                    time_series = data.get("Time Series (Daily)", {})
                    if not time_series:
                        logger.warning(f"No time series data found for {symbol}")
                        return True

                    daily_prices = []
                    for date_str, price_data in time_series.items():
                        try:
                            # date 객체를 datetime으로 변환
                            date_obj = datetime.strptime(date_str, "%Y-%m-%d")

                            daily_price = DailyPrice(
                                symbol=symbol,
                                date=date_obj,
                                open=Decimal(str(price_data["1. open"])),
                                high=Decimal(str(price_data["2. high"])),
                                low=Decimal(str(price_data["3. low"])),
                                close=Decimal(str(price_data["4. close"])),
                                volume=int(price_data["6. volume"]),
                                adjusted_close=Decimal(
                                    str(price_data["5. adjusted close"])
                                ),
                                dividend_amount=Decimal(
                                    str(price_data.get("7. dividend amount", 0))
                                ),
                                split_coefficient=Decimal(
                                    str(price_data.get("8. split coefficient", 1))
                                ),
                                data_quality_score=95.0,  # 기본 품질 점수
                                source="alpha_vantage",
                                price_change=Decimal("0.0"),
                                price_change_percent=Decimal("0.0"),
                                # Anomaly 필드 추가
                                iso_anomaly_score=0.0,
                                prophet_anomaly_score=0.0,
                                volume_z_score=0.0,
                                anomaly_severity=None,
                                anomaly_reasons=[],
                            )
                            daily_prices.append(daily_price)
                        except (ValueError, KeyError) as parse_error:
                            logger.warning(
                                f"Failed to parse price data for {date_str}: {parse_error}"
                            )
                            continue

                    if daily_prices:
                        # DuckDB 캐시에 저장
                        success = await self._store_to_duckdb_cache(
                            cache_key=cache_key,
                            data=daily_prices,
                            table_name="stock_cache",
                        )

                        if success:
                            logger.info(
                                f"Stock data cached successfully: {cache_key} ({len(daily_prices)} items)"
                            )
                        return success

                except Exception as model_error:
                    logger.warning(f"Failed to create DailyPrice models: {model_error}")
                    # 원본 데이터를 딕셔너리로 저장
                    if self._db_manager:
                        return self._db_manager.store_cache_data(
                            cache_key=cache_key, data=[data], table_name="stock_cache"
                        )

            logger.info(f"No valid stock data to cache for: {cache_key}")
            return True

        except Exception as e:
            logger.error(f"Error saving stock data to cache: {e}")
            return False

    async def _get_from_cache(self, **kwargs):
        """캐시에서 주식 데이터 조회"""
        try:
            cache_key = kwargs.get("cache_key", "stock_data")

            # DuckDB 캐시에서 데이터 조회
            cached_data = await self._get_from_duckdb_cache(
                cache_key=cache_key,
                start_date=kwargs.get("start_date"),
                end_date=kwargs.get("end_date"),
                ignore_ttl=kwargs.get("ignore_ttl", False),
            )

            if cached_data:
                logger.info(f"Stock cache hit: {cache_key} ({len(cached_data)} items)")
                return cached_data
            else:
                logger.debug(f"Stock cache miss: {cache_key}")
                return None

        except Exception as e:
            logger.error(f"Error getting stock data from cache: {e}")
            return None

    async def get_real_time_quote(
        self, symbol: str, force_refresh: bool = False
    ) -> QuoteData:
        """실시간 주식 호가 조회 (Alpha Vantage GLOBAL_QUOTE)

        Args:
            symbol: 주식 심볼
            force_refresh: True인 경우 캐시 무시하고 실시간 데이터 조회

        Returns:
            QuoteData: 실시간 호가 정보 객체
        """
        if force_refresh:
            # 실시간 데이터가 필요한 경우 캐시 무시
            logger.info(f"Force refresh requested for {symbol} quote")
            return await self._fetch_quote_from_alpha_vantage(symbol)

        # 매우 짧은 TTL로 캐시 적용 (2분)
        cache_key = f"realtime_quote_{symbol.upper()}"

        async def refresh_callback():
            return [await self._fetch_quote_from_alpha_vantage(symbol)]

        try:
            # 실시간 데이터는 리스트 형태로 캐시 저장
            results = await self.get_data_with_unified_cache(
                cache_key=cache_key,
                model_class=dict,  # 딕셔너리 형태로 저장
                data_type="realtime_quote",
                symbol=symbol,
                refresh_callback=refresh_callback,
                ttl_hours=1,  # 1시간 (실시간 데이터이지만 API 절약을 위해 적절한 TTL)
            )

            # 첫 번째 요소 반환 (단일 호가 데이터)
            if results and len(results) > 0:
                quote_dict = results[0]
                # dict를 QuoteData로 변환
                return self._dict_to_quote_data(quote_dict)
            else:
                # 캐시에서 가져오지 못한 경우 직접 API 호출
                return await self._fetch_quote_from_alpha_vantage(symbol)

        except Exception as e:
            logger.warning(f"Error with cached quote for {symbol}: {e}")
            # 캐시 오류 시 직접 API 호출로 fallback
            return await self._fetch_quote_from_alpha_vantage(symbol)

    async def _fetch_quote_from_alpha_vantage(self, symbol: str) -> QuoteData:
        """Alpha Vantage에서 실시간 호가 데이터 가져오기"""
        try:
            logger.info(f"Fetching real-time quote for {symbol} from Alpha Vantage")
            response = await self.alpha_vantage.stock.quote(symbol=symbol)

            if isinstance(response, dict):
                logger.info(
                    f"Successfully fetched quote for {symbol}: price={response.get('price', 'N/A')}"
                )
                return self._dict_to_quote_data(response)
            else:
                logger.warning(
                    f"Unexpected quote response type for {symbol}: {type(response)}"
                )
                raise ValueError(f"Invalid quote response for {symbol}")

        except Exception as e:
            logger.error(f"Failed to fetch quote from Alpha Vantage for {symbol}: {e}")
            raise

    def _dict_to_quote_data(self, quote_dict: dict) -> QuoteData:
        """딕셔너리를 QuoteData 객체로 변환"""
        change_percent_str = str(quote_dict.get("change_percent", "0"))
        change_percent_value = change_percent_str.rstrip("%")

        # 타임스탬프 처리
        timestamp = datetime.now()
        if "latest_trading_day" in quote_dict:
            try:
                timestamp = datetime.fromisoformat(
                    str(quote_dict["latest_trading_day"])
                )
            except (ValueError, TypeError):
                pass

        return QuoteData(
            symbol=str(quote_dict.get("symbol", "")).upper(),
            timestamp=timestamp,
            price=Decimal(str(quote_dict.get("price", 0))),
            change=(
                Decimal(str(quote_dict.get("change", 0)))
                if quote_dict.get("change")
                else None
            ),
            change_percent=(
                Decimal(str(change_percent_value)) if change_percent_value else None
            ),
            previous_close=(
                Decimal(str(quote_dict.get("previous_close", 0)))
                if quote_dict.get("previous_close")
                else None
            ),
            open_price=(
                Decimal(str(quote_dict.get("open", 0)))
                if quote_dict.get("open")
                else None
            ),
            high_price=(
                Decimal(str(quote_dict.get("high", 0)))
                if quote_dict.get("high")
                else None
            ),
            low_price=(
                Decimal(str(quote_dict.get("low", 0)))
                if quote_dict.get("low")
                else None
            ),
            volume=(
                int(quote_dict.get("volume", 0)) if quote_dict.get("volume") else None
            ),
            # Alpha Vantage GLOBAL_QUOTE는 호가 정보를 제공하지 않으므로 None으로 설정
            bid_price=None,
            ask_price=None,
            bid_size=None,
            ask_size=None,
        )

    async def get_intraday_data(
        self,
        symbol: str,
        interval: Literal["1min", "5min", "15min", "30min", "60min"] = "15min",
        adjusted: bool = False,
        extended_hours: bool = False,
        outputsize: Literal["compact", "full"] | None = "full",
        month: Optional[str] = None,
    ) -> List[DailyPrice]:
        """실시간/인트라데이 데이터 조회 (Alpha Vantage TIME_SERIES_INTRADAY)

        Args:
            symbol: 주식 심볼
            interval: 데이터 간격 (1min, 5min, 15min, 30min, 60min)
            adjusted: 조정된 가격 사용 여부
            extended_hours: 장외 시간 포함 여부
            outputsize: 출력 크기 (compact: 100 data points, full: 30 days or full month)
            month: 조회할 월 (YYYY-MM 형식, Premium plan only)

        Returns:
            인트라데이 가격 데이터 리스트
        """
        # 인터벌에 따른 적절한 TTL 설정
        interval_ttl_mapping = {
            "1min": 1,  # 1분 데이터는 1시간 TTL
            "5min": 2,  # 5분 데이터는 2시간 TTL
            "15min": 4,  # 15분 데이터는 4시간 TTL
            "30min": 6,  # 30분 데이터는 6시간 TTL
            "60min": 12,  # 1시간 데이터는 12시간 TTL
        }

        ttl_hours = interval_ttl_mapping.get(interval, 4)
        cache_key = f"intraday_{symbol}_{interval}_{adjusted}_{extended_hours}_{outputsize}_{month or 'latest'}"

        async def refresh_callback():
            """Alpha Vantage에서 인트라데이 데이터를 가져옵니다"""
            return await self._fetch_intraday_from_alpha_vantage(
                symbol, interval, adjusted, extended_hours, outputsize, month
            )

        results = await self.get_data_with_unified_cache(
            cache_key=cache_key,
            model_class=DailyPrice,  # DailyPrice 모델 재사용 (datetime 필드 포함)
            data_type="stock_intraday",
            symbol=symbol,
            refresh_callback=refresh_callback,
            ttl_hours=ttl_hours,
        )

        # 타입 캐스팅 (실제로는 DailyPrice 객체들이 반환됨)
        return cast(List[DailyPrice], results)

    async def _fetch_intraday_from_alpha_vantage(
        self,
        symbol: str,
        interval: Literal["1min", "5min", "15min", "30min", "60min"] = "15min",
        adjusted: bool = False,
        extended_hours: bool = False,
        outputsize: Literal["compact", "full"] | None = "full",
        month: Optional[str] = None,
    ) -> List[DailyPrice]:
        """Alpha Vantage에서 인트라데이 데이터 가져오기"""
        try:
            logger.info(
                f"📊 Fetching intraday data for {symbol} ({interval}, month={month or 'latest'}) from Alpha Vantage"
            )

            # month 파라미터를 datetime으로 변환 (YYYY-MM -> datetime)
            month_dt = None
            if month:
                try:
                    # "2025-01" -> datetime(2025, 1, 1)
                    year, month_num = month.split("-")
                    month_dt = datetime(int(year), int(month_num), 1)
                except ValueError:
                    logger.warning(f"Invalid month format: {month}. Expected YYYY-MM.")

            # Alpha Vantage API 호출 (리스트 반환)
            response = await self.alpha_vantage.stock.intraday(
                symbol=symbol,
                interval=interval,
                adjusted=adjusted,
                extended_hours=extended_hours,
                outputsize=outputsize,
                month=month_dt,  # Premium plan only
            )

            if not isinstance(response, list):
                logger.warning(
                    f"⚠️ Unexpected intraday response type for {symbol}: {type(response)}"
                )
                return []

            if not response:
                logger.warning(f"⚠️ No intraday data returned for {symbol}")
                return []

            logger.info(f"✅ Fetched {len(response)} intraday records for {symbol}")

            # DailyPrice 모델로 변환 (datetime 필드 포함)
            intraday_prices = []
            for item in response:
                try:
                    # datetime 또는 date 필드 확인
                    date_value = item.get("datetime") or item.get("date")
                    if not date_value:
                        logger.warning(
                            f"⚠️ Missing datetime/date field in item: {item}"
                        )
                        continue

                    # datetime 객체로 변환
                    if isinstance(date_value, str):
                        # "2025-01-11 09:30:00" 형식 파싱
                        try:
                            date_obj = datetime.strptime(
                                date_value, "%Y-%m-%d %H:%M:%S"
                            )
                        except ValueError:
                            # "2025-01-11" 형식 폴백
                            date_obj = datetime.strptime(date_value, "%Y-%m-%d")
                    elif isinstance(date_value, datetime):
                        date_obj = date_value
                    else:
                        logger.warning(f"⚠️ Unexpected date type: {type(date_value)}")
                        continue

                    # DailyPrice 모델로 변환 (dict 형태)
                    price_dict = {
                        "symbol": symbol.upper(),
                        "date": date_obj,
                        "open": Decimal(str(item.get("open", 0))),
                        "high": Decimal(str(item.get("high", 0))),
                        "low": Decimal(str(item.get("low", 0))),
                        "close": Decimal(str(item.get("close", 0))),
                        "volume": int(item.get("volume", 0)),
                        "adjusted_close": Decimal(
                            str(item.get("adjusted_close", item.get("close", 0)))
                        ),
                        "dividend_amount": Decimal(str(item.get("dividend_amount", 0))),
                        "split_coefficient": Decimal(
                            str(item.get("split_coefficient", 1))
                        ),
                        "data_quality_score": 95.0,
                        "source": "alpha_vantage",
                        "price_change": Decimal("0.0"),
                        "price_change_percent": Decimal("0.0"),
                    }

                    intraday_prices.append(price_dict)

                except (ValueError, KeyError) as e:
                    logger.warning(f"⚠️ Failed to parse intraday data: {e}")
                    continue

            logger.info(f"✅ Parsed {len(intraday_prices)} intraday prices for {symbol}")
            return intraday_prices

        except Exception as e:
            logger.error(
                f"❌ Failed to fetch intraday data from Alpha Vantage for {symbol}: {e}",
                exc_info=True,
            )
            return []

    async def get_historical_data(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> dict:
        """장기 히스토리 데이터 조회 (Alpha Vantage TIME_SERIES_DAILY_ADJUSTED)"""
        try:
            logger.info(f"Fetching historical data for {symbol}")

            # Alpha Vantage daily adjusted 데이터 호출 (full outputsize)
            response = await self.alpha_vantage.stock.daily_adjusted(
                symbol=symbol,
                outputsize="full",  # type: ignore
            )

            if isinstance(response, list) and len(response) > 0:
                response = response[0]  # type: ignore

            if not isinstance(response, dict) or "Time Series (Daily)" not in response:
                logger.warning(f"Invalid historical response for {symbol}")
                return {}

            meta_data = response.get("Meta Data", {})
            time_series = response.get("Time Series (Daily)", {})

            # 날짜 필터링 (start_date, end_date가 주어진 경우)
            filtered_data = {}
            for date_str, data in time_series.items():
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")

                    # 날짜 범위 필터링
                    if start_date and date_obj < start_date:
                        continue
                    if end_date and date_obj > end_date:
                        continue

                    filtered_data[date_str] = data

                except ValueError:
                    continue

            return {
                "symbol": symbol,
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
                "meta_data": {
                    "information": meta_data.get("1. Information"),
                    "symbol": meta_data.get("2. Symbol"),
                    "last_refreshed": meta_data.get("3. Last Refreshed"),
                    "output_size": meta_data.get("4. Output Size"),
                    "time_zone": meta_data.get("5. Time Zone"),
                },
                "time_series": filtered_data,
                "data_points": len(filtered_data),
                "timestamp": datetime.now().isoformat(),
                "source": "alpha_vantage",
            }

        except Exception as e:
            logger.error(f"Failed to fetch historical data for {symbol}: {e}")
            return {}

    async def search_symbols(self, keywords: str):
        """심볼 검색 (Alpha Vantage SYMBOL_SEARCH API 호출)"""
        try:
            logger.info(f"Searching symbols for keywords: {keywords}")

            # Alpha Vantage SYMBOL_SEARCH API 호출
            response = await self.alpha_vantage.stock.search(keywords=keywords)

            # 응답 데이터 로깅
            logger.info(f"Search response type: {type(response)}")

            # Alpha Vantage 응답은 {"bestMatches": [...]} 형태
            if isinstance(response, dict) and "bestMatches" in response:
                best_matches = response.get("bestMatches", [])
                logger.info(f"Found {len(best_matches)} search results")
                return response
            else:
                logger.warning(f"Unexpected response format: {response}")
                return {"bestMatches": []}

        except Exception as e:
            logger.error(f"Failed to search symbols for {keywords}: {e}")
            return {"bestMatches": []}

    # async def get_available_symbols(self) -> List[str]:
    #     try:
    #         response = self.db_manager.get_available_symbols()
    #         return response
    #     except Exception as e:
    #         logger.error(f"Failed to get available symbols: {e}")
    #         return []

    # ==================== Coverage & Caching Helper Methods ====================

    async def _get_or_create_coverage(
        self, symbol: str, data_type: str
    ) -> StockDataCoverage:
        """Coverage 레코드 조회 또는 생성"""
        coverage = await StockDataCoverage.find_one(
            {"symbol": symbol, "data_type": data_type}
        )

        if not coverage:
            coverage = StockDataCoverage(
                symbol=symbol,
                data_type=data_type,
                is_active=True,
                update_frequency="daily",
                total_records=0,
                source="alpha_vantage",
                data_quality_score=0.0,
            )
            await coverage.insert()

        return coverage

    async def _update_coverage(
        self,
        coverage: StockDataCoverage,
        data_records: List,  # Union type으로 인한 타입 체크 우회
        update_type: Literal["full", "delta"],
    ) -> None:
        """Coverage 레코드 업데이트"""
        if not data_records:
            return

        # 날짜 범위 계산
        dates = [record.date for record in data_records]
        first_date = min(dates)
        last_date = max(dates)

        # Coverage 업데이트
        coverage.total_records = len(data_records)
        coverage.first_date = first_date
        coverage.last_date = last_date

        if update_type == "full":
            coverage.last_full_update = datetime.now(timezone.utc)
        else:
            coverage.last_delta_update = datetime.now(timezone.utc)

        # 다음 업데이트 예정일 (daily는 1일, weekly는 7일, monthly는 30일 후)
        update_intervals = {"daily": 1, "weekly": 7, "monthly": 30}
        days_offset = update_intervals.get(coverage.data_type, 1)
        coverage.next_update_due = datetime.now(timezone.utc) + timedelta(
            days=days_offset
        )

        await coverage.save()

    async def _fetch_and_store_daily_prices(
        self, symbol: str, adjusted: bool = True, is_full: bool = True
    ) -> List[DailyPrice]:
        """
        Alpha Vantage에서 Daily Prices를 가져와 MongoDB에 저장

        Args:
            symbol: 종목 심볼
            adjusted: True면 adjusted prices 사용
            is_full: True면 전체 데이터 (full), False면 최근 데이터 (compact)
        """
        outputsize = "full" if is_full else "compact"

        # Alpha Vantage API 호출 (항상 adjusted 사용)
        prices = await self._fetch_daily_prices_from_alpha_vantage(
            symbol, outputsize=outputsize
        )

        if not prices:
            return []

        # MongoDB에 저장 (기존 데이터는 삭제 후 재저장)
        if is_full:
            # Full update: 기존 데이터 삭제
            await DailyPrice.find({"symbol": symbol}).delete()

        # DailyPrice 객체로 변환 및 저장
        price_objects: list[DailyPrice] = []
        for price_data in prices:
            if isinstance(price_data, dict):
                price_obj = DailyPrice(**price_data)
            else:
                price_obj = price_data
            price_objects.append(price_obj)

        # 데이터 품질 센티널 실행 (가능한 경우)
        if self.data_quality_sentinel:
            try:
                await self.data_quality_sentinel.evaluate_daily_prices(
                    symbol, price_objects, source="alpha_vantage"
                )
            except Exception as exc:
                logger.warning(
                    "Data quality sentinel evaluation failed for %s: %s", symbol, exc
                )

        saved_prices: list[DailyPrice] = []
        for price_obj in price_objects:
            # Upsert (symbol + date로 unique)
            existing = await DailyPrice.find_one(
                {"symbol": price_obj.symbol, "date": price_obj.date}
            )

            if existing:
                # 업데이트
                existing.open = price_obj.open
                existing.high = price_obj.high
                existing.low = price_obj.low
                existing.close = price_obj.close
                existing.volume = price_obj.volume
                existing.adjusted_close = price_obj.adjusted_close
                existing.dividend_amount = price_obj.dividend_amount
                existing.split_coefficient = price_obj.split_coefficient
                existing.iso_anomaly_score = price_obj.iso_anomaly_score
                existing.prophet_anomaly_score = price_obj.prophet_anomaly_score
                existing.volume_z_score = price_obj.volume_z_score
                existing.anomaly_severity = price_obj.anomaly_severity
                existing.anomaly_reasons = price_obj.anomaly_reasons
                await existing.save()
                saved_prices.append(existing)
            else:
                # 신규 저장
                await price_obj.insert()
                saved_prices.append(price_obj)

        logger.info(
            f"Stored {len(saved_prices)} daily prices for {symbol} "
            f"(adjusted={adjusted}, full={is_full})"
        )

        return saved_prices

    async def _fetch_and_store_weekly_prices(
        self, symbol: str, adjusted: bool = True
    ) -> List[WeeklyPrice]:
        """
        Alpha Vantage에서 Weekly Prices를 가져와 MongoDB에 저장
        """
        # Alpha Vantage API 호출 (항상 adjusted, full)
        prices = await self._fetch_weekly_prices_from_alpha_vantage(
            symbol, outputsize="full"
        )

        if not prices:
            return []

        # MongoDB에 저장 (기존 데이터 삭제 후 재저장)
        await WeeklyPrice.find({"symbol": symbol}).delete()

        # WeeklyPrice 객체로 변환 및 저장
        saved_prices = []
        for price_data in prices:
            if isinstance(price_data, dict):
                price_obj = WeeklyPrice(**price_data)
            else:
                price_obj = price_data

            await price_obj.insert()
            saved_prices.append(price_obj)

        logger.info(f"Stored {len(saved_prices)} weekly prices for {symbol}")
        return saved_prices

    async def _fetch_and_store_monthly_prices(
        self, symbol: str, adjusted: bool = True
    ) -> List[MonthlyPrice]:
        """
        Alpha Vantage에서 Monthly Prices를 가져와 MongoDB에 저장
        """
        # Alpha Vantage API 호출 (항상 adjusted, full)
        prices = await self._fetch_monthly_prices_from_alpha_vantage(
            symbol, outputsize="full"
        )

        if not prices:
            return []

        # MongoDB에 저장 (기존 데이터 삭제 후 재저장)
        await MonthlyPrice.find({"symbol": symbol}).delete()

        # MonthlyPrice 객체로 변환 및 저장
        saved_prices = []
        for price_data in prices:
            if isinstance(price_data, dict):
                price_obj = MonthlyPrice(**price_data)
            else:
                price_obj = price_data

            await price_obj.insert()
            saved_prices.append(price_obj)

        logger.info(f"Stored {len(saved_prices)} monthly prices for {symbol}")
        return saved_prices
