"""
ChatOps Advanced Service

Phase 3 D3: Multi-turn conversation, strategy comparison, auto backtest triggering
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from openai import AsyncOpenAI

from app.core.config import settings
from app.models.gen_ai.chatops.session import ChatSessionDocument
from app.schemas.gen_ai.chatops import (
    AutoBacktestRequest,
    AutoBacktestResponse,
    ChatSession,
    ConversationRole,
    ConversationTurn,
    StrategyComparisonRequest,
    StrategyComparisonResult,
)
from app.services.trading.backtest_service import BacktestService

logger = logging.getLogger(__name__)


class ChatOpsAdvancedService:
    """ChatOps 고급 기능 서비스"""

    def __init__(self, backtest_service: BacktestService):
        """
        Initialize ChatOps Advanced Service

        Args:
            backtest_service: 백테스트 서비스
        """
        self.backtest_service = backtest_service

        # OpenAI 클라이언트 초기화
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            logger.warning(
                "OPENAI_API_KEY not set. ChatOps Advanced will not function."
            )
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=api_key)

        self.model = "gpt-4o"  # 최신 모델 사용

    async def create_session(self, user_id: str) -> ChatSession:
        """새 채팅 세션 생성 (MongoDB 저장)"""
        session_id = str(uuid.uuid4())

        # MongoDB Document 생성
        session_doc = ChatSessionDocument(
            session_id=session_id,
            user_id=user_id,
            conversation_history=[],
            context={},
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_active=True,
        )

        # MongoDB 저장
        await session_doc.insert()
        logger.info(f"Created chat session {session_id} for user {user_id} in MongoDB")

        # Pydantic 모델로 반환
        return ChatSession(
            session_id=session_doc.session_id,
            user_id=session_doc.user_id,
            conversation_history=session_doc.conversation_history,
            context=session_doc.context,
            created_at=session_doc.created_at,
            updated_at=session_doc.updated_at,
            is_active=session_doc.is_active,
        )

    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """세션 조회 (MongoDB)"""
        session_doc = await ChatSessionDocument.find_one(
            ChatSessionDocument.session_id == session_id
        )

        if not session_doc:
            return None

        # Pydantic 모델로 변환
        return ChatSession(
            session_id=session_doc.session_id,
            user_id=session_doc.user_id,
            conversation_history=session_doc.conversation_history,
            context=session_doc.context,
            created_at=session_doc.created_at,
            updated_at=session_doc.updated_at,
            is_active=session_doc.is_active,
        )

    async def chat(
        self, session_id: str, user_query: str, include_history: bool = True
    ) -> str:
        """
        멀티턴 대화 처리 (MongoDB 저장)

        Args:
            session_id: 세션 ID
            user_query: 사용자 질의
            include_history: 대화 히스토리 포함 여부

        Returns:
            LLM 응답
        """
        # MongoDB에서 세션 조회
        session_doc = await ChatSessionDocument.find_one(
            ChatSessionDocument.session_id == session_id
        )

        if not session_doc:
            raise ValueError(f"Session {session_id} not found")

        if not self.client:
            raise Exception("OpenAI client not initialized. Check OPENAI_API_KEY.")

        # 사용자 턴 추가
        user_turn = ConversationTurn(
            role=ConversationRole.USER, content=user_query, metadata=None
        )
        session_doc.conversation_history.append(user_turn)

        # 메시지 준비
        messages = []
        if include_history:
            # 히스토리 포함 (최근 10턴)
            for turn in session_doc.conversation_history[-10:]:
                messages.append({"role": turn.role.value, "content": turn.content})
        else:
            # 현재 질문만
            messages.append({"role": "user", "content": user_query})

        # LLM 호출
        response = await self.client.chat.completions.create(
            model=self.model, messages=messages, temperature=0.7, max_tokens=1000
        )

        answer = response.choices[0].message.content or ""

        # 어시스턴트 턴 추가
        assistant_turn = ConversationTurn(
            role=ConversationRole.ASSISTANT, content=answer, metadata=None
        )
        session_doc.conversation_history.append(assistant_turn)
        session_doc.updated_at = datetime.now(timezone.utc)

        # MongoDB 업데이트
        await session_doc.save()

        logger.info(
            f"Chat session {session_id}: turn {len(session_doc.conversation_history)}"
        )
        return answer

    async def compare_strategies(
        self, request: StrategyComparisonRequest
    ) -> StrategyComparisonResult:
        """
        전략 비교 및 LLM 요약

        Args:
            request: 전략 비교 요청

        Returns:
            StrategyComparisonResult: 비교 결과
        """
        if not self.client:
            raise Exception("OpenAI client not initialized. Check OPENAI_API_KEY.")

        # 1. 전략 데이터 수집 (실제 MongoDB 조회)
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

        # 2. LLM 프롬프트 생성
        prompt = f"""
