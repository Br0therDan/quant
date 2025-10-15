"""
StrategyExecutor 테스트
Phase 3 - 전략 신호 생성 검증
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime, timedelta

from app.models.trading.backtest import BacktestConfig
from app.services.backtest.executor import StrategyExecutor


@pytest.fixture
def mock_strategy_service():
    """전략 서비스 Mock"""
    service = MagicMock()
    return service


@pytest.fixture
def executor(mock_strategy_service):
    """StrategyExecutor 인스턴스"""
    return StrategyExecutor(mock_strategy_service)


@pytest.fixture
def sample_market_data():
    """샘플 시장 데이터"""
    dates = [datetime.now() - timedelta(days=i) for i in range(30, 0, -1)]
    return {
        "AAPL": {
            "timestamp": dates,
            "open": [100 + i * 0.5 for i in range(30)],
            "high": [102 + i * 0.5 for i in range(30)],
            "low": [99 + i * 0.5 for i in range(30)],
            "close": [101 + i * 0.5 for i in range(30)],
            "volume": [1000000 + i * 10000 for i in range(30)],
        }
    }


@pytest.fixture
def sample_config():
    """샘플 백테스트 설정"""
    return BacktestConfig(
        name="Test Config",
        start_date=datetime.now() - timedelta(days=30),
        end_date=datetime.now(),
        symbols=["AAPL"],
        initial_cash=100000.0,
        rebalance_frequency="daily",
    )


class TestStrategyExecutor:
    """StrategyExecutor 테스트"""

    def test_initialization(self, executor):
        """초기화 검증"""
        assert executor is not None
        assert executor.strategy_service is not None

    def test_has_required_methods(self, executor):
        """필수 메서드 존재 확인"""
        assert hasattr(executor, "generate_signals")
        assert hasattr(executor, "_calculate_indicators")

    @pytest.mark.asyncio
    async def test_generate_signals_basic(
        self, executor, sample_market_data, sample_config
    ):
        """기본 신호 생성 테스트"""
        # Given: Mock 전략 및 전략 인스턴스 반환
        mock_strategy = MagicMock()
        mock_strategy.strategy_type = "MA_CROSSOVER"
        mock_strategy.config = {}

        mock_strategy_instance = MagicMock()
        mock_strategy_instance.generate_signals = MagicMock(
            return_value=[
                {
                    "symbol": "AAPL",
                    "action": "BUY",
                    "quantity": 10,
                    "price": 150.0,
                    "timestamp": datetime.now(),
                }
            ]
        )

        executor.strategy_service.get_strategy = AsyncMock(return_value=mock_strategy)
        executor.strategy_service.get_strategy_instance = AsyncMock(
            return_value=mock_strategy_instance
        )

        # When: 신호 생성
        signals = await executor.generate_signals(
            strategy_id="test_strategy",
            market_data=sample_market_data,
            config=sample_config,
        )

        # Then: 신호 반환됨
        assert signals is not None
        assert len(signals) > 0
        assert signals[0]["symbol"] == "AAPL"
        assert signals[0]["action"] in ["BUY", "SELL"]

    @pytest.mark.asyncio
    async def test_strategy_not_found(
        self, executor, sample_market_data, sample_config
    ):
        """전략을 찾을 수 없을 때 처리"""
        # Given: 전략 None 반환
        executor.strategy_service.get_strategy = AsyncMock(return_value=None)

        # When & Then: ValueError 발생
        with pytest.raises(ValueError, match="Strategy not found"):
            await executor.generate_signals(
                strategy_id="non_existent",
                market_data=sample_market_data,
                config=sample_config,
            )

    @pytest.mark.asyncio
    async def test_empty_market_data(self, executor, sample_config):
        """시장 데이터가 없을 때 처리"""
        # Given: 빈 시장 데이터 + Mock 전략
        empty_data = {}

        mock_strategy = MagicMock()
        mock_strategy.strategy_type = "MA_CROSSOVER"
        mock_strategy.config = {}

        mock_strategy_instance = MagicMock()
        mock_strategy_instance.generate_signals = MagicMock(return_value=[])

        executor.strategy_service.get_strategy = AsyncMock(return_value=mock_strategy)
        executor.strategy_service.get_strategy_instance = AsyncMock(
            return_value=mock_strategy_instance
        )

        # When: 신호 생성 시도
        signals = await executor.generate_signals(
            strategy_id="test_strategy",
            market_data=empty_data,
            config=sample_config,
        )

        # Then: 빈 리스트 반환
        assert signals == []
