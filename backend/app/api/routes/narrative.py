"""
Narrative Report Generation API Routes
Phase 3 D1: LLM 기반 백테스트 내러티브 리포트 생성 엔드포인트
"""

import logging
import time
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.schemas.narrative import NarrativeReportResponse
from app.services.service_factory import service_factory

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/backtests/{backtest_id}/report",
    response_model=NarrativeReportResponse,
    name="generate_narrative_report",
    description="백테스트 결과에 대한 LLM 기반 내러티브 리포트 생성",
)
async def generate_narrative_report(
    backtest_id: str,
    include_phase1_insights: bool = Query(
        True, description="Phase 1 인사이트 포함 여부 (ML Signal, Regime, Forecast)"
    ),
    language: Optional[str] = Query("ko", description="리포트 언어 (ko/en)"),
    detail_level: Optional[str] = Query(
        "standard", description="상세도 수준 (brief/standard/detailed)"
    ),
) -> NarrativeReportResponse:
    """
    백테스트 결과를 분석하여 전문 퀀트 애널리스트 수준의 내러티브 리포트를 생성합니다.

    **주요 기능:**
    - OpenAI GPT-4 기반 자연어 분석
    - Phase 1 예측 인텔리전스 통합 (ML Signal, Regime Detection, Probabilistic Forecast)
    - Pydantic 스키마 기반 구조화된 출력
    - 팩트 체크 (실제 백테스트 KPI와 교차 검증)

    **리포트 섹션:**
    - Executive Summary: 핵심 요약, 추천 액션
    - Performance Analysis: 수익률, 위험, 샤프 비율 해석
    - Strategy Insights: 전략 파라미터 민감도, 강점/약점
    - Risk Assessment: 변동성, 최대 낙폭, 집중도 위험
    - Market Context: 시장 체제 분석 (Phase 1 D2), ML 신호 (Phase 1 D1), 예측 전망 (Phase 1 D3)
    - Recommendations: 구체적인 액션 플랜, 최적화 제안

    **Parameters:**
    - `backtest_id`: 분석할 백테스트 ID
    - `include_phase1_insights`: Phase 1 인사이트 포함 여부 (기본값: True)
    - `language`: 리포트 언어 (ko/en, 기본값: ko)
    - `detail_level`: 상세도 수준 (brief/standard/detailed, 기본값: standard)

    **Returns:**
    - `BacktestNarrativeReport`: 구조화된 내러티브 리포트
    - `metadata`: 생성 시간, LLM 모델, 팩트 체크 결과

    **Raises:**
    - `404`: 백테스트를 찾을 수 없음
    - `400`: 백테스트가 완료되지 않음 (리포트 생성 불가)
    - `500`: LLM API 호출 실패, 검증 실패

    **Example:**
    ```python
    import httpx

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8500/api/v1/narrative/backtests/abc123/report",
            params={
                "include_phase1_insights": True,
                "language": "ko",
                "detail_level": "standard"
            }
        )
        report = response.json()
        print(report["executive_summary"]["overview"])
    ```
    """
    try:
        start_time = time.perf_counter()

        logger.info(
            f"Generating narrative report for backtest {backtest_id}",
            extra={
                "include_phase1": include_phase1_insights,
                "language": language,
                "detail_level": detail_level,
            },
        )

        # ServiceFactory에서 서비스 가져오기
        narrative_service = service_factory.get_narrative_report_service()

        # 리포트 생성
        report = await narrative_service.generate_report(
            backtest_id=backtest_id,
            include_phase1_insights=include_phase1_insights,
            language=language or "ko",
            detail_level=detail_level or "standard",
        )

        # 처리 시간 계산
        processing_time_ms = (time.perf_counter() - start_time) * 1000

        # 응답 래핑
        response = NarrativeReportResponse(
            status="success",
            message="리포트 생성 완료",
            data=report,
            processing_time_ms=processing_time_ms,
            cached=False,
        )

        logger.info(
            "Narrative report generated successfully",
            extra={
                "backtest_id": backtest_id,
                "fact_check_passed": report.fact_check_passed,
                "validation_errors": len(report.validation_errors or []),
                "processing_time_ms": processing_time_ms,
            },
        )

        return response

    except ValueError as e:
        # 백테스트 없음 or 불완전한 백테스트
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=f"백테스트를 찾을 수 없습니다: {e}")
        elif "incomplete" in error_msg.lower() or "완료되지" in error_msg:
            raise HTTPException(
                status_code=400,
                detail=f"백테스트가 완료되지 않아 리포트를 생성할 수 없습니다: {e}",
            )
        else:
            raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(
            f"Failed to generate narrative report: {e}",
            extra={"backtest_id": backtest_id},
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=f"리포트 생성 중 오류 발생: {str(e)}")
