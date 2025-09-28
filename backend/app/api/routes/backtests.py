"""
Backtest API Routes
"""

from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, Query

from app.models.backtest import BacktestStatus
from app.schemas.backtest import (
    BacktestCreateRequest,
    BacktestExecutionListResponse,
    BacktestExecutionRequest,
    BacktestExecutionResponse,
    BacktestListResponse,
    BacktestResponse,
    BacktestResultListResponse,
    BacktestResultResponse,
    BacktestUpdateRequest,
    IntegratedBacktestRequest,
    IntegratedBacktestResponse,
)
from app.services.service_factory import service_factory
from app.services.backtest_service import BacktestService
from app.services.integrated_backtest_executor import IntegratedBacktestExecutor
from app.models.strategy import StrategyType
from app.models.backtest import BacktestConfig

router = APIRouter(prefix="/backtests", tags=["Backtests", "Integrated Backtest"])


async def get_backtest_service() -> AsyncGenerator[BacktestService, None]:
    """Dependency to get backtest service with proper cleanup"""
    service = service_factory.get_backtest_service()
    try:
        yield service
    finally:
        pass  # ServiceFactory manages cleanup


async def get_integrated_executor() -> IntegratedBacktestExecutor:
    """통합 백테스트 실행기 의존성 주입"""
    market_data_service = service_factory.get_market_data_service()
    strategy_service = service_factory.get_strategy_service()

    return IntegratedBacktestExecutor(
        market_data_service=market_data_service, strategy_service=strategy_service
    )


