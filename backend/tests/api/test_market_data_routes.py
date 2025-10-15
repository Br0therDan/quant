"""
Test for Market Data API Routes

NOTE: 이 테스트는 레거시 API 구조를 테스트합니다.
현재 API는 도메인별로 분리되어 새로운 구조로 개선되었습니다.
"""

import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app
from app.services.market_data import MarketDataService

pytestmark = pytest.mark.skip(reason="Legacy API tests - 새 API 구조로 마이그레이션 필요")


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def mock_service():
    """Mock service fixture"""
    return AsyncMock(spec=MarketDataService)


def test_health_check(client):
    """Test health check endpoint"""
    with (
        patch("app.api.routes.health.get_settings") as mock_settings,
        patch("app.api.routes.health.MarketData.aggregate") as mock_aggregate,
    ):
        mock_settings.return_value.alpha_vantage_api_key = "test_key"
        mock_aggregate.return_value.to_list = AsyncMock(
            return_value=[
                {
                    "unique_symbols": ["AAPL", "GOOGL"],
                    "latest_date": datetime.now(timezone.utc),
                }
            ]
        )

        response = client.get("/api/v1/health/")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["alpha_vantage_available"] is True


def test_get_available_symbols(client):
    """Test get available symbols endpoint"""
    with patch(
        "app.api.routes.market_data.get_market_data_service"
    ) as mock_get_service:
        mock_service = AsyncMock()
        mock_service.get_available_symbols.return_value = ["AAPL", "GOOGL", "MSFT"]
        mock_get_service.return_value = mock_service

        response = client.get("/api/v1/market-data/symbols")

        assert response.status_code == 200
        assert response.json() == ["AAPL", "GOOGL", "MSFT"]


def test_get_market_data_invalid_date_range(client):
    """Test get market data with invalid date range"""
    response = client.get(
        "/api/v1/market-data/data/AAPL",
        params={
            "start_date": "2023-12-31",
            "end_date": "2023-01-01",  # End before start
        },
    )

    assert response.status_code == 400
    assert "Start date must be before end date" in response.json()["detail"]


def test_get_market_data_future_date(client):
    """Test get market data with future start date"""
    # Test invalid date range (future dates)
    response = client.get(
        "/api/v1/market-data/data/AAPL",
        params={"start_date": "2030-01-01", "end_date": "2030-12-31"},  # Future date
    )

    assert response.status_code == 400
    assert "Start date cannot be in the future" in response.json()["detail"]


def test_get_data_coverage(client):
    """Test get data coverage endpoint"""
    with patch(
        "app.api.routes.market_data.get_market_data_service"
    ) as mock_get_service:
        mock_service = AsyncMock()
        mock_service.get_data_coverage.return_value = {
            "symbol": "AAPL",
            "available": True,
            "total_records": 252,
            "date_range": {
                "start": datetime(2023, 1, 1),
                "end": datetime(2023, 12, 31),
            },
        }
        mock_get_service.return_value = mock_service

        response = client.get("/api/v1/market-data/coverage/AAPL")

        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "AAPL"
        assert data["available"] is True


def test_bulk_data_request_empty_symbols(client):
    """Test bulk data request with empty symbols list"""
    response = client.post(
        "/api/v1/market-data/data/bulk",
        json={
            "symbols": [],  # Empty list
            "start_date": "2023-01-01T00:00:00",
            "end_date": "2023-12-31T00:00:00",
        },
    )

    assert response.status_code == 400
    assert "Symbols list cannot be empty" in response.json()["detail"]


def test_analyze_data_quality(client):
    """Test analyze data quality endpoint"""
    with patch(
        "app.api.routes.market_data.get_market_data_service"
    ) as mock_get_service:
        mock_service = AsyncMock()
        mock_quality = AsyncMock()
        mock_quality.symbol = "AAPL"
        mock_quality.date_range_start = datetime(2023, 1, 1)
        mock_quality.date_range_end = datetime(2023, 12, 31)
        mock_quality.total_records = 252
        mock_quality.missing_days = 0
        mock_quality.duplicate_records = 0
        mock_quality.price_anomalies = 0
        mock_quality.quality_score = 100.0
        mock_quality.analyzed_at = datetime.now(timezone.utc)

        mock_service.analyze_data_quality.return_value = mock_quality
        mock_get_service.return_value = mock_service

        response = client.get(
            "/api/v1/market-data/quality/AAPL",
            params={
                "start_date": "2023-01-01T00:00:00",
                "end_date": "2023-12-31T00:00:00",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "AAPL"
        assert data["quality_score"] == 100.0
