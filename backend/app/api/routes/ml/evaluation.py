"""Evaluation harness API routes (Phase 4 D3)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.schemas.ml_platform.evaluation_harness import (
    ABTestCreate,
    ABTestResponse,
    BenchmarkCreate,
    BenchmarkResponse,
    BenchmarkRunRequest,
    BenchmarkRunResponse,
    DetailedMetrics,
    EvaluationReport,
    EvaluationRequest,
    EvaluationRunResponse,
    FairnessAuditRequest,
    FairnessReportResponse,
    ScenarioCreate,
    ScenarioResponse,
    ScenarioUpdate,
)
from app.services.evaluation_harness_service import EvaluationHarnessService
from app.services.service_factory import service_factory

router = APIRouter(prefix="/evaluation", tags=["Evaluation Harness"])


def get_service() -> EvaluationHarnessService:
    return service_factory.get_evaluation_harness_service()


@router.post(
    "/scenarios", response_model=ScenarioResponse, status_code=status.HTTP_201_CREATED
)
async def register_scenario(
    payload: ScenarioCreate,
    service: Annotated[EvaluationHarnessService, Depends(get_service)],
) -> ScenarioResponse:
    try:
        scenario = await service.register_scenario(payload.model_dump())
    except ValueError as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ScenarioResponse.model_validate(scenario)


@router.patch("/scenarios/{name}", response_model=ScenarioResponse)
async def update_scenario(
    name: str,
    payload: ScenarioUpdate,
    service: Annotated[EvaluationHarnessService, Depends(get_service)],
) -> ScenarioResponse:
    scenario = await service.update_scenario(
        name, payload.model_dump(exclude_none=True)
    )
    if scenario is None:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return ScenarioResponse.model_validate(scenario)


@router.get("/scenarios", response_model=list[ScenarioResponse])
async def list_scenarios(
    service: Annotated[EvaluationHarnessService, Depends(get_service)],
) -> list[ScenarioResponse]:
    scenarios = await service.list_scenarios()
    return [ScenarioResponse.model_validate(item) for item in scenarios]


@router.post(
    "/runs", response_model=EvaluationRunResponse, status_code=status.HTTP_201_CREATED
)
async def run_evaluation(
    payload: EvaluationRequest,
    service: Annotated[EvaluationHarnessService, Depends(get_service)],
) -> EvaluationRunResponse:
    try:
        run = await service.run_evaluation(payload.model_dump())
    except ValueError as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return EvaluationRunResponse.model_validate(run)


@router.get("/runs", response_model=list[EvaluationRunResponse])
async def list_evaluation_runs(
    service: Annotated[EvaluationHarnessService, Depends(get_service)],
    scenario_name: str | None = Query(default=None),
) -> list[EvaluationRunResponse]:
    runs = await service.list_runs(scenario_name=scenario_name)
    return [EvaluationRunResponse.model_validate(run) for run in runs]


@router.get("/runs/{run_id}/report", response_model=EvaluationReport)
async def get_evaluation_report(
    run_id: str,
    service: Annotated[EvaluationHarnessService, Depends(get_service)],
) -> EvaluationReport:
    report = await service.get_report(run_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Evaluation run not found")
    return EvaluationReport(**report)


@router.get("/runs/{run_id}/metrics", response_model=DetailedMetrics)
async def get_detailed_metrics(
    run_id: str,
    service: Annotated[EvaluationHarnessService, Depends(get_service)],
) -> DetailedMetrics:
    """상세 평가 메트릭 조회 (confusion matrix, ROC curve 등)"""
    run = await service.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Evaluation run not found")
    if run.summary is None or run.summary.detailed_metrics is None:
        raise HTTPException(
            status_code=404, detail="Detailed metrics not available for this run"
        )
    return run.summary.detailed_metrics


# ============================================================================
# Benchmark Suite Endpoints
# ============================================================================


@router.post(
    "/benchmarks",
    response_model=BenchmarkResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_benchmark(
    payload: BenchmarkCreate,
    service: Annotated[EvaluationHarnessService, Depends(get_service)],
) -> BenchmarkResponse:
    """벤치마크 스위트 생성"""
    try:
        benchmark = await service.create_benchmark(payload.model_dump())
    except ValueError as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return BenchmarkResponse.model_validate(benchmark)


@router.get("/benchmarks", response_model=list[BenchmarkResponse])
async def list_benchmarks(
    service: Annotated[EvaluationHarnessService, Depends(get_service)],
) -> list[BenchmarkResponse]:
    """벤치마크 스위트 목록 조회"""
    benchmarks = await service.list_benchmarks()
    return [BenchmarkResponse.model_validate(b) for b in benchmarks]


@router.post("/benchmarks/run", response_model=BenchmarkRunResponse)
async def run_benchmark(
    payload: BenchmarkRunRequest,
    service: Annotated[EvaluationHarnessService, Depends(get_service)],
) -> BenchmarkRunResponse:
    """벤치마크 실행"""
    try:
        run = await service.run_benchmark(payload.model_dump())
    except ValueError as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return BenchmarkRunResponse.model_validate(run)


# ============================================================================
# A/B Testing Endpoints
# ============================================================================


@router.post(
    "/ab-tests", response_model=ABTestResponse, status_code=status.HTTP_201_CREATED
)
async def create_ab_test(
    payload: ABTestCreate,
    service: Annotated[EvaluationHarnessService, Depends(get_service)],
) -> ABTestResponse:
    """A/B 테스트 생성"""
    try:
        ab_test = await service.create_ab_test(payload.model_dump())
    except ValueError as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ABTestResponse.model_validate(ab_test)


@router.get("/ab-tests", response_model=list[ABTestResponse])
async def list_ab_tests(
    service: Annotated[EvaluationHarnessService, Depends(get_service)],
) -> list[ABTestResponse]:
    """A/B 테스트 목록 조회"""
    ab_tests = await service.list_ab_tests()
    return [ABTestResponse.model_validate(t) for t in ab_tests]


@router.get("/ab-tests/{test_id}", response_model=ABTestResponse)
async def get_ab_test(
    test_id: str,
    service: Annotated[EvaluationHarnessService, Depends(get_service)],
) -> ABTestResponse:
    """A/B 테스트 상세 조회"""
    ab_test = await service.get_ab_test(test_id)
    if ab_test is None:
        raise HTTPException(status_code=404, detail="A/B test not found")
    return ABTestResponse.model_validate(ab_test)


# ============================================================================
# Fairness Audit Endpoints
# ============================================================================


@router.post(
    "/fairness/audit",
    response_model=FairnessReportResponse,
    status_code=status.HTTP_201_CREATED,
)
async def request_fairness_audit(
    payload: FairnessAuditRequest,
    service: Annotated[EvaluationHarnessService, Depends(get_service)],
) -> FairnessReportResponse:
    """공정성 감사 요청"""
    report = await service.request_fairness_audit(payload.model_dump())
    return FairnessReportResponse.model_validate(report)


@router.get("/fairness/reports", response_model=list[FairnessReportResponse])
async def list_fairness_reports(
    service: Annotated[EvaluationHarnessService, Depends(get_service)],
    model_id: str | None = Query(default=None),
) -> list[FairnessReportResponse]:
    """공정성 감사 보고서 목록 조회"""
    reports = await service.list_fairness_reports(model_id=model_id)
    return [FairnessReportResponse.model_validate(r) for r in reports]


@router.get("/fairness/reports/{report_id}", response_model=FairnessReportResponse)
async def get_fairness_report(
    report_id: str,
    service: Annotated[EvaluationHarnessService, Depends(get_service)],
) -> FairnessReportResponse:
    """공정성 감사 보고서 상세 조회"""
    report = await service.get_fairness_report(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Fairness report not found")
    return FairnessReportResponse.model_validate(report)
