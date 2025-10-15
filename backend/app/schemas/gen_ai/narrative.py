"""
Narrative Report Schemas for LLM-generated backtest analysis.

Phase 3 D1: Narrative Report Generator
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.enums import ReportRecommendation


class ExecutiveSummary(BaseModel):
    """임원용 요약"""

    title: str = Field(..., description="리포트 제목")
    overview: str = Field(
        ..., description="백테스트 개요 (2-3 문장)", min_length=50, max_length=500
    )
    key_findings: List[str] = Field(
        ..., description="핵심 발견사항 (3-5개)", min_length=3, max_length=5
    )
    recommendation: ReportRecommendation = Field(..., description="최종 추천 액션")
    confidence_level: float = Field(..., ge=0.0, le=1.0, description="추천 신뢰도 (0-1)")


class PerformanceAnalysis(BaseModel):
    """성과 분석"""

    summary: str = Field(..., description="성과 요약 (2-3 문장)", max_length=500)
    return_analysis: str = Field(..., description="수익률 분석", max_length=300)
    risk_analysis: str = Field(..., description="리스크 분석", max_length=300)
    sharpe_interpretation: str = Field(..., description="샤프 비율 해석", max_length=200)
    drawdown_commentary: str = Field(..., description="낙폭 해설", max_length=200)
    trade_statistics_summary: str = Field(..., description="거래 통계 요약", max_length=200)


class StrategyInsights(BaseModel):
    """전략 인사이트"""

    strategy_name: str = Field(..., description="전략 이름")
    strategy_description: str = Field(..., description="전략 설명", max_length=300)
    key_parameters: dict = Field(..., description="핵심 파라미터")
    parameter_sensitivity: str = Field(..., description="파라미터 민감도 분석", max_length=300)
    strengths: List[str] = Field(
        ..., description="전략 강점 (2-4개)", min_length=2, max_length=4
    )
    weaknesses: List[str] = Field(
        ..., description="전략 약점 (2-4개)", min_length=2, max_length=4
    )


class RiskAssessment(BaseModel):
    """리스크 평가"""

    overall_risk_level: str = Field(
        ..., description="전체 리스크 수준 (Low/Medium/High/Very High)"
    )
    risk_summary: str = Field(..., description="리스크 요약", max_length=300)
    volatility_assessment: str = Field(..., description="변동성 평가", max_length=200)
    max_drawdown_context: str = Field(..., description="최대 낙폭 맥락", max_length=200)
    concentration_risk: str = Field(..., description="집중 리스크 분석", max_length=200)
    tail_risk: str = Field(..., description="테일 리스크 평가", max_length=200)


class MarketContext(BaseModel):
    """시장 맥락 (Phase 1 통합)"""

    regime_analysis: str = Field(
        ..., description="시장 레짐 분석 (Phase 1 D2)", max_length=300
    )
    ml_signal_confidence: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="ML 시그널 신뢰도 (Phase 1 D1)"
    )
    forecast_outlook: Optional[str] = Field(
        None, description="포트폴리오 예측 전망 (Phase 1 D3)", max_length=200
    )
    external_factors: List[str] = Field(
        default_factory=list, description="외부 요인 (뉴스, 경제 지표 등)", max_length=5
    )


class Recommendations(BaseModel):
    """추천 사항"""

    action: ReportRecommendation = Field(..., description="추천 액션")
    rationale: str = Field(..., description="추천 근거", max_length=400)
    next_steps: List[str] = Field(
        ..., description="다음 단계 (2-4개)", min_length=2, max_length=4
    )
    optimization_suggestions: Optional[List[str]] = Field(
        None, description="최적화 제안 (선택 사항)", max_length=5
    )
    risk_mitigation: Optional[List[str]] = Field(
        None, description="리스크 완화 방안 (선택 사항)", max_length=5
    )


class BacktestNarrativeReport(BaseModel):
    """백테스트 내러티브 리포트 (전체)"""

    # 메타데이터
    backtest_id: str = Field(..., description="백테스트 ID")
    generated_at: datetime = Field(..., description="리포트 생성 시간")
    llm_model: str = Field(..., description="사용된 LLM 모델")
    llm_version: Optional[str] = Field(None, description="LLM 버전")

    # 리포트 섹션
    executive_summary: ExecutiveSummary = Field(..., description="임원용 요약")
    performance_analysis: PerformanceAnalysis = Field(..., description="성과 분석")
    strategy_insights: StrategyInsights = Field(..., description="전략 인사이트")
    risk_assessment: RiskAssessment = Field(..., description="리스크 평가")
    market_context: MarketContext = Field(..., description="시장 맥락")
    recommendations: Recommendations = Field(..., description="추천 사항")

    # 검증 메타데이터
    fact_check_passed: bool = Field(..., description="사실 확인 통과 여부")
    validation_errors: List[str] = Field(
        default_factory=list, description="검증 오류 (있는 경우)"
    )


class NarrativeReportRequest(BaseModel):
    """내러티브 리포트 생성 요청"""

    backtest_id: str = Field(..., description="백테스트 ID")
    include_phase1_insights: bool = Field(
        default=True,
        description="Phase 1 인사이트 포함 여부 (ML Signal, Regime, Forecast)",
    )
    language: str = Field(default="ko", description="리포트 언어 (ko/en)")
    detail_level: str = Field(
        default="standard", description="상세 수준 (brief/standard/detailed)"
    )
    model_id: Optional[str] = Field(
        default=None,
        description="사용할 OpenAI 모델 ID (지정하지 않으면 서비스 기본값)",
    )


class NarrativeReportResponse(BaseModel):
    """내러티브 리포트 응답"""

    status: str = Field(..., description="응답 상태")
    message: str = Field(..., description="응답 메시지")
    data: Optional[BacktestNarrativeReport] = Field(None, description="리포트 데이터")
    processing_time_ms: float = Field(..., description="처리 시간 (밀리초)")
    cached: bool = Field(default=False, description="캐시된 결과 여부")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="응답 시간")
