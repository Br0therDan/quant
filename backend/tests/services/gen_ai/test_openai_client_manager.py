"""Unit tests for the OpenAIClientManager singleton."""

from types import SimpleNamespace

import pytest

from app.core.config import settings
from app.services.gen_ai.core.openai_client_manager import (
    InvalidModelError,
    ModelTier,
    OpenAIClientManager,
)


@pytest.fixture(autouse=True)
def reset_manager(monkeypatch):
    """Ensure a clean singleton instance for every test."""

    monkeypatch.setattr(settings, "OPENAI_API_KEY", "test-key", raising=False)
    OpenAIClientManager._reset_instance()
    yield
    OpenAIClientManager._reset_instance()


def test_singleton_returns_same_instance():
    """The manager should behave as a singleton."""

    manager_a = OpenAIClientManager()
    manager_b = OpenAIClientManager()
    assert manager_a is manager_b


def test_validate_model_for_service_returns_default_when_not_specified():
    """If no model is provided the service default should be returned."""

    manager = OpenAIClientManager()

    config = manager.validate_model_for_service("strategy_builder", None)

    assert config.model_id == "gpt-4o-mini"
    assert config.tier == ModelTier.MINI


def test_validate_model_for_service_rejects_disallowed_model():
    """A model outside the allowed tier should raise an error."""

    manager = OpenAIClientManager()

    with pytest.raises(InvalidModelError):
        manager.validate_model_for_service("strategy_builder", "o1-preview")


def test_track_usage_calculates_cost():
    """Cost should be derived from the configured price table."""

    manager = OpenAIClientManager()
    usage = SimpleNamespace(prompt_tokens=5000, completion_tokens=2500)

    record = manager.track_usage("strategy_builder", "gpt-4o-mini", usage)

    assert record is not None
    assert record.input_tokens == 5000
    assert record.output_tokens == 2500
    # 5000 tokens -> 0.005 of 1M, 2500 tokens -> 0.0025 of 1M
    expected_cost = (0.005 * 0.15) + (0.0025 * 0.60)
    assert pytest.approx(record.total_cost_usd, rel=1e-6) == expected_cost
