"""Schemas for ChatOps agent interactions."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .dashboard import DataQualitySeverity, DataQualitySummary


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
    notes: List[str] = Field(
        default_factory=list, description="추가 관찰 사항 또는 경고"
    )


class FailureInsight(BaseModel):
    """Represents a recent operational failure surfaced to the operator."""

    source: str = Field(..., description="실패 이벤트 출처 (예: backtest, data_quality)")
    identifier: str = Field(..., description="이벤트 식별자 또는 연관 객체")
    occurred_at: datetime = Field(..., description="실패가 발생한 시간")
    severity: Optional[DataQualitySeverity] = Field(
        default=None, description="데이터 품질 이벤트의 심각도"
    )
    message: str = Field(..., description="사용자에게 노출할 메시지")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="추가 컨텍스트 메타데이터"
    )


class ChatOpsResponse(BaseModel):
    """Response payload returned by the ChatOps agent."""

    answer: str = Field(..., description="사용자에게 제공되는 요약 응답")
    used_tools: List[str] = Field(
        default_factory=list, description="실행된 ChatOps 툴 목록"
    )
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
]
