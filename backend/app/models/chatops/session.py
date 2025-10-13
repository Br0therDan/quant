"""ChatOps 세션 모델"""

from datetime import datetime
from typing import Any, Dict, List

from beanie import Document
from pymongo import IndexModel, ASCENDING, DESCENDING
from pydantic import ConfigDict, Field

from app.schemas.chatops import ConversationTurn


class ChatSessionDocument(Document):
    """
    ChatOps 세션 MongoDB 문서

    인메모리 Dict를 대체하여 영구 저장 및 분산 환경 지원
    """

    session_id: str = Field(..., description="세션 고유 ID (UUID)")
    user_id: str = Field(..., description="사용자 ID")
    conversation_history: List[ConversationTurn] = Field(
        default_factory=list, description="대화 히스토리"
    )
    context: Dict[str, Any] = Field(default_factory=dict, description="세션 컨텍스트")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="생성 일시")
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="최종 업데이트 일시"
    )
    is_active: bool = Field(default=True, description="세션 활성 상태")

    class Settings:
        name = "chat_sessions"
        indexes = [
            IndexModel([("session_id", ASCENDING)], unique=True, name="idx_session_id"),
            IndexModel([("user_id", ASCENDING)], name="idx_user_id"),
            IndexModel(
                [("updated_at", DESCENDING)],
                name="idx_updated_at_ttl",
                expireAfterSeconds=86400,  # 24시간 TTL
            ),
            IndexModel([("is_active", ASCENDING)], name="idx_is_active"),
            IndexModel(
                [("user_id", ASCENDING), ("is_active", ASCENDING)],
                name="idx_user_active",
            ),
        ]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "ce6887b6-a78e-4621-bae7-7869a046135a",
                "user_id": "test_user",
                "conversation_history": [
                    {
                        "role": "user",
                        "content": "현재 DuckDB 캐시 상태는?",
                        "timestamp": "2025-10-14T10:00:00Z",
                        "metadata": None,
                    }
                ],
                "context": {"last_query": "cache_status"},
                "created_at": "2025-10-14T10:00:00Z",
                "updated_at": "2025-10-14T10:00:00Z",
                "is_active": True,
            }
        }
    )
