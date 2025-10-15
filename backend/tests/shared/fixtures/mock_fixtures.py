"""Reusable mocks for external integrations."""

from __future__ import annotations

from collections.abc import Iterator
from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def mock_alpha_vantage(monkeypatch) -> Iterator[MagicMock]:
    """Patch AlphaVantage client construction to return a MagicMock instance."""

    client = MagicMock(name="AlphaVantageClient")
    factory = MagicMock(return_value=client)
    monkeypatch.setattr("app.alpha_vantage.client.AlphaVantageClient", factory)
    monkeypatch.setattr("app.alpha_vantage.AlphaVantageClient", factory)
    yield client
    client.reset_mock()


@pytest.fixture
def mock_openai(monkeypatch) -> Iterator[AsyncMock]:
    """Patch the OpenAI async client used by the GenAI services."""

    client = AsyncMock(name="AsyncOpenAIClient")
    factory = MagicMock(return_value=client)
    monkeypatch.setattr("openai.AsyncOpenAI", factory)
    monkeypatch.setattr(
        "app.services.gen_ai.core.openai_client_manager.AsyncOpenAI", factory
    )
    yield client
    client.reset_mock()