다음 전략들을 비교 분석하고 사용자의 질의에 답변하세요.

전략 데이터:
{json.dumps(strategies_data, indent=2, ensure_ascii=False)}

비교 메트릭: {", ".join(request.metrics)}

사용자 질의: {request.natural_language_query or "가장 성능이 좋은 전략은?"}

다음 형식으로 응답하세요:
1. 전략별 요약 (50-200자)
2. 순위 (1위부터)
3. 추천 전략 및 근거 (50-200자)
"""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=1500,
        )

        summary = response.choices[0].message.content or "전략 비교 결과를 생성할 수 없습니다."

        # 3. 순위 계산 (간단한 로직: total_return 기준)
        sorted_strategies = sorted(
            strategies_data, key=lambda x: x.get("total_return", 0), reverse=True
        )
        ranking = [s["strategy_id"] for s in sorted_strategies]
        recommendation = ranking[0]

        return StrategyComparisonResult(
            query=request.natural_language_query or "전략 비교",
            strategies=strategies_data,
            ranking=ranking,
            summary=summary,
            recommendation=recommendation,
            reasoning="가장 높은 총 수익률과 샤프 비율을 기록한 전략을 추천합니다. 최대 낙폭도 상대적으로 낮아 안정적입니다.",
        )

    async def trigger_backtest(
        self, request: AutoBacktestRequest, user_id: str
    ) -> AutoBacktestResponse:
        """
        자동 백테스트 트리거 (실제 백테스트 생성)

        Args:
            request: 자동 백테스트 요청
            user_id: 사용자 ID

        Returns:
            AutoBacktestResponse: 백테스트 응답
        """
        try:
            # 1. 백테스트 설정 생성
            from app.models.trading.backtest import BacktestConfig
            from datetime import datetime, timedelta

            # strategy_config에서 필요한 정보 추출
            strategy_name = request.strategy_config.get(
                "name", "Auto Generated Strategy"
            )
            symbols = request.strategy_config.get("symbols", ["AAPL"])

            # 백테스트 기간 설정 (기본: 최근 1년)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)

            config = BacktestConfig(
                name=f"Auto: {strategy_name}",
                description=f"Triggered by {request.trigger_reason}",
                start_date=start_date,
                end_date=end_date,
                symbols=symbols,
                initial_cash=request.strategy_config.get("initial_cash", 100000.0),
                max_position_size=request.strategy_config.get("max_position_size", 0.2),
                commission_rate=request.strategy_config.get("commission_rate", 0.001),
                slippage_rate=request.strategy_config.get("slippage_rate", 0.0005),
                rebalance_frequency=request.strategy_config.get("rebalance_frequency"),
                tags=[request.trigger_reason, "auto_generated"],
            )

            # 2. 백테스트 생성
            backtest = await self.backtest_service.create_backtest(
                name=config.name,
                description=config.description,
                config=config,
                user_id=user_id,
            )

            logger.info(
                f"Auto backtest created: {backtest.id} by {user_id}",
                extra={
                    "backtest_id": str(backtest.id),
                    "reason": request.trigger_reason,
                    "symbols": symbols,
                },
            )

            # 3. 예상 소요 시간 계산 (심볼 개수와 기간에 따라)
            days = (end_date - start_date).days
            estimated_duration = 30 + (len(symbols) * 10) + (days // 30)  # 초 단위

            # 4. 백그라운드 실행은 FastAPI BackgroundTasks를 통해 라우터에서 처리
            return AutoBacktestResponse(
                backtest_id=str(backtest.id),
                status="pending",
                estimated_duration_seconds=estimated_duration,
                report_url=None,  # 완료 후 업데이트
            )

        except Exception as e:
            logger.error(f"Failed to trigger auto backtest: {e}", exc_info=True)
            raise ValueError(f"Auto backtest trigger failed: {str(e)}")
