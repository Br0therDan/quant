"""
Test for Market Data Service
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

from app.services.market_data_service import MarketDataService
from app.models.market_data import MarketData


@pytest.fixture
def service():
    """Fixture for MarketDataService"""
    return MarketDataService()


@pytest.fixture
def sample_market_data():
    """Fixture for sample market data"""
    base_date = datetime(2023, 1, 1)
    return [
        MarketData(
            symbol="AAPL",
            date=base_date + timedelta(days=i),
            open_price=150.0 + i,
            high_price=155.0 + i,
            low_price=148.0 + i,
            close_price=152.0 + i,
            volume=1000000 + i * 1000,
            source="alpha_vantage",
        )
        for i in range(5)
    ]


@pytest.mark.asyncio
async def test_get_market_data_cached(service, sample_market_data):
    """Test getting cached market data"""
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 1, 5)

    with patch.object(MarketData, "find") as mock_find:
        mock_find.return_value.sort.return_value.to_list = AsyncMock(
            return_value=sample_market_data
        )

        result = await service.get_market_data("AAPL", start_date, end_date)

        assert len(result) == 5
        assert result[0].symbol == "AAPL"
        mock_find.assert_called_once()


@pytest.mark.asyncio
async def test_get_available_symbols(service):
    """Test getting available symbols"""
    mock_result = [{"_id": "AAPL"}, {"_id": "GOOGL"}, {"_id": "MSFT"}]

    with patch.object(MarketData, "aggregate") as mock_aggregate:
        mock_aggregate.return_value.to_list = AsyncMock(return_value=mock_result)

        symbols = await service.get_available_symbols()

        assert symbols == ["AAPL", "GOOGL", "MSFT"]
        mock_aggregate.assert_called_once()


@pytest.mark.asyncio
async def test_get_data_coverage(service):
    """Test getting data coverage"""
    mock_result = [
        {
            "_id": "AAPL",
            "min_date": datetime(2023, 1, 1),
            "max_date": datetime(2023, 12, 31),
            "total_records": 252,
        }
    ]

    with patch.object(MarketData, "aggregate") as mock_aggregate:
        mock_aggregate.return_value.to_list = AsyncMock(return_value=mock_result)

        coverage = await service.get_data_coverage("AAPL")

        assert coverage["symbol"] == "AAPL"
        assert coverage["available"] is True
        assert coverage["total_records"] == 252
        assert coverage["date_range"]["start"] == datetime(2023, 1, 1)


@pytest.mark.asyncio
async def test_analyze_data_quality(service, sample_market_data):
    """Test data quality analysis"""
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 1, 5)

    with (
        patch.object(MarketData, "find") as mock_find,
        patch(
            "app.models.market_data.DataQuality.insert", new_callable=AsyncMock
        ) as mock_insert,
    ):
        mock_find.return_value.sort.return_value.to_list = AsyncMock(
            return_value=sample_market_data
        )

        quality = await service.analyze_data_quality("AAPL", start_date, end_date)

        assert quality.symbol == "AAPL"
        assert quality.total_records == 5
        assert quality.quality_score >= 0
        mock_insert.assert_called_once()


def test_calculate_quality_score(service):
    """Test quality score calculation"""
    score = service._calculate_quality_score(
        total_records=250,
        missing_days=2,
        duplicate_records=0,
        price_anomalies=1,
        expected_days=252,
    )

    # Should be close to 100 with minimal deductions
    assert 95 <= score <= 100


def test_is_data_complete(service, sample_market_data):
    """Test data completeness check"""
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 1, 5)

    # Data should be complete
    assert service._is_data_complete(sample_market_data, start_date, end_date) is True

    # Data should be incomplete for wider range
    end_date_extended = datetime(2023, 1, 10)
    assert (
        service._is_data_complete(sample_market_data, start_date, end_date_extended)
        is False
    )
