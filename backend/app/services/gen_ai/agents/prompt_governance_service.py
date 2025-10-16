"""Prompt governance service (Phase 4 D4)."""

from __future__ import annotations

import logging
import re
from datetime import UTC, datetime
from typing import Any

from beanie import SortDirection
from beanie.operators import In

from app.models.gen_ai.prompt_governance import (
    PromptAuditLog,
    PromptEvaluationSummary,
    PromptRiskLevel,
    PromptStatus,
    PromptTemplate,
    PromptUsageLog,
)

logger = logging.getLogger(__name__)

_TOXIC_PATTERNS = [
    re.compile(r"\b(dumb|stupid|idiot)\b", re.IGNORECASE),
    re.compile(r"\b(hate|kill)\b", re.IGNORECASE),
]

_HALLUCINATION_PATTERNS = [
    re.compile(r"100%\s+guarantee", re.IGNORECASE),
    re.compile(r"never\s+fails", re.IGNORECASE),
]


class PromptGovernanceService:
    """Manages prompt templates, approvals, and evaluation logs."""

    async def create_template(self, payload: dict[str, Any]) -> PromptTemplate:
        existing = await PromptTemplate.find_one(
            PromptTemplate.prompt_id == payload["prompt_id"],
            PromptTemplate.version == payload["version"],
        )
        if existing:
            raise ValueError(
                f"Prompt {payload['prompt_id']} v{payload['version']} already exists"
            )

        template = PromptTemplate(**payload)
        template.evaluation = self._evaluate_content(
            template.content, evaluator=payload.get("owner", "automated")
        )
        await template.insert()
        await self._log_audit(
            template.prompt_id,
            template.version,
            "created",
            payload.get("owner", "system"),
        )
        logger.info(
            "Created prompt template %s v%s", template.prompt_id, template.version
        )
        return template

    async def update_template(
        self, prompt_id: str, version: str, payload: dict[str, Any]
    ) -> PromptTemplate | None:
        template = await PromptTemplate.find_one(
            PromptTemplate.prompt_id == prompt_id,
            PromptTemplate.version == version,
        )
        if template is None:
            return None

        if "content" in payload and payload["content"] is not None:
            template.content = payload["content"]
            template.evaluation = self._evaluate_content(
                template.content, evaluator=payload.get("owner", "automated")
            )
        for field in (
            "name",
            "description",
            "tags",
            "risk_level",
            "policies",
            "status",
            "approval_notes",
        ):
            if field in payload and payload[field] is not None:
                setattr(template, field, payload[field])
        template.updated_at = datetime.now(UTC)
        await template.save()
        await self._log_audit(
            template.prompt_id,
            template.version,
            "updated",
            payload.get("owner", "system"),
        )
        logger.info("Updated prompt template %s v%s", prompt_id, version)
        return template

    async def list_templates(
        self,
        *,
        status: PromptStatus | None = None,
        tag: str | None = None,
    ) -> list[PromptTemplate]:
        filters = []
        if status:
            filters.append(PromptTemplate.status == status)
        if tag:
            filters.append(In(PromptTemplate.tags, [tag]))

        cursor = PromptTemplate.find(*filters) if filters else PromptTemplate.find_all()
        return await cursor.sort(("updated_at", SortDirection.DESCENDING)).to_list()

    async def submit_for_review(
        self, prompt_id: str, version: str, reviewer: str
    ) -> PromptTemplate | None:
        template = await self.update_template(
            prompt_id,
            version,
            {
                "status": PromptStatus.IN_REVIEW,
                "approval_notes": None,
                "owner": reviewer,
            },
        )
        if template:
            await self._log_audit(
                template.prompt_id, template.version, "submitted_for_review", reviewer
            )
        return template

    async def approve_template(
        self,
        prompt_id: str,
        version: str,
        reviewer: str,
        notes: str | None = None,
    ) -> PromptTemplate | None:
        template = await self.update_template(
            prompt_id,
            version,
            {
                "status": PromptStatus.APPROVED,
                "approval_notes": notes,
                "owner": reviewer,
            },
        )
        if template:
            await self._log_audit(
                template.prompt_id,
                template.version,
                "approved",
                reviewer,
                extra={"notes": notes},
            )
        return template

    async def reject_template(
        self, prompt_id: str, version: str, reviewer: str, notes: str | None = None
    ) -> PromptTemplate | None:
        template = await self.update_template(
            prompt_id,
            version,
            {
                "status": PromptStatus.REJECTED,
                "approval_notes": notes,
                "owner": reviewer,
            },
        )
        if template:
            await self._log_audit(
                template.prompt_id,
                template.version,
                "rejected",
                reviewer,
                extra={"notes": notes},
            )
        return template

    async def log_usage(self, payload: dict[str, Any]) -> PromptUsageLog:
        log_entry = PromptUsageLog(**payload)
        await log_entry.insert()
        await self._log_audit(
            payload["prompt_id"],
            payload["version"],
            "usage_logged",
            payload.get("session_id", "system"),
            extra={"outcome": payload.get("outcome")},
        )
        return log_entry

    async def list_audit_logs(
        self, prompt_id: str, version: str
    ) -> list[PromptAuditLog]:
        return (
            await PromptAuditLog.find(
                PromptAuditLog.prompt_id == prompt_id,
                PromptAuditLog.version == version,
            )
            .sort(("created_at", SortDirection.DESCENDING))
            .to_list()
        )

    def evaluate_prompt(
        self, content: str, evaluator: str = "automated"
    ) -> PromptEvaluationSummary:
        return self._evaluate_content(content, evaluator=evaluator)

    def _evaluate_content(
        self, content: str, *, evaluator: str = "automated"
    ) -> PromptEvaluationSummary:
        toxicity_score = self._calculate_score(content, _TOXIC_PATTERNS)
        hallucination_score = self._calculate_score(content, _HALLUCINATION_PATTERNS)
        factual_consistency = max(0.0, 1.0 - hallucination_score)

        if toxicity_score >= 0.6 or hallucination_score >= 0.6:
            risk_level = PromptRiskLevel.HIGH
        elif toxicity_score >= 0.3 or hallucination_score >= 0.3:
            risk_level = PromptRiskLevel.MEDIUM
        else:
            risk_level = PromptRiskLevel.LOW

        return PromptEvaluationSummary(
            toxicity_score=toxicity_score,
            hallucination_score=hallucination_score,
            factual_consistency=factual_consistency,
            risk_level=risk_level,
            evaluator=evaluator,
            evaluated_at=datetime.now(UTC),
        )

    def _calculate_score(self, content: str, patterns: list[re.Pattern[str]]) -> float:
        matches = sum(bool(pattern.search(content)) for pattern in patterns)
        if not matches:
            return 0.0
        return min(1.0, matches * 0.3)

    async def _log_audit(
        self,
        prompt_id: str,
        version: str,
        action: str,
        actor: str,
        *,
        extra: dict[str, Any] | None = None,
    ) -> None:
        audit = PromptAuditLog(
            prompt_id=prompt_id,
            version=version,
            action=action,
            actor=actor,
            details=extra or {},
        )
        await audit.insert()
        logger.debug("Prompt audit logged: %s %s v%s", action, prompt_id, version)
