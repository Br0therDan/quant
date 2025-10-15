"""
Backtest Service - CRUD Operations Only (Phase 2)

Phase 2 변경사항:
- 실행 로직 제거 → BacktestOrchestrator로 이동
- CRUD 및 조회 기능만 유지
- 700 lines → 150 lines 축소
"""

import logging
from datetime import datetime
from typing import Optional

from beanie import PydanticObjectId

from app.models.trading.backtest import (
    Backtest,
    BacktestConfig,
    BacktestExecution,
    BacktestResult,
    BacktestStatus,
    PerformanceMetrics,
)
from app.models.trading.strategy import Strategy
from app.schemas.enums import StrategyType
from app.strategies.configs import BuyAndHoldConfig

logger = logging.getLogger(__name__)


class BacktestService:
    """백테스트 CRUD 서비스

    Phase 2에서 실행 로직은 BacktestOrchestrator로 분리되었습니다.
    이 서비스는 순수 CRUD 작업만 담당합니다.
    """

    async def create_backtest(
        self,
        name: str,
        description: str = "",
        config: Optional[BacktestConfig] = None,
        user_id: Optional[str] = None,
    ) -> Backtest:
        """백테스트 생성 (Phase 2: 기본 전략 자동 생성)"""
        if config is None:
            config = BacktestConfig(
                name=name,
                symbols=["AAPL"],
                start_date=datetime.now(),
                end_date=datetime.now(),
                initial_cash=100000.0,
                commission_rate=0.001,
                rebalance_frequency=None,
            )

        # Phase 2: 기본 Buy & Hold 전략 자동 생성
        default_strategy = Strategy(
            name=f"{name} - Buy & Hold Strategy",
            strategy_type=StrategyType.BUY_AND_HOLD,
            description="Auto-generated buy and hold strategy",
            config=BuyAndHoldConfig(
                config_type="buy_and_hold",
                allocation={
                    symbol: 1.0 / len(config.symbols) for symbol in config.symbols
                },
            ),
            is_active=True,
            is_template=False,
            created_by=user_id or "system",
            user_id=user_id,
        )
        await default_strategy.insert()
        logger.info(f"Created default strategy: {default_strategy.id}")

        backtest = Backtest(
            name=name,
            description=description,
            config=config,
            strategy_id=str(default_strategy.id),  # Phase 2: 전략 연결
            user_id=user_id,
            status=BacktestStatus.PENDING,
            start_time=None,
            end_time=None,
            duration_seconds=None,
            performance=None,
            portfolio_history_path=None,
            trades_history_path=None,
            error_message=None,
            created_by="system",
            created_at=datetime.now(),
        )

        await backtest.insert()
        logger.info(f"Created backtest: {backtest.id}")
        return backtest

    async def get_backtests(
        self,
        status: Optional[BacktestStatus] = None,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[str] = None,
    ) -> list[Backtest]:
        """백테스트 목록 조회"""
        query = {}
        if status:
            query["status"] = status
        if user_id:
            query["user_id"] = user_id

        return await Backtest.find(query).skip(skip).limit(limit).to_list()

    async def get_backtest(self, backtest_id: str) -> Optional[Backtest]:
        """백테스트 상세 조회"""
        try:
            return await Backtest.get(PydanticObjectId(backtest_id))
        except Exception as e:
            logger.error(f"Failed to get backtest {backtest_id}: {e}")
            return None

    async def update_backtest(
        self,
        backtest_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        config: Optional[BacktestConfig] = None,
    ) -> Optional[Backtest]:
        """백테스트 수정"""
        backtest = await self.get_backtest(backtest_id)
        if not backtest:
            return None

        if name is not None:
            backtest.name = name
        if description is not None:
            backtest.description = description
        if config is not None:
            backtest.config = config

        backtest.updated_at = datetime.now()
        await backtest.save()
        logger.info(f"Updated backtest: {backtest_id}")
        return backtest

    async def delete_backtest(self, backtest_id: str) -> bool:
        """백테스트 삭제"""
        backtest = await self.get_backtest(backtest_id)
        if not backtest:
            return False

        await backtest.delete()
        logger.info(f"Deleted backtest: {backtest_id}")
        return True

    async def get_backtest_executions(
        self,
        backtest_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[BacktestExecution]:
        """백테스트 실행 내역 조회"""
        return (
            await BacktestExecution.find(BacktestExecution.backtest_id == backtest_id)
            .skip(skip)
            .limit(limit)
            .sort("-start_time")
            .to_list()
        )

    async def get_backtest_results(
        self,
        backtest_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[BacktestResult]:
        """백테스트 결과 조회"""
        query = {}
        if backtest_id:
            query["backtest_id"] = backtest_id
        if execution_id:
            query["execution_id"] = execution_id

        return await BacktestResult.find(query).skip(skip).limit(limit).to_list()

    async def create_backtest_result(
        self,
        backtest_id: str,
        execution_id: str,
        performance_metrics: PerformanceMetrics,
        final_portfolio_value: float = 0.0,
        cash_remaining: float = 0.0,
        total_invested: float = 100000.0,
    ) -> BacktestResult:
        """백테스트 결과 생성"""
        result = BacktestResult(
            backtest_id=backtest_id,
            execution_id=execution_id,
            performance=performance_metrics,
            final_portfolio_value=final_portfolio_value,
            cash_remaining=cash_remaining,
            total_invested=total_invested,
            var_95=None,
            var_99=None,
            calmar_ratio=None,
            sortino_ratio=None,
            benchmark_return=None,
            alpha=None,
            beta=None,
            created_at=datetime.now(),
        )

        await result.insert()
        logger.info(f"Created backtest result: {execution_id}")
        return result