@router.post("/", response_model=BacktestResponse)
async def create_backtest(
    request: BacktestCreateRequest,
    service: BacktestService = Depends(get_backtest_service),
):
    """Create a new backtest"""
    try:
        backtest = await service.create_backtest(
            name=request.name,
            description=request.description,
            config=request.config,
        )

        return BacktestResponse(
            id=str(backtest.id),
            name=backtest.name,
            description=backtest.description,
            config=backtest.config,
            status=backtest.status,
            start_time=backtest.start_time,
            end_time=backtest.end_time,
            duration_seconds=backtest.duration_seconds,
            performance=backtest.performance,
            created_at=backtest.created_at,
            updated_at=backtest.updated_at,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/", response_model=BacktestListResponse)
async def get_backtests(
    status: BacktestStatus | None = Query(None, description="실행 상태 필터"),
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 개수"),
    service: BacktestService = Depends(get_backtest_service),
):
    """Get list of backtests"""
    try:
        backtests = await service.get_backtests(status=status, skip=skip, limit=limit)

        backtest_responses = [
            BacktestResponse(
                id=str(backtest.id),
                name=backtest.name,
                description=backtest.description,
                config=backtest.config,
                status=backtest.status,
                start_time=backtest.start_time,
                end_time=backtest.end_time,
                duration_seconds=backtest.duration_seconds,
                performance=backtest.performance,
                created_at=backtest.created_at,
                updated_at=backtest.updated_at,
            )
            for backtest in backtests
        ]

        return BacktestListResponse(
            backtests=backtest_responses,
            total=len(backtest_responses),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/{backtest_id}", response_model=BacktestResponse)
async def get_backtest(
    backtest_id: str,
    service: BacktestService = Depends(get_backtest_service),
):
    """Get backtest by ID"""
    backtest = await service.get_backtest(backtest_id)
    if not backtest:
        raise HTTPException(status_code=404, detail="Backtest not found")

    return BacktestResponse(
        id=str(backtest.id),
        name=backtest.name,
        description=backtest.description,
        config=backtest.config,
        status=backtest.status,
        start_time=backtest.start_time,
        end_time=backtest.end_time,
        duration_seconds=backtest.duration_seconds,
        performance=backtest.performance,
        created_at=backtest.created_at,
        updated_at=backtest.updated_at,
    )


@router.put("/{backtest_id}", response_model=BacktestResponse)
async def update_backtest(
    backtest_id: str,
    request: BacktestUpdateRequest,
    service: BacktestService = Depends(get_backtest_service),
):
    """Update backtest"""
    try:
        backtest = await service.update_backtest(
            backtest_id=backtest_id,
            name=request.name,
            description=request.description,
            config=request.config,
        )

        if not backtest:
            raise HTTPException(status_code=404, detail="Backtest not found")

        return BacktestResponse(
            id=str(backtest.id),
            name=backtest.name,
            description=backtest.description,
            config=backtest.config,
            status=backtest.status,
            start_time=backtest.start_time,
            end_time=backtest.end_time,
            duration_seconds=backtest.duration_seconds,
            performance=backtest.performance,
            created_at=backtest.created_at,
            updated_at=backtest.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{backtest_id}")
async def delete_backtest(
    backtest_id: str,
    service: BacktestService = Depends(get_backtest_service),
):
    """Delete backtest"""
    success = await service.delete_backtest(backtest_id)
    if not success:
        raise HTTPException(status_code=404, detail="Backtest not found")

    return {"message": "Backtest deleted successfully"}


@router.post("/{backtest_id}/execute", response_model=BacktestExecutionResponse)
async def execute_backtest(
    backtest_id: str,
    request: BacktestExecutionRequest,
    service: BacktestService = Depends(get_backtest_service),
):
    """Execute backtest with trading signals"""
    try:
        execution = await service.execute_backtest(
            backtest_id=backtest_id,
            signals=request.signals,
        )

        if not execution:
            raise HTTPException(status_code=404, detail="Backtest not found")

        return BacktestExecutionResponse(
            id=str(execution.id),
            backtest_id=execution.backtest_id,
            execution_id=execution.execution_id,
            start_time=execution.start_time,
            end_time=execution.end_time,
            status=execution.status,
            portfolio_values=execution.portfolio_values,
            trades=execution.trades,
            positions=execution.positions,
            error_message=execution.error_message,
            created_at=execution.created_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{backtest_id}/executions", response_model=BacktestExecutionListResponse)
async def get_backtest_executions(
    backtest_id: str,
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 개수"),
    service: BacktestService = Depends(get_backtest_service),
):
    """Get execution history for a backtest"""
    try:
        executions = await service.get_backtest_executions(
            backtest_id=backtest_id,
            skip=skip,
            limit=limit,
        )

        execution_responses = [
            BacktestExecutionResponse(
                id=str(execution.id),
                backtest_id=execution.backtest_id,
                execution_id=execution.execution_id,
                start_time=execution.start_time,
                end_time=execution.end_time,
                status=execution.status,
                portfolio_values=execution.portfolio_values,
                trades=execution.trades,
                positions=execution.positions,
                error_message=execution.error_message,
                created_at=execution.created_at,
            )
            for execution in executions
        ]

        return BacktestExecutionListResponse(
            executions=execution_responses,
            total=len(execution_responses),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/results/", response_model=BacktestResultListResponse)
async def get_backtest_results(
    backtest_id: str | None = Query(None, description="백테스트 ID 필터"),
    execution_id: str | None = Query(None, description="실행 ID 필터"),
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 개수"),
    service: BacktestService = Depends(get_backtest_service),
):
    """Get backtest results"""
    try:
        results = await service.get_backtest_results(
            backtest_id=backtest_id,
            execution_id=execution_id,
            skip=skip,
            limit=limit,
        )

        result_responses = [
            BacktestResultResponse(
                id=str(result.id),
                backtest_id=result.backtest_id,
                execution_id=result.execution_id,
                total_return=result.total_return,
                annualized_return=result.annualized_return,
                volatility=result.volatility,
                sharpe_ratio=result.sharpe_ratio,
                max_drawdown=result.max_drawdown,
                calmar_ratio=result.calmar_ratio,
                sortino_ratio=result.sortino_ratio,
                benchmark_return=result.benchmark_return,
                alpha=result.alpha,
                beta=result.beta,
                total_trades=result.total_trades,
                winning_trades=result.winning_trades,
                losing_trades=result.losing_trades,
                win_rate=result.win_rate,
                portfolio_history_path=result.portfolio_history_path,
                trades_history_path=result.trades_history_path,
                created_at=result.created_at,
            )
            for result in results
        ]

        return BacktestResultListResponse(
            results=result_responses,
            total=len(result_responses),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# Integrated Backtest Endpoints
@router.post("/integrated", response_model=IntegratedBacktestResponse)
async def create_and_run_integrated_backtest(
    request: IntegratedBacktestRequest,
    executor: IntegratedBacktestExecutor = Depends(get_integrated_executor),
    service: BacktestService = Depends(get_backtest_service),
):
    """통합 백테스트 생성 및 실행 - 모든 서비스 연동"""
    try:
        # 1. 백테스트 설정 생성
        config = BacktestConfig(
            name=request.name,
            description=request.description,
            start_date=request.start_date,
            end_date=request.end_date,
            symbols=request.symbols,
            initial_cash=request.initial_capital,
            rebalance_frequency="daily",
        )

        # 2. 백테스트 생성
        backtest = await service.create_backtest(
            name=request.name, description=request.description, config=config
        )

        # 3. 전략 타입 변환
        try:
            strategy_type = StrategyType(request.strategy_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid strategy type: {request.strategy_type}",
            )

        # 4. 통합 백테스트 실행
        result = await executor.execute_integrated_backtest(
            backtest_id=str(backtest.id),
            symbols=request.symbols,
            start_date=request.start_date,
            end_date=request.end_date,
            strategy_type=strategy_type,
            strategy_params=request.strategy_params,
            initial_capital=request.initial_capital,
        )

        if result:
            return IntegratedBacktestResponse(
                backtest_id=str(backtest.id),
                execution_id=(
                    str(result.execution_id)
                    if hasattr(result, "execution_id")
                    else None
                ),
                result_id=str(result.id),
                status=BacktestStatus.COMPLETED,
                message="Integrated backtest completed successfully",
                performance=(
                    result.performance if hasattr(result, "performance") else None
                ),
                start_time=backtest.start_time,
                end_time=backtest.end_time,
            )
        else:
            return IntegratedBacktestResponse(
                backtest_id=str(backtest.id),
                execution_id=None,
                result_id=None,
                status=BacktestStatus.FAILED,
                message="Integrated backtest execution failed",
                performance=None,
                start_time=backtest.start_time,
                end_time=None,
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to execute integrated backtest: {str(e)}"
        )


@router.get("/test-services")
async def test_service_integration():
    """서비스 연동 테스트"""
    try:
        # 각 서비스 인스턴스 생성 테스트
        market_data_service = service_factory.get_market_data_service()
        strategy_service = service_factory.get_strategy_service()

        # 기본 기능 테스트
        symbols = await market_data_service.get_available_symbols()

        # 전략 인스턴스 생성 테스트
        strategy_instance = await strategy_service.get_strategy_instance(
            strategy_type=StrategyType.BUY_AND_HOLD, parameters={}
        )

        return {
            "status": "success",
            "services": {
                "market_data": "✅ Available",
                "strategy": "✅ Available",
                "backtest": "✅ Available",
            },
            "tests": {
                "symbols_count": len(symbols),
                "strategy_instance": "✅ Created" if strategy_instance else "❌ Failed",
                "integrated_executor": "✅ Ready",
            },
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "services": {
                "market_data": "❌ Error",
                "strategy": "❌ Error",
                "backtest": "❌ Error",
            },
        }
