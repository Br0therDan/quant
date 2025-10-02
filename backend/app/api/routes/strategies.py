"""
Strategy API Routes
"""

from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import ValidationError

from mysingle_quant.auth import get_current_active_verified_user, User
from app.models.strategy import StrategyType
from app.schemas.strategy import (
    ExecutionListResponse,
    ExecutionResponse,
    PerformanceResponse,
    StrategyCreateRequest,
    StrategyExecuteRequest,
    StrategyListResponse,
    StrategyResponse,
    StrategyUpdateRequest,
)
from .templates import router as templates_router
from app.services.service_factory import service_factory
from app.services.strategy_service import StrategyService

router = APIRouter(dependencies=[Depends(get_current_active_verified_user)])


async def get_strategy_service() -> AsyncGenerator[StrategyService, None]:
    """Dependency to get strategy service with proper cleanup"""
    service = service_factory.get_strategy_service()
    try:
        yield service
    finally:
        pass  # ServiceFactory manages cleanup


@router.post("/", response_model=StrategyResponse)
async def create_strategy(
    request: StrategyCreateRequest,
    current_user: User = Depends(get_current_active_verified_user),
    service: StrategyService = Depends(get_strategy_service),
):
    """Create a new strategy"""
    try:
        strategy = await service.create_strategy(
            name=request.name,
            strategy_type=request.strategy_type,
            description=request.description,
            parameters=request.parameters,
            tags=(
                [tag for tag in request.tags if tag is not None]
                if request.tags
                else None
            ),
            user_id=str(current_user.id),
        )

        return StrategyResponse(
            id=str(strategy.id),
            name=strategy.name,
            strategy_type=strategy.strategy_type,
            description=strategy.description,
            parameters=strategy.parameters,
            is_active=strategy.is_active,
            is_template=strategy.is_template,
            created_by=strategy.created_by,
            created_at=strategy.created_at,
            updated_at=strategy.updated_at,
            tags=strategy.tags,
        )

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=StrategyListResponse)
async def get_strategies(
    strategy_type: StrategyType | None = Query(None, description="전략 타입 필터"),
    is_active: bool | None = Query(None, description="활성화 상태 필터"),
    is_template: bool | None = Query(None, description="템플릿 여부 필터"),
    limit: int = Query(50, ge=1, le=200, description="결과 수 제한"),
    current_user: User = Depends(get_current_active_verified_user),
    service: StrategyService = Depends(get_strategy_service),
):
    """Get list of strategies"""
    try:
        strategies = await service.get_strategies(
            strategy_type=strategy_type,
            is_active=is_active,
            is_template=is_template,
            limit=limit,
            user_id=str(current_user.id),
        )

        strategy_responses = [
            StrategyResponse(
                id=str(strategy.id),
                name=strategy.name,
                strategy_type=strategy.strategy_type,
                description=strategy.description,
                parameters=strategy.parameters,
                is_active=strategy.is_active,
                is_template=strategy.is_template,
                created_by=strategy.created_by,
                created_at=strategy.created_at,
                updated_at=strategy.updated_at,
                tags=strategy.tags,
            )
            for strategy in strategies
        ]

        return StrategyListResponse(
            strategies=strategy_responses,
            total=len(strategy_responses),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(
    strategy_id: str,
    current_user: User = Depends(get_current_active_verified_user),
    service: StrategyService = Depends(get_strategy_service),
):
    """Get strategy by ID"""
    try:
        strategy = await service.get_strategy(strategy_id)

        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")

        # 소유권 체크 (템플릿이 아닌 경우)
        if not strategy.is_template and strategy.user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Access denied")

        return StrategyResponse(
            id=str(strategy.id),
            name=strategy.name,
            strategy_type=strategy.strategy_type,
            description=strategy.description,
            parameters=strategy.parameters,
            is_active=strategy.is_active,
            is_template=strategy.is_template,
            created_by=strategy.created_by,
            created_at=strategy.created_at,
            updated_at=strategy.updated_at,
            tags=strategy.tags,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(
    strategy_id: str,
    request: StrategyUpdateRequest,
    current_user: User = Depends(get_current_active_verified_user),
    service: StrategyService = Depends(get_strategy_service),
):
    """Update strategy"""
    try:
        # 먼저 소유권 확인
        existing_strategy = await service.get_strategy(strategy_id)
        if not existing_strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")

        if not existing_strategy.is_template and existing_strategy.user_id != str(
            current_user.id
        ):
            raise HTTPException(status_code=403, detail="Access denied")

        strategy = await service.update_strategy(
            strategy_id=strategy_id,
            name=request.name,
            description=request.description,
            parameters=request.parameters,
            is_active=request.is_active,
            tags=(
                [tag for tag in request.tags if tag is not None]
                if request.tags
                else None
            ),
        )

        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")

        return StrategyResponse(
            id=str(strategy.id),
            name=strategy.name,
            strategy_type=strategy.strategy_type,
            description=strategy.description,
            parameters=strategy.parameters,
            is_active=strategy.is_active,
            is_template=strategy.is_template,
            created_by=strategy.created_by,
            created_at=strategy.created_at,
            updated_at=strategy.updated_at,
            tags=strategy.tags,
        )

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{strategy_id}")
async def delete_strategy(
    strategy_id: str,
    current_user: User = Depends(get_current_active_verified_user),
    service: StrategyService = Depends(get_strategy_service),
):
    """Delete strategy (soft delete)"""
    try:
        # 먼저 소유권 확인
        existing_strategy = await service.get_strategy(strategy_id)
        if not existing_strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")

        if not existing_strategy.is_template and existing_strategy.user_id != str(
            current_user.id
        ):
            raise HTTPException(status_code=403, detail="Access denied")

        success = await service.delete_strategy(strategy_id)

        if not success:
            raise HTTPException(status_code=404, detail="Strategy not found")

        return {"message": "Strategy deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{strategy_id}/execute", response_model=ExecutionResponse)
async def execute_strategy(
    strategy_id: str,
    request: StrategyExecuteRequest,
    current_user: User = Depends(get_current_active_verified_user),
    service: StrategyService = Depends(get_strategy_service),
):
    """Execute strategy and generate signal"""
    try:
        # 먼저 소유권 확인
        existing_strategy = await service.get_strategy(strategy_id)
        if not existing_strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")

        if not existing_strategy.is_template and existing_strategy.user_id != str(
            current_user.id
        ):
            raise HTTPException(status_code=403, detail="Access denied")

        execution = await service.execute_strategy(
            strategy_id=strategy_id,
            symbol=request.symbol,
            market_data=request.market_data,
        )

        if not execution:
            raise HTTPException(
                status_code=404, detail="Strategy not found or execution failed"
            )

        return ExecutionResponse(
            id=str(execution.id),
            strategy_id=execution.strategy_id,
            strategy_name=execution.strategy_name,
            symbol=execution.symbol,
            signal_type=execution.signal_type,
            signal_strength=execution.signal_strength,
            price=execution.price,
            timestamp=execution.timestamp,
            metadata=execution.metadata,
            backtest_id=execution.backtest_id,
            created_at=execution.created_at,
        )

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{strategy_id}/executions", response_model=ExecutionListResponse)
async def get_strategy_executions(
    strategy_id: str,
    limit: int = Query(100, ge=1, le=500, description="결과 수 제한"),
    service: StrategyService = Depends(get_strategy_service),
):
    """Get strategy execution history"""
    try:
        executions = await service.get_strategy_executions(
            strategy_id=strategy_id,
            limit=limit,
        )

        execution_responses = [
            ExecutionResponse(
                id=str(execution.id),
                strategy_id=execution.strategy_id,
                strategy_name=execution.strategy_name,
                symbol=execution.symbol,
                signal_type=execution.signal_type,
                signal_strength=execution.signal_strength,
                price=execution.price,
                timestamp=execution.timestamp,
                metadata=execution.metadata,
                backtest_id=execution.backtest_id,
                created_at=execution.created_at,
            )
            for execution in executions
        ]

        return ExecutionListResponse(
            executions=execution_responses,
            total=len(execution_responses),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{strategy_id}/performance", response_model=PerformanceResponse)
async def get_strategy_performance(
    strategy_id: str,
    service: StrategyService = Depends(get_strategy_service),
):
    """Get strategy performance metrics"""
    try:
        performance = await service.get_strategy_performance(strategy_id)

        if not performance:
            # Calculate performance if not exists
            performance = await service.calculate_performance_metrics(strategy_id)

        if not performance:
            raise HTTPException(
                status_code=404, detail="Performance data not available"
            )

        return PerformanceResponse(
            id=str(performance.id),
            strategy_id=performance.strategy_id,
            strategy_name=performance.strategy_name,
            total_signals=performance.total_signals,
            buy_signals=performance.buy_signals,
            sell_signals=performance.sell_signals,
            hold_signals=performance.hold_signals,
            total_return=performance.total_return,
            win_rate=performance.win_rate,
            avg_return_per_trade=performance.avg_return_per_trade,
            max_drawdown=performance.max_drawdown,
            sharpe_ratio=performance.sharpe_ratio,
            calmar_ratio=performance.calmar_ratio,
            volatility=performance.volatility,
            start_date=performance.start_date,
            end_date=performance.end_date,
            accuracy=performance.accuracy,
            avg_signal_strength=performance.avg_signal_strength,
            created_at=performance.created_at,
            updated_at=performance.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


router.include_router(templates_router, prefix="/templates")
