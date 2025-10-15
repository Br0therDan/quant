"""
Deployment Approval and Checklist Management
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Iterable

from app.models.ml_platform.model_lifecycle import (
    ChecklistStatus,
    DeploymentChecklistItem,
    ModelVersion,
)

logger = logging.getLogger(__name__)


class ApprovalManager:
    """Deployment approval and checklist management handler"""

    def __init__(self) -> None:
        pass

    async def append_checklist_item(
        self,
        model_name: str,
        version: str,
        item: DeploymentChecklistItem,
    ) -> ModelVersion | None:
        """Append a checklist item to model version

        Args:
            model_name: Model name
            version: Version identifier
            item: Checklist item to append

        Returns:
            Updated ModelVersion if found, None otherwise
        """
        entry = await ModelVersion.find_one(
            (ModelVersion.model_name == model_name) & (ModelVersion.version == version)
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
        """Update checklist status and approval information

        Args:
            model_name: Model name
            version: Version identifier
            checklist: Optional new checklist (replaces existing)
            approved_by: Approver username
            approval_notes: Approval or rollback notes

        Returns:
            Updated ModelVersion if found, None otherwise
        """
        entry = await ModelVersion.find_one(
            (ModelVersion.model_name == model_name) & (ModelVersion.version == version)
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


def build_checklist(
    items: Iterable[str],
    *,
    default_status: str = "pending",
) -> list[DeploymentChecklistItem]:
    """Utility helper to bootstrap checklist items

    Args:
        items: Checklist item names
        default_status: Default status for all items (pending, approved, rejected)

    Returns:
        List of DeploymentChecklistItem with default status
    """
    status_value = default_status.lower()
    try:
        resolved = ChecklistStatus(status_value)
    except ValueError:
        resolved = ChecklistStatus.PENDING

    return [
        DeploymentChecklistItem(
            name=name, status=resolved, note=None, completed_at=None
        )
        for name in items
    ]
