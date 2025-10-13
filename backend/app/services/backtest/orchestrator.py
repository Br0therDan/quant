"""
백테스트 워크플로우 조율자 (Orchestrator Pattern - Phase 2)
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING, Any

from beanie import PydanticObjectId

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

        logger.info("BacktestOrchestrator initialized (Phase 2)")

    async def execute_backtest(self, backtest_id: str) -> Optional[BacktestResult]:
        """백테스트 실행"""
        backtest = None
        execution = None

        try:
            backtest = await Backtest.get(PydanticObjectId(backtest_id))
            if not backtest:
                return None

            execution_id = str(uuid.uuid4())
            execution = await self._init_execution(backtest, execution_id)

            # 데이터 수집
            raw_data = await self._collect_data(
                backtest.config.symbols,
                backtest.config.start_date,
                backtest.config.end_date,
            )

            # 전처리
            market_data = await self.data_processor.process_market_data(
                raw_data=raw_data,
                required_columns=["open", "high", "low", "close", "volume"],
                min_data_points=30,
            )

            if not market_data:
                raise Exception("No market data")

            # 신호 생성
            signals = await self.strategy_executor.generate_signals(
                strategy_id=str(backtest.strategy_id),
                market_data=market_data,
                config=backtest.config,
            )

            # 시뮬레이션
            trades, portfolio_values = self._simulate(backtest, signals)

            # 성과 분석
            performance = await self.performance_analyzer.calculate_metrics(
                portfolio_values=portfolio_values,
                trades=trades,
                initial_capital=backtest.config.initial_cash,
            )

            # 저장
            result = await self._save_results(
                backtest, execution, performance, trades, portfolio_values
            )

            await self._complete(backtest, execution, performance)

            logger.info(f"Backtest completed: {backtest_id}")
            return result

        except Exception as e:
            logger.error(f"Backtest failed: {e}")
            await self._fail(backtest, execution, str(e))
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
        market_data = {}
        for symbol in symbols:
            try:
                data = await self.market_data_service.stock.get_historical_data(
                    symbol=symbol,
                    start_date=start_date,
                    end_date=end_date,
                )
                if data:
                    market_data[symbol] = data
            except Exception as e:
                logger.error(f"Failed {symbol}: {e}")
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

        if self.database_manager:
            try:
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
                self.database_manager.save_backtest_result(result_data)
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
