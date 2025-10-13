"""Evaluation harness API routes (Phase 4 D3)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.schemas.evaluation_harness import (
    EvaluationReport,
    EvaluationRequest,
    EvaluationRunResponse,
    ScenarioCreate,
    ScenarioResponse,
    ScenarioUpdate,
)
from app.services.evaluation_harness_service import EvaluationHarnessService
from app.services.service_factory import service_factory

router = APIRouter(prefix="/evaluation", tags=["Evaluation Harness"])


def get_service() -> EvaluationHarnessService:
    return service_factory.get_evaluation_harness_service()


@router.post("/scenarios", response_model=ScenarioResponse, status_code=status.HTTP_201_CREATED)
async def register_scenario(
    payload: ScenarioCreate,
    service: Annotated[EvaluationHarnessService, Depends(get_service)],
) -> ScenarioResponse:
    try:
        scenario = await service.register_scenario(payload.model_dump())
    except ValueError as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ScenarioResponse.model_validate(scenario)


@router.patch("/scenarios/{name}", response_model=ScenarioResponse)
async def update_scenario(
    name: str,
    payload: ScenarioUpdate,
    service: Annotated[EvaluationHarnessService, Depends(get_service)],
) -> ScenarioResponse:
    scenario = await service.update_scenario(name, payload.model_dump(exclude_none=True))
    if scenario is None:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return ScenarioResponse.model_validate(scenario)


@router.get("/scenarios", response_model=list[ScenarioResponse])
async def list_scenarios(
    service: Annotated[EvaluationHarnessService, Depends(get_service)] = Depends(),
) -> list[ScenarioResponse]:
    scenarios = await service.list_scenarios()
    return [ScenarioResponse.model_validate(item) for item in scenarios]


@router.post("/runs", response_model=EvaluationRunResponse, status_code=status.HTTP_201_CREATED)
async def run_evaluation(
    payload: EvaluationRequest,
    service: Annotated[EvaluationHarnessService, Depends(get_service)],
) -> EvaluationRunResponse:
    try:
        run = await service.run_evaluation(payload.model_dump())
    except ValueError as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return EvaluationRunResponse.model_validate(run)


@router.get("/runs", response_model=list[EvaluationRunResponse])
async def list_evaluation_runs(
    scenario_name: str | None = Query(default=None),
    service: Annotated[EvaluationHarnessService, Depends(get_service)] = Depends(),
) -> list[EvaluationRunResponse]:
    runs = await service.list_runs(scenario_name=scenario_name)
    return [EvaluationRunResponse.model_validate(run) for run in runs]


@router.get("/runs/{run_id}/report", response_model=EvaluationReport)
async def get_evaluation_report(
    run_id: str,
    service: Annotated[EvaluationHarnessService, Depends(get_service)],
) -> EvaluationReport:
    report = await service.get_report(run_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Evaluation run not found")
    return EvaluationReport(**report)
