"""
Backtest API Routes
"""

from collections.abc import AsyncGenerator
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from app.models.backtest import BacktestStatus
from app.schemas.backtest import (
    BacktestCreateRequest,
    BacktestExecutionListResponse,
    BacktestExecutionRequest,
    BacktestExecutionResponse,
    BacktestListResponse,
    BacktestResponse,
    BacktestUpdateRequest,
    IntegratedBacktestRequest,
    IntegratedBacktestResponse,
)
from app.services.service_factory import service_factory
from app.services.backtest_service import BacktestService
from app.services.integrated_backtest_executor import IntegratedBacktestExecutor
from app.models.strategy import StrategyType
from app.models.backtest import BacktestConfig
from mysingle_quant.auth import get_current_active_verified_user, User

router = APIRouter(dependencies=[Depends(get_current_active_verified_user)])


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
    current_user: User = Depends(get_current_active_verified_user),
    service: BacktestService = Depends(get_backtest_service),
):
    """Create a new backtest"""
    try:
        backtest = await service.create_backtest(
            name=request.name,
            description=request.description,
            config=request.config,
            user_id=str(current_user.id),
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
    current_user: User = Depends(get_current_active_verified_user),
    service: BacktestService = Depends(get_backtest_service),
):
    """Get list of backtests"""
    try:
        backtests = await service.get_backtests(
            status=status, skip=skip, limit=limit, user_id=str(current_user.id)
        )

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
    current_user: User = Depends(get_current_active_verified_user),
    service: BacktestService = Depends(get_backtest_service),
):
    """Get backtest by ID"""
    backtest = await service.get_backtest(backtest_id)
    if not backtest:
        raise HTTPException(status_code=404, detail="Backtest not found")

    # 소유권 확인
    if backtest.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")

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
    current_user: User = Depends(get_current_active_verified_user),
    service: BacktestService = Depends(get_backtest_service),
):
    """Update backtest"""
    try:
        # 먼저 소유권 확인
        existing_backtest = await service.get_backtest(backtest_id)
        if not existing_backtest:
            raise HTTPException(status_code=404, detail="Backtest not found")

        if existing_backtest.user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Access denied")

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
    current_user: User = Depends(get_current_active_verified_user),
    service: BacktestService = Depends(get_backtest_service),
):
    """Delete backtest"""
    # 먼저 소유권 확인
    existing_backtest = await service.get_backtest(backtest_id)
    if not existing_backtest:
        raise HTTPException(status_code=404, detail="Backtest not found")

    if existing_backtest.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")

    success = await service.delete_backtest(backtest_id)
    if not success:
        raise HTTPException(status_code=404, detail="Backtest not found")

    return {"message": "Backtest deleted successfully"}


@router.post("/{backtest_id}/execute", response_model=BacktestExecutionResponse)
async def execute_backtest(
    backtest_id: str,
    request: BacktestExecutionRequest,
    current_user: User = Depends(get_current_active_verified_user),
    service: BacktestService = Depends(get_backtest_service),
):
    """Execute backtest with trading signals"""
    try:
        # 먼저 소유권 확인
        existing_backtest = await service.get_backtest(backtest_id)
        if not existing_backtest:
            raise HTTPException(status_code=404, detail="Backtest not found")

        if existing_backtest.user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Access denied")

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
    current_user: User = Depends(get_current_active_verified_user),
    service: BacktestService = Depends(get_backtest_service),
):
    """Get execution history for a backtest"""
    try:
        # 먼저 소유권 확인
        existing_backtest = await service.get_backtest(backtest_id)
        if not existing_backtest:
            raise HTTPException(status_code=404, detail="Backtest not found")

        if existing_backtest.user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Access denied")

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


