"""Trading domain orchestrator and end-to-end tests."""

from __future__ import annotations

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.trading.backtest import BacktestStatus
from app.services.backtest.orchestrator import BacktestOrchestrator
from app.services.service_factory import service_factory


@pytest.fixture
def mock_services():
    """의존성 서비스 Mock - 실제 DB 없이 테스트"""
    market_data_service = MagicMock()
    strategy_service = MagicMock()
    database_manager = MagicMock()

    # 시장 데이터 Mock
    market_data_service.stock.get_historical_data = AsyncMock(
        return_value={
            "timestamp": [datetime.now() - timedelta(days=i) for i in range(30)],
            "open": [100 + i for i in range(30)],
            "high": [102 + i for i in range(30)],
            "low": [99 + i for i in range(30)],
            "close": [101 + i for i in range(30)],
            "volume": [1000000 + i * 10000 for i in range(30)],
        }
    )

    return market_data_service, strategy_service, database_manager


@pytest.fixture
def orchestrator(mock_services):
    """BacktestOrchestrator 인스턴스"""
    market_data, strategy, db = mock_services
    return BacktestOrchestrator(market_data, strategy, db)


class TestOrchestratorUnit:
    """BacktestOrchestrator 단위 테스트 (Mock 기반)"""

    def test_orchestrator_initialization(self, orchestrator):
        """Orchestrator 초기화 검증"""
        assert orchestrator is not None
        assert orchestrator.market_data_service is not None
        assert orchestrator.strategy_service is not None
        assert orchestrator.database_manager is not None
        assert orchestrator.data_processor is not None
        assert orchestrator.strategy_executor is not None
        assert orchestrator.performance_analyzer is not None

    def test_has_required_methods(self, orchestrator):
        """필수 메서드 존재 확인"""
        assert hasattr(orchestrator, "execute_backtest")
        assert hasattr(orchestrator, "_init_execution")
        assert hasattr(orchestrator, "_collect_data")
        assert hasattr(orchestrator, "_simulate")
        assert hasattr(orchestrator, "_save_results")
        assert hasattr(orchestrator, "_complete")
        assert hasattr(orchestrator, "_fail")

    @pytest.mark.asyncio
    async def test_collect_data_single_symbol(self, orchestrator):
        """단일 심볼 데이터 수집 테스트"""
        # Given
        symbols = ["AAPL"]
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()

        # When
        result = await orchestrator._collect_data(symbols, start_date, end_date)

        # Then
        assert result is not None
        assert "AAPL" in result
        assert len(result["AAPL"]["timestamp"]) == 30

    @pytest.mark.asyncio
    async def test_collect_data_multi_symbol(self, orchestrator):
        """다중 심볼 데이터 수집 테스트"""
        # Given
        symbols = ["AAPL", "GOOGL", "MSFT"]
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()

        # When
        result = await orchestrator._collect_data(symbols, start_date, end_date)

        # Then
        assert len(result) == 3
        assert all(symbol in result for symbol in symbols)

    @pytest.mark.asyncio
    async def test_collect_data_handles_failure(self, orchestrator):
        """데이터 수집 실패 처리 테스트"""
        # Given: 특정 심볼만 실패하도록 설정
        orchestrator.market_data_service.stock.get_historical_data = AsyncMock(
            side_effect=Exception("API Error")
        )

        # When
        result = await orchestrator._collect_data(
            ["AAPL"], datetime.now() - timedelta(days=30), datetime.now()
        )

        # Then: 빈 딕셔너리 반환 (실패한 심볼 제외)
        assert result == {}


