"""Evaluation harness service (Phase 4 D3)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from statistics import mean
from typing import Any

from beanie import PydanticObjectId, SortDirection

from app.models.backtest import Backtest
from app.models.evaluation import (
    BenchmarkMetric,
    ComplianceStatus,
    EvaluationRun,
    EvaluationScenario,
    EvaluationStatus,
    EvaluationSummary,
    ExplainabilityArtifact,
    MetricComparison,
)

logger = logging.getLogger(__name__)


class EvaluationHarnessService:
    """Runs benchmark scenarios and stores explainability artifacts."""

    async def register_scenario(self, payload: dict[str, Any]) -> EvaluationScenario:
        existing = await EvaluationScenario.find_one(
            EvaluationScenario.name == payload["name"]
        )
        if existing:
            raise ValueError(f"Scenario '{payload['name']}' already exists")

        scenario = EvaluationScenario(**payload)
        await scenario.insert()
        logger.info("Registered evaluation scenario %s", scenario.name)
        return scenario

    async def update_scenario(
        self, name: str, payload: dict[str, Any]
    ) -> EvaluationScenario | None:
        scenario = await EvaluationScenario.find_one(
            EvaluationScenario.name == name
        )
        if scenario is None:
            return None

        for field, value in payload.items():
            setattr(scenario, field, value)
        scenario.updated_at = datetime.now(UTC)
        await scenario.save()
        logger.info("Updated scenario %s", name)
        return scenario

    async def list_scenarios(self) -> list[EvaluationScenario]:
        return await EvaluationScenario.find_all().sort(
            (EvaluationScenario.created_at, SortDirection.DESCENDING)
        ).to_list()

    async def run_evaluation(self, payload: dict[str, Any]) -> EvaluationRun:
        scenario = await EvaluationScenario.find_one(
            EvaluationScenario.name == payload["scenario_name"]
        )
        if scenario is None:
            raise ValueError(
                f"Scenario '{payload['scenario_name']}' is not registered"
            )

        run = EvaluationRun(
            scenario_name=scenario.name,
            candidate_backtest_id=payload["candidate_backtest_id"],
            candidate_model_name=payload["candidate_model_name"],
            candidate_model_version=payload.get("candidate_model_version"),
            status=EvaluationStatus.RUNNING,
        )
        await run.insert()

        baseline_metrics = await self._collect_baseline_metrics(
            scenario.baseline_backtest_ids
        )
        candidate_metrics = await self._resolve_candidate_metrics(payload)

        comparisons = self._build_comparisons(
            candidate_metrics, baseline_metrics
        )
        compliance = self._evaluate_compliance(
            comparisons, scenario.benchmark_metrics
        )
        explainability = [
            ExplainabilityArtifact(**artifact)
            if isinstance(artifact, dict)
            else artifact
            for artifact in payload.get("explainability", [])
        ]

        run.summary = EvaluationSummary(
            metrics=comparisons,
            compliance=compliance,
            notes=payload.get("compliance_inputs", {}).get("notes"),
        )
        run.explainability = explainability
        run.compliance_checks = self._build_compliance_checks(
            scenario.benchmark_metrics,
            comparisons,
            payload.get("compliance_inputs", {}),
        )
        run.status = (
            EvaluationStatus.COMPLETED
            if compliance != ComplianceStatus.FAILED
            else EvaluationStatus.FAILED
        )
        run.completed_at = datetime.now(UTC)
        await run.save()

        logger.info(
            "Evaluation completed for %s (%s)",
            run.candidate_model_name,
            run.candidate_model_version or "unversioned",
        )
        return run

    async def list_runs(
        self, *, scenario_name: str | None = None
    ) -> list[EvaluationRun]:
        cursor = (
            EvaluationRun.find(EvaluationRun.scenario_name == scenario_name)
            if scenario_name
            else EvaluationRun.find_all()
        )
        return await cursor.sort(
            (EvaluationRun.started_at, SortDirection.DESCENDING)
        ).to_list()

    async def get_report(self, run_id: str) -> dict[str, Any] | None:
        try:
            object_id = PydanticObjectId(run_id)
        except Exception:  # noqa: BLE001
            object_id = None
        run = (
            await EvaluationRun.get(object_id)
            if object_id is not None
            else await EvaluationRun.find_one(EvaluationRun.id == run_id)
        )
        if run is None or run.summary is None:
            return None
        return {
            "scenario_name": run.scenario_name,
            "candidate_model_name": run.candidate_model_name,
            "candidate_model_version": run.candidate_model_version,
            "compliance": run.summary.compliance,
            "metrics": [comparison.model_dump() for comparison in run.summary.metrics],
            "notes": run.summary.notes,
            "explainability": [artifact.model_dump() for artifact in run.explainability],
            "compliance_checks": run.compliance_checks,
        }

    async def _collect_baseline_metrics(
        self, baseline_backtest_ids: list[str]
    ) -> dict[str, list[float]]:
        metrics: dict[str, list[float]] = {}
        for backtest_id in baseline_backtest_ids:
            try:
                object_id = PydanticObjectId(backtest_id)
            except Exception:  # noqa: BLE001
                object_id = None
            backtest = (
                await Backtest.get(object_id)
                if object_id is not None
                else await Backtest.find_one(Backtest.id == backtest_id)
            )
            if backtest is None or backtest.performance is None:
                continue
            for metric_name, value in backtest.performance.model_dump().items():
                if isinstance(value, (int, float)):
                    metrics.setdefault(metric_name, []).append(float(value))
        return metrics

    async def _resolve_candidate_metrics(
        self, payload: dict[str, Any]
    ) -> dict[str, float]:
        metrics = payload.get("candidate_metrics", {})
        if metrics:
            return {key: float(value) for key, value in metrics.items()}

        try:
            candidate_id = PydanticObjectId(payload["candidate_backtest_id"])
        except Exception:  # noqa: BLE001
            candidate_id = None

        candidate_backtest = (
            await Backtest.get(candidate_id)
            if candidate_id is not None
            else await Backtest.find_one(
                Backtest.id == payload["candidate_backtest_id"]
            )
        )
        if candidate_backtest and candidate_backtest.performance:
            return {
                key: float(value)
                for key, value in candidate_backtest.performance.model_dump().items()
                if isinstance(value, (int, float))
            }
        return {}

    def _build_comparisons(
        self,
        candidate_metrics: dict[str, float],
        baseline_metrics: dict[str, list[float]],
    ) -> list[MetricComparison]:
        comparisons: list[MetricComparison] = []
        for metric_name, candidate_value in candidate_metrics.items():
            values = baseline_metrics.get(metric_name)
            baseline_average = mean(values) if values else None
            delta = (
                candidate_value - baseline_average
                if baseline_average is not None
                else None
            )
            comparisons.append(
                MetricComparison(
                    metric_name=metric_name,
                    candidate=candidate_value,
                    baseline_average=baseline_average,
                    delta=delta,
                )
            )
        return comparisons

    def _evaluate_compliance(
        self,
        comparisons: list[MetricComparison],
        benchmark_metrics: list[BenchmarkMetric],
    ) -> ComplianceStatus:
        if not benchmark_metrics:
            return ComplianceStatus.PASSED

        status = ComplianceStatus.PASSED
        threshold_map = {metric.name: metric for metric in benchmark_metrics}
        for comparison in comparisons:
            benchmark = threshold_map.get(comparison.metric_name)
            if benchmark is None or benchmark.threshold is None:
                continue
            candidate_value = comparison.candidate
            threshold = benchmark.threshold
            meets_expectation = (
                candidate_value >= threshold
                if benchmark.higher_is_better
                else candidate_value <= threshold
            )
            if not meets_expectation:
                status = (
                    ComplianceStatus.FAILED
                    if benchmark.higher_is_better
                    else ComplianceStatus.WARNING
                )
                break
        return status

    def _build_compliance_checks(
        self,
        benchmark_metrics: list[BenchmarkMetric],
        comparisons: list[MetricComparison],
        compliance_inputs: dict[str, Any],
    ) -> dict[str, Any]:
        check_results: dict[str, Any] = {
            "benchmarks": [metric.model_dump() for metric in benchmark_metrics],
            "inputs": compliance_inputs,
        }
        for comparison in comparisons:
            check_results[comparison.metric_name] = comparison.model_dump()
        return check_results
