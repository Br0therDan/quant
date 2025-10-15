"""시장 데이터 변환기

시장 데이터를 다양한 형식으로 변환하는 로직을 제공합니다.
"""

import logging
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


class MarketDataTransformer:
    """시장 데이터 변환기

    시장 데이터를 DataFrame, dict 등 다양한 형식으로 변환합니다.
    """

    @staticmethod
    def to_dataframe(
        data_points: list[dict[str, Any]],
        date_column: str = "date",
    ) -> pd.DataFrame:
        """데이터 포인트를 DataFrame으로 변환

        Args:
            data_points: 데이터 포인트 리스트
            date_column: 날짜 컬럼명 (인덱스로 사용)

        Returns:
            pandas DataFrame

        Example:
            >>> data = [
            ...     {"date": "2024-01-01", "close": 150.0, "volume": 1000000},
            ...     {"date": "2024-01-02", "close": 152.0, "volume": 1100000},
            ... ]
            >>> df = MarketDataTransformer.to_dataframe(data)
            >>> print(df.head())
        """
        if not data_points:
            return pd.DataFrame()

        df = pd.DataFrame(data_points)

        # 날짜 컬럼을 datetime으로 변환 및 인덱스 설정
        if date_column in df.columns:
            df[date_column] = pd.to_datetime(df[date_column])
            df.set_index(date_column, inplace=True)
            df.sort_index(inplace=True)

        return df

    @staticmethod
    def to_ohlcv_dict(
        data_points: list[dict[str, Any]],
    ) -> dict[str, list[float]]:
        """데이터 포인트를 OHLCV 딕셔너리로 변환

        Args:
            data_points: 데이터 포인트 리스트

        Returns:
            OHLCV 딕셔너리 {컬럼명: 값 리스트}

        Example:
            >>> data = [{"open": 100, "high": 105, "low": 99, "close": 103, "volume": 1000}]
            >>> ohlcv = MarketDataTransformer.to_ohlcv_dict(data)
            >>> print(ohlcv["close"])
            [103]
        """
        if not data_points:
            return {"open": [], "high": [], "low": [], "close": [], "volume": []}

        ohlcv: dict[str, list[float]] = {
            "open": [],
            "high": [],
            "low": [],
            "close": [],
            "volume": [],
        }

        for point in data_points:
            ohlcv["open"].append(point.get("open", 0.0))
            ohlcv["high"].append(point.get("high", 0.0))
            ohlcv["low"].append(point.get("low", 0.0))
            ohlcv["close"].append(point.get("close", 0.0))
            ohlcv["volume"].append(point.get("volume", 0.0))

        return ohlcv

    @staticmethod
    def resample(
        df: pd.DataFrame,
        target_interval: str = "1D",
        agg_rules: dict[str, str] | None = None,
    ) -> pd.DataFrame:
        """시계열 데이터 리샘플링

        Args:
            df: 원본 DataFrame (DatetimeIndex 필수)
            target_interval: 목표 간격 (예: "1D", "1H", "5T")
            agg_rules: 집계 규칙 {컬럼명: "first"|"last"|"mean"|"sum"}

        Returns:
            리샘플링된 DataFrame

        Example:
            >>> # 1분 데이터를 1시간 데이터로 변환
            >>> hourly_df = MarketDataTransformer.resample(df, "1H")
        """
        if df.empty:
            return df

        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("DataFrame must have DatetimeIndex")

        # 기본 집계 규칙
        if agg_rules is None:
            agg_rules = {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum",
            }

        # 리샘플링
        resampled = df.resample(target_interval).agg(agg_rules)  # type: ignore[arg-type]

        # NaN 제거
        resampled.dropna(inplace=True)

        return resampled

    @staticmethod
    def calculate_returns(
        df: pd.DataFrame,
        price_column: str = "close",
        method: str = "simple",
    ) -> pd.Series:
        """수익률 계산

        Args:
            df: 가격 데이터 DataFrame
            price_column: 가격 컬럼명
            method: 계산 방법 ("simple" 또는 "log")

        Returns:
            수익률 Series

        Example:
            >>> returns = MarketDataTransformer.calculate_returns(df)
            >>> print(f"Average return: {returns.mean():.2%}")
        """
        if df.empty or price_column not in df.columns:
            return pd.Series(dtype=float)

        prices = df[price_column]

        if method == "simple":
            # 단순 수익률: (P_t / P_{t-1}) - 1
            returns = prices.pct_change()
        elif method == "log":
            # 로그 수익률: ln(P_t / P_{t-1})
            returns = (
                pd.Series(
                    data=pd.Series.to_numpy(prices).astype(float),
                    index=prices.index,
                )
                .apply(lambda x: x if x > 0 else 0.01)
                .pipe(lambda x: x.pct_change())
            )
            returns = returns.apply(lambda x: 0.0 if pd.isna(x) else x)
        else:
            raise ValueError(f"Unknown method: {method}. Use 'simple' or 'log'.")

        # 첫 번째 NaN 제거
        returns = returns.fillna(0.0)

        return returns
