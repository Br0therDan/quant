"""
Backtest API Routes
"""

from collections.abc import AsyncGenerator
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from app.models.backtest import BacktestStatus
from app.schemas.backtest import (
    BacktestCreate,
    BacktestExecutionListResponse,
    BacktestExecutionRequest,
    BacktestExecutionResponse,
    BacktestListResponse,
    BacktestResponse,
    BacktestUpdate,
    # IntegratedBacktestRequest,  # ❌ Removed in P3.0
    # IntegratedBacktestResponse,  # ❌ Removed in P3.0
)
from app.services.service_factory import service_factory
from app.services.backtest_service import BacktestService
from app.services.backtest import BacktestOrchestrator
from .optimize_backtests import router as optimize_router

# from app.models.backtest import BacktestConfig  # ❌ Removed in P3.0
from mysingle_quant.auth import get_current_active_verified_user, User

router = APIRouter(dependencies=[Depends(get_current_active_verified_user)])


async def get_backtest_service() -> AsyncGenerator[BacktestService, None]:
    """Dependency to get backtest service with proper cleanup"""
    service = service_factory.get_backtest_service()
    try:
        yield service
    finally:
        pass  # ServiceFactory manages cleanup


async def get_backtest_orchestrator() -> BacktestOrchestrator:
    """백테스트 Orchestrator 의존성 주입 (Phase 2)"""
    return service_factory.get_backtest_orchestrator()


@router.get("/health")
async def health_check():
    """백테스트 시스템 상태 확인 (Phase 2)"""
    try:
        # DuckDB 상태 확인
        database_manager = service_factory.get_database_manager()
        duckdb_connected = database_manager.connection is not None

        # DuckDB 데이터 상태 확인
        duckdb_symbols = (
            database_manager.get_available_symbols() if duckdb_connected else []
        )

        # MongoDB 백테스트 카운트
        backtest_service = service_factory.get_backtest_service()
        backtests = await backtest_service.get_backtests()
        results_count = len(backtests)

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "databases": {
                "duckdb": {
                    "connected": duckdb_connected,
                    "symbols_count": len(duckdb_symbols),
                },
                "mongodb": {
                    "connected": True,
                    "backtest_count": results_count,
                },
            },
            "services": {
                "market_data": "✅ Ready",
                "strategy": "✅ Ready",
                "backtest": "✅ Ready (Phase 2)",
                "orchestrator": "✅ Ready",
            },
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "databases": {"duckdb": "❌ Error", "mongodb": "❌ Error"},
        }


@router.post("/", response_model=BacktestResponse)
async def create_backtest(
    request: BacktestCreate,
    current_user: User = Depends(get_current_active_verified_user),
    service: BacktestService = Depends(get_backtest_service),
) -> BacktestResponse:
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
    request: BacktestUpdate,
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
    orchestrator: BacktestOrchestrator = Depends(get_backtest_orchestrator),
):
    """Execute backtest with trading signals (Phase 2)"""
    try:
        # 먼저 소유권 확인
        existing_backtest = await service.get_backtest(backtest_id)
        if not existing_backtest:
            raise HTTPException(status_code=404, detail="Backtest not found")

        if existing_backtest.user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Access denied")

        # Orchestrator로 실행 (Phase 2)
        result = await orchestrator.execute_backtest(backtest_id=backtest_id)

        if not result:
            raise HTTPException(status_code=500, detail="Backtest execution failed")

        # Execution 가져오기
        executions = await service.get_backtest_executions(backtest_id)
        if not executions:
            raise HTTPException(status_code=404, detail="Execution not found")

        execution = executions[0]  # 가장 최근 실행

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


# ❌ DEPRECATED: /results/duckdb endpoint (P3.0 API cleanup)
# Reason: DuckDB storage not implemented yet (_save_to_duckdb is empty)
# Currently returns MongoDB data, which is misleading
# TODO: Re-enable when DuckDB storage is implemented in P3.2
# For now, use GET /{id}/executions for execution results

# @router.get("/results/duckdb", response_model=dict)
# async def get_backtest_results_from_duckdb(
#     backtest_id: str | None = Query(None, description="백테스트 ID 필터"),
#     execution_id: str | None = Query(None, description="실행 ID 필터"),
#     skip: int = Query(0, ge=0, description="건너뛸 개수"),
#     limit: int = Query(100, ge=1, le=1000, description="조회할 개수"),
#     current_user: User = Depends(get_current_active_verified_user),
#     service: BacktestService = Depends(get_backtest_service),
# ):
#     """Get backtest results (MongoDB 기반 - Phase 2)"""
#     try:
#         # backtest_id가 제공된 경우 소유권 확인
#         if backtest_id:
#             existing_backtest = await service.get_backtest(backtest_id)
#             if existing_backtest and existing_backtest.user_id != str(current_user.id):
#                 raise HTTPException(status_code=403, detail="Access denied")
#
#         # MongoDB에서 백테스트 결과 조회
#         results = await service.get_backtest_results()
#
#         # 딕셔너리로 변환
#         results_summary = [
#             {
#                 "backtest_id": str(r.backtest_id),
#                 "execution_id": r.execution_id,
#                 "total_return": r.performance.total_return,
#                 "sharpe_ratio": r.performance.sharpe_ratio,
#                 "max_drawdown": r.performance.max_drawdown,
#             }
#             for r in results
#         ]
#
#         # 필터링 적용
#         filtered_results = results_summary
#         if backtest_id:
#             filtered_results = [
#                 r for r in filtered_results if r.get("backtest_id") == backtest_id
#             ]
#         if execution_id:
#             filtered_results = [
#                 r for r in filtered_results if r.get("execution_id") == execution_id
#             ]
#
#         # 페이지네이션 적용
#         total = len(filtered_results)
#         paginated_results = filtered_results[skip : skip + limit]
#
#         return {
#             "results": paginated_results,
#             "total": total,
#             "skip": skip,
#             "limit": limit,
#             "source": "mongodb",
#             "message": "Results from MongoDB (Phase 2)",
#         }
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e)) from e


