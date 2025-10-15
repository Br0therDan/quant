"""
백테스트 워크플로우 조율자 (Orchestrator Pattern)

현재 구현 단계:
- Phase 2: 핵심 Orchestrator 패턴 (레이어드 아키텍처) ✅
- Phase 3 선행 구현 기능 (조기 도입):
  * 병렬 데이터 수집 및 DuckDB 저장 (원래 Phase 3.2)
  * Circuit Breaker 패턴 (원래 Phase 3.3)
  * 모니터링 및 메트릭 수집 (원래 Phase 3.4)

Phase 3 기능을 Phase 2에 포함한 이유:
- 성능 및 안정성을 초기부터 고려
- 리팩토링 비용 절감 (나중에 추가하는 것보다 효율적)
- 프로덕션 환경 대비
"""

import logging
import uuid
from typing import Optional, TYPE_CHECKING, Dict

from beanie import PydanticObjectId
import structlog

from app.services.backtest.monitoring import (
    BacktestMonitor,
    get_global_metrics,
    log_backtest_event,
    log_error,
)

if TYPE_CHECKING:
    from app.services.market_data import MarketDataService
    from app.services.trading.strategy_service import StrategyService
    from app.services.database_manager import DatabaseManager
    from app.services.ml_platform.services.ml_signal_service import MLSignalService
    from app.schemas.ml_platform.predictive import MLSignalInsight

from app.models.trading.backtest import (
    Backtest,
    BacktestResult,
)
from app.services.backtest.executor import StrategyExecutor
from app.services.backtest.performance import PerformanceAnalyzer
from app.services.backtest.data_processor import DataProcessor

from .base import CircuitBreaker
from .initialization import BacktestInitializer
from .data_collection import DataCollector
from .simulation import SimulationRunner
from .result_storage import ResultStorage


logger = logging.getLogger(__name__)
structured_logger = structlog.get_logger(__name__)


