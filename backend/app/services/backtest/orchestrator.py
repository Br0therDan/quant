"""
백테스트 워크플로우 조율자 (Orchestrator Pattern - Phase 2)
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING, Any

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
    """Circuit Breaker 패턴 구현 (P3.3)"""

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
        elapsed = (datetime.now(timezone.utc) - self.last_failure_time).total_seconds()
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
        self.last_failure_time = datetime.now(timezone.utc)

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.error(
                f"Circuit Breaker: CLOSED -> OPEN "
                f"({self.failure_count} failures reached threshold)"
            )


class BacktestOrchestrator:
    """백테스트 워크플로우 조율자 (Phase 2)"""

    def __init__(
        self,
        market_data_service: "MarketDataService",
        strategy_service: "StrategyService",
        database_manager: "DatabaseManager",
    ):
        self.market_data_service = market_data_service
        self.strategy_service = strategy_service
        self.database_manager = database_manager

        # Phase 2 컴포넌트
        self.data_processor = DataProcessor()
        self.strategy_executor = StrategyExecutor(strategy_service)
        self.performance_analyzer = PerformanceAnalyzer()

        # P3.3: Circuit Breaker
        self.circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60)

        # P3.4: Monitoring
        self.metrics = get_global_metrics()

        logger.info("BacktestOrchestrator initialized (Phase 2, P3.3+P3.4 enhanced)")
        structured_logger.info(
            "orchestrator_initialized",
            phase="2",
            enhancements=["circuit_breaker", "monitoring"],
        )

    async def execute_backtest(self, backtest_id: str) -> Optional[BacktestResult]:
        """백테스트 실행 (P3.4: 모니터링 통합)"""
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
                self.metrics.stop_timer("signal_generation")

                log_backtest_event(
                    "signals_generated",
                    backtest_id=backtest_id,
                    signal_count=len(signals),
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
        backtest.start_time = datetime.now(timezone.utc)
        await backtest.save()

        execution = BacktestExecution(
            backtest_id=str(backtest.id),
            execution_id=execution_id,
            status=BacktestStatus.RUNNING,
            start_time=datetime.now(timezone.utc),
            end_time=None,
            error_message=None,
        )
        await execution.insert()
        return execution

    async def _collect_data(
        self, symbols: list[str], start_date: Any, end_date: Any
    ) -> dict:
        """병렬 데이터 수집 (P3.2 최적화) with Retry (P3.3)"""
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
            timestamp = signal.get("timestamp", datetime.now(timezone.utc))

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

        # DuckDB 저장 (P3.2 개선)
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

                # 2. 포트폴리오 히스토리 저장 (P3.2 신규)
                if portfolio_values:
                    from datetime import datetime, timezone

                    portfolio_history = []
                    start_value = backtest.config.initial_cash
                    for value in portfolio_values:
                        portfolio_history.append(
                            {
                                "timestamp": datetime.now(timezone.utc),
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

                # 3. 거래 내역 저장 (P3.2 신규)
                if trades:
                    trades_data = []
                    for trade in trades:
                        trades_data.append(
                            {
                                "timestamp": trade.get(
                                    "timestamp", datetime.now(timezone.utc)
                                ),
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
        end_time = datetime.now(timezone.utc)

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
        end_time = datetime.now(timezone.utc)

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
