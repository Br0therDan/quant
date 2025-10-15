"""
Model Drift Monitoring
"""

from __future__ import annotations

import logging
from typing import Any

from beanie import SortDirection

from app.models.ml_platform.model_lifecycle import (
    DriftEvent,
    DriftSeverity,
)

logger = logging.getLogger(__name__)


class DriftMonitor:
    """Model drift detection and monitoring handler"""

    def __init__(self) -> None:
        pass

    async def record_drift_event(self, payload: dict[str, Any]) -> DriftEvent:
        """Record a drift detection event with warning log

        Args:
            payload: Drift event data including model_name, version, metric_name, etc.

        Returns:
            Created DriftEvent
        """
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
        """List drift events with optional filters

        Args:
            model_name: Filter by model name
            severity: Filter by drift severity (LOW, MEDIUM, HIGH, CRITICAL)

        Returns:
            List of drift events sorted by detection time (descending)
        """
        filters = []
        if model_name:
            filters.append(DriftEvent.model_name == model_name)
        if severity:
            filters.append(DriftEvent.severity == severity)

        if filters:
            cursor = DriftEvent.find(*filters)
        else:
            cursor = DriftEvent.find_all()

        return await cursor.sort(("detected_at", SortDirection.DESCENDING)).to_list()