# ❌ REMOVED: /integrated endpoint (P3.0 API cleanup)
# Reason: Duplicate functionality with POST / + POST /{id}/execute
# Use two-step process: 1) Create backtest, 2) Execute backtest
# For convenience, frontend can chain these calls


@router.get("/analytics/performance-stats")
async def get_performance_analytics(
    service: BacktestService = Depends(get_backtest_service),
):
    """백테스트 성과 분석 (MongoDB 기반 - Phase 2)"""
    try:
        # MongoDB에서 백테스트 결과 가져오기
        results = await service.get_backtest_results()

        if not results:
            return {
                "status": "success",
                "analytics": {
                    "total_backtests": 0,
                    "message": "No backtest results found",
                },
                "source": "mongodb",
                "computed_at": datetime.now().isoformat(),
            }

        # 기본 통계 계산
        total_count = len(results)
        avg_return = (
            sum(r.performance.total_return for r in results) / total_count
            if total_count > 0
            else 0
        )
        avg_sharpe = (
            sum(r.performance.sharpe_ratio for r in results) / total_count
            if total_count > 0
            else 0
        )

        return {
            "status": "success",
            "analytics": {
                "total_backtests": total_count,
                "average_return": avg_return,
                "average_sharpe_ratio": avg_sharpe,
                "results_preview": [
                    {
                        "backtest_id": str(r.backtest_id),
                        "total_return": r.performance.total_return,
                        "sharpe_ratio": r.performance.sharpe_ratio,
                    }
                    for r in results[:5]
                ],
            },
            "source": "mongodb",
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
    """거래 기록 분석 (MongoDB 기반)"""
    try:
        if execution_id:
            # MongoDB에서 실행 정보 가져오기
            executions = await service.get_backtest_executions(execution_id)
            trades = executions[0].trades if executions else []
            analysis_scope = f"execution_{execution_id}"
        else:
            trades = []
            analysis_scope = "all_executions"

        return {
            "status": "success",
            "analysis_scope": analysis_scope,
            "trades_count": len(trades),
            "trades": trades,
            "source": "mongodb",
            "queried_at": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"거래 분석 실패: {str(e)}")


# ❌ REMOVED: /analytics/summary endpoint (P3.0 API cleanup)
# Reason: Duplicate functionality with /analytics/performance-stats
# Use /analytics/performance-stats instead for performance metrics
# Or use GET /{id}/executions for detailed execution data

# @router.get("/analytics/summary")
# async def get_backtest_summary_analytics(
#     service: BacktestService = Depends(get_backtest_service),
# ):
#     """백테스트 결과 요약 분석 (MongoDB 기반)"""
#     try:
#         # MongoDB에서 백테스트 결과 가져오기
#         results = await service.get_backtest_results()
#
#         return {
#             "status": "success",
#             "summary": {
#                 "total_backtests": len(results),
#                 "recent_results": results[:10],  # 최근 10개
#                 "source": "mongodb",
#             },
#             "analyzed_at": datetime.now().isoformat(),
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"요약 분석 실패: {str(e)}")


# ===== P3.2: DuckDB 조회 API =====


@router.get("/{backtest_id}/portfolio-history")
async def get_portfolio_history(
    backtest_id: str,
):
    """백테스트 포트폴리오 히스토리 조회 (DuckDB)

    P3.2: 고성능 시계열 조회를 위한 DuckDB 조회
    """
    try:
        db_manager = service_factory.get_database_manager()
        df = db_manager.get_portfolio_history(backtest_id)

        if df is None or df.empty:
            raise HTTPException(
                status_code=404, detail=f"Portfolio history not found: {backtest_id}"
            )

        return {
            "status": "success",
            "backtest_id": backtest_id,
            "count": len(df),
            "data": df.to_dict(orient="records"),
            "source": "duckdb",
            "queried_at": datetime.now().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"포트폴리오 히스토리 조회 실패: {str(e)}")


@router.get("/{backtest_id}/trades-history")
async def get_trades_history(
    backtest_id: str,
):
    """백테스트 거래 내역 조회 (DuckDB)

    P3.2: 고성능 거래 내역 조회를 위한 DuckDB 조회
    """
    try:
        db_manager = service_factory.get_database_manager()
        df = db_manager.get_trades_history(backtest_id)

        if df is None or df.empty:
            raise HTTPException(
                status_code=404, detail=f"Trades history not found: {backtest_id}"
            )

        return {
            "status": "success",
            "backtest_id": backtest_id,
            "count": len(df),
            "data": df.to_dict(orient="records"),
            "source": "duckdb",
            "queried_at": datetime.now().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"거래 내역 조회 실패: {str(e)}")


# Include optimization routes


router.include_router(optimize_router, prefix="/optimize", tags=["Optimization"])
