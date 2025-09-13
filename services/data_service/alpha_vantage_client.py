"""Alpha Vantage API 클라이언트

Alpha Vantage API를 통해 주식 시계열 데이터를 수집하는 클라이언트
"""

import asyncio
import time
from datetime import datetime
from typing import Optional

import aiohttp
import pandas as pd
from pydantic import BaseModel

from shared.config.settings import Settings


class APIResponse(BaseModel):
    """API 응답 모델"""

    model_config = {"arbitrary_types_allowed": True}

    symbol: str
    data: pd.DataFrame
    metadata: dict[str, str]
    last_refreshed: datetime


class RateLimiter:
    """API 요청 속도 제한"""

    def __init__(self, calls_per_minute: int = 5):
        self.calls_per_minute = calls_per_minute
        self.min_interval = 60.0 / calls_per_minute
        self.last_call = 0.0

    async def wait(self) -> None:
        """필요한 경우 대기"""
        now = time.time()
        time_since_last_call = now - self.last_call

        if time_since_last_call < self.min_interval:
            wait_time = self.min_interval - time_since_last_call
            await asyncio.sleep(wait_time)

        self.last_call = time.time()


class AlphaVantageClient:
    """Alpha Vantage API 클라이언트"""

    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self, api_key: Optional[str] = None):
        self.settings = Settings()
        self.api_key = api_key or self.settings.alphavantage_api_key
        self.rate_limiter = RateLimiter(calls_per_minute=5)  # 무료 계정 기준
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """컨텍스트 매니저 진입"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        if self.session:
            await self.session.close()

    async def _make_request(self, params: dict[str, str]) -> dict:
        """API 요청 실행"""
        if not self.session:
            raise RuntimeError("클라이언트가 초기화되지 않았습니다. async with를 사용하세요.")

        params["apikey"] = self.api_key

        await self.rate_limiter.wait()

        async with self.session.get(self.BASE_URL, params=params) as response:
            response.raise_for_status()
            data = await response.json()

            # API 에러 확인
            if "Error Message" in data:
                raise ValueError(f"API Error: {data['Error Message']}")

            if "Note" in data:
                raise ValueError(f"API Limit: {data['Note']}")

            return data

    async def get_daily_adjusted(
        self, symbol: str, outputsize: str = "compact"
    ) -> APIResponse:
        """일일 조정된 주가 데이터 조회

        Args:
            symbol: 주식 심볼 (예: AAPL)
            outputsize: 'compact' (최근 100일) 또는 'full' (전체)

        Returns:
            APIResponse: 조회된 데이터
        """
        params = {
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": symbol,
            "outputsize": outputsize,
        }

        data = await self._make_request(params)

        # 메타데이터
        metadata = data.get("Meta Data", {})

        # 시계열 데이터
        time_series_key = "Time Series (Daily)"
        if time_series_key not in data:
            raise ValueError(f"응답에서 시계열 데이터를 찾을 수 없습니다: {list(data.keys())}")

        time_series = data[time_series_key]

        # DataFrame으로 변환
        df = pd.DataFrame.from_dict(time_series, orient="index")
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()

        # 컬럼명 정리
        df.columns = [
            "open",
            "high",
            "low",
            "close",
            "adjusted_close",
            "volume",
            "dividend_amount",
            "split_coefficient",
        ]

        # 데이터 타입 변환
        numeric_columns = [
            "open",
            "high",
            "low",
            "close",
            "adjusted_close",
            "volume",
            "dividend_amount",
            "split_coefficient",
        ]
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # 심볼 컬럼 추가
        df["symbol"] = symbol

        return APIResponse(
            symbol=symbol, data=df, metadata=metadata, last_refreshed=datetime.now()
        )

    async def get_intraday(
        self, symbol: str, interval: str = "5min", outputsize: str = "compact"
    ) -> APIResponse:
        """인트라데이 데이터 조회

        Args:
            symbol: 주식 심볼
            interval: '1min', '5min', '15min', '30min', '60min'
            outputsize: 'compact' 또는 'full'

        Returns:
            APIResponse: 조회된 데이터
        """
        params = {
            "function": "TIME_SERIES_INTRADAY",
            "symbol": symbol,
            "interval": interval,
            "outputsize": outputsize,
        }

        data = await self._make_request(params)

        # 메타데이터
        metadata = data.get("Meta Data", {})

        # 시계열 데이터
        time_series_key = f"Time Series ({interval})"
        if time_series_key not in data:
            raise ValueError(f"응답에서 시계열 데이터를 찾을 수 없습니다: {list(data.keys())}")

        time_series = data[time_series_key]

        # DataFrame으로 변환
        df = pd.DataFrame.from_dict(time_series, orient="index")
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()

        # 컬럼명 정리
        df.columns = ["open", "high", "low", "close", "volume"]

        # 데이터 타입 변환
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # 심볼 컬럼 추가
        df["symbol"] = symbol

        return APIResponse(
            symbol=symbol, data=df, metadata=metadata, last_refreshed=datetime.now()
        )

    async def get_company_overview(self, symbol: str) -> dict:
        """회사 기본 정보 조회

        Args:
            symbol: 주식 심볼

        Returns:
            Dict: 회사 정보
        """
        params = {"function": "OVERVIEW", "symbol": symbol}

        return await self._make_request(params)

    async def search_endpoint(self, keywords: str) -> list[dict]:
        """주식 심볼 검색

        Args:
            keywords: 검색 키워드

        Returns:
            List[Dict]: 검색 결과
        """
        params = {"function": "SYMBOL_SEARCH", "keywords": keywords}

        data = await self._make_request(params)
        return data.get("bestMatches", [])


async def get_stock_data(
    symbol: str,
    data_type: str = "daily",
    interval: str = "5min",
    outputsize: str = "compact",
) -> APIResponse:
    """주식 데이터 조회 헬퍼 함수

    Args:
        symbol: 주식 심볼
        data_type: 'daily' 또는 'intraday'
        interval: 인트라데이인 경우 간격
        outputsize: 'compact' 또는 'full'

    Returns:
        APIResponse: 조회된 데이터
    """
    async with AlphaVantageClient() as client:
        if data_type == "daily":
            return await client.get_daily_adjusted(symbol, outputsize)
        elif data_type == "intraday":
            return await client.get_intraday(symbol, interval, outputsize)
        else:
            raise ValueError(f"지원하지 않는 데이터 타입: {data_type}")


if __name__ == "__main__":
    # 사용 예시
    async def main():
        async with AlphaVantageClient() as client:
            # 일일 데이터 조회
            response = await client.get_daily_adjusted("AAPL", "compact")
            print(f"Symbol: {response.symbol}")
            print(f"Data shape: {response.data.shape}")
            print(response.data.head())

            # 회사 정보 조회
            overview = await client.get_company_overview("AAPL")
            print(f"Company: {overview.get('Name', 'N/A')}")

    # asyncio.run(main())
