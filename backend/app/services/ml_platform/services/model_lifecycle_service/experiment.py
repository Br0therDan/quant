"""
Model Experiment Management
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from beanie import SortDirection

from app.models.ml_platform.model_lifecycle import (
    ExperimentStatus,
    ModelExperiment,
)

logger = logging.getLogger(__name__)


class ExperimentManager:
    """Model experiment CRUD operations handler"""

    def __init__(self) -> None:
        pass

    async def create_experiment(self, payload: dict[str, Any]) -> ModelExperiment:
        """Create a new experiment

        Args:
            payload: Experiment data including name, description, owner, etc.

        Returns:
            Created ModelExperiment

        Raises:
            ValueError: If experiment with same name already exists
        """
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
        """Update experiment fields

        Args:
            name: Experiment name
            updates: Fields to update

        Returns:
            Updated ModelExperiment if found, None otherwise
        """
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
        """List experiments with optional filters

        Args:
            owner: Filter by owner username
            status: Filter by experiment status

        Returns:
            List of experiments sorted by creation date (descending)
        """
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
            ("created_at", SortDirection.DESCENDING)
        ).to_list()
        return experiments

    async def get_experiment(self, name: str) -> ModelExperiment | None:
        """Get experiment by name

        Args:
            name: Experiment name

        Returns:
            ModelExperiment if found, None otherwise
        """
        experiment = await ModelExperiment.find_one(ModelExperiment.name == name)
        return experiment
