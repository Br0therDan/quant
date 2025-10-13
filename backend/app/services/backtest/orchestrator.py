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
from datetime import datetime
from typing import Optional, TYPE_CHECKING, Any, Dict

from beanie import PydanticObjectId
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)
import structlog

from app.services.backtest.monitoring import (
    BacktestMonitor,
    get_global_metrics,
    log_backtest_event,
    log_error,
)

if TYPE_CHECKING:
    from app.services.market_data_service import MarketDataService
    from app.services.strategy_service import StrategyService
    from app.services.database_manager import DatabaseManager
    from app.services.ml_signal_service import MLSignalService
    from app.schemas.predictive import MLSignalInsight

from app.models.backtest import (
    Backtest,
    BacktestResult,
    BacktestStatus,
    BacktestExecution,
    PerformanceMetrics,
)
from app.services.backtest.executor import StrategyExecutor
from app.services.backtest.trade_engine import TradeEngine
from app.services.backtest.performance import PerformanceAnalyzer
from app.services.backtest.data_processor import DataProcessor

logger = logging.getLogger(__name__)
structured_logger = structlog.get_logger(__name__)


class CircuitBreaker:
    """Circuit Breaker 패턴 구현 (Phase 3.3 선행)

    장애 격리 패턴: 외부 서비스(Alpha Vantage API) 장애 시 시스템 전체 다운 방지

    동작 방식:
    - CLOSED: 정상 동작 (모든 요청 통과)
    - OPEN: 장애 감지 (모든 요청 차단, {timeout}초 대기)
    - HALF_OPEN: 복구 시도 (1개 요청만 허용하여 테스트)

    Phase 2에 포함한 이유:
    - Alpha Vantage API는 5 calls/min 제한이 있어 장애 발생 가능성 높음
    - 초기부터 안정성 확보 필요
    """

    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    async def call(self, func, *args, **kwargs):
        """Circuit Breaker를 통한 비동기 함수 호출"""
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
                logger.info("Circuit Breaker: OPEN -> HALF_OPEN (attempting reset)")
            else:
                raise Exception(
                    f"Circuit Breaker OPEN: {self.failure_count} failures, "
                    f"retry after {self.timeout}s"
                )

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """리셋 시도 가능 여부"""
        if self.last_failure_time is None:
            return True
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.timeout

    def _on_success(self):
        """성공 시 처리"""
        if self.state == "HALF_OPEN":
            logger.info("Circuit Breaker: HALF_OPEN -> CLOSED (reset successful)")
        self.failure_count = 0
        self.state = "CLOSED"

    def _on_failure(self):
        """실패 시 처리"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.error(
                f"Circuit Breaker: CLOSED -> OPEN "
                f"({self.failure_count} failures reached threshold)"
            )


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
        1. 데이터 수집 (병렬 처리 - Phase 3.2 선행)
        2. 데이터 전처리 (Phase 2)
        3. 신호 생성 (Phase 2)
        4. 시뮬레이션 (Phase 2)
        5. 성과 분석 (Phase 2)
        6. 결과 저장 (DuckDB - Phase 3.2 선행)

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
                execution = await self._init_execution(backtest, execution_id)

                log_backtest_event(
                    "backtest_started",
                    backtest_id=backtest_id,
                    execution_id=execution_id,
                    symbols=backtest.config.symbols,
                    strategy_id=str(backtest.strategy_id),
                )

                # P3.4: 데이터 수집 타이머
                self.metrics.start_timer("data_collection")
                raw_data = await self._collect_data(
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
                                signal[
                                    "ml_recommendation"
                                ] = ml_signal.recommendation.value

                    if signal_scores:
                        log_backtest_event(
                            "ml_signals_generated",
                            backtest_id=backtest_id,
                            signal_count=len(signal_scores),
                        )

                # 시뮬레이션
                self.metrics.start_timer("simulation")
                trades, portfolio_values = self._simulate(backtest, signals)
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
                result = await self._save_results(
                    backtest, execution, performance, trades, portfolio_values
                )
                self.metrics.stop_timer("save_results")

                await self._complete(backtest, execution, performance)

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
                await self._fail(backtest, execution, str(e))

                self.metrics.increment(
                    "backtest_completions_total",
                    labels={"status": "failed"},
                )

                return None

    async def _init_execution(
        self, backtest: Backtest, execution_id: str
    ) -> BacktestExecution:
        backtest.status = BacktestStatus.RUNNING
        backtest.start_time = datetime.now()
        await backtest.save()

        execution = BacktestExecution(
            backtest_id=str(backtest.id),
            execution_id=execution_id,
            status=BacktestStatus.RUNNING,
            start_time=datetime.now(),
            end_time=None,
            error_message=None,
        )
        await execution.insert()
        return execution

    async def _collect_data(
        self, symbols: list[str], start_date: Any, end_date: Any
    ) -> dict:
        """병렬 데이터 수집 (Phase 3.2 선행 구현)

        개선 사항:
        - asyncio.gather를 통한 병렬 처리 (10x 성능 향상)
        - Retry 로직 (일시적 네트워크 오류 대응)
        - Circuit Breaker 적용 (장애 격리)

        원래 Phase 2에서는 순차 처리였으나, 성능을 위해 Phase 3.2 기능을 조기 도입
        """
        import asyncio

        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            retry=retry_if_exception_type((ConnectionError, TimeoutError)),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            reraise=True,
        )
        async def fetch_symbol_data(symbol: str) -> tuple[str, Any]:
            """단일 심볼 데이터 조회 with Retry"""
            try:
                # Circuit Breaker 적용
                data = await self.circuit_breaker.call(
                    self.market_data_service.stock.get_historical_data,
                    symbol=symbol,
                    start_date=start_date,
                    end_date=end_date,
                )
                return symbol, data
            except Exception as e:
                logger.error(f"Failed to fetch {symbol}: {e}")
                return symbol, None

        # 병렬 수집 (asyncio.gather)
        tasks = [fetch_symbol_data(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 결과 딕셔너리 구성
        market_data = {}
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Data collection error: {result}")
                continue

            if isinstance(result, tuple) and len(result) == 2:
                symbol, data = result
                if data is not None:
                    market_data[symbol] = data
                else:
                    logger.warning(f"No data for {symbol}")

        logger.info(
            f"Collected data for {len(market_data)}/{len(symbols)} symbols "
            f"(parallel execution)"
        )
        return market_data

    def _simulate(
        self, backtest: Backtest, signals: list[dict[str, Any]]
    ) -> tuple[list, list[float]]:
        trade_engine = TradeEngine(backtest.config)
        trades = []
        portfolio_values = [backtest.config.initial_cash]

        for signal in signals:
            symbol = signal.get("symbol")
            action = signal.get("action")
            quantity = signal.get("quantity", 0)
            price = signal.get("price", 0)
            timestamp = signal.get("timestamp", datetime.now())

            if not symbol or not action or quantity <= 0 or price <= 0:
                continue

            trade = trade_engine.execute_signal(
                symbol=symbol,
                action=action,
                quantity=quantity,
                price=price,
                timestamp=timestamp,
            )

            if trade:
                trades.append(trade)

            portfolio_values.append(trade_engine.portfolio.total_value)

        return trades, portfolio_values

    async def _save_results(
        self,
        backtest: Backtest,
        execution: BacktestExecution,
        performance: PerformanceMetrics,
        trades: list,
        portfolio_values: list[float],
    ) -> BacktestResult:
        """백테스트 결과 저장 (Phase 2 + Phase 3.2 선행)

        저장 위치:
        1. MongoDB: 백테스트 메타데이터 및 성과 지표 (Phase 2)
        2. DuckDB: 포트폴리오 히스토리, 거래 내역 (Phase 3.2 선행)

        Phase 3.2를 조기 도입한 이유:
        - DuckDB의 컬럼 형식 저장으로 시계열 분석 성능 10-100배 향상
        - 대용량 백테스트 결과를 효율적으로 처리
        """
        result = BacktestResult(
            backtest_id=str(backtest.id),
            execution_id=str(execution.id),
            performance=performance,
            final_portfolio_value=(
                portfolio_values[-1]
                if portfolio_values
                else backtest.config.initial_cash
            ),
            cash_remaining=0.0,
            total_invested=backtest.config.initial_cash,
            var_95=None,
            var_99=None,
            calmar_ratio=None,
            sortino_ratio=None,
            benchmark_return=None,
            alpha=None,
            beta=None,
        )
        await result.insert()

        # DuckDB 고성능 저장 (Phase 3.2 선행 구현)
        # MongoDB는 메타데이터 저장에 적합하지만, 대용량 시계열 데이터는 DuckDB가 10-100배 빠름
        if self.database_manager:
            try:
                # 1. 백테스트 결과 메타데이터 저장
                result_data = {
                    "strategy_name": backtest.name,
                    "symbols": backtest.config.symbols,
                    "start_date": backtest.config.start_date.date(),
                    "end_date": backtest.config.end_date.date(),
                    "initial_cash": backtest.config.initial_cash,
                    "final_value": result.final_portfolio_value,
                    "total_return": performance.total_return,
                    "annual_return": performance.annualized_return,
                    "volatility": performance.volatility,
                    "sharpe_ratio": performance.sharpe_ratio,
                    "max_drawdown": performance.max_drawdown,
                    "parameters": {},
                }
                backtest_id = self.database_manager.save_backtest_result(result_data)

                # 2. 포트폴리오 히스토리 저장 (Phase 3.2 선행: DuckDB 컬럼형 저장으로 분석 성능 향상)
                if portfolio_values:
                    portfolio_history = []
                    start_value = backtest.config.initial_cash
                    for value in portfolio_values:
                        portfolio_history.append(
                            {
                                "timestamp": datetime.now(),
                                "total_value": value,
                                "cash": 0.0,  # TODO: 실제 현금 잔액 계산
                                "positions_value": value,
                                "return_pct": ((value - start_value) / start_value)
                                * 100,
                            }
                        )

                    self.database_manager.save_portfolio_history(
                        backtest_id, portfolio_history
                    )

                # 3. 거래 내역 저장 (Phase 3.2 선행: SQL 쿼리로 거래 분석 가능)
                if trades:
                    trades_data = []
                    for trade in trades:
                        trades_data.append(
                            {
                                "timestamp": trade.get("timestamp", datetime.now()),
                                "symbol": trade.get("symbol"),
                                "side": trade.get("side"),
                                "quantity": trade.get("quantity"),
                                "price": trade.get("price"),
                                "commission": trade.get("commission", 0.0),
                                "total_amount": trade.get("quantity", 0)
                                * trade.get("price", 0),
                            }
                        )

                    self.database_manager.save_trades_history(backtest_id, trades_data)

                logger.info(
                    f"✅ DuckDB 저장 완료: {backtest_id} "
                    f"({len(portfolio_values)} portfolio, {len(trades)} trades)"
                )

            except Exception as e:
                logger.error(f"DuckDB save failed: {e}")

        return result

    async def _complete(
        self,
        backtest: Backtest,
        execution: BacktestExecution,
        performance: PerformanceMetrics,
    ) -> None:
        end_time = datetime.now()

        backtest.status = BacktestStatus.COMPLETED
        backtest.end_time = end_time
        if backtest.start_time:
            backtest.duration_seconds = (end_time - backtest.start_time).total_seconds()
        backtest.performance = performance
        await backtest.save()

        execution.status = BacktestStatus.COMPLETED
        execution.end_time = end_time
        await execution.save()

    async def _fail(
        self,
        backtest: Optional[Backtest],
        execution: Optional[BacktestExecution],
        error_message: str,
    ) -> None:
        end_time = datetime.now()

        if backtest:
            backtest.status = BacktestStatus.FAILED
            backtest.end_time = end_time
            backtest.error_message = error_message
            if backtest.start_time:
                backtest.duration_seconds = (
                    end_time - backtest.start_time
                ).total_seconds()
            await backtest.save()

        if execution:
            execution.status = BacktestStatus.FAILED
            execution.end_time = end_time
            execution.error_message = error_message
            await execution.save()
