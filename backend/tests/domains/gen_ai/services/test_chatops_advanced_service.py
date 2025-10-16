"""Tests for :mod:`app.services.gen_ai.applications.chatops_advanced_service`."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.gen_ai.applications.chatops_advanced_service import (
    ChatOpsAdvancedService,
)
from app.services.gen_ai.core.openai_client_manager import (
    InvalidModelError,
    ModelCapability,
    ModelConfig,
    ModelTier,
)
from app.schemas.gen_ai.rag import RAGContext


class _DummyOpenAIManager:
    def __init__(self, model_config: ModelConfig, *, raise_invalid: bool = False) -> None:
        self._model_config = model_config
        self._raise_invalid = raise_invalid
        self.get_client = MagicMock(return_value=MagicMock(name="AsyncOpenAI"))

    def get_service_policy(self, service_name: str) -> SimpleNamespace:
        return SimpleNamespace(default_model=self._model_config.model_id)

    def validate_model_for_service(
        self, service_name: str, requested_model_id: str | None
    ) -> ModelConfig:
        if self._raise_invalid:
            raise InvalidModelError("invalid model")
        if requested_model_id and requested_model_id != self._model_config.model_id:
            raise InvalidModelError("invalid model")
        return self._model_config


@pytest.fixture
def model_config() -> ModelConfig:
    return ModelConfig(
        model_id="gpt-4o",
        tier=ModelTier.STANDARD,
        capabilities=[
            ModelCapability.CHAT,
            ModelCapability.ANALYSIS,
            ModelCapability.FUNCTION_CALLING,
        ],
        input_price_per_1m=0.1,
        output_price_per_1m=0.2,
        max_tokens=128_000,
        supports_rag=True,
        description="test model",
    )


@pytest.fixture
def chatops_service(model_config: ModelConfig) -> ChatOpsAdvancedService:
    manager = _DummyOpenAIManager(model_config)
    return ChatOpsAdvancedService(
        backtest_service=MagicMock(name="BacktestService"),
        openai_manager=manager,
        rag_service=SimpleNamespace(search_similar_backtests=AsyncMock()),
    )


def test_format_rag_instruction_compiles_summary() -> None:
    contexts = [
        RAGContext(
            document_id="doc-1",
            content="Alpha strategy delivered 12% excess return.",
            similarity_score=0.92,
            metadata={
                "strategy_name": "Alpha",
                "start_date": "2024-01-01",
                "end_date": "2024-03-31",
                "total_return": 0.12,
                "sharpe_ratio": 1.45,
                "win_rate": 0.58,
            },
        )
    ]

    instruction = ChatOpsAdvancedService._format_rag_instruction(contexts)

    assert "Alpha" in instruction
    assert "총 수익률 12.00%" in instruction
    assert "샤프 1.45" in instruction
    assert instruction.strip().startswith("사용자의 과거 백테스트")


def test_resolve_model_config_invalid(model_config: ModelConfig) -> None:
    service = ChatOpsAdvancedService(
        backtest_service=MagicMock(),
        openai_manager=_DummyOpenAIManager(model_config, raise_invalid=True),
    )

    with pytest.raises(ValueError):
        service._resolve_model_config("gpt-4o")


@pytest.mark.asyncio
async def test_chat_raises_when_session_missing(chatops_service: ChatOpsAdvancedService, monkeypatch: pytest.MonkeyPatch) -> None:
    find_one = AsyncMock(return_value=None)
    monkeypatch.setattr(
        "app.services.gen_ai.applications.chatops_advanced_service.ChatSessionDocument.find_one",
        find_one,
    )

    with pytest.raises(ValueError):
        await chatops_service.chat("missing", "status?", include_history=False)

    find_one.assert_awaited_once()
