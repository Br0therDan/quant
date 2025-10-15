"""
ChatOps Advanced API Routes

Phase 3 D3: Multi-turn conversation, strategy comparison, auto backtest
"""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, status, BackgroundTasks

from app.schemas.gen_ai.chatops import (
    ChatOpsRequest,
    StrategyComparisonRequest,
    StrategyComparisonResult,
    AutoBacktestRequest,
    AutoBacktestResponse,
)
from app.services.service_factory import service_factory

logger = logging.getLogger(__name__)

router = APIRouter()


# 백그라운드 백테스트 실행 함수
async def run_backtest_in_background(backtest_id: str, notify: bool = True):
    """
    백그라운드에서 백테스트 실행

    Args:
        backtest_id: 백테스트 ID
        notify: 완료 시 알림 여부
    """
    try:
        logger.info(f"Starting background backtest execution: {backtest_id}")

        # ServiceFactory를 통해 필요한 서비스 가져오기
        from app.services.backtest.orchestrator import BacktestOrchestrator

        market_data_service = service_factory.get_market_data_service()
        strategy_service = service_factory.get_strategy_service()
        database_manager = service_factory.get_database_manager()
        ml_signal_service = service_factory.get_ml_signal_service()

        orchestrator = BacktestOrchestrator(
            market_data_service=market_data_service,
            strategy_service=strategy_service,
            database_manager=database_manager,
            ml_signal_service=ml_signal_service,
        )

        # 백테스트 실행
        result = await orchestrator.execute_backtest(backtest_id)

        if result:
            logger.info(
                f"Background backtest completed: {backtest_id}",
                extra={
                    "total_return": result.performance.total_return,
                    "sharpe_ratio": result.performance.sharpe_ratio,
                },
            )
        else:
            logger.warning(f"Background backtest returned no result: {backtest_id}")

        # 완료 알림 (향후 구현: 이메일, Slack 등)
        if notify:
            logger.info(f"Notification: Backtest {backtest_id} completed")

    except Exception as e:
        logger.error(
            f"Background backtest failed: {backtest_id}",
            exc_info=True,
            extra={"error": str(e)},
        )


@router.post("/session/create", response_model=dict[str, str])
async def create_chat_session(user_id: str) -> dict[str, str]:
    """
    새 채팅 세션 생성 (멀티턴 대화용, MongoDB 저장)

    **Phase 3 D3**

    Args:
        user_id: 사용자 ID

    Returns:
        session_id: 생성된 세션 ID
    """
    try:
        service = service_factory.get_chatops_advanced_service()
        session = await service.create_session(user_id)
        return {"session_id": session.session_id}
    except Exception as e:
        logger.error(f"Failed to create chat session: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}",
        )


@router.post("/session/{session_id}/chat", response_model=dict[str, Any])
async def chat_with_session(session_id: str, request: ChatOpsRequest) -> dict[str, Any]:
    """
    멀티턴 대화 (세션 기반)

    **Phase 3 D3**

    Args:
        session_id: 세션 ID
        request: ChatOps 요청

    Returns:
        응답 메시지 및 메타데이터
    """
    try:
        service = service_factory.get_chatops_advanced_service()
        answer = await service.chat(
            session_id, request.question, include_history=request.include_history
        )

        session = await service.get_session(session_id)
        conversation_turn = len(session.conversation_history) if session else 0

        return {
            "session_id": session_id,
            "query": request.question,
            "answer": answer,
            "conversation_turn": conversation_turn,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Chat failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat failed: {str(e)}",
        )


@router.post("/strategies/compare", response_model=StrategyComparisonResult)
async def compare_strategies(
    request: StrategyComparisonRequest,
) -> StrategyComparisonResult:
    """
    전략 비교 및 LLM 요약

    **Phase 3 D3**

    자연어 질의를 기반으로 여러 전략을 비교하고 추천을 제공합니다.

    Example:
        ```
        POST /api/v1/chatops-advanced/strategies/compare
        {
            "strategy_ids": ["strategy_1", "strategy_2", "strategy_3"],
            "metrics": ["total_return", "sharpe_ratio", "max_drawdown"],
            "natural_language_query": "가장 안정적인 전략은?"
        }
        ```

    Args:
        request: 전략 비교 요청

    Returns:
        StrategyComparisonResult: 비교 결과, 순위, 추천
    """
    try:
        service = service_factory.get_chatops_advanced_service()
        result = await service.compare_strategies(request)
        return result
    except Exception as e:
        logger.error(f"Strategy comparison failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Strategy comparison failed: {str(e)}",
        )


