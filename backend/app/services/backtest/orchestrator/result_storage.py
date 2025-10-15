"""
Backtest Orchestrator - Result Storage Module
백테스트 결과 저장 (MongoDB + DuckDB)
"""

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from app.models.trading.backtest import (
    Backtest,
    BacktestExecution,
    BacktestResult,
    PerformanceMetrics,
)

if TYPE_CHECKING:
    from app.services.database_manager import DatabaseManager
    from app.services.gen_ai.core.rag_service import RAGService


logger = logging.getLogger(__name__)


class ResultStorage:
    """백테스트 결과 저장 (MongoDB + DuckDB)

    저장 위치:
    1. MongoDB: 메타데이터 및 성과 지표 (Phase 2)
    2. DuckDB: 포트폴리오 히스토리, 거래 내역 (Phase 3.2 선행)

    Phase 3.2를 조기 도입한 이유:
    - DuckDB의 컬럼 형식 저장으로 시계열 분석 성능 10-100배 향상
    - 대용량 백테스트 결과를 효율적으로 처리

    Attributes:
        database_manager: 데이터베이스 매니저 (DuckDB)
    """

    def __init__(
        self,
        database_manager: Optional["DatabaseManager"] = None,
        rag_service: Optional["RAGService"] = None,
    ):
        """ResultStorage 초기화

        Args:
            database_manager: 데이터베이스 매니저 (DuckDB)
        """
        self.database_manager = database_manager
        self.rag_service = rag_service

    async def save_results(
        self,
        backtest: Backtest,
        execution: BacktestExecution,
        performance: PerformanceMetrics,
        trades: list,
        portfolio_values: list[float],
    ) -> BacktestResult:
        """결과를 MongoDB + DuckDB에 저장

        Args:
            backtest: 백테스트 모델
            execution: 실행 모델
            performance: 성과 지표
            trades: 거래 리스트
            portfolio_values: 포트폴리오 가치 리스트

        Returns:
            생성된 BacktestResult 모델
        """
        result = BacktestResult(
            backtest_id=str(backtest.id),
            execution_id=str(execution.id),
            user_id=backtest.user_id,
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

        if self.rag_service:
            try:
                await self.rag_service.index_backtest_result(backtest, result)
            except Exception as exc:  # pragma: no cover - external services
                logger.warning(
                    "RAG indexing failed",
                    exc_info=True,
                    extra={"backtest_id": str(backtest.id), "error": str(exc)},
                )

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