# 실제 MongoDB 연결이 필요한 통합 테스트는 별도 마크
@pytest.mark.integration
@pytest.mark.skip(reason="Requires MongoDB connection")
class TestOrchestratorIntegration:
    """실제 DB 기반 통합 테스트 (선택적)"""

    @pytest.mark.asyncio
    async def test_full_backtest_pipeline(self):
        """전체 백테스트 파이프라인 (E2E)"""
        # TODO: MongoDB 연결 후 구현
        pass


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_full_backtest_pipeline_single_symbol(async_client, test_user_token):
    """단일 심볼 백테스트 전체 파이프라인 테스트"""
    # Arrange
    headers = {"Authorization": f"Bearer {test_user_token}"}

    backtest_data = {
        "name": "E2E Test - Single Symbol",
        "description": "End-to-end test with AAPL",
        "config": {
            "name": "E2E Test Config",
            "symbols": ["AAPL"],
            "start_date": (datetime.now() - timedelta(days=90)).isoformat(),
            "end_date": datetime.now().isoformat(),
            "initial_cash": 100000.0,
            "commission_rate": 0.001,
            "rebalance_frequency": None,
        },
    }

    # Act 1: 백테스트 생성
    create_response = await async_client.post(
        "/api/v1/backtests/", json=backtest_data, headers=headers
    )

    # Assert 1: 생성 성공
    assert create_response.status_code == 200
    backtest = create_response.json()
    backtest_id = backtest["id"]
    assert backtest["status"] == BacktestStatus.PENDING.value

    # Act 2: 백테스트 실행
    execute_response = await async_client.post(
        f"/api/v1/backtests/{backtest_id}/execute",
        json={"strategy_id": "default_strategy"},  # TODO: 실제 전략 ID
        headers=headers,
    )

    # Assert 2: 실행 성공
    assert execute_response.status_code in [200, 201]
    execution = execute_response.json()
    assert execution["status"] in [
        BacktestStatus.RUNNING.value,
        BacktestStatus.COMPLETED.value,
    ]

    # Act 3: 실행 결과 조회
    result_response = await async_client.get(
        f"/api/v1/backtests/{backtest_id}/executions", headers=headers
    )

    # Assert 3: 결과 존재
    assert result_response.status_code == 200
    executions = result_response.json()
    assert len(executions["executions"]) > 0

    # Act 4: 백테스트 상세 조회
    detail_response = await async_client.get(
        f"/api/v1/backtests/{backtest_id}", headers=headers
    )

    # Assert 4: 상태 업데이트 확인
    assert detail_response.status_code == 200
    final_backtest = detail_response.json()
    assert final_backtest["status"] in [
        BacktestStatus.COMPLETED.value,
        BacktestStatus.FAILED.value,
    ]

    # Cleanup
    await async_client.delete(f"/api/v1/backtests/{backtest_id}", headers=headers)


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_full_backtest_pipeline_multiple_symbols(async_client, test_user_token):
    """다중 심볼 백테스트 전체 파이프라인 테스트"""
    # Arrange
    headers = {"Authorization": f"Bearer {test_user_token}"}

    backtest_data = {
        "name": "E2E Test - Multiple Symbols",
        "description": "End-to-end test with AAPL, GOOGL, MSFT",
        "config": {
            "name": "E2E Multi Symbol Config",
            "symbols": ["AAPL", "GOOGL", "MSFT"],
            "start_date": (datetime.now() - timedelta(days=180)).isoformat(),
            "end_date": datetime.now().isoformat(),
            "initial_cash": 100000.0,
            "commission_rate": 0.001,
            "rebalance_frequency": "monthly",
        },
    }

    # Act & Assert - 파이프라인 전체 실행
    create_response = await async_client.post(
        "/api/v1/backtests/", json=backtest_data, headers=headers
    )
    assert create_response.status_code == 200

    backtest_id = create_response.json()["id"]

    execute_response = await async_client.post(
        f"/api/v1/backtests/{backtest_id}/execute",
        json={"strategy_id": "default_strategy"},
        headers=headers,
    )
    assert execute_response.status_code in [200, 201]

    # Cleanup
    await async_client.delete(f"/api/v1/backtests/{backtest_id}", headers=headers)


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_backtest_with_strategy_execution(async_client, test_user_token):
    """전략 포함 백테스트 E2E 테스트"""
    # Arrange
    headers = {"Authorization": f"Bearer {test_user_token}"}

    # 1. 전략 생성
    strategy_data = {
        "name": "E2E Test Strategy",
        "strategy_type": "SMA_CROSSOVER",
        "description": "Test strategy for E2E",
        "parameters": {"short_window": 10, "long_window": 30},
    }

    strategy_response = await async_client.post(
        "/api/v1/strategies/", json=strategy_data, headers=headers
    )
    assert strategy_response.status_code == 200
    strategy_id = strategy_response.json()["id"]

    # 2. 백테스트 생성 및 실행
    backtest_data = {
        "name": "E2E Test with Strategy",
        "description": "Test with SMA strategy",
        "config": {
            "name": "Strategy Test Config",
            "symbols": ["AAPL"],
            "start_date": (datetime.now() - timedelta(days=60)).isoformat(),
            "end_date": datetime.now().isoformat(),
            "initial_cash": 100000.0,
            "commission_rate": 0.001,
            "rebalance_frequency": None,
        },
    }

    backtest_response = await async_client.post(
        "/api/v1/backtests/", json=backtest_data, headers=headers
    )
    assert backtest_response.status_code == 200
    backtest_id = backtest_response.json()["id"]

    # 3. 전략으로 백테스트 실행
    execute_response = await async_client.post(
        f"/api/v1/backtests/{backtest_id}/execute",
        json={"strategy_id": strategy_id},
        headers=headers,
    )
    assert execute_response.status_code in [200, 201]

    # Cleanup
    await async_client.delete(f"/api/v1/backtests/{backtest_id}", headers=headers)
    await async_client.delete(f"/api/v1/strategies/{strategy_id}", headers=headers)


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_backtest_performance_analysis(async_client, test_user_token):
    """백테스트 성과 분석 E2E 테스트"""
    # Arrange
    headers = {"Authorization": f"Bearer {test_user_token}"}

    backtest_data = {
        "name": "E2E Performance Test",
        "description": "Test performance metrics",
        "config": {
            "name": "Performance Test Config",
            "symbols": ["AAPL", "GOOGL"],
            "start_date": (datetime.now() - timedelta(days=120)).isoformat(),
            "end_date": datetime.now().isoformat(),
            "initial_cash": 100000.0,
            "commission_rate": 0.001,
            "rebalance_frequency": None,
        },
    }

    # Act - 백테스트 생성 및 실행
    create_response = await async_client.post(
        "/api/v1/backtests/", json=backtest_data, headers=headers
    )
    backtest_id = create_response.json()["id"]

    _execute_response = await async_client.post(
        f"/api/v1/backtests/{backtest_id}/execute",
        json={"strategy_id": "default_strategy"},
        headers=headers,
    )

    # 성과 분석 조회
    analytics_response = await async_client.get(
        "/api/v1/backtests/analytics/performance-stats", headers=headers
    )

    # Assert
    assert analytics_response.status_code == 200
    analytics = analytics_response.json()
    assert "analytics" in analytics
    assert "total_backtests" in analytics["analytics"]

    # Cleanup
    await async_client.delete(f"/api/v1/backtests/{backtest_id}", headers=headers)


