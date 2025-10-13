"""
Test for Market Data Service
"""

import pytest
from unittest.mock import MagicMock

from app.services.market_data_service import MarketDataService
from app.services.database_manager import DatabaseManager


@pytest.fixture
def mock_database_manager():
    """Mock DatabaseManager"""
    mock_dm = MagicMock(spec=DatabaseManager)
    mock_dm.connect = MagicMock()
    return mock_dm


@pytest.fixture
def service(mock_database_manager):
    """Fixture for MarketDataService"""
    return MarketDataService(database_manager=mock_database_manager)


@pytest.mark.asyncio
async def test_health_check(service):
    """Test service health check"""
    health = await service.health_check()

    assert health is not None
    assert "status" in health
    assert "services" in health
    assert health["status"] in ["healthy", "degraded", "error"]


@pytest.mark.asyncio
async def test_stock_service_property(service):
    """Test stock service property access"""
    stock_service = service.stock

    assert stock_service is not None
    # Singleton 패턴 검증
    assert service.stock is stock_service


@pytest.mark.asyncio
async def test_crypto_service_property(service):
    """Test crypto service property access"""
    crypto_service = service.crypto

    assert crypto_service is not None
    assert service.crypto is crypto_service


@pytest.mark.asyncio
async def test_fundamental_service_property(service):
    """Test fundamental service property access"""
    fundamental_service = service.fundamental

    assert fundamental_service is not None
    assert service.fundamental is fundamental_service


@pytest.mark.asyncio
async def test_economic_service_property(service):
    """Test economic indicator service property access"""
    economic_service = service.economic

    assert economic_service is not None
    assert service.economic is economic_service


@pytest.mark.asyncio
async def test_intelligence_service_property(service):
    """Test intelligence service property access"""
    intelligence_service = service.intelligence

    assert intelligence_service is not None
    assert service.intelligence is intelligence_service


@pytest.mark.asyncio
async def test_close(service):
    """Test service cleanup"""
    # Initialize all services
    _ = service.stock
    _ = service.crypto
    _ = service.fundamental

    # Close should not raise
    await service.close()

    # After close, services should still be accessible (lazy init)
    assert service.stock is not None