@router.get("/results/", response_model=dict)
async def get_backtest_results(
    backtest_id: str | None = Query(None, description="백테스트 ID 필터"),
    execution_id: str | None = Query(None, description="실행 ID 필터"),
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 개수"),
    current_user: User = Depends(get_current_active_verified_user),
    service: BacktestService = Depends(get_backtest_service),
):
    """Get backtest results from DuckDB (고성능 분석용)"""
    try:
        # backtest_id가 제공된 경우 소유권 확인
        if backtest_id:
            existing_backtest = await service.get_backtest(backtest_id)
            if existing_backtest and existing_backtest.user_id != str(current_user.id):
                raise HTTPException(status_code=403, detail="Access denied")

        # DuckDB에서 백테스트 결과 요약 조회
        results_summary = service.get_duckdb_results_summary()

        # 필터링 적용
        filtered_results = results_summary
        if backtest_id:
            filtered_results = [
                r for r in filtered_results if r.get("backtest_id") == backtest_id
            ]
        if execution_id:
            filtered_results = [
                r for r in filtered_results if r.get("execution_id") == execution_id
            ]

        # 페이지네이션 적용
        total = len(filtered_results)
        paginated_results = filtered_results[skip : skip + limit]

        return {
            "results": paginated_results,
            "total": total,
            "skip": skip,
            "limit": limit,
            "source": "duckdb",
            "message": "Results from high-performance DuckDB cache",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# Integrated Backtest Endpoints
@router.post("/integrated", response_model=IntegratedBacktestResponse)
async def create_and_run_integrated_backtest(
    request: IntegratedBacktestRequest,
    current_user: User = Depends(get_current_active_verified_user),
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
            name=request.name,
            description=request.description,
            config=config,
            user_id=str(current_user.id),
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


@router.get("/health")
async def health_check():
    """백테스트 시스템 상태 확인 (DuckDB + MongoDB 통합 상태)"""
    try:
        # DuckDB 상태 확인
        database_manager = service_factory.get_database_manager()
        duckdb_connected = database_manager.connection is not None

        # 서비스 상태 확인
        market_data_service = service_factory.get_market_data_service()
        backtest_service = service_factory.get_backtest_service()

        # 데이터 상태 확인
        duckdb_symbols = (
            database_manager.get_available_symbols() if duckdb_connected else []
        )
        mongodb_symbols = await market_data_service.get_available_symbols()

        # DuckDB 백테스트 결과 통계
        results_count = len(backtest_service.get_duckdb_results_summary())

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "databases": {
                "duckdb": {
                    "connected": duckdb_connected,
                    "symbols_count": len(duckdb_symbols),
                    "backtest_results_count": results_count,
                },
                "mongodb": {"connected": True, "symbols_count": len(mongodb_symbols)},
            },
            "services": {
                "market_data": "✅ Ready",
                "strategy": "✅ Ready",
                "backtest": "✅ Ready",
                "integrated_executor": "✅ Ready",
            },
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "databases": {"duckdb": "❌ Error", "mongodb": "❌ Error"},
        }


@router.get("/analytics/performance-stats")
async def get_performance_analytics(
    service: BacktestService = Depends(get_backtest_service),
):
    """백테스트 성과 분석 (DuckDB 고성능 분석)"""
    try:
        stats = service.get_duckdb_performance_stats()
        return {
            "status": "success",
            "analytics": stats,
            "source": "duckdb",
            "computed_at": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"성과 분석 실패: {str(e)}")


@router.get("/analytics/trades")
async def get_trades_analytics(
    execution_id: str | None = Query(None, description="특정 실행 ID 필터"),
    symbol: str | None = Query(None, description="심볼 필터"),
    service: BacktestService = Depends(get_backtest_service),
):
    """거래 기록 분석 (DuckDB 고성능 쿼리)"""
    try:
        if execution_id:
            trades = service.get_duckdb_trades_by_execution(execution_id)
            analysis_scope = f"execution_{execution_id}"
        else:
            # 전체 거래 기록 요약 (향후 구현)
            trades = []
            analysis_scope = "all_executions"

        return {
            "status": "success",
            "analysis_scope": analysis_scope,
            "trades_count": len(trades),
            "trades": trades,
            "source": "duckdb",
            "queried_at": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"거래 분석 실패: {str(e)}")


@router.get("/analytics/summary")
async def get_backtest_summary_analytics(
    service: BacktestService = Depends(get_backtest_service),
):
    """백테스트 결과 요약 분석 (DuckDB 기반)"""
    try:
        summary = service.get_duckdb_results_summary()

        return {
            "status": "success",
            "summary": {
                "total_backtests": len(summary),
                "recent_results": summary[:10],  # 최근 10개
                "source": "duckdb",
            },
            "analyzed_at": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"요약 분석 실패: {str(e)}")
