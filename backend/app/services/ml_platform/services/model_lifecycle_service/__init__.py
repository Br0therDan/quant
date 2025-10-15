"""
Model Lifecycle Management Service
Delegates to specialized sub-modules for experiment, run, registry, approval, drift, and deployment management.
"""

from __future__ import annotations

from typing import Any

from app.models.ml_platform.model_lifecycle import (
    Deployment,
    DeploymentChecklistItem,
    DeploymentEnvironment,
    DeploymentStatus,
    DriftEvent,
    DriftSeverity,
    ExperimentStatus,
    ModelExperiment,
    ModelRun,
    ModelStage,
    ModelVersion,
    RunStatus,
)

from .approval import ApprovalManager, build_checklist
from .deployment import DeploymentManager
from .drift import DriftMonitor
from .experiment import ExperimentManager
from .registry import ModelRegistry
from .run import RunTracker

__all__ = [
    "ModelLifecycleService",
    "build_checklist",
]


class ModelLifecycleService:
    """
    Unified Model Lifecycle Service - delegates to specialized modules:
    - ExperimentManager: experiment creation & retrieval
    - RunTracker: run logging, MLflow sync
    - ModelRegistry: model version management, comparison
    - ApprovalManager: checklist & approval workflow
    - DriftMonitor: drift event tracking
    - DeploymentManager: deployment lifecycle (Phase 4)
    """

    def __init__(self, mlflow_tracking_uri: str | None = None) -> None:
        self.experiment_manager = ExperimentManager()
        self.run_tracker = RunTracker(tracking_uri=mlflow_tracking_uri)
        self.model_registry = ModelRegistry()
        self.approval_manager = ApprovalManager()
        self.drift_monitor = DriftMonitor()
        self.deployment_manager = DeploymentManager()

    # ========== Experiment Methods ==========

    async def create_experiment(self, payload: dict[str, Any]) -> ModelExperiment:
        """Create new experiment (delegates to ExperimentManager)"""
        return await self.experiment_manager.create_experiment(payload)

    async def update_experiment(
        self, name: str, updates: dict[str, Any]
    ) -> ModelExperiment | None:
        """Update experiment (delegates to ExperimentManager)"""
        return await self.experiment_manager.update_experiment(name, updates)

    async def list_experiments(
        self, owner: str | None = None, status: ExperimentStatus | None = None
    ) -> list[ModelExperiment]:
        """List experiments with filters (delegates to ExperimentManager)"""
        return await self.experiment_manager.list_experiments(
            owner=owner, status=status
        )

    async def get_experiment(self, name: str) -> ModelExperiment | None:
        """Get experiment by name (delegates to ExperimentManager)"""
        return await self.experiment_manager.get_experiment(name)

    # ========== Run Methods ==========

    async def log_run(self, payload: dict[str, Any]) -> ModelRun:
        """Log run and sync to MLflow (delegates to RunTracker)"""
        return await self.run_tracker.log_run(payload)

    async def update_run(self, run_id: str, payload: dict[str, Any]) -> ModelRun | None:
        """Update run (delegates to RunTracker)"""
        return await self.run_tracker.update_run(run_id, payload)

    async def list_runs(
        self,
        experiment_name: str | None = None,
        statuses: list[RunStatus] | None = None,
    ) -> list[ModelRun]:
        """List runs with filters (delegates to RunTracker)"""
        return await self.run_tracker.list_runs(
            experiment_name=experiment_name, statuses=statuses
        )

    async def get_run(self, run_id: str) -> ModelRun | None:
        """Get run by ID (delegates to RunTracker)"""
        return await self.run_tracker.get_run(run_id)

    # ========== Model Registry Methods ==========

    async def register_model_version(self, payload: dict[str, Any]) -> ModelVersion:
        """Register model version (delegates to ModelRegistry)"""
        return await self.model_registry.register_model_version(payload)

    async def update_model_version(
        self, model_name: str, version: str, payload: dict[str, Any]
    ) -> ModelVersion | None:
        """Update model version (delegates to ModelRegistry)"""
        return await self.model_registry.update_model_version(
            model_name, version, payload
        )

    async def compare_model_versions(
        self,
        model_name: str,
        versions: list[str],
    ) -> dict[str, dict[str, float]]:
        """Compare metrics across multiple versions (delegates to ModelRegistry)"""
        return await self.model_registry.compare_model_versions(
            model_name=model_name,
            versions=versions,
        )

    async def list_model_versions(
        self, model_name: str | None = None, stage: ModelStage | None = None
    ) -> list[ModelVersion]:
        """List model versions with filters (delegates to ModelRegistry)"""
        return await self.model_registry.list_model_versions(
            model_name=model_name, stage=stage
        )

    async def get_model_version(
        self, model_name: str, version: str
    ) -> ModelVersion | None:
        """Get model version (delegates to ModelRegistry)"""
        return await self.model_registry.get_model_version(model_name, version)

    async def set_stage(
        self, model_name: str, version: str, stage: ModelStage
    ) -> ModelVersion | None:
        """Set model version stage (delegates to ModelRegistry)"""
        return await self.model_registry.set_stage(model_name, version, stage)

    # ========== Approval Methods ==========

    async def append_checklist_item(
        self, model_name: str, version: str, item: DeploymentChecklistItem
    ) -> ModelVersion | None:
        """Append checklist item (delegates to ApprovalManager)"""
        return await self.approval_manager.append_checklist_item(
            model_name, version, item
        )

    async def mark_checklist_status(
        self,
        model_name: str,
        version: str,
        *,
        checklist: list[DeploymentChecklistItem] | None = None,
        approved_by: str | None = None,
        approval_notes: str | None = None,
    ) -> ModelVersion | None:
        """Update checklist and approval (delegates to ApprovalManager)"""
        return await self.approval_manager.mark_checklist_status(
            model_name=model_name,
            version=version,
            checklist=checklist,
            approved_by=approved_by,
            approval_notes=approval_notes,
        )

    # ========== Drift Methods ==========

    async def record_drift_event(self, payload: dict[str, Any]) -> DriftEvent:
        """Record drift event (delegates to DriftMonitor)"""
        return await self.drift_monitor.record_drift_event(payload)

    async def list_drift_events(
        self, model_name: str | None = None, severity: DriftSeverity | None = None
    ) -> list[DriftEvent]:
        """List drift events with filters (delegates to DriftMonitor)"""
        return await self.drift_monitor.list_drift_events(
            model_name=model_name, severity=severity
        )

    # ========== Deployment Methods (Phase 4 D4) ==========

    async def list_deployments(
        self,
        model_name: str | None = None,
        environment: DeploymentEnvironment | None = None,
        status: DeploymentStatus | None = None,
    ) -> list[Deployment]:
        """List deployments with filters (delegates to DeploymentManager)"""
        return await self.deployment_manager.list_deployments(
            model_name, environment, status
        )

    async def create_deployment(self, payload: dict[str, Any]) -> Deployment:
        """Create deployment (delegates to DeploymentManager)"""
        return await self.deployment_manager.create_deployment(payload)

    async def get_deployment(self, deployment_id: str) -> Deployment | None:
        """Get deployment by ID (delegates to DeploymentManager)"""
        return await self.deployment_manager.get_deployment(deployment_id)

    async def update_deployment(
        self, deployment_id: str, payload: dict[str, Any]
    ) -> Deployment | None:
        """Update deployment (delegates to DeploymentManager)"""
        return await self.deployment_manager.update_deployment(deployment_id, payload)
