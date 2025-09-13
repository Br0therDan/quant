"""모의 데이터 생성기

Alpha Vantage API가 제한될 때 사용할 모의 주식 데이터 생성
"""

import random
from datetime import datetime

import numpy as np
import pandas as pd

from .alpha_vantage_client import APIResponse


class MockDataGenerator:
    """모의 주식 데이터 생성기"""

    def __init__(self, seed: int = 42):
        """
        Args:
            seed: 랜덤 시드 (재현 가능한 데이터를 위해)
        """
        random.seed(seed)
        np.random.seed(seed)

    def generate_daily_prices(
        self,
        symbol: str,
        start_date: str = "2023-01-01",
        end_date: str = "2024-01-01",
        initial_price: float = 100.0,
        volatility: float = 0.02,
    ) -> APIResponse:
        """일일 주가 데이터 생성

        Args:
            symbol: 주식 심볼
            start_date: 시작일
            end_date: 종료일
            initial_price: 초기 가격
            volatility: 변동성 (일일 변동률의 표준편차)

        Returns:
            APIResponse: 생성된 데이터
        """
        # 날짜 범위 생성 (주말 제외)
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        dates = pd.bdate_range(start=start, end=end, freq="B")  # 영업일만

        # 주가 생성 (기하 브라운 운동)
        n_days = len(dates)
        returns = np.random.normal(0, volatility, n_days)
        returns[0] = 0  # 첫날은 변화 없음

        # 누적 수익률로 가격 계산
        price_multipliers = np.exp(np.cumsum(returns))
        closes = initial_price * price_multipliers

        # OHLV 데이터 생성
        data = []
        for i, date in enumerate(dates):
            close = closes[i]

            # 일중 변동 범위 (보통 종가 기준 ±2%)
            intraday_range = close * 0.02

            # 고가/저가 생성 (종가를 포함하는 범위)
            high = close + random.uniform(0, intraday_range)
            low = close - random.uniform(0, intraday_range)

            # 시가 생성 (전일 종가 근처)
            if i == 0:
                open_price = close
            else:
                gap = random.uniform(-intraday_range / 2, intraday_range / 2)
                open_price = max(low, min(high, closes[i - 1] + gap))

            # 고가/저가 조정 (시가와 종가를 포함해야 함)
            high = max(high, open_price, close)
            low = min(low, open_price, close)

            # 거래량 생성 (로그정규분포, 평균 1M주)
            volume = int(np.random.lognormal(np.log(1000000), 0.5))

            data.append(
                {
                    "date": date,
                    "open": round(open_price, 2),
                    "high": round(high, 2),
                    "low": round(low, 2),
                    "close": round(close, 2),
                    "adjusted_close": round(close, 2),  # 간단히 종가와 동일
                    "volume": volume,
                    "dividend_amount": 0.0,  # 배당은 0으로 설정
                    "split_coefficient": 1.0,  # 분할은 1로 설정
                    "symbol": symbol,
                }
            )

        # DataFrame 생성
        df = pd.DataFrame(data)
        df.set_index("date", inplace=True)

        # 메타데이터 생성
        metadata = {
            "1. Information": "Mock Daily Time Series with Splits and Dividend",
            "2. Symbol": symbol,
            "3. Last Refreshed": datetime.now().strftime("%Y-%m-%d"),
            "4. Output Size": "Compact",
            "5. Time Zone": "US/Eastern",
        }

        return APIResponse(
            symbol=symbol, data=df, metadata=metadata, last_refreshed=datetime.now()
        )

    def generate_company_info(self, symbol: str) -> dict:
        """회사 기본 정보 생성

        Args:
            symbol: 주식 심볼

        Returns:
            Dict: 회사 정보
        """
        # 심볼별 기본 정보 설정
        company_info = {
            "AAPL": {
                "Name": "Apple Inc",
                "Sector": "Technology",
                "Industry": "Consumer Electronics",
                "MarketCapitalization": "3000000000000",
                "Country": "USA",
                "Currency": "USD",
                "Exchange": "NASDAQ",
            },
            "MSFT": {
                "Name": "Microsoft Corporation",
                "Sector": "Technology",
                "Industry": "Software",
                "MarketCapitalization": "2500000000000",
                "Country": "USA",
                "Currency": "USD",
                "Exchange": "NASDAQ",
            },
            "GOOGL": {
                "Name": "Alphabet Inc",
                "Sector": "Technology",
                "Industry": "Internet Services",
                "MarketCapitalization": "1800000000000",
                "Country": "USA",
                "Currency": "USD",
                "Exchange": "NASDAQ",
            },
            "TSLA": {
                "Name": "Tesla Inc",
                "Sector": "Consumer Cyclical",
                "Industry": "Auto Manufacturers",
                "MarketCapitalization": "800000000000",
                "Country": "USA",
                "Currency": "USD",
                "Exchange": "NASDAQ",
            },
            "SPY": {
                "Name": "SPDR S&P 500 ETF Trust",
                "Sector": "ETF",
                "Industry": "Exchange Traded Fund",
                "MarketCapitalization": "400000000000",
                "Country": "USA",
                "Currency": "USD",
                "Exchange": "NYSE",
            },
        }

        # 기본값 설정
        default_info = {
            "Name": f"{symbol} Corporation",
            "Sector": "Technology",
            "Industry": "Software",
            "MarketCapitalization": "100000000000",
            "Country": "USA",
            "Currency": "USD",
            "Exchange": "NYSE",
        }

        info = company_info.get(symbol, default_info.copy())
        info["Symbol"] = symbol

        return info


# 전역 인스턴스
mock_generator = MockDataGenerator()


def generate_mock_response(symbol: str, data_type: str = "daily") -> APIResponse:
    """간편한 모의 데이터 생성 함수

    Args:
        symbol: 주식 심볼
        data_type: 데이터 타입 ("daily" 등)

    Returns:
        APIResponse: 생성된 모의 데이터
    """
    if data_type == "daily":
        return mock_generator.generate_daily_prices(symbol)
    else:
        raise ValueError(f"지원하지 않는 데이터 타입: {data_type}")


if __name__ == "__main__":
    # 사용 예시
    generator = MockDataGenerator()

    # AAPL 데이터 생성
    response = generator.generate_daily_prices("AAPL")
    print(f"Symbol: {response.symbol}")
    print(f"Data shape: {response.data.shape}")
    print(response.data.head())

    # 회사 정보 생성
    info = generator.generate_company_info("AAPL")
    print(f"Company: {info['Name']}")
    print(f"Sector: {info['Sector']}")
