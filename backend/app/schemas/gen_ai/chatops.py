"""Schemas for ChatOps agent interactions."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.schemas.enums import ConversationRole
from app.schemas.user.dashboard import DataQualitySeverity, DataQualitySummary


# Phase 3 D3: Multi-turn conversation schemas
class ConversationTurn(BaseModel):
    """대화 턴"""

    role: ConversationRole = Field(..., description="화자 역할")
    content: str = Field(..., min_length=1, max_length=5000, description="메시지 내용")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="발화 시각")
    metadata: Optional[Dict[str, Any]] = Field(None, description="추가 메타데이터")


class ChatSession(BaseModel):
    """채팅 세션"""

    session_id: str = Field(..., description="세션 고유 ID")
    user_id: str = Field(..., description="사용자 ID")
    conversation_history: List[ConversationTurn] = Field(
        default_factory=list, description="대화 히스토리"
    )
    context: Dict[str, Any] = Field(
        default_factory=dict, description="세션 컨텍스트 (전략 ID, 심볼 등)"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow, description="생성 시각")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="최종 업데이트")
    is_active: bool = Field(default=True, description="활성 상태")


class ChatOpsRequest(BaseModel):
    """Request payload for ChatOps interactions."""

    question: str = Field(..., description="사용자 질문 또는 명령")
    user_roles: List[str] = Field(
        default_factory=list,
        description="요청을 수행하는 사용자의 역할 목록",
    )
    channel: Optional[str] = Field(
        default=None,
        description="질문이 발생한 채널(Slack, Console 등)",
    )
    # Phase 3 D3: Multi-turn support
    session_id: Optional[str] = Field(None, description="세션 ID (멀티턴 대화)")
    include_history: bool = Field(default=True, description="대화 히스토리 포함 여부")
    model_id: Optional[str] = Field(
        default=None,
        description="사용할 OpenAI 모델 ID (지정하지 않으면 기본 정책 사용)",
    )


class CacheStatusSnapshot(BaseModel):
    """Current cache backend health snapshot."""

    duckdb_status: str = Field(..., description="DuckDB 연결 상태")
    duckdb_row_count: Optional[int] = Field(
        default=None, description="DuckDB 일별 시계열 행 수"
    )
    duckdb_last_updated: Optional[datetime] = Field(
        default=None, description="DuckDB 최신 시계열 업데이트 시간"
    )
    mongodb_status: str = Field(..., description="MongoDB 연결 상태")
    mongodb_last_event_at: Optional[datetime] = Field(
        default=None, description="MongoDB에서 관측된 최신 데이터 품질 이벤트 시간"
    )
    notes: List[str] = Field(default_factory=list, description="추가 관찰 사항 또는 경고")


class FailureInsight(BaseModel):
    """Represents a recent operational failure surfaced to the operator."""

    source: str = Field(..., description="실패 이벤트 출처 (예: backtest, data_quality)")
    identifier: str = Field(..., description="이벤트 식별자 또는 연관 객체")
    occurred_at: datetime = Field(..., description="실패가 발생한 시간")
    severity: Optional[DataQualitySeverity] = Field(
        default=None, description="데이터 품질 이벤트의 심각도"
    )
    message: str = Field(..., description="사용자에게 노출할 메시지")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="추가 컨텍스트 메타데이터")


class ChatOpsResponse(BaseModel):
    """Response payload returned by the ChatOps agent."""

    answer: str = Field(..., description="사용자에게 제공되는 요약 응답")
    used_tools: List[str] = Field(default_factory=list, description="실행된 ChatOps 툴 목록")
    denied_tools: List[str] = Field(
        default_factory=list, description="권한 부족으로 실행되지 않은 툴 목록"
    )
    cache_status: Optional[CacheStatusSnapshot] = Field(
        default=None, description="캐시 및 저장소 상태 스냅샷"
    )
    data_quality: Optional[DataQualitySummary] = Field(
        default=None, description="데이터 품질 센티널 요약"
    )
    recent_failures: List[FailureInsight] = Field(
        default_factory=list, description="최근 운영 실패 목록"
    )
    external_services: Dict[str, Any] = Field(
        default_factory=dict, description="외부 서비스 상태"
    )


__all__ = [
    "ChatOpsRequest",
    "ChatOpsResponse",
    "CacheStatusSnapshot",
    "FailureInsight",
    # Phase 3 D3
    "ConversationRole",
    "ConversationTurn",
    "ChatSession",
    "StrategyComparisonRequest",
    "StrategyComparisonResult",
    "AutoBacktestRequest",
    "AutoBacktestResponse",
]


# Phase 3 D3: Strategy Comparison
class StrategyComparisonRequest(BaseModel):
    """전략 비교 요청"""

    strategy_ids: List[str] = Field(
        ..., min_length=2, max_length=5, description="비교할 전략 ID 목록 (2-5개)"
    )
    metrics: List[str] = Field(
        default_factory=lambda: ["total_return", "sharpe_ratio", "max_drawdown"],
        description="비교할 메트릭 목록",
    )
    natural_language_query: Optional[str] = Field(
        None, description="자연어 비교 질의 (예: '가장 안정적인 전략은?')"
    )


class StrategyComparisonResult(BaseModel):
    """전략 비교 결과"""

    query: str = Field(..., description="원본 질의")
    strategies: List[Dict[str, Any]] = Field(..., description="전략별 메트릭")
    ranking: List[str] = Field(..., description="순위 (전략 ID 목록)")
    summary: str = Field(..., min_length=50, max_length=1000, description="LLM 요약")
    recommendation: str = Field(..., description="추천 전략 ID")
    reasoning: str = Field(..., min_length=50, max_length=500, description="추천 근거")


# Phase 3 D3: Auto Backtest Triggering
class AutoBacktestRequest(BaseModel):
    """자동 백테스트 트리거 요청"""

    strategy_config: Dict[str, Any] = Field(..., description="전략 설정 (JSON)")
    trigger_reason: str = Field(
        ..., description="트리거 사유 (예: 'strategy_builder', 'optimization')"
    )
    generate_report: bool = Field(default=True, description="내러티브 리포트 자동 생성")
    notify_on_completion: bool = Field(default=True, description="완료 시 알림")


class AutoBacktestResponse(BaseModel):
    """자동 백테스트 응답"""

    backtest_id: str = Field(..., description="생성된 백테스트 ID")
    status: str = Field(..., description="상태 (pending, running, completed)")
    estimated_duration_seconds: int = Field(..., description="예상 소요 시간 (초)")
    report_url: Optional[str] = Field(None, description="리포트 URL (완료 후)")
