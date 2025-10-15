"""
Backtest Orchestrator - Initialization Module
백테스트 초기화 및 종료 처리
"""

import logging
from datetime import datetime
from typing import Optional

from app.models.trading.backtest import (
    Backtest,
    BacktestExecution,
    BacktestStatus,
    PerformanceMetrics,
)


logger = logging.getLogger(__name__)


class BacktestInitializer:
    """백테스트 초기화 및 종료 처리

    책임:
    - 백테스트 실행 시작 시 BacktestExecution 생성 및 상태 업데이트
    - 백테스트 완료 시 상태 및 성과 지표 업데이트
    - 백테스트 실패 시 에러 메시지 기록
    """

    async def init_execution(
        self, backtest: Backtest, execution_id: str
    ) -> BacktestExecution:
        """백테스트 실행 초기화

        Args:
            backtest: 백테스트 모델
            execution_id: 실행 ID

        Returns:
            생성된 BacktestExecution 모델
        """
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

    async def complete(
        self,
        backtest: Backtest,
        execution: BacktestExecution,
        performance: PerformanceMetrics,
    ) -> None:
        """백테스트 완료 처리

        Args:
            backtest: 백테스트 모델
            execution: 실행 모델
            performance: 성과 지표
        """
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

    async def fail(
        self,
        backtest: Optional[Backtest],
        execution: Optional[BacktestExecution],
        error_message: str,
    ) -> None:
        """백테스트 실패 처리

        Args:
            backtest: 백테스트 모델 (선택사항)
            execution: 실행 모델 (선택사항)
            error_message: 에러 메시지
        """
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