@router.post("/strategies/compare/debug", response_model=dict[str, Any])
async def debug_compare_strategies(
    request: StrategyComparisonRequest,
) -> dict[str, Any]:
    """
    전략 비교 디버그 (LLM 없이 데이터만 조회)

    **Phase 3 D3 Debug**

    MongoDB에서 실제 데이터를 조회하는 로직을 테스트합니다.
    LLM 호출 없이 전략 데이터만 반환합니다.

    Args:
        request: 전략 비교 요청

    Returns:
        조회된 전략 데이터 목록
    """
    try:
        from app.models.trading.strategy import Strategy
        from app.models.trading.backtest import Backtest, BacktestResult

        strategies_data = []
        for strategy_id in request.strategy_ids:
            # 전략 조회
            strategy = await Strategy.get(strategy_id)
            if not strategy:
                strategies_data.append(
                    {
                        "strategy_id": strategy_id,
                        "name": "Unknown Strategy",
                        "error": "전략을 찾을 수 없습니다",
                    }
                )
                continue

            # 최신 백테스트 결과 조회
            backtest = await Backtest.find_one(
                Backtest.strategy_id == strategy_id,
                Backtest.status == "completed",
                sort=[("created_at", -1)],
            )

            if not backtest:
                strategies_data.append(
                    {
                        "strategy_id": strategy_id,
                        "name": strategy.name,
                        "error": "완료된 백테스트 결과가 없습니다",
                    }
                )
                continue

            # 백테스트 결과 조회
            result = await BacktestResult.find_one(
                BacktestResult.backtest_id == str(backtest.id)
            )

            if not result:
                strategies_data.append(
                    {
                        "strategy_id": strategy_id,
                        "name": strategy.name,
                        "error": "백테스트 결과를 찾을 수 없습니다",
                    }
                )
                continue

            # 실제 데이터 추가
            strategies_data.append(
                {
                    "strategy_id": strategy_id,
                    "name": strategy.name,
                    "total_return": result.performance.total_return,
                    "sharpe_ratio": result.performance.sharpe_ratio,
                    "max_drawdown": result.performance.max_drawdown,
                    "backtest_period": {
                        "start": backtest.config.start_date.isoformat(),
                        "end": backtest.config.end_date.isoformat(),
                    },
                }
            )

        return {
            "status": "success",
            "query": request.natural_language_query or "No query provided",
            "strategies_data": strategies_data,
            "total_strategies": len(strategies_data),
        }
    except Exception as e:
        logger.error(f"Debug strategy comparison failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Debug failed: {str(e)}",
        )


@router.post("/backtest/trigger", response_model=AutoBacktestResponse)
async def trigger_auto_backtest(
    request: AutoBacktestRequest,
    background_tasks: BackgroundTasks,
    user_id: str = "system",
) -> AutoBacktestResponse:
    """
    자동 백테스트 트리거 (백그라운드 실행)

    **Phase 3 D3**

    전략 빌더 또는 최적화 결과를 기반으로 백테스트를 자동 생성하고 백그라운드에서 실행합니다.

    Example:
        ```
        POST /api/v1/chatops-advanced/backtest/trigger?user_id=user_123
        {
            "strategy_config": {
                "name": "RSI Strategy",
                "symbols": ["AAPL", "MSFT"],
                "initial_cash": 100000.0
            },
            "trigger_reason": "strategy_builder",
            "generate_report": true,
            "notify_on_completion": true
        }
        ```

    Args:
        request: 자동 백테스트 요청
        background_tasks: FastAPI 백그라운드 태스크
        user_id: 사용자 ID (기본: system)

    Returns:
        AutoBacktestResponse: 백테스트 ID, 상태, 예상 소요 시간
    """
    try:
        # 1. 백테스트 생성 (동기)
        service = service_factory.get_chatops_advanced_service()
        response = await service.trigger_backtest(request, user_id)

        # 2. 백그라운드 실행 추가
        background_tasks.add_task(
            run_backtest_in_background,
            response.backtest_id,
            request.notify_on_completion,
        )

        logger.info(
            f"Auto backtest queued for background execution: {response.backtest_id}"
        )

        return response
    except Exception as e:
        logger.error(f"Auto backtest trigger failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Auto backtest trigger failed: {str(e)}",
        )
