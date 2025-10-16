"""Tests for :class:`PromptGovernanceService`."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from app.models.gen_ai.prompt_governance import PromptEvaluationSummary, PromptTemplate
from app.schemas.enums import PromptRiskLevel, PromptStatus
from app.services.gen_ai.agents.prompt_governance_service import (
    PromptGovernanceService,
    _TOXIC_PATTERNS,
)


@pytest.fixture
def service() -> PromptGovernanceService:
    return PromptGovernanceService()


def test_calculate_score_detects_patterns(service: PromptGovernanceService) -> None:
    clean = service._calculate_score("Hello world", _TOXIC_PATTERNS)
    assert clean == 0.0

    score = service._calculate_score("This idea is dumb and I hate it", _TOXIC_PATTERNS)
    assert score == pytest.approx(0.3)


def test_evaluate_content_sets_risk_levels(service: PromptGovernanceService) -> None:
    summary = service._evaluate_content("This never fails and always wins", evaluator="qa")

    assert isinstance(summary, PromptEvaluationSummary)
    assert summary.risk_level is PromptRiskLevel.MEDIUM
    assert summary.evaluator == "qa"
    assert 0 <= summary.toxicity_score <= 1
    assert summary.hallucination_score > 0
    assert summary.factual_consistency <= 1.0


@pytest.mark.asyncio
async def test_create_template_inserts_and_logs(monkeypatch: pytest.MonkeyPatch) -> None:
    service = PromptGovernanceService()
    payload = {
        "prompt_id": "risk-check",
        "version": "v1",
        "name": "Risk Check",
        "description": "Ensure compliance",
        "content": "Always evaluate risk exposure",
        "owner": "alice",
        "tags": ["compliance"],
        "risk_level": PromptRiskLevel.MEDIUM,
        "policies": ["base"],
    }

    find_one = AsyncMock(return_value=None)
    insert_mock = AsyncMock()
    log_audit = AsyncMock()

    monkeypatch.setattr(
        "app.services.gen_ai.agents.prompt_governance_service.PromptTemplate.find_one",
        find_one,
    )
    monkeypatch.setattr(
        "app.services.gen_ai.agents.prompt_governance_service.PromptTemplate.insert",
        insert_mock,
    )
    monkeypatch.setattr(service, "_log_audit", log_audit)

    template = await service.create_template(payload)

    find_one.assert_awaited_once()
    insert_mock.assert_awaited_once()
    log_audit.assert_awaited_once()
    assert template.prompt_id == "risk-check"
    assert template.evaluation is not None


@pytest.mark.asyncio
async def test_create_template_rejects_duplicates(monkeypatch: pytest.MonkeyPatch) -> None:
    service = PromptGovernanceService()
    payload = {
        "prompt_id": "risk-check",
        "version": "v1",
        "name": "Risk Check",
        "description": "Ensure compliance",
        "content": "Always evaluate risk exposure",
        "owner": "alice",
        "tags": ["compliance"],
        "risk_level": PromptRiskLevel.MEDIUM,
        "policies": ["base"],
    }

    existing = PromptTemplate(
        prompt_id="risk-check",
        version="v1",
        name="Risk Check",
        description="Ensure compliance",
        content="Always evaluate risk exposure",
        owner="alice",
        tags=["compliance"],
        status=PromptStatus.DRAFT,
        risk_level=PromptRiskLevel.MEDIUM,
        policies=["base"],
        evaluation=None,
        approval_notes=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    find_one = AsyncMock(return_value=existing)
    monkeypatch.setattr(
        "app.services.gen_ai.agents.prompt_governance_service.PromptTemplate.find_one",
        find_one,
    )

    with pytest.raises(ValueError):
        await service.create_template(payload)
