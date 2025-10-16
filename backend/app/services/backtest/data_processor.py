"""
데이터 처리기 - 시장 데이터 정제 및 검증
"""

import logging
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


class DataProcessor:
    """데이터 처리기

    시장 데이터를 정제하고 검증합니다.
    Phase 2에서 도입된 컴포넌트입니다.
    """

    async def process_market_data(
        self,
        raw_data: dict[str, Any],
        required_columns: list[str],
        min_data_points: int = 30,
    ) -> dict[str, pd.DataFrame]:
        """시장 데이터 처리

        Args:
            raw_data: 원시 시장 데이터
            required_columns: 필수 컬럼 리스트
            min_data_points: 최소 데이터 포인트 수

        Returns:
            처리된 데이터 딕셔너리
        """
        processed = {}

        for symbol, data in raw_data.items():
            try:
                # 1. DataFrame 변환
                df = self._to_dataframe(data)

                # 2. 필수 컬럼 검증
                if not self._validate_columns(df, required_columns):
                    logger.warning(f"Missing required columns for {symbol}")
                    continue

                # 3. 최소 데이터 포인트 검증
                if len(df) < min_data_points:
                    logger.warning(
                        f"Insufficient data points for {symbol}: {len(df)} < {min_data_points}"
                    )
                    continue

                # 4. 결측치 처리
                df = self._handle_missing_values(df)

                # 5. 이상치 탐지 및 처리
                df = self._handle_outliers(df)

                # 6. 데이터 정렬
                df = df.sort_index()

                processed[symbol] = df

            except Exception as e:
                logger.error(f"Failed to process data for {symbol}: {e}")
                continue

        logger.info(f"Successfully processed {len(processed)}/{len(raw_data)} symbols")
        return processed

    def _to_dataframe(self, data: Any) -> pd.DataFrame:
        """데이터를 DataFrame으로 변환

        지원 형식:
        1. pandas.DataFrame
        2. dict (records 키를 가진 경우)
        3. dict (일반 딕셔너리)
        4. list (레코드 리스트)
        """
        if isinstance(data, pd.DataFrame):
            return data

        # mysingle_quant 클라이언트가 반환하는 형태: {"records": [...]}
        if isinstance(data, dict) and "records" in data:
            records = data["records"]
            if not records:
                return pd.DataFrame()

            # 레코드를 DataFrame으로 변환
            df = pd.DataFrame(records)

            # date 컬럼을 인덱스로 설정
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"])
                df = df.set_index("date")

            return df

        # 일반 딕셔너리 (기존 로직)
        if isinstance(data, dict):
            return pd.DataFrame(data)

        # 직접 리스트로 전달된 경우
        if isinstance(data, list):
            df = pd.DataFrame(data)
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"])
                df = df.set_index("date")
            return df

        raise ValueError(f"Unsupported data type: {type(data)}")

    def _validate_columns(self, df: pd.DataFrame, required: list[str]) -> bool:
        """필수 컬럼 검증"""
        return all(col in df.columns for col in required)

    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """결측치 처리

        전진 채움(forward fill) 방식 사용
        """
        return df.ffill().bfill()

    def _handle_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """이상치 처리

        IQR 방식으로 이상치 탐지 및 제한
        """
        for col in ["open", "high", "low", "close"]:
            if col not in df.columns:
                continue

            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1

            lower_bound = Q1 - 3 * IQR
            upper_bound = Q3 + 3 * IQR

            df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)

        return df

    async def validate_data_quality(self, data: pd.DataFrame) -> dict[str, Any]:
        """데이터 품질 검증

        Returns:
            품질 지표 딕셔너리
        """
        return {
            "total_rows": len(data),
            "missing_values": data.isnull().sum().to_dict(),
            "date_range": {
                "start": str(data.index.min()),
                "end": str(data.index.max()),
            },
            "columns": list(data.columns),
        }
