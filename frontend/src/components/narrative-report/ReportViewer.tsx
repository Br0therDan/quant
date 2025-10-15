/**
 * ReportViewer Component
 *
 * 백테스트 내러티브 리포트 뷰어 (Markdown 렌더링)
 *
 * 기능:
 * - Executive Summary, Performance Analysis, Strategy Insights 등 6개 섹션 표시
 * - react-markdown 기반 Markdown 렌더링
 * - 사실 확인 배지, 생성 정보, LLM 메타데이터
 * - 내보내기/공유/재생성 액션 버튼
 *
 * Phase: 3
 * 작성일: 2025-10-14
 */

import { useNarrativeReport } from "@/hooks/useNarrativeReport";
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
} from "@mui/icons-material";
import {
  Alert,
  Box,
  Card,
  CardContent,
  CardHeader,
  Chip,
  CircularProgress,
  Divider,
  Stack,
  Typography,
} from "@mui/material";
import type React from "react";
import { useEffect } from "react";
import { ExportButton } from "./ExportButton";
import { RegenerationButton } from "./RegenerationButton";
import { SectionRenderer } from "./SectionRenderer";
import { ShareDialog } from "./ShareDialog";

// ========================================================================================
// Props Interface
// ========================================================================================

export interface ReportViewerProps {
  backtestId: string;
  autoGenerate?: boolean; // 컴포넌트 마운트 시 자동 생성 여부
}

// ========================================================================================
// Main Component
// ========================================================================================

