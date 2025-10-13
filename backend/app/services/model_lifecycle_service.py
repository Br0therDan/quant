"""Model lifecycle management service (Phase 4 D2)."""

from __future__ import annotations

import logging
import os
from datetime import UTC, datetime
from typing import Any, Iterable

from beanie import SortDirection
from beanie.operators import In

from app.models.model_lifecycle import (
    ChecklistStatus,
    DeploymentChecklistItem,
    DriftEvent,
    DriftSeverity,
    ExperimentStatus,
    ModelExperiment,
    ModelRun,
    ModelStage,
    ModelVersion,
    RunStatus,
)

logger = logging.getLogger(__name__)


class ModelLifecycleService:
    """Service orchestrating experiments, runs, and registry lifecycle."""

    def __init__(self, tracking_uri: str | None = None) -> None:
        self._tracking_uri = tracking_uri or os.getenv("MLFLOW_TRACKING_URI")
        self._mlflow_available = False
        try:  # pragma: no cover - optional dependency
            import mlflow

            self._mlflow_available = True
            if self._tracking_uri:
                mlflow.set_tracking_uri(self._tracking_uri)
        except Exception:  # noqa: BLE001
            logger.info("MLflow not available - falling back to document-only tracking")

    # ------------------------------------------------------------------
    # Experiments
    # ------------------------------------------------------------------
    async def create_experiment(self, payload: dict[str, Any]) -> ModelExperiment:
        existing = await ModelExperiment.find_one(
            ModelExperiment.name == payload["name"]
        )
        if existing:
            raise ValueError(f"Experiment '{payload['name']}' already exists")

        experiment = ModelExperiment(**payload)
        await experiment.insert()
        logger.info("Created experiment %s", experiment.name)
        return experiment

    async def update_experiment(
        self, name: str, updates: dict[str, Any]
    ) -> ModelExperiment | None:
        experiment = await ModelExperiment.find_one(ModelExperiment.name == name)
        if experiment is None:
            return None

        for field, value in updates.items():
            setattr(experiment, field, value)
        experiment.updated_at = datetime.now(UTC)
        await experiment.save()
        logger.info("Updated experiment %s", name)
        return experiment

    async def list_experiments(
        self,
        *,
        owner: str | None = None,
        status: ExperimentStatus | None = None,
    ) -> list[ModelExperiment]:
        query_filters = []
        if owner:
            query_filters.append(ModelExperiment.owner == owner)
        if status:
            query_filters.append(ModelExperiment.status == status)

        if query_filters:
            cursor = ModelExperiment.find(*query_filters)
        else:
            cursor = ModelExperiment.find_all()

        experiments = await cursor.sort(
            (ModelExperiment.created_at, SortDirection.DESCENDING)
        ).to_list()
        return experiments

    # ------------------------------------------------------------------
    # Runs
    # ------------------------------------------------------------------
    async def log_run(self, payload: dict[str, Any]) -> ModelRun:
        experiment = await ModelExperiment.find_one(
            ModelExperiment.name == payload["experiment_name"]
        )
        if experiment is None:
            raise ValueError(
                f"Experiment '{payload['experiment_name']}' does not exist"
            )

        run = ModelRun(**payload)
        await run.insert()
        logger.info(
            "Logged run %s for experiment %s", run.run_id, run.experiment_name
        )

        await self._sync_run_to_mlflow(run)
        return run

    async def update_run(self, run_id: str, payload: dict[str, Any]) -> ModelRun | None:
        run = await ModelRun.find_one(ModelRun.run_id == run_id)
        if run is None:
            return None

        for field, value in payload.items():
            setattr(run, field, value)
        if payload.get("status") in {RunStatus.COMPLETED, RunStatus.FAILED}:
            run.completed_at = run.completed_at or datetime.now(UTC)
        await run.save()
        logger.info("Updated run %s", run_id)

        await self._sync_run_to_mlflow(run, update_only=True)
        return run

    async def list_runs(
        self,
        *,
        experiment_name: str | None = None,
        statuses: Iterable[RunStatus] | None = None,
    ) -> list[ModelRun]:
        filters = []
        if experiment_name:
            filters.append(ModelRun.experiment_name == experiment_name)
        if statuses:
            filters.append(In(ModelRun.status, list(statuses)))

        if filters:
            cursor = ModelRun.find(*filters)
        else:
            cursor = ModelRun.find_all()

        runs = await cursor.sort(
            (ModelRun.started_at, SortDirection.DESCENDING)
        ).to_list()
        return runs

    async def get_run(self, run_id: str) -> ModelRun | None:
        return await ModelRun.find_one(ModelRun.run_id == run_id)

    # ------------------------------------------------------------------
    # Model registry
    # ------------------------------------------------------------------
    async def register_model_version(
        self, payload: dict[str, Any]
    ) -> ModelVersion:
        existing = await ModelVersion.find_one(
            (ModelVersion.model_name == payload["model_name"]) &
            (ModelVersion.version == payload["version"])
        )
        if existing:
            raise ValueError(
                f"Model {payload['model_name']} version {payload['version']} already exists"
            )

        version = ModelVersion(**payload)
        await version.insert()
        logger.info(
            "Registered model %s version %s",
            version.model_name,
            version.version,
        )
        return version

    async def update_model_version(
        self, model_name: str, version: str, payload: dict[str, Any]
    ) -> ModelVersion | None:
        registry_entry = await ModelVersion.find_one(
            (ModelVersion.model_name == model_name)
            & (ModelVersion.version == version)
        )
        if registry_entry is None:
            return None

        for field, value in payload.items():
            setattr(registry_entry, field, value)
        registry_entry.updated_at = datetime.now(UTC)
        await registry_entry.save()
        logger.info("Updated model %s version %s", model_name, version)
        return registry_entry

    async def compare_model_versions(
        self, model_name: str, versions: list[str]
    ) -> dict[str, float | dict[str, float]]:
        entries = await ModelVersion.find(
            (ModelVersion.model_name == model_name)
            & In(ModelVersion.version, versions)
        ).to_list()
        metrics: dict[str, dict[str, float]] = {}
        for entry in entries:
            for snapshot in entry.metrics:
                metrics.setdefault(snapshot.metric_name, {})[entry.version] = (
                    snapshot.value
                )
        return metrics

    async def list_model_versions(
        self,
        *,
        model_name: str | None = None,
        stage: ModelStage | None = None,
    ) -> list[ModelVersion]:
        filters = []
        if model_name:
            filters.append(ModelVersion.model_name == model_name)
        if stage:
            filters.append(ModelVersion.stage == stage)

        if filters:
            cursor = ModelVersion.find(*filters)
        else:
            cursor = ModelVersion.find_all()

        versions = await cursor.sort(
            (ModelVersion.created_at, SortDirection.DESCENDING)
        ).to_list()
        return versions

    # ------------------------------------------------------------------
    # Drift monitoring
    # ------------------------------------------------------------------
    async def record_drift_event(self, payload: dict[str, Any]) -> DriftEvent:
        event = DriftEvent(**payload)
        await event.insert()
        logger.warning(
            "Drift detected for %s v%s on %s (severity=%s)",
            event.model_name,
            event.version,
            event.metric_name,
            event.severity,
        )
        return event

    async def list_drift_events(
        self,
        *,
        model_name: str | None = None,
        severity: DriftSeverity | None = None,
    ) -> list[DriftEvent]:
        filters = []
        if model_name:
            filters.append(DriftEvent.model_name == model_name)
        if severity:
            filters.append(DriftEvent.severity == severity)

        if filters:
            cursor = DriftEvent.find(*filters)
        else:
            cursor = DriftEvent.find_all()

        return await cursor.sort(
            (DriftEvent.detected_at, SortDirection.DESCENDING)
        ).to_list()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    async def _sync_run_to_mlflow(
        self, run: ModelRun, update_only: bool = False
    ) -> None:
        if not self._mlflow_available:
            return
        try:  # pragma: no cover - optional integration
            import mlflow

            with mlflow.start_run(run_id=run.run_id, experiment_id=None) as active_run:
                if active_run is None:
                    return
                for param in run.parameters:
                    mlflow.log_param(param.name, param.value)
                for metric in run.metrics:
                    mlflow.log_metric(metric.metric_name, metric.value)
                for artifact in run.artifacts:
                    mlflow.set_tag(f"artifact:{artifact.name}", artifact.uri)
                mlflow.set_tag("dataset_name", run.dataset_name or "unknown")
                mlflow.set_tag("dataset_version", run.dataset_version or "unknown")
                mlflow.set_tag("status", run.status.value)
                if update_only and run.completed_at:
                    mlflow.set_tag(
                        "completed_at", run.completed_at.isoformat(timespec="seconds")
                    )
        except Exception as exc:  # noqa: BLE001
            logger.debug("Failed to sync run %s to MLflow: %s", run.run_id, exc)

    async def append_checklist_item(
        self,
        model_name: str,
        version: str,
        item: DeploymentChecklistItem,
    ) -> ModelVersion | None:
        entry = await ModelVersion.find_one(
            (ModelVersion.model_name == model_name)
            & (ModelVersion.version == version)
        )
        if entry is None:
            return None
        entry.approval_checklist.append(item)
        entry.updated_at = datetime.now(UTC)
        await entry.save()
        logger.info(
            "Appended checklist item '%s' to %s v%s",
            item.name,
            model_name,
            version,
        )
        return entry

    async def mark_checklist_status(
        self,
        model_name: str,
        version: str,
        *,
        checklist: list[DeploymentChecklistItem] | None = None,
        approved_by: str | None = None,
        approval_notes: str | None = None,
    ) -> ModelVersion | None:
        entry = await ModelVersion.find_one(
            (ModelVersion.model_name == model_name)
            & (ModelVersion.version == version)
        )
        if entry is None:
            return None

        if checklist is not None:
            entry.approval_checklist = checklist
        if approved_by:
            entry.approved_by = approved_by
            entry.approved_at = datetime.now(UTC)
        if approval_notes:
            entry.rollback_notes = approval_notes
        entry.updated_at = datetime.now(UTC)
        await entry.save()
        logger.info("Updated checklist for %s v%s", model_name, version)
        return entry

    async def set_stage(
        self, model_name: str, version: str, stage: ModelStage
    ) -> ModelVersion | None:
        entry = await ModelVersion.find_one(
            (ModelVersion.model_name == model_name)
            & (ModelVersion.version == version)
        )
        if entry is None:
            return None
        entry.stage = stage
        entry.updated_at = datetime.now(UTC)
        await entry.save()
        logger.info("Model %s moved to stage %s", model_name, stage)
        return entry


def build_checklist(
    items: Iterable[str],
    *,
    default_status: str = "pending",
) -> list[DeploymentChecklistItem]:
    """Utility helper to bootstrap checklist items."""

    status_value = default_status.lower()
    try:
        resolved = ChecklistStatus(status_value)
    except ValueError:
        resolved = ChecklistStatus.PENDING

    return [
        DeploymentChecklistItem(name=name, status=resolved)
        for name in items
    ]
