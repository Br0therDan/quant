"""
ServiceFactory 의존성 주입 테스트
"""

from app.services.service_factory import service_factory


def test_backtest_service_singleton():
    """백테스트 서비스 싱글톤 검증"""
    # Given/When
    service1 = service_factory.get_backtest_service()
    service2 = service_factory.get_backtest_service()

    # Then
    assert service1 is not None
    assert service1 is service2


def test_service_initialization_order():
    """서비스 초기화 순서 검증"""
    # Given/When
    db_manager = service_factory.get_database_manager()
    market_service = service_factory.get_market_data_service()
    strategy_service = service_factory.get_strategy_service()
    backtest_service = service_factory.get_backtest_service()

    # Then - 모든 서비스가 올바르게 초기화되어야 함
    assert db_manager is not None
    assert market_service is not None
    assert strategy_service is not None
    assert backtest_service is not None


def test_market_data_service_dependencies():
    """마켓 데이터 서비스 의존성 주입 검증"""
    # Given
    market_service = service_factory.get_market_data_service()

    # Then
    assert market_service is not None
    assert market_service.database_manager is not None


def test_strategy_service_dependencies():
    """전략 서비스 의존성 주입 검증"""
    # Given
    strategy_service = service_factory.get_strategy_service()

    # Then
    assert strategy_service is not None
