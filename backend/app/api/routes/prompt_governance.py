"""Prompt governance API routes (Phase 4 D4)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.schemas.prompt_governance import (
    PromptAuditLogResponse,
    PromptEvaluationRequest,
    PromptEvaluationResponse,
    PromptTemplateCreate,
    PromptTemplateResponse,
    PromptTemplateUpdate,
    PromptUsageLogCreate,
    PromptUsageLogResponse,
    PromptWorkflowAction,
)
from app.services.llm.prompt_governance_service import PromptGovernanceService
from app.services.service_factory import service_factory

router = APIRouter(prefix="/prompts", tags=["Prompt Governance"])


def get_service() -> PromptGovernanceService:
    return service_factory.get_prompt_governance_service()


@router.post("/templates", response_model=PromptTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_prompt_template(
    payload: PromptTemplateCreate,
    service: Annotated[PromptGovernanceService, Depends(get_service)],
) -> PromptTemplateResponse:
    try:
        template = await service.create_template(payload.model_dump())
    except ValueError as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return PromptTemplateResponse.model_validate(template)


@router.patch("/templates/{prompt_id}/{version}", response_model=PromptTemplateResponse)
async def update_prompt_template(
    prompt_id: str,
    version: str,
    payload: PromptTemplateUpdate,
    service: Annotated[PromptGovernanceService, Depends(get_service)],
) -> PromptTemplateResponse:
    template = await service.update_template(
        prompt_id,
        version,
        payload.model_dump(exclude_none=True),
    )
    if template is None:
        raise HTTPException(status_code=404, detail="Prompt template not found")
    return PromptTemplateResponse.model_validate(template)


@router.get("/templates", response_model=list[PromptTemplateResponse])
async def list_prompt_templates(
    status_filter: str | None = Query(default=None, alias="status"),
    tag: str | None = Query(default=None),
    service: Annotated[PromptGovernanceService, Depends(get_service)] = Depends(),
) -> list[PromptTemplateResponse]:
    status_enum = None
    if status_filter:
        from app.models.prompt_governance import PromptStatus

        try:
            status_enum = PromptStatus(status_filter)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status filter")
    templates = await service.list_templates(status=status_enum, tag=tag)
    return [PromptTemplateResponse.model_validate(item) for item in templates]


@router.post("/templates/{prompt_id}/{version}/submit", response_model=PromptTemplateResponse)
async def submit_prompt_for_review(
    prompt_id: str,
    version: str,
    action: PromptWorkflowAction,
    service: Annotated[PromptGovernanceService, Depends(get_service)],
) -> PromptTemplateResponse:
    template = await service.submit_for_review(prompt_id, version, reviewer=action.reviewer)
    if template is None:
        raise HTTPException(status_code=404, detail="Prompt template not found")
    return PromptTemplateResponse.model_validate(template)


@router.post("/templates/{prompt_id}/{version}/approve", response_model=PromptTemplateResponse)
async def approve_prompt(
    prompt_id: str,
    version: str,
    action: PromptWorkflowAction,
    service: Annotated[PromptGovernanceService, Depends(get_service)],
) -> PromptTemplateResponse:
    template = await service.approve_template(
        prompt_id,
        version,
        reviewer=action.reviewer,
        notes=action.notes,
    )
    if template is None:
        raise HTTPException(status_code=404, detail="Prompt template not found")
    return PromptTemplateResponse.model_validate(template)


@router.post("/templates/{prompt_id}/{version}/reject", response_model=PromptTemplateResponse)
async def reject_prompt(
    prompt_id: str,
    version: str,
    action: PromptWorkflowAction,
    service: Annotated[PromptGovernanceService, Depends(get_service)],
) -> PromptTemplateResponse:
    template = await service.reject_template(
        prompt_id,
        version,
        reviewer=action.reviewer,
        notes=action.notes,
    )
    if template is None:
        raise HTTPException(status_code=404, detail="Prompt template not found")
    return PromptTemplateResponse.model_validate(template)


@router.post("/evaluate", response_model=PromptEvaluationResponse)
async def evaluate_prompt(
    payload: PromptEvaluationRequest,
    service: Annotated[PromptGovernanceService, Depends(get_service)],
) -> PromptEvaluationResponse:
    evaluation = service.evaluate_prompt(payload.content, evaluator=payload.evaluator)
    return PromptEvaluationResponse(evaluation=evaluation)


@router.post("/templates/{prompt_id}/{version}/usage", response_model=PromptUsageLogResponse, status_code=status.HTTP_201_CREATED)
async def log_prompt_usage(
    prompt_id: str,
    version: str,
    payload: PromptUsageLogCreate,
    service: Annotated[PromptGovernanceService, Depends(get_service)],
) -> PromptUsageLogResponse:
    if payload.prompt_id != prompt_id or payload.version != version:
        raise HTTPException(status_code=400, detail="Payload prompt identifiers mismatch")
    log_entry = await service.log_usage(payload.model_dump())
    return PromptUsageLogResponse.model_validate(log_entry)


@router.get("/templates/{prompt_id}/{version}/audit", response_model=list[PromptAuditLogResponse])
async def list_prompt_audit_logs(
    prompt_id: str,
    version: str,
    service: Annotated[PromptGovernanceService, Depends(get_service)],
) -> list[PromptAuditLogResponse]:
    logs = await service.list_audit_logs(prompt_id, version)
    return [PromptAuditLogResponse.model_validate(log) for log in logs]
