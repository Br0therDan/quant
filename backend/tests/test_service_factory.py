"""
ServiceFactory 의존성 주입 테스트
"""

from app.services.service_factory import service_factory


def test_backtest_service_dependencies():
    """백테스트 서비스 의존성 주입 검증"""
    # Given
    backtest_service = service_factory.get_backtest_service()

    # Then
    assert backtest_service is not None
    assert backtest_service.market_data_service is not None
    assert backtest_service.strategy_service is not None
    assert backtest_service.database_manager is not None
    assert backtest_service.integrated_executor is not None


def test_backtest_service_singleton():
    """백테스트 서비스 싱글톤 검증"""
    # Given/When
    service1 = service_factory.get_backtest_service()
    service2 = service_factory.get_backtest_service()

    # Then
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

    # 의존성 체인 검증
    assert backtest_service.database_manager is db_manager
    assert backtest_service.market_data_service is market_service
    assert backtest_service.strategy_service is strategy_service
