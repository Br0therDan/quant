"""
Model Run Tracking with MLflow Integration
"""

from __future__ import annotations

import logging
import os
from datetime import UTC, datetime
from typing import Any, Iterable

from beanie import SortDirection
from beanie.operators import In

from app.models.ml_platform.model_lifecycle import (
    ModelExperiment,
    ModelRun,
    RunStatus,
)

logger = logging.getLogger(__name__)


class RunTracker:
    """Model run tracking and MLflow synchronization handler"""

    def __init__(self, tracking_uri: str | None = None) -> None:
        """Initialize RunTracker with optional MLflow integration

        Args:
            tracking_uri: MLflow tracking server URI (defaults to MLFLOW_TRACKING_URI env var)
        """
        self._tracking_uri = tracking_uri or os.getenv("MLFLOW_TRACKING_URI")
        self._mlflow_available = self._check_mlflow_availability()

    def _check_mlflow_availability(self) -> bool:
        """Check if MLflow is available and configure tracking URI

        Returns:
            True if MLflow is available, False otherwise
        """
        try:  # pragma: no cover - optional dependency
            import mlflow

            if self._tracking_uri:
                mlflow.set_tracking_uri(self._tracking_uri)
            logger.info(
                "MLflow available at %s", self._tracking_uri or "default location"
            )
            return True
        except Exception:  # noqa: BLE001
            logger.info("MLflow not available - falling back to document-only tracking")
            return False

    async def log_run(self, payload: dict[str, Any]) -> ModelRun:
        """Log a new model run with automatic MLflow sync

        Args:
            payload: Run data including experiment_name, run_id, parameters, metrics, etc.

        Returns:
            Created ModelRun

        Raises:
            ValueError: If experiment does not exist
        """
        experiment = await ModelExperiment.find_one(
            ModelExperiment.name == payload["experiment_name"]
        )
        if experiment is None:
            raise ValueError(
                f"Experiment '{payload['experiment_name']}' does not exist"
            )

        run = ModelRun(**payload)
        await run.insert()
        logger.info("Logged run %s for experiment %s", run.run_id, run.experiment_name)

        await self._sync_run_to_mlflow(run)
        return run

    async def update_run(self, run_id: str, payload: dict[str, Any]) -> ModelRun | None:
        """Update run status, metrics, or other fields

        Args:
            run_id: Run identifier
            payload: Fields to update

        Returns:
            Updated ModelRun if found, None otherwise
        """
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
        """List runs with optional filters

        Args:
            experiment_name: Filter by experiment name
            statuses: Filter by run statuses

        Returns:
            List of runs sorted by start time (descending)
        """
        filters = []
        if experiment_name:
            filters.append(ModelRun.experiment_name == experiment_name)
        if statuses:
            filters.append(In(ModelRun.status, list(statuses)))

        if filters:
            cursor = ModelRun.find(*filters)
        else:
            cursor = ModelRun.find_all()

        runs = await cursor.sort(("started_at", SortDirection.DESCENDING)).to_list()
        return runs

    async def get_run(self, run_id: str) -> ModelRun | None:
        """Get run by ID

        Args:
            run_id: Run identifier

        Returns:
            ModelRun if found, None otherwise
        """
        return await ModelRun.find_one(ModelRun.run_id == run_id)

    async def _sync_run_to_mlflow(
        self, run: ModelRun, update_only: bool = False
    ) -> None:
        """Synchronize run data to MLflow tracking server

        Args:
            run: ModelRun to synchronize
            update_only: If True, only update existing run (don't create new)

        Note:
            Silently fails if MLflow is not available
        """
        if not self._mlflow_available:
            return

        try:  # pragma: no cover - optional integration
            import mlflow

            with mlflow.start_run(run_id=run.run_id, experiment_id=None) as active_run:
                if active_run is None:
                    return

                # Log parameters
                for param in run.parameters:
                    mlflow.log_param(param.name, param.value)

                # Log metrics
                for metric in run.metrics:
                    mlflow.log_metric(metric.metric_name, metric.value)

                # Log artifacts as tags (actual artifact upload handled separately)
                for artifact in run.artifacts:
                    mlflow.set_tag(f"artifact:{artifact.name}", artifact.uri)

                # Log dataset information
                mlflow.set_tag("dataset_name", run.dataset_name or "unknown")
                mlflow.set_tag("dataset_version", run.dataset_version or "unknown")

                # Log run status
                mlflow.set_tag("status", run.status.value)

                # Log completion time if updated
                if update_only and run.completed_at:
                    mlflow.set_tag(
                        "completed_at", run.completed_at.isoformat(timespec="seconds")
                    )

        except Exception as exc:  # noqa: BLE001
            logger.debug("Failed to sync run %s to MLflow: %s", run.run_id, exc)
