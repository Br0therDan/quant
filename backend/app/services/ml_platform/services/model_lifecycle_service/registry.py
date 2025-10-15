"""
Model Registry and Version Management
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from beanie import SortDirection
from beanie.operators import In

from app.models.ml_platform.model_lifecycle import (
    ModelStage,
    ModelVersion,
)

logger = logging.getLogger(__name__)


class ModelRegistry:
    """Model version registry and comparison handler"""

    def __init__(self) -> None:
        pass

    async def register_model_version(self, payload: dict[str, Any]) -> ModelVersion:
        """Register a new model version

        Args:
            payload: Model version data including model_name, version, metrics, etc.

        Returns:
            Created ModelVersion

        Raises:
            ValueError: If model version already exists
        """
        existing = await ModelVersion.find_one(
            (ModelVersion.model_name == payload["model_name"])
            & (ModelVersion.version == payload["version"])
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
        """Update model version fields

        Args:
            model_name: Model name
            version: Version identifier
            payload: Fields to update

        Returns:
            Updated ModelVersion if found, None otherwise
        """
        registry_entry = await ModelVersion.find_one(
            (ModelVersion.model_name == model_name) & (ModelVersion.version == version)
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
    ) -> dict[str, dict[str, float]]:
        """Compare metrics across multiple model versions

        Args:
            model_name: Model name
            versions: List of version identifiers to compare

        Returns:
            Dictionary mapping metric names to version-value pairs
            Example: {"accuracy": {"v1": 0.95, "v2": 0.97}, "f1_score": {...}}
        """
        entries = await ModelVersion.find(
            ModelVersion.model_name == model_name, In(ModelVersion.version, versions)
        ).to_list()

        metrics: dict[str, dict[str, float]] = {}
        for entry in entries:
            for snapshot in entry.metrics:
                metrics.setdefault(snapshot.metric_name, {})[
                    entry.version
                ] = snapshot.value
        return metrics

    async def list_model_versions(
        self,
        *,
        model_name: str | None = None,
        stage: ModelStage | None = None,
    ) -> list[ModelVersion]:
        """List model versions with optional filters

        Args:
            model_name: Filter by model name
            stage: Filter by model stage (None, Staging, Production, Archived)

        Returns:
            List of model versions sorted by creation date (descending)
        """
        filters = []
        if model_name:
            filters.append(ModelVersion.model_name == model_name)
        if stage:
            filters.append(ModelVersion.stage == stage)

        if filters:
            cursor = ModelVersion.find(*filters)
        else:
            cursor = ModelVersion.find_all()

        versions = await cursor.sort(("created_at", SortDirection.DESCENDING)).to_list()
        return versions

    async def get_model_version(
        self, model_name: str, version: str
    ) -> ModelVersion | None:
        """Get model version by name and version

        Args:
            model_name: Model name
            version: Version identifier

        Returns:
            ModelVersion if found, None otherwise
        """
        model = await ModelVersion.find_one(
            ModelVersion.model_name == model_name,
            ModelVersion.version == version,
        )
        return model

    async def set_stage(
        self, model_name: str, version: str, stage: ModelStage
    ) -> ModelVersion | None:
        """Set model stage (e.g., move to Production)

        Args:
            model_name: Model name
            version: Version identifier
            stage: Target stage (None, Staging, Production, Archived)

        Returns:
            Updated ModelVersion if found, None otherwise
        """
        entry = await ModelVersion.find_one(
            (ModelVersion.model_name == model_name) & (ModelVersion.version == version)
        )
        if entry is None:
            return None

        entry.stage = stage
        entry.updated_at = datetime.now(UTC)
        await entry.save()
        logger.info("Model %s version %s moved to stage %s", model_name, version, stage)
        return entry
