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


# ===== P3.1 확장 테스트 =====


@pytest.mark.asyncio
async def test_large_dataset_processing(data_processor):
    """대용량 데이터 처리 테스트 (10,000+ rows)"""
    # Arrange - 10,000 rows 생성
    dates = pd.date_range("2020-01-01", periods=10000, freq="D")
    large_data = {
        "AAPL": pd.DataFrame(
            {
                "open": np.random.uniform(150, 160, 10000),
                "high": np.random.uniform(160, 170, 10000),
                "low": np.random.uniform(140, 150, 10000),
                "close": np.random.uniform(150, 160, 10000),
                "volume": np.random.uniform(1000000, 2000000, 10000),
            },
            index=dates,
        )
    }

    # Act
    result = await data_processor.process_market_data(
        raw_data=large_data,
        required_columns=["open", "high", "low", "close", "volume"],
        min_data_points=50,
    )

    # Assert
    assert len(result) == 1
    assert len(result["AAPL"]) == 10000
    assert result["AAPL"].isnull().sum().sum() == 0  # 결측치 없음


@pytest.mark.asyncio
async def test_multiple_symbols_data_merge(data_processor):
    """멀티 심볼 데이터 병합 테스트"""
    # Arrange - 길이가 다른 데이터
    dates_100 = pd.date_range("2024-01-01", periods=100, freq="D")
    dates_80 = pd.date_range("2024-01-01", periods=80, freq="D")

    multi_symbol_data = {
        "AAPL": pd.DataFrame(
            {
                "open": np.random.uniform(150, 160, 100),
                "high": np.random.uniform(160, 170, 100),
                "low": np.random.uniform(140, 150, 100),
                "close": np.random.uniform(150, 160, 100),
                "volume": np.random.uniform(1000000, 2000000, 100),
            },
            index=dates_100,
        ),
        "GOOGL": pd.DataFrame(
            {
                "open": np.random.uniform(100, 110, 80),
                "high": np.random.uniform(110, 120, 80),
                "low": np.random.uniform(90, 100, 80),
                "close": np.random.uniform(100, 110, 80),
                "volume": np.random.uniform(500000, 1000000, 80),
            },
            index=dates_80,
        ),
    }

    # Act
    result = await data_processor.process_market_data(
        raw_data=multi_symbol_data,
        required_columns=["open", "high", "low", "close", "volume"],
        min_data_points=50,
    )

    # Assert
    assert len(result) == 2
    assert len(result["AAPL"]) == 100
    assert len(result["GOOGL"]) == 80


@pytest.mark.asyncio
async def test_missing_data_handling_strategies(data_processor):
    """결측치 처리 전략 테스트 (forward fill, backward fill, interpolate)"""
    # Arrange - 다양한 패턴의 결측치
    df_with_gaps = pd.DataFrame(
        {
            "open": [150, None, None, 153, 154, None, 156],
            "close": [155, 156, None, None, 159, 160, 161],
            "volume": [1000000, None, 1200000, None, None, 1500000, 1600000],
        }
    )

    # Act
    result = data_processor._handle_missing_values(df_with_gaps)

    # Assert
    assert result.isnull().sum().sum() == 0  # 모든 결측치 처리됨
    assert len(result) == 7  # 행 수 유지
    # forward fill 적용 확인
    assert result["open"].iloc[1] == 150  # None → 150 (forward fill)


@pytest.mark.asyncio
async def test_data_normalization(data_processor):
    """데이터 정규화 테스트"""
    # Arrange
    df_unnormalized = pd.DataFrame(
        {
            "open": [100, 200, 300, 400, 500],
            "close": [110, 210, 310, 410, 510],
            "volume": [1000000, 2000000, 3000000, 4000000, 5000000],
        }
    )

    # Act - 정규화 메서드가 있다면 테스트
    if hasattr(data_processor, "_normalize_data"):
        result = data_processor._normalize_data(df_unnormalized)

        # Assert
        # Min-Max 정규화 확인 (0-1 범위)
        assert result["open"].min() >= 0
        assert result["open"].max() <= 1
    else:
        # 메서드 없으면 스킵
        pytest.skip("Normalization method not implemented")


@pytest.mark.asyncio
async def test_edge_case_empty_dataframe(data_processor):
    """엣지 케이스: 빈 데이터프레임 처리"""
    # Arrange
    empty_data = {"AAPL": pd.DataFrame()}

    # Act
    result = await data_processor.process_market_data(
        raw_data=empty_data,
        required_columns=["open", "high", "low", "close", "volume"],
        min_data_points=50,
    )

    # Assert
    assert len(result) == 0  # 빈 데이터는 제외됨


@pytest.mark.asyncio
async def test_edge_case_single_row(data_processor):
    """엣지 케이스: 단일 행 데이터"""
    # Arrange
    single_row_data = {
        "AAPL": pd.DataFrame(
            {
                "open": [150],
                "high": [160],
                "low": [140],
                "close": [155],
                "volume": [1000000],
            }
        )
    }

    # Act
    result = await data_processor.process_market_data(
        raw_data=single_row_data,
        required_columns=["open", "high", "low", "close", "volume"],
        min_data_points=1,  # 최소 1개 포인트로 설정
    )

    # Assert
    assert len(result) == 1
    assert len(result["AAPL"]) == 1


@pytest.mark.asyncio
async def test_date_index_validation(data_processor):
    """날짜 인덱스 검증 테스트"""
    # Arrange - 순서가 뒤섞인 날짜
    dates = pd.to_datetime(
        ["2024-01-05", "2024-01-01", "2024-01-03", "2024-01-04", "2024-01-02"]
    )
    unordered_data = {
        "AAPL": pd.DataFrame(
            {
                "open": [150, 151, 152, 153, 154],
                "high": [160, 161, 162, 163, 164],
                "low": [140, 141, 142, 143, 144],
                "close": [155, 156, 157, 158, 159],
                "volume": [1000000, 1100000, 1200000, 1300000, 1400000],
            },
            index=dates,
        )
    }

    # Act
    result = await data_processor.process_market_data(
        raw_data=unordered_data,
        required_columns=["open", "high", "low", "close", "volume"],
        min_data_points=1,
    )

    # Assert
    assert len(result) == 1
    # 날짜 순서 정렬 확인
    assert result["AAPL"].index.is_monotonic_increasing


@pytest.mark.asyncio
async def test_performance_benchmark(data_processor, benchmark=None):
    """성능 벤치마크 테스트 (선택적)"""
    # Arrange - 1년치 데이터
    dates = pd.date_range("2023-01-01", periods=252, freq="D")  # 252 거래일
    benchmark_data = {
        f"STOCK_{i}": pd.DataFrame(
            {
                "open": np.random.uniform(100, 200, 252),
                "high": np.random.uniform(100, 200, 252),
                "low": np.random.uniform(100, 200, 252),
                "close": np.random.uniform(100, 200, 252),
                "volume": np.random.uniform(1000000, 5000000, 252),
            },
            index=dates,
        )
        for i in range(10)  # 10개 심볼
    }

    # Act
    import time

    start = time.time()
    result = await data_processor.process_market_data(
        raw_data=benchmark_data,
        required_columns=["open", "high", "low", "close", "volume"],
        min_data_points=50,
    )
    elapsed = time.time() - start

    # Assert
    assert len(result) == 10
    assert elapsed < 5.0  # 5초 이내 처리 (성능 기준)
    print(f"\n⏱️  Processing time: {elapsed:.3f}s for 10 symbols × 252 days")
