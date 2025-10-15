"""
Model Deployment Management (Phase 4 D4)
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from app.models.ml_platform.model_lifecycle import (
    Deployment,
    DeploymentEnvironment,
    DeploymentStatus,
    ModelVersion,
)

logger = logging.getLogger(__name__)


class DeploymentManager:
    """Model deployment lifecycle management handler (Phase 4)"""

    def __init__(self) -> None:
        pass

    async def list_deployments(
        self,
        model_name: str | None = None,
        environment: DeploymentEnvironment | None = None,
        status: DeploymentStatus | None = None,
    ) -> list[Deployment]:
        """List deployments with optional filters

        Args:
            model_name: Filter by model name
            environment: Filter by deployment environment (DEV, STAGING, PRODUCTION)
            status: Filter by deployment status (PENDING, ACTIVE, FAILED, TERMINATED)

        Returns:
            List of deployments
        """
        query = {}
        if model_name:
            query["model_name"] = model_name
        if environment:
            query["environment"] = environment
        if status:
            query["status"] = status

        deployments = await Deployment.find(query).to_list()
        return deployments

    async def create_deployment(self, payload: dict[str, Any]) -> Deployment:
        """Create a new deployment

        Args:
            payload: Deployment data including model_name, model_version, environment, etc.

        Returns:
            Created Deployment

        Raises:
            ValueError: If model version does not exist
        """
        # Validate model exists
        model = await ModelVersion.find_one(
            ModelVersion.model_name == payload["model_name"],
            ModelVersion.version == payload["model_version"],
        )
        if not model:
            msg = f"Model {payload['model_name']}:{payload['model_version']} not found"
            raise ValueError(msg)

        deployment = Deployment(
            model_name=payload["model_name"],
            model_version=payload["model_version"],
            experiment_name=payload["experiment_name"],
            environment=payload["environment"],
            endpoint=payload["endpoint"],
            endpoint_config=payload.get("endpoint_config"),
            status=DeploymentStatus.PENDING,
            health_status="pending",
            created_by=payload["created_by"],
            deployed_at=datetime.now(UTC),
            deployment_notes=payload.get("deployment_notes"),
            terminated_at=None,
            rollback_from=None,
            error_message=None,
        )
        await deployment.insert()
        logger.info(
            "Deployment created: %s (%s) to %s",
            deployment.model_name,
            deployment.model_version,
            deployment.environment.value,
        )
        return deployment

    async def get_deployment(self, deployment_id: str) -> Deployment | None:
        """Get deployment by ID

        Args:
            deployment_id: Deployment identifier

        Returns:
            Deployment if found, None otherwise
        """
        return await Deployment.get(deployment_id)

    async def update_deployment(
        self, deployment_id: str, payload: dict[str, Any]
    ) -> Deployment | None:
        """Update deployment status and metrics

        Args:
            deployment_id: Deployment identifier
            payload: Fields to update (status, health_status, metrics, endpoint, etc.)

        Returns:
            Updated Deployment if found, None otherwise
        """
        deployment = await Deployment.get(deployment_id)
        if not deployment:
            return None

        if "status" in payload:
            deployment.status = payload["status"]
        if "health_status" in payload:
            deployment.health_status = payload["health_status"]
        if "metrics" in payload:
            deployment.metrics = payload["metrics"]
        if "endpoint" in payload:
            deployment.endpoint = payload["endpoint"]
        if "error_message" in payload:
            deployment.error_message = payload["error_message"]

        if payload.get("status") == DeploymentStatus.TERMINATED:
            deployment.terminated_at = datetime.now(UTC)

        await deployment.save()
        logger.info("Deployment %s updated: %s", deployment_id, deployment.status.value)
        return deployment
