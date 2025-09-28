"""데이터 파이프라인

Alpha Vantage API에서 데이터를 수집하고 DuckDB에 저장하는 파이프라인
"""

import asyncio
import logging
from datetime import datetime, timedelta

import pandas as pd

from .alpha_vantage_client import AlphaVantageClient, get_stock_data
from .database import DatabaseManager

logger = logging.getLogger(__name__)


class DataPipeline:
    """데이터 수집 및 저장 파이프라인"""

    def __init__(self, db_manager: DatabaseManager | None = None):
        self.db_manager = db_manager or DatabaseManager()
        self.symbols_to_update: list[str] = []

    async def collect_stock_info(self, symbol: str, use_mock: bool = False) -> bool:
        """주식 기본 정보 수집"""
        try:
            if use_mock:
                # Mock 데이터 사용
                from .mock_data import mock_generator

                info = mock_generator.generate_company_info(symbol)
            else:
                # 실제 API 호출
                async with AlphaVantageClient() as client:
                    info = await client.get_company_overview(symbol)

            if info and ("Symbol" in info or "Name" in info):
                with self.db_manager:
                    self.db_manager.insert_stock_info(symbol, info)
                logger.info(f"주식 정보 수집 완료: {symbol}")
                return True
            else:
                logger.warning(f"주식 정보 없음: {symbol}")
                return False

        except Exception as e:
            logger.error(f"주식 정보 수집 실패 {symbol}: {e}")
            # API 실패 시 mock 데이터로 대체 시도
            if not use_mock:
                logger.info(f"Mock 정보로 대체 시도: {symbol}")
                try:
                    from .mock_data import mock_generator

                    info = mock_generator.generate_company_info(symbol)

                    with self.db_manager:
                        self.db_manager.insert_stock_info(symbol, info)
                    logger.info(f"Mock 주식 정보 수집 완료: {symbol}")
                    return True
                except Exception as mock_error:
                    logger.error(f"Mock 정보 생성 실패 {symbol}: {mock_error}")

            return False

    async def collect_daily_data(
        self, symbol: str, outputsize: str = "compact", use_mock: bool = False
    ) -> bool:
        """일일 주가 데이터 수집"""
        try:
            if use_mock:
                # Mock 데이터 사용
                from .mock_data import generate_mock_response

                response = generate_mock_response(symbol, "daily")
            else:
                # 실제 API 호출
                response = await get_stock_data(symbol, "daily", outputsize=outputsize)

            if not response.data.empty:
                with self.db_manager:
                    rows_inserted = self.db_manager.insert_daily_prices(response.data)

                logger.info(f"일일 데이터 수집 완료: {symbol} ({rows_inserted}건)")
                return True
            else:
                logger.warning(f"일일 데이터 없음: {symbol}")
                return False

        except Exception as e:
            logger.error(f"일일 데이터 수집 실패 {symbol}: {e}")
            # API 실패 시 mock 데이터로 대체 시도
            if not use_mock:
                logger.info(f"Mock 데이터로 대체 시도: {symbol}")
                try:
                    from .mock_data import generate_mock_response

                    response = generate_mock_response(symbol, "daily")

                    if not response.data.empty:
                        with self.db_manager:
                            rows_inserted = self.db_manager.insert_daily_prices(
                                response.data
                            )
                        logger.info(f"Mock 일일 데이터 수집 완료: {symbol} ({rows_inserted}건)")
                        return True
                except Exception as mock_error:
                    logger.error(f"Mock 데이터 생성 실패 {symbol}: {mock_error}")

            return False

    async def collect_intraday_data(
        self, symbol: str, interval: str = "5min", outputsize: str = "compact"
    ) -> bool:
        """인트라데이 주가 데이터 수집"""
        try:
            response = await get_stock_data(
                symbol, "intraday", interval=interval, outputsize=outputsize
            )

            if not response.data.empty:
                with self.db_manager:
                    rows_inserted = self.db_manager.insert_intraday_prices(
                        response.data, interval
                    )

                logger.info(f"인트라데이 데이터 수집 완료: {symbol} ({rows_inserted}건)")
                return True
            else:
                logger.warning(f"인트라데이 데이터 없음: {symbol}")
                return False

        except Exception as e:
            logger.error(f"인트라데이 데이터 수집 실패 {symbol}: {e}")
            return False

    async def update_symbol_data(
        self,
        symbol: str,
        include_info: bool = True,
        include_intraday: bool = False,
        outputsize: str = "compact",
        use_mock: bool = False,
    ) -> dict:
        """심볼의 모든 데이터 업데이트"""
        results = {
            "symbol": symbol,
            "info_success": False,
            "daily_success": False,
            "intraday_success": False,
            "timestamp": datetime.now(),
        }

        try:
            # 기본 정보 수집
            if include_info:
                results["info_success"] = await self.collect_stock_info(
                    symbol, use_mock
                )

            # 일일 데이터 수집
            results["daily_success"] = await self.collect_daily_data(
                symbol, outputsize, use_mock
            )

            # 인트라데이 데이터 수집 (선택적)
            if include_intraday:
                results["intraday_success"] = await self.collect_intraday_data(
                    symbol, outputsize=outputsize
                )

            logger.info(f"심볼 데이터 업데이트 완료: {symbol}")

        except Exception as e:
            logger.error(f"심볼 데이터 업데이트 실패 {symbol}: {e}")

        return results

    async def bulk_update(
        self,
        symbols: list[str],
        include_info: bool = True,
        include_intraday: bool = False,
        outputsize: str = "compact",
        batch_size: int = 5,
        delay_between_batches: float = 60.0,
        use_mock: bool = False,
    ) -> list[dict]:
        """여러 심볼의 데이터를 배치로 업데이트"""
        all_results = []

        # 배치로 나누어 처리 (API 제한 고려)
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i : i + batch_size]
            logger.info(
                f"배치 처리 중: {i//batch_size + 1}/{(len(symbols) + batch_size - 1)//batch_size}"
            )

            # 배치 내 심볼들을 병렬 처리
            batch_tasks = [
                self.update_symbol_data(
                    symbol, include_info, include_intraday, outputsize, use_mock
                )
                for symbol in batch
            ]

            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

            # 예외 처리
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"배치 처리 중 오류: {result}")
                else:
                    all_results.append(result)

            # 배치 간 대기 (마지막 배치가 아닌 경우)
            if i + batch_size < len(symbols):
                logger.info(f"{delay_between_batches}초 대기 중...")
                await asyncio.sleep(delay_between_batches)

        return all_results

    def get_missing_data_ranges(self, symbol: str) -> list[tuple]:
        """누락된 데이터 기간 찾기"""
        with self.db_manager:
            start_date, end_date = self.db_manager.get_data_range(symbol)

            if not start_date or not end_date:
                # 데이터가 없으면 전체 기간
                return [("2020-01-01", datetime.now().strftime("%Y-%m-%d"))]

            # 날짜를 문자열로 변환
            from datetime import date

            if isinstance(end_date, date):
                end_date_str = end_date.strftime("%Y-%m-%d")
            else:
                end_date_str = str(end_date)

            missing_ranges = []

            # 최신 데이터 확인 (어제까지 있어야 함)
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            if end_date_str < yesterday:
                missing_ranges.append((end_date_str, yesterday))

            return missing_ranges

    async def incremental_update(self, symbols: list[str]) -> list[dict]:
        """증분 업데이트 (누락된 데이터만 수집)"""
        results = []

        for symbol in symbols:
            missing_ranges = self.get_missing_data_ranges(symbol)

            if missing_ranges:
                logger.info(f"{symbol} 누락 데이터 발견: {missing_ranges}")
                result = await self.update_symbol_data(
                    symbol,
                    include_info=False,  # 증분 업데이트에서는 정보 제외
                    outputsize="full",  # 전체 데이터로 누락분 채우기
                )
                results.append(result)
            else:
                logger.info(f"{symbol} 데이터 최신 상태")
                results.append(
                    {
                        "symbol": symbol,
                        "daily_success": True,
                        "up_to_date": True,
                        "timestamp": datetime.now(),
                    }
                )

        return results

    def get_data_summary(self) -> dict:
        """데이터 현황 요약"""
        with self.db_manager:
            symbols = self.db_manager.get_available_symbols()

            summary = {
                "total_symbols": len(symbols),
                "symbols": [],
                "last_updated": datetime.now(),
            }

            for symbol in symbols:
                start_date, end_date = self.db_manager.get_data_range(symbol)
                summary["symbols"].append(
                    {
                        "symbol": symbol,
                        "start_date": start_date,
                        "end_date": end_date,
                        "days_count": (
                            None
                            if not start_date or not end_date
                            else (
                                pd.to_datetime(end_date) - pd.to_datetime(start_date)
                            ).days
                        ),
                    }
                )

            return summary


