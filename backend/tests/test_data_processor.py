"""
DataProcessor 단위 테스트
"""

import pytest
import pandas as pd
import numpy as np

from app.services.backtest.data_processor import DataProcessor


@pytest.fixture
def data_processor():
    """DataProcessor 픽스처"""
    return DataProcessor()


@pytest.fixture
def sample_market_data():
    """샘플 시장 데이터"""
    dates = pd.date_range("2024-01-01", periods=100, freq="D")
    return {
        "AAPL": pd.DataFrame(
            {
                "open": np.random.uniform(150, 160, 100),
                "high": np.random.uniform(160, 170, 100),
                "low": np.random.uniform(140, 150, 100),
                "close": np.random.uniform(150, 160, 100),
                "volume": np.random.uniform(1000000, 2000000, 100),
            },
            index=dates,
        ),
        "GOOGL": pd.DataFrame(
            {
                "open": np.random.uniform(100, 110, 100),
                "high": np.random.uniform(110, 120, 100),
                "low": np.random.uniform(90, 100, 100),
                "close": np.random.uniform(100, 110, 100),
                "volume": np.random.uniform(500000, 1000000, 100),
            },
            index=dates,
        ),
    }


@pytest.mark.asyncio
async def test_process_market_data_success(data_processor, sample_market_data):
    """시장 데이터 처리 성공 테스트"""
    # Act
    result = await data_processor.process_market_data(
        raw_data=sample_market_data,
        required_columns=["open", "high", "low", "close", "volume"],
        min_data_points=50,
    )

    # Assert
    assert len(result) == 2
    assert "AAPL" in result
    assert "GOOGL" in result
    assert isinstance(result["AAPL"], pd.DataFrame)
    assert len(result["AAPL"]) == 100


@pytest.mark.asyncio
async def test_process_market_data_insufficient_points(data_processor):
    """데이터 포인트 부족 테스트"""
    # Arrange
    insufficient_data = {
        "AAPL": pd.DataFrame(
            {
                "open": [150, 151, 152],
                "high": [160, 161, 162],
                "low": [140, 141, 142],
                "close": [155, 156, 157],
                "volume": [1000000, 1100000, 1200000],
            }
        )
    }

    # Act
    result = await data_processor.process_market_data(
        raw_data=insufficient_data,
        required_columns=["open", "high", "low", "close", "volume"],
        min_data_points=50,
    )

    # Assert
    assert len(result) == 0  # 데이터 포인트 부족으로 제외됨


@pytest.mark.asyncio
async def test_process_market_data_missing_columns(data_processor):
    """필수 컬럼 누락 테스트"""
    # Arrange
    invalid_data = {
        "AAPL": pd.DataFrame(
            {
                "open": np.random.uniform(150, 160, 100),
                "close": np.random.uniform(150, 160, 100),
                # high, low, volume 누락
            }
        )
    }

    # Act
    result = await data_processor.process_market_data(
        raw_data=invalid_data,
        required_columns=["open", "high", "low", "close", "volume"],
        min_data_points=50,
    )

    # Assert
    assert len(result) == 0  # 필수 컬럼 누락으로 제외됨


@pytest.mark.asyncio
async def test_handle_missing_values(data_processor):
    """결측치 처리 테스트"""
    # Arrange
    df_with_nulls = pd.DataFrame(
        {
            "open": [150, None, 152, 153, None],
            "close": [155, 156, None, 158, 159],
        }
    )

    # Act
    result = data_processor._handle_missing_values(df_with_nulls)

    # Assert
    assert result.isnull().sum().sum() == 0  # 결측치 없음


@pytest.mark.asyncio
async def test_handle_outliers(data_processor):
    """이상치 처리 테스트"""
    # Arrange
    df_with_outliers = pd.DataFrame(
        {
            "open": [150, 151, 152, 1000, 153],  # 1000은 이상치
            "close": [155, 156, 157, 158, 159],
        }
    )

    # Act
    result = data_processor._handle_outliers(df_with_outliers)

    # Assert
    # 이상치가 IQR 기준으로 클리핑됨
    assert result["open"].max() < 1000


@pytest.mark.asyncio
async def test_validate_data_quality(data_processor, sample_market_data):
    """데이터 품질 검증 테스트"""
    # Act
    quality = await data_processor.validate_data_quality(sample_market_data["AAPL"])

    # Assert
    assert "total_rows" in quality
    assert "missing_values" in quality
    assert "date_range" in quality
    assert "columns" in quality
    assert quality["total_rows"] == 100
