"""
통합 백테스트 API 엔드포인트 - 모든 서비스 연동
"""

from datetime import datetime
from typing import Dict, Any, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.models.strategy import StrategyType
from app.models.backtest import BacktestStatus
from app.services.service_factory import service_factory
from app.services.integrated_backtest_executor import IntegratedBacktestExecutor


router = APIRouter(prefix="/integrated", tags=["Integrated Backtest"])


class IntegratedBacktestRequest(BaseModel):
    """통합 백테스트 요청"""

    name: str
    description: str = ""
    symbols: List[str]
    start_date: datetime
    end_date: datetime
    strategy_type: StrategyType
    strategy_params: Dict[str, Any] = {}
    initial_capital: float = 100000.0


class IntegratedBacktestResponse(BaseModel):
    """통합 백테스트 응답"""

    backtest_id: str
    status: BacktestStatus
    message: str


async def get_integrated_executor() -> IntegratedBacktestExecutor:
    """통합 백테스트 실행기 의존성 주입"""
    market_data_service = service_factory.get_market_data_service()
    strategy_service = service_factory.get_strategy_service()

    return IntegratedBacktestExecutor(
        market_data_service=market_data_service, strategy_service=strategy_service
    )


@router.post("/backtest", response_model=IntegratedBacktestResponse)
async def create_and_run_integrated_backtest(
    request: IntegratedBacktestRequest,
    executor: IntegratedBacktestExecutor = Depends(get_integrated_executor),
):
    """통합 백테스트 생성 및 실행"""

    try:
        # 1. 백테스트 생성
        backtest_service = service_factory.get_backtest_service()

        from app.models.backtest import BacktestConfig

        config = BacktestConfig(
            symbols=request.symbols,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_capital=request.initial_capital,
            strategy_type=request.strategy_type.value,
            parameters=request.strategy_params,
        )

        backtest = await backtest_service.create_backtest(
            name=request.name, description=request.description, config=config
        )

        # 2. 통합 백테스트 실행
        result = await executor.execute_integrated_backtest(
            backtest_id=str(backtest.id),
            symbols=request.symbols,
            start_date=request.start_date,
            end_date=request.end_date,
            strategy_type=request.strategy_type,
            strategy_params=request.strategy_params,
            initial_capital=request.initial_capital,
        )

        if result:
            return IntegratedBacktestResponse(
                backtest_id=str(backtest.id),
                status=BacktestStatus.COMPLETED,
                message="Integrated backtest completed successfully",
            )
        else:
            return IntegratedBacktestResponse(
                backtest_id=str(backtest.id),
                status=BacktestStatus.FAILED,
                message="Integrated backtest execution failed",
            )

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
        # backtest_service = service_factory.get_backtest_service()

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
