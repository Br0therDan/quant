"""
ChatOps Advanced API Routes

Phase 3 D3: Multi-turn conversation, strategy comparison, auto backtest
"""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.schemas.chatops import (
    ChatOpsRequest,
    StrategyComparisonRequest,
    StrategyComparisonResult,
    AutoBacktestRequest,
    AutoBacktestResponse,
)
from app.services.service_factory import service_factory

logger = logging.getLogger(__name__)

router = APIRouter()


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


@router.post("/backtest/trigger", response_model=AutoBacktestResponse)
async def trigger_auto_backtest(
    request: AutoBacktestRequest, user_id: str = "system"
) -> AutoBacktestResponse:
    """
    자동 백테스트 트리거

    **Phase 3 D3**

    전략 빌더 또는 최적화 결과를 기반으로 백테스트를 자동 실행합니다.

    Example:
        ```
        POST /api/v1/chatops-advanced/backtest/trigger?user_id=user_123
        {
            "strategy_config": { "name": "RSI Strategy", "indicators": [...] },
            "trigger_reason": "strategy_builder",
            "generate_report": true,
            "notify_on_completion": true
        }
        ```

    Args:
        request: 자동 백테스트 요청
        user_id: 사용자 ID (기본: system)

    Returns:
        AutoBacktestResponse: 백테스트 ID, 상태, 예상 소요 시간
    """
    try:
        service = service_factory.get_chatops_advanced_service()
        response = await service.trigger_backtest(request, user_id)
        return response
    except Exception as e:
        logger.error(f"Auto backtest trigger failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Auto backtest trigger failed: {str(e)}",
        )
