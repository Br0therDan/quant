"""
BacktestOrchestrator 통합 테스트
Phase 3 - 전체 백테스트 파이프라인 검증

Note: 실제 MongoDB 연결이 필요합니다.
pytest-asyncio 설치 필요: uv add --dev pytest-asyncio
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from app.services.backtest.orchestrator import BacktestOrchestrator


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
