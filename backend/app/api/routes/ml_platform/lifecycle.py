"""Model lifecycle API routes (Phase 4 D2)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.schemas.ml_platform.model_lifecycle import (
    ChecklistUpdateRequest,
    DeploymentCreate,
    DeploymentResponse,
    DeploymentUpdate,
    DriftEventCreate,
    DriftEventResponse,
    ExperimentCreate,
    ExperimentResponse,
    ExperimentUpdate,
    MetricComparison,
    ModelComparisonRequest,
    ModelComparisonResponse,
    ModelVersionCreate,
    ModelVersionResponse,
    RunCreate,
    RunResponse,
    RunUpdate,
)
from app.services.ml_platform.services.model_lifecycle_service import (
    ModelLifecycleService,
)
from app.services.service_factory import service_factory

router = APIRouter(prefix="/lifecycle", tags=["Model Lifecycle"])


def get_service() -> ModelLifecycleService:
    return service_factory.get_model_lifecycle_service()


@router.post(
    "/experiments",
    response_model=ExperimentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_experiment(
    payload: ExperimentCreate,
    service: Annotated[ModelLifecycleService, Depends(get_service)],
) -> ExperimentResponse:
    experiment = await service.create_experiment(payload.model_dump())
    return ExperimentResponse.model_validate(experiment)


@router.get("/experiments", response_model=list[ExperimentResponse])
async def list_experiments(
    service: Annotated[ModelLifecycleService, Depends(get_service)],
    owner: str | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
) -> list[ExperimentResponse]:
    status_enum = None
    if status_filter:
        from app.schemas.enums import ExperimentStatus

        try:
            status_enum = ExperimentStatus(status_filter)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status filter")
    experiments = await service.list_experiments(owner=owner, status=status_enum)
    return [ExperimentResponse.model_validate(exp) for exp in experiments]


@router.get("/experiments/{name}", response_model=ExperimentResponse)
async def get_experiment(
    name: str,
    service: Annotated[ModelLifecycleService, Depends(get_service)],
) -> ExperimentResponse:
    """Get experiment by name."""
    experiment = await service.get_experiment(name)
    if experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return ExperimentResponse.model_validate(experiment)


@router.patch("/experiments/{name}", response_model=ExperimentResponse)
async def update_experiment(
    name: str,
    payload: ExperimentUpdate,
    service: Annotated[ModelLifecycleService, Depends(get_service)],
) -> ExperimentResponse:
    experiment = await service.update_experiment(
        name, payload.model_dump(exclude_none=True)
    )
    if experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return ExperimentResponse.model_validate(experiment)


@router.post("/runs", response_model=RunResponse, status_code=status.HTTP_201_CREATED)
async def log_run(
    payload: RunCreate,
    service: Annotated[ModelLifecycleService, Depends(get_service)],
) -> RunResponse:
    try:
        run = await service.log_run(payload.model_dump())
    except ValueError as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return RunResponse.model_validate(run)


@router.patch("/runs/{run_id}", response_model=RunResponse)
async def update_run(
    run_id: str,
    payload: RunUpdate,
    service: Annotated[ModelLifecycleService, Depends(get_service)],
) -> RunResponse:
    run = await service.update_run(run_id, payload.model_dump(exclude_none=True))
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return RunResponse.model_validate(run)


@router.get("/runs", response_model=list[RunResponse])
async def list_runs(
    service: Annotated[ModelLifecycleService, Depends(get_service)],
    experiment_name: str | None = Query(default=None),
    statuses: list[str] | None = Query(default=None),
) -> list[RunResponse]:
    status_enums = None
    if statuses:
        from app.schemas.enums import RunStatus

        try:
            status_enums = [RunStatus(status) for status in statuses]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status value")
    runs = await service.list_runs(
        experiment_name=experiment_name,
        statuses=status_enums,
    )
    return [RunResponse.model_validate(run) for run in runs]


@router.get("/runs/{run_id}", response_model=RunResponse)
async def get_run(
    run_id: str,
    service: Annotated[ModelLifecycleService, Depends(get_service)],
) -> RunResponse:
    run = await service.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return RunResponse.model_validate(run)


@router.post(
    "/models",
    response_model=ModelVersionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_model_version(
    payload: ModelVersionCreate,
    service: Annotated[ModelLifecycleService, Depends(get_service)],
) -> ModelVersionResponse:
    try:
        version = await service.register_model_version(payload.model_dump())
    except ValueError as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ModelVersionResponse.model_validate(version)


@router.patch(
    "/models/{model_name}/{version}",
    response_model=ModelVersionResponse,
)
async def update_model_version(
    model_name: str,
    version: str,
    payload: ChecklistUpdateRequest,
    service: Annotated[ModelLifecycleService, Depends(get_service)],
) -> ModelVersionResponse:
    updates = payload.model_dump(exclude_none=True)
    if "checklist" in updates:
        updates["approval_checklist"] = updates.pop("checklist")
    if payload.stage is not None:
        updates["stage"] = payload.stage
    version_doc = await service.update_model_version(model_name, version, updates)
    if version_doc is None:
        raise HTTPException(status_code=404, detail="Model version not found")
    if payload.approved_by:
        version_doc = (
            await service.mark_checklist_status(
                model_name,
                version,
                checklist=updates.get(
                    "approval_checklist", version_doc.approval_checklist
                ),
                approved_by=payload.approved_by,
                approval_notes=payload.approval_notes,
            )
            or version_doc
        )
    return ModelVersionResponse.model_validate(version_doc)


@router.get("/models", response_model=list[ModelVersionResponse])
async def list_model_versions(
    service: Annotated[ModelLifecycleService, Depends(get_service)],
    model_name: str | None = Query(default=None),
    stage: str | None = Query(default=None),
) -> list[ModelVersionResponse]:
    stage_enum = None
    if stage:
        from app.models.ml_platform.model_lifecycle import ModelStage

        try:
            stage_enum = ModelStage(stage)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid stage value")
    versions = await service.list_model_versions(
        model_name=model_name, stage=stage_enum
    )
    return [ModelVersionResponse.model_validate(item) for item in versions]


@router.get("/models/{model_name}/{version}", response_model=ModelVersionResponse)
async def get_model_version(
    model_name: str,
    version: str,
    service: Annotated[ModelLifecycleService, Depends(get_service)],
) -> ModelVersionResponse:
    """Get model version by name and version."""
    model = await service.get_model_version(model_name, version)
    if model is None:
        raise HTTPException(status_code=404, detail="Model version not found")
    return ModelVersionResponse.model_validate(model)


@router.post(
    "/models/{model_name}/compare",
    response_model=ModelComparisonResponse,
)
async def compare_model_versions(
    model_name: str,
    payload: ModelComparisonRequest,
    service: Annotated[ModelLifecycleService, Depends(get_service)],
) -> ModelComparisonResponse:
    metrics = await service.compare_model_versions(model_name, payload.versions)
    comparisons = [
        MetricComparison(metric_name=metric_name, values=values)
        for metric_name, values in metrics.items()
    ]
    return ModelComparisonResponse(model_name=model_name, comparisons=comparisons)


@router.post("/drift-events", response_model=DriftEventResponse)
async def record_drift_event(
    payload: DriftEventCreate,
    service: Annotated[ModelLifecycleService, Depends(get_service)],
) -> DriftEventResponse:
    event = await service.record_drift_event(payload.model_dump())
    return DriftEventResponse.model_validate(event)


@router.get("/drift-events", response_model=list[DriftEventResponse])
async def list_drift_events(
    service: Annotated[ModelLifecycleService, Depends(get_service)],
    model_name: str | None = Query(default=None),
    severity: str | None = Query(default=None),
) -> list[DriftEventResponse]:
    severity_enum = None
    if severity:
        from app.models.ml_platform.model_lifecycle import DriftSeverity

        try:
            severity_enum = DriftSeverity(severity)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid severity value")
    events = await service.list_drift_events(
        model_name=model_name, severity=severity_enum
    )
    return [DriftEventResponse.model_validate(event) for event in events]


# ==============================================================================
# Deployment Endpoints (Phase 4 D4)
# ==============================================================================


@router.post(
    "/deployments",
    response_model=DeploymentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_deployment(
    payload: DeploymentCreate,
    service: Annotated[ModelLifecycleService, Depends(get_service)],
) -> DeploymentResponse:
    """Create a new deployment."""
    try:
        deployment = await service.create_deployment(payload.model_dump())
        return DeploymentResponse.model_validate(deployment)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/deployments", response_model=list[DeploymentResponse])
async def list_deployments(
    service: Annotated[ModelLifecycleService, Depends(get_service)],
    model_name: str | None = Query(default=None),
    environment: str | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
) -> list[DeploymentResponse]:
    """List deployments with optional filters."""
    from app.schemas.enums import DeploymentEnvironment, DeploymentStatus

    env_enum = None
    if environment:
        try:
            env_enum = DeploymentEnvironment(environment)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid environment value")

    status_enum = None
    if status_filter:
        try:
            status_enum = DeploymentStatus(status_filter)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status value")

    deployments = await service.list_deployments(
        model_name=model_name, environment=env_enum, status=status_enum
    )
    return [DeploymentResponse.model_validate(d) for d in deployments]


@router.get("/deployments/{deployment_id}", response_model=DeploymentResponse)
async def get_deployment(
    deployment_id: str,
    service: Annotated[ModelLifecycleService, Depends(get_service)],
) -> DeploymentResponse:
    """Get deployment details."""
    deployment = await service.get_deployment(deployment_id)
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return DeploymentResponse.model_validate(deployment)


@router.patch("/deployments/{deployment_id}", response_model=DeploymentResponse)
async def update_deployment(
    deployment_id: str,
    payload: DeploymentUpdate,
    service: Annotated[ModelLifecycleService, Depends(get_service)],
) -> DeploymentResponse:
    """Update deployment status and metrics."""
    deployment = await service.update_deployment(
        deployment_id, payload.model_dump(exclude_unset=True)
    )
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return DeploymentResponse.model_validate(deployment)
