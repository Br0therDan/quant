"""API tests for prompt governance endpoints."""

from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.schemas.enums import PromptRiskLevel, PromptStatus
from app.schemas.gen_ai.prompt_governance import PromptEvaluationSummary


@pytest.fixture
def prompt_service_stub(monkeypatch: pytest.MonkeyPatch) -> SimpleNamespace:
    service = SimpleNamespace(
        create_template=AsyncMock(),
        update_template=AsyncMock(),
        list_templates=AsyncMock(return_value=[]),
        submit_for_review=AsyncMock(),
        approve_template=AsyncMock(),
        reject_template=AsyncMock(),
        evaluate_prompt=lambda content, evaluator=None: PromptEvaluationSummary(
            toxicity_score=0.1,
            hallucination_score=0.0,
            factual_consistency=1.0,
            risk_level=PromptRiskLevel.LOW,
            evaluator=evaluator or "automated",
            evaluated_at=datetime.now(UTC),
        ),
        log_usage=AsyncMock(),
        list_audit_logs=AsyncMock(return_value=[]),
    )

    monkeypatch.setattr(
        "app.api.routes.gen_ai.prompt_governance.service_factory.get_prompt_governance_service",
        lambda: service,
    )
    return service


def _template_response() -> SimpleNamespace:
    now = datetime.now(UTC)
    return SimpleNamespace(
        prompt_id="risk-check",
        version="v1",
        name="Risk Check",
        description="Ensure compliance",
        content="Always evaluate risk.",
        owner="alice",
        tags=["compliance"],
        status=PromptStatus.APPROVED,
        risk_level=PromptRiskLevel.LOW,
        policies=["base"],
        evaluation=PromptEvaluationSummary(
            toxicity_score=0.1,
            hallucination_score=0.0,
            factual_consistency=0.9,
            risk_level=PromptRiskLevel.LOW,
            evaluator="qa",
            evaluated_at=now,
        ),
        approval_notes="Looks good",
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
async def test_create_template_success(async_client, auth_headers, prompt_service_stub) -> None:
    prompt_service_stub.create_template.return_value = _template_response()

    response = await async_client.post(
        "/api/v1/gen-ai/prompt-governance/prompts/templates",
        headers=auth_headers,
        json={
            "prompt_id": "risk-check",
            "version": "v1",
            "name": "Risk Check",
            "description": "Ensure compliance",
            "content": "Always evaluate risk.",
            "owner": "alice",
            "tags": ["compliance"],
            "risk_level": "medium",
            "policies": ["base"],
        },
    )

    assert response.status_code == 201
    prompt_service_stub.create_template.assert_awaited_once()
    payload = response.json()
    assert payload["prompt_id"] == "risk-check"


@pytest.mark.asyncio
async def test_create_template_duplicate(async_client, auth_headers, prompt_service_stub) -> None:
    prompt_service_stub.create_template.side_effect = ValueError("duplicate")

    response = await async_client.post(
        "/api/v1/gen-ai/prompt-governance/prompts/templates",
        headers=auth_headers,
        json={
            "prompt_id": "risk-check",
            "version": "v1",
            "name": "Risk Check",
            "description": "Ensure compliance",
            "content": "Always evaluate risk.",
            "owner": "alice",
            "tags": ["compliance"],
            "risk_level": "medium",
            "policies": ["base"],
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "duplicate"


@pytest.mark.asyncio
async def test_list_templates_invalid_status(async_client, auth_headers, prompt_service_stub) -> None:
    response = await async_client.get(
        "/api/v1/gen-ai/prompt-governance/prompts/templates",
        headers=auth_headers,
        params={"status": "invalid"},
    )

    assert response.status_code == 400
    assert "Invalid status" in response.json()["detail"]


@pytest.mark.asyncio
async def test_evaluate_prompt_returns_summary(async_client, auth_headers, prompt_service_stub) -> None:
    response = await async_client.post(
        "/api/v1/gen-ai/prompt-governance/prompts/evaluate",
        headers=auth_headers,
        json={
            "prompt_id": "risk-check",
            "version": "v1",
            "content": "Always check risk",
            "evaluator": "qa",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["evaluation"]["risk_level"] == "low"


@pytest.mark.asyncio
async def test_log_usage_mismatch(async_client, auth_headers, prompt_service_stub) -> None:
    response = await async_client.post(
        "/api/v1/gen-ai/prompt-governance/prompts/templates/risk-check/v1/usage",
        headers=auth_headers,
        json={
            "prompt_id": "other",
            "version": "v1",
            "session_id": "sess-1",
            "outcome": "success",
        },
    )

    assert response.status_code == 400
    assert "mismatch" in response.json()["detail"]