async def update_watchlist(symbols: list[str], full_update: bool = False) -> list[dict]:
    """관심 종목 리스트 업데이트

    Args:
        symbols: 업데이트할 심볼 리스트
        full_update: True면 전체 업데이트, False면 증분 업데이트

    Returns:
        업데이트 결과 리스트
    """
    pipeline = DataPipeline()

    if full_update:
        return await pipeline.bulk_update(symbols, include_info=True, outputsize="full")
    else:
        return await pipeline.incremental_update(symbols)


async def setup_default_symbols() -> list:
    """기본 심볼들 설정"""
    default_symbols = [
        "AAPL",  # Apple
        "MSFT",  # Microsoft
        "GOOGL",  # Alphabet
        "AMZN",  # Amazon
        "TSLA",  # Tesla
        "META",  # Meta
        "NVDA",  # NVIDIA
        "SPY",  # S&P 500 ETF
        "QQQ",  # NASDAQ ETF
        "VTI",  # Total Stock Market ETF
    ]

    pipeline = DataPipeline()
    return await pipeline.bulk_update(
        default_symbols,
        include_info=True,
        outputsize="compact",  # 처음에는 compact로 빠르게
        use_mock=True,  # 개발용으로 mock 데이터 사용
    )


if __name__ == "__main__":
    # 사용 예시
    async def main():
        # 기본 심볼 설정
        print("기본 심볼 데이터 수집 중...")
        results = await setup_default_symbols()

        for result in results:
            print(
                f"{result['symbol']}: "
                f"정보={result.get('info_success', False)}, "
                f"일일={result.get('daily_success', False)}"
            )

        # 데이터 현황 확인
        pipeline = DataPipeline()
        summary = pipeline.get_data_summary()
        print(f"\n전체 심볼 수: {summary['total_symbols']}")

        for symbol_info in summary["symbols"][:5]:
            print(
                f"{symbol_info['symbol']}: "
                f"{symbol_info['start_date']} ~ {symbol_info['end_date']} "
                f"({symbol_info['days_count']}일)"
            )

    # asyncio.run(main())