class BacktestOrchestrator:
    """백테스트 워크플로우 조율자

    Phase 2 구현: 레이어드 아키텍처 + Orchestrator 패턴
    - 데이터 수집 → 전처리 → 신호 생성 → 시뮬레이션 → 성과 분석
    - 각 단계를 전문 컴포넌트로 분리 (DataProcessor, StrategyExecutor, TradeEngine, PerformanceAnalyzer)

    Phase 3 선행 기능 (프로덕션 품질 향상):
    - 병렬 데이터 수집 (asyncio.gather)
    - Circuit Breaker 패턴 (장애 격리)
    - 실시간 모니터링 (메트릭 수집)
    - DuckDB 결과 저장 (고성능 분석)
    """

    def __init__(
        self,
        market_data_service: "MarketDataService",
        strategy_service: "StrategyService",
        database_manager: "DatabaseManager",
        ml_signal_service: "MLSignalService | None" = None,
    ):
        self.market_data_service = market_data_service
        self.strategy_service = strategy_service
        self.database_manager = database_manager
        self.ml_signal_service = ml_signal_service

        # Phase 2 핵심 컴포넌트
        self.data_processor = DataProcessor()
        self.strategy_executor = StrategyExecutor(strategy_service)
        self.performance_analyzer = PerformanceAnalyzer()

        # Phase 3 선행 구현: Circuit Breaker (장애 격리)
        self.circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60)

        # 모듈 인스턴스 생성 (Delegation 패턴)
        self._initializer = BacktestInitializer()
        self._data_collector = DataCollector(market_data_service, self.circuit_breaker)
        self._simulator = SimulationRunner()
        self._storage = ResultStorage(database_manager)

        # Phase 3 선행 구현: 모니터링 (메트릭 수집)
        self.metrics = get_global_metrics()

        logger.info("BacktestOrchestrator initialized (Phase 2 + Phase 3 선행 기능)")
        structured_logger.info(
            "orchestrator_initialized",
            phase="2",
            enhancements=[
                "parallel_data_collection",
                "circuit_breaker",
                "monitoring",
                "duckdb_storage",
            ],
        )

    async def execute_backtest(self, backtest_id: str) -> Optional[BacktestResult]:
        """백테스트 실행 (Phase 2 핵심 + Phase 3 선행 기능)

        실행 흐름:
        1. 초기화 (BacktestInitializer)
        2. 데이터 수집 (DataCollector - 병렬 처리, Phase 3.2 선행)
        3. 데이터 전처리 (DataProcessor - Phase 2)
        4. 신호 생성 (StrategyExecutor - Phase 2)
        5. 시뮬레이션 (SimulationRunner - Phase 2)
        6. 성과 분석 (PerformanceAnalyzer - Phase 2)
        7. 결과 저장 (ResultStorage - DuckDB, Phase 3.2 선행)
        8. 완료/실패 (BacktestInitializer)

        모니터링: 각 단계별 메트릭 수집 (Phase 3.4 선행)
        장애 격리: Circuit Breaker 적용 (Phase 3.3 선행)
        """
        backtest = None
        execution = None

        # P3.4: 모니터링 컨텍스트
        with BacktestMonitor(
            backtest_id=backtest_id,
            operation="execute_backtest",
            metrics_collector=self.metrics,
        ):
            try:
                backtest = await Backtest.get(PydanticObjectId(backtest_id))
                if not backtest:
                    return None

                execution_id = str(uuid.uuid4())
                execution = await self._initializer.init_execution(
                    backtest, execution_id
                )

                log_backtest_event(
                    "backtest_started",
                    backtest_id=backtest_id,
                    execution_id=execution_id,
                    symbols=backtest.config.symbols,
                    strategy_id=str(backtest.strategy_id),
                )

                # P3.4: 데이터 수집 타이머
                self.metrics.start_timer("data_collection")
                raw_data = await self._data_collector.collect_data(
                    backtest.config.symbols,
                    backtest.config.start_date,
                    backtest.config.end_date,
                )
                data_collection_time = self.metrics.stop_timer(
                    "data_collection",
                    labels={"symbol_count": str(len(backtest.config.symbols))},
                )

                # 전처리
                self.metrics.start_timer("data_processing")
                market_data = await self.data_processor.process_market_data(
                    raw_data=raw_data,
                    required_columns=["open", "high", "low", "close", "volume"],
                    min_data_points=30,
                )
                self.metrics.stop_timer("data_processing")

                if not market_data:
                    raise Exception("No market data after processing")

                log_backtest_event(
                    "data_collected",
                    backtest_id=backtest_id,
                    symbol_count=len(backtest.config.symbols),
                    data_points=sum(len(df) for df in market_data.values()),
                    collection_time=data_collection_time,
                )

                # 신호 생성
                self.metrics.start_timer("signal_generation")
                signals = await self.strategy_executor.generate_signals(
                    strategy_id=str(backtest.strategy_id),
                    market_data=market_data,
                    config=backtest.config,
                )
                signals = await self.strategy_executor.validate_signals(
                    signals, market_data
                )
                self.metrics.stop_timer("signal_generation")

                log_backtest_event(
                    "signals_generated",
                    backtest_id=backtest_id,
                    signal_count=len(signals),
                )

                signal_scores: Dict[str, "MLSignalInsight"] = {}
                if self.ml_signal_service and backtest.config.symbols:
                    signal_scores = await self.ml_signal_service.score_symbols(
                        backtest.config.symbols
                    )
                    for signal in signals:
                        symbol = signal.get("symbol")
                        if symbol and isinstance(symbol, str):
                            ml_signal = signal_scores.get(symbol)
                            if ml_signal:
                                signal["ml_probability"] = ml_signal.probability
                                signal["ml_recommendation"] = (
                                    ml_signal.recommendation.value
                                )

                    if signal_scores:
                        log_backtest_event(
                            "ml_signals_generated",
                            backtest_id=backtest_id,
                            signal_count=len(signal_scores),
                        )

                # 시뮬레이션
                self.metrics.start_timer("simulation")
                trades, portfolio_values = self._simulator.simulate(backtest, signals)
                self.metrics.stop_timer("simulation")

                log_backtest_event(
                    "simulation_completed",
                    backtest_id=backtest_id,
                    trade_count=len(trades),
                    portfolio_snapshots=len(portfolio_values),
                )

                # 성과 분석
                self.metrics.start_timer("performance_analysis")
                performance = await self.performance_analyzer.calculate_metrics(
                    portfolio_values=portfolio_values,
                    trades=trades,
                    initial_capital=backtest.config.initial_cash,
                )
                self.metrics.stop_timer("performance_analysis")

                # 저장
                self.metrics.start_timer("save_results")
                result = await self._storage.save_results(
                    backtest, execution, performance, trades, portfolio_values
                )
                self.metrics.stop_timer("save_results")

                await self._initializer.complete(backtest, execution, performance)

                logger.info(f"Backtest completed: {backtest_id}")
                log_backtest_event(
                    "backtest_completed",
                    backtest_id=backtest_id,
                    total_return=performance.total_return,
                    sharpe_ratio=performance.sharpe_ratio,
                )

                self.metrics.increment(
                    "backtest_completions_total",
                    labels={"status": "success"},
                )

                return result

            except Exception as e:
                logger.error(f"Backtest failed: {e}")
                log_error(e, backtest_id=backtest_id, operation="execute_backtest")
                await self._initializer.fail(backtest, execution, str(e))

                self.metrics.increment(
                    "backtest_completions_total",
                    labels={"status": "failed"},
                )

                return None