export const ReportViewer: React.FC<ReportViewerProps> = ({
  backtestId,
  autoGenerate = false,
}) => {
  const {
    report,
    isLoading,
    isGenerating,
    error,
    executiveSummary,
    performanceAnalysis,
    strategyInsights,
    riskAssessment,
    marketContext,
    recommendations,
    generateReport,
    regenerateReport,
    exportPDF,
    shareReport,
  } = useNarrativeReport(backtestId);

  // 자동 생성
  useEffect(() => {
    if (autoGenerate && !report && !isLoading && !isGenerating) {
      generateReport({});
    }
  }, [autoGenerate, report, isLoading, isGenerating, generateReport]);

  // --------------------------------------------------------------------------------------
  // Loading State
  // --------------------------------------------------------------------------------------

  if (isLoading || isGenerating) {
    return (
      <Box
        sx={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          minHeight: 400,
          gap: 2,
        }}
      >
        <CircularProgress size={60} />
        <Typography variant="h6" color="text.secondary">
          {isGenerating ? "LLM이 리포트를 생성하고 있습니다..." : "로딩 중..."}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          최대 10초 소요될 수 있습니다
        </Typography>
      </Box>
    );
  }

  // --------------------------------------------------------------------------------------
  // Error State
  // --------------------------------------------------------------------------------------

  if (error) {
    return (
      <Alert severity="error" icon={<ErrorIcon />}>
        <Typography variant="h6">리포트 로딩 실패</Typography>
        <Typography variant="body2">
          {error instanceof Error
            ? error.message
            : "알 수 없는 오류가 발생했습니다"}
        </Typography>
      </Alert>
    );
  }

  // --------------------------------------------------------------------------------------
  // Empty State (리포트 미생성)
  // --------------------------------------------------------------------------------------

  if (!report) {
    return (
      <Card>
        <CardContent>
          <Box sx={{ textAlign: "center", py: 4 }}>
            <InfoIcon color="info" sx={{ fontSize: 60, mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              아직 리포트가 생성되지 않았습니다
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              LLM 기반 내러티브 리포트를 생성하여 백테스트 결과를 심층 분석할 수
              있습니다.
            </Typography>
            <RegenerationButton
              backtestId={backtestId}
              onRegenerate={() => generateReport({})}
              isGenerating={isGenerating}
              label="리포트 생성"
            />
          </Box>
        </CardContent>
      </Card>
    );
  }

  // --------------------------------------------------------------------------------------
  // Report Viewer
  // --------------------------------------------------------------------------------------

  return (
    <Box sx={{ maxWidth: 1200, mx: "auto" }}>
      {/* 헤더: 메타데이터 + 액션 버튼 */}
      <Card sx={{ mb: 3 }}>
        <CardHeader
          title="백테스트 내러티브 리포트"
          action={
            <Stack direction="row" spacing={1}>
              <ExportButton backtestId={backtestId} onExport={exportPDF} />
              <ShareDialog backtestId={backtestId} onShare={shareReport} />
              <RegenerationButton
                backtestId={backtestId}
                onRegenerate={() => regenerateReport({})}
                isGenerating={isGenerating}
              />
            </Stack>
          }
        />
        <Divider />
        <CardContent>
          <Stack
            direction="row"
            spacing={2}
            alignItems="center"
            flexWrap="wrap"
          >
            {/* 사실 확인 배지 */}
            <Chip
              icon={
                report.fact_check_passed ? <CheckCircleIcon /> : <ErrorIcon />
              }
              label={
                report.fact_check_passed ? "사실 확인 통과" : "사실 확인 실패"
              }
              color={report.fact_check_passed ? "success" : "error"}
              variant="outlined"
            />

            {/* 생성 시간 */}
            <Chip
              icon={<InfoIcon />}
              label={`생성: ${new Date(report.generated_at).toLocaleString(
                "ko-KR"
              )}`}
              variant="outlined"
            />

            {/* LLM 모델 */}
            <Chip
              label={`${report.llm_model}${
                report.llm_version ? ` v${report.llm_version}` : ""
              }`}
              variant="outlined"
            />
          </Stack>

          {/* 검증 오류 경고 */}
          {!report.fact_check_passed &&
            report.validation_errors &&
            report.validation_errors.length > 0 && (
              <Alert severity="warning" sx={{ mt: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  검증 오류 ({report.validation_errors.length}건):
                </Typography>
                <ul style={{ margin: 0, paddingLeft: 20 }}>
                  {report.validation_errors.map((error, idx) => (
                    <li key={idx}>
                      <Typography variant="body2">{error}</Typography>
                    </li>
                  ))}
                </ul>
              </Alert>
            )}
        </CardContent>
      </Card>

      {/* 섹션 1: Executive Summary */}
      {executiveSummary && (
        <SectionRenderer
          title="📋 요약"
          icon={<InfoIcon />}
          content={{
            type: "executive_summary",
            overview: executiveSummary.overview,
            key_findings: executiveSummary.key_findings,
            title: executiveSummary.title,
            recommendation: executiveSummary.recommendation,
            confidence_level: executiveSummary.confidence_level,
          }}
        />
      )}

      {/* 섹션 2: Performance Analysis */}
      {performanceAnalysis && (
        <SectionRenderer
          title="📈 성과 분석"
          content={{
            type: "performance_analysis",
            summary: performanceAnalysis.summary,
            return_analysis: performanceAnalysis.return_analysis,
            risk_analysis: performanceAnalysis.risk_analysis,
            sharpe_interpretation: performanceAnalysis.sharpe_interpretation,
            drawdown_commentary: performanceAnalysis.drawdown_commentary,
            trade_statistics_summary:
              performanceAnalysis.trade_statistics_summary,
          }}
        />
      )}

      {/* 섹션 3: Strategy Insights */}
      {strategyInsights && (
        <SectionRenderer
          title="💡 전략 인사이트"
          content={{
            type: "strategy_insights",
            data: strategyInsights,
          }}
        />
      )}

      {/* 섹션 4: Risk Assessment */}
      {riskAssessment && (
        <SectionRenderer
          title="⚠️ 리스크 평가"
          content={{
            type: "risk_assessment",
            data: riskAssessment,
          }}
        />
      )}

      {/* 섹션 5: Market Context */}
      {marketContext && (
        <SectionRenderer
          title="🌍 시장 맥락"
          content={{
            type: "market_context",
            data: marketContext,
          }}
        />
      )}

      {/* 섹션 6: Recommendations */}
      {recommendations && (
        <SectionRenderer
          title="✅ 권장사항"
          content={{
            type: "recommendations",
            data: recommendations,
          }}
        />
      )}

      {/* Footer: 면책 조항 */}
      <Card sx={{ mt: 3, bgcolor: "background.default" }}>
        <CardContent>
          <Typography variant="caption" color="text.secondary" display="block">
            ⚠️ 본 리포트는 AI(LLM)가 생성한 분석이며, 투자 조언이 아닙니다. 실제
            투자 결정 시 반드시 전문가와 상담하시기 바랍니다.
          </Typography>
          <Typography
            variant="caption"
            color="text.secondary"
            display="block"
            sx={{ mt: 1 }}
          >
            📌 사실 확인 통과 여부는 백테스트 메트릭과 LLM 생성 텍스트 간의
            일관성을 검증한 결과입니다.
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};