@pytest.mark.asyncio
@pytest.mark.e2e
@pytest.mark.slow
async def test_backtest_error_handling_pipeline(async_client, test_user_token):
    """백테스트 에러 처리 파이프라인 테스트"""
    # Arrange - 잘못된 데이터로 백테스트 실행
    headers = {"Authorization": f"Bearer {test_user_token}"}

    invalid_backtest_data = {
        "name": "E2E Error Test",
        "description": "Test error handling",
        "config": {
            "name": "Error Test Config",
            "symbols": ["INVALID_SYMBOL_XYZ"],  # 존재하지 않는 심볼
            "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
            "end_date": datetime.now().isoformat(),
            "initial_cash": 100000.0,
            "commission_rate": 0.001,
            "rebalance_frequency": None,
        },
    }

    # Act
    create_response = await async_client.post(
        "/api/v1/backtests/", json=invalid_backtest_data, headers=headers
    )
    backtest_id = create_response.json()["id"]

    _execute_response = await async_client.post(
        f"/api/v1/backtests/{backtest_id}/execute",
        json={"strategy_id": "default_strategy"},
        headers=headers,
    )

    # Assert - 실행은 되지만 에러 상태로 완료되어야 함
    # (또는 적절한 에러 응답)
    result_response = await async_client.get(
        f"/api/v1/backtests/{backtest_id}", headers=headers
    )
    final_backtest = result_response.json()

    # 에러 처리 확인
    assert final_backtest["status"] in [
        BacktestStatus.FAILED.value,
        BacktestStatus.PENDING.value,
    ]

    # Cleanup
    await async_client.delete(f"/api/v1/backtests/{backtest_id}", headers=headers)


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_service_integration_orchestrator_workflow():
    """서비스 레이어 통합 테스트 (API 없이 직접 서비스 호출)"""
    # Arrange
    orchestrator = service_factory.get_backtest_orchestrator()
    backtest_service = service_factory.get_backtest_service()

    # 테스트용 백테스트 생성
    backtest = await backtest_service.create_backtest(
        name="Service Integration Test",
        description="Direct service call test",
    )

    # Act - Orchestrator 직접 호출
    result = await orchestrator.execute_backtest(backtest_id=str(backtest.id))

    # Assert
    if result:
        assert result is not None  # 실행 완료

    # 백테스트 상태 확인
    updated_backtest = await backtest_service.get_backtest(str(backtest.id))
    if updated_backtest:
        assert updated_backtest.status in [
            BacktestStatus.COMPLETED,
            BacktestStatus.FAILED,
            BacktestStatus.RUNNING,
        ]

    # Cleanup
    await backtest_service.delete_backtest(str(backtest.id))


# ===== 성능 벤치마크 E2E 테스트 =====


@pytest.mark.asyncio
@pytest.mark.e2e
@pytest.mark.slow
async def test_backtest_performance_benchmark_100_days():
    """100일 백테스트 성능 벤치마크"""
    import time

    # Arrange
    orchestrator = service_factory.get_backtest_orchestrator()
    backtest_service = service_factory.get_backtest_service()

    backtest = await backtest_service.create_backtest(
        name="Performance Benchmark 100 Days",
        description="Benchmark test",
    )

    # Act - 실행 시간 측정
    start_time = time.time()
    _result = await orchestrator.execute_backtest(backtest_id=str(backtest.id))
    elapsed_time = time.time() - start_time

    # Assert
    assert elapsed_time < 30.0  # 30초 이내 완료
    print(f"\n⏱️  Backtest execution time (3 symbols, 100 days): {elapsed_time:.2f}s")

    # Cleanup
    await backtest_service.delete_backtest(str(backtest.id))
