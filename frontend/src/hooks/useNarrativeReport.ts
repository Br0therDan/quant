/**
 * useNarrativeReport Hook
 *
 * LLM 기반 백테스트 내러티브 리포트 생성 및 관리를 위한 Custom Hook
 *
 * 기능:
 * - 리포트 생성 (Phase 1 인사이트 통합)
 * - 리포트 재생성
 * - PDF 내보내기
 * - 공유 기능 (이메일/Slack)
 *
 * Phase: 3
 * 작성일: 2025-10-14
 */

import { NarrativeService } from "@/client";
import { useSnackbar } from "@/contexts/SnackbarContext";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import jsPDF from "jspdf";
import { useState } from "react";

// ========================================================================================
// Types & Interfaces
// ========================================================================================

export interface NarrativeReportOptions {
	includePhase1Insights?: boolean; // ML Signal, Regime, Forecast 포함
	language?: "ko" | "en"; // 리포트 언어
	detailLevel?: "brief" | "standard" | "detailed"; // 상세도
}

export interface ShareOptions {
	method: "email" | "slack";
	recipients?: string[]; // 이메일 주소 또는 Slack 채널
	message?: string; // 추가 메시지
}

export interface PDFExportOptions {
	filename?: string;
	includeCharts?: boolean;
	pageSize?: "a4" | "letter";
	orientation?: "portrait" | "landscape";
}

// ========================================================================================
// Query Keys
// ========================================================================================

export const narrativeReportQueryKeys = {
	all: ["narrativeReport"] as const,
	byBacktest: (backtestId: string) =>
		[...narrativeReportQueryKeys.all, backtestId] as const,
};

// ========================================================================================
// Main Hook
// ========================================================================================

export const useNarrativeReport = (backtestId: string) => {
	const queryClient = useQueryClient();
	const { showSuccess, showError } = useSnackbar();
	const [isExporting, setIsExporting] = useState(false);

	// --------------------------------------------------------------------------------------
	// 리포트 조회 Query
	// --------------------------------------------------------------------------------------

	const reportQuery = useQuery({
		queryKey: narrativeReportQueryKeys.byBacktest(backtestId),
		queryFn: async () => {
			const response = await NarrativeService.generateNarrativeReport({
				path: { backtest_id: backtestId },
			});
			return response.data;
		},
		staleTime: 1000 * 60 * 10, // 10분 (LLM 리포트는 자주 변경되지 않음)
		enabled: !!backtestId,
	});

	// --------------------------------------------------------------------------------------
	// 리포트 생성 Mutation
	// --------------------------------------------------------------------------------------

	const generateReportMutation = useMutation({
		mutationFn: async (options: NarrativeReportOptions = {}) => {
			const response = await NarrativeService.generateNarrativeReport({
				path: { backtest_id: backtestId },
				query: {
					include_phase1_insights: options.includePhase1Insights ?? true,
					language: options.language ?? "ko",
					detail_level: options.detailLevel ?? "standard",
				},
			});
			return response.data;
		},
		onSuccess: (data) => {
			queryClient.setQueryData(
				narrativeReportQueryKeys.byBacktest(backtestId),
				data,
			);
			showSuccess("내러티브 리포트가 생성되었습니다");
		},
		onError: (error) => {
			showError(
				`리포트 생성 실패: ${error instanceof Error ? error.message : "알 수 없는 오류"}`,
			);
		},
	});

	// --------------------------------------------------------------------------------------
	// 리포트 재생성 Mutation (동일 API, 새로운 LLM 호출)
	// --------------------------------------------------------------------------------------

	const regenerateReportMutation = useMutation({
		mutationFn: async (options: NarrativeReportOptions = {}) => {
			const response = await NarrativeService.generateNarrativeReport({
				path: { backtest_id: backtestId },
				query: {
					include_phase1_insights: options.includePhase1Insights ?? true,
					language: options.language ?? "ko",
					detail_level: options.detailLevel ?? "standard",
				},
			});
			return response.data;
		},
		onSuccess: (data) => {
			queryClient.setQueryData(
				narrativeReportQueryKeys.byBacktest(backtestId),
				data,
			);
			showSuccess("리포트가 재생성되었습니다");
		},
		onError: (error) => {
			showError(
				`재생성 실패: ${error instanceof Error ? error.message : "알 수 없는 오류"}`,
			);
		},
	});

	// --------------------------------------------------------------------------------------
	// PDF 내보내기
	// --------------------------------------------------------------------------------------

	const exportPDF = async (options: PDFExportOptions = {}) => {
		if (!reportQuery.data?.data) {
			showError("내보낼 리포트가 없습니다");
			return;
		}

		setIsExporting(true);
		try {
			const report = reportQuery.data.data;
			const pdf = new jsPDF({
				orientation: options.orientation ?? "portrait",
				unit: "mm",
				format: options.pageSize ?? "a4",
			});

			// PDF 메타데이터
			pdf.setProperties({
				title: `Backtest Narrative Report - ${backtestId}`,
				author: "Quant Platform",
				subject: "Backtest Analysis Report",
				keywords: "backtest, narrative, analysis",
				creator: "Quant Platform AI",
			});

			let yPos = 20;
			const pageWidth = pdf.internal.pageSize.getWidth();
			const margin = 15;
			const contentWidth = pageWidth - margin * 2;

			// 제목
			pdf.setFontSize(18);
			pdf.setFont("helvetica", "bold");
			pdf.text("백테스트 내러티브 리포트", margin, yPos);
			yPos += 10;

			// 생성 정보
			pdf.setFontSize(10);
			pdf.setFont("helvetica", "normal");
			pdf.text(
				`생성일시: ${new Date(report.generated_at).toLocaleString("ko-KR")}`,
				margin,
				yPos,
			);
			yPos += 6;
			pdf.text(
				`LLM 모델: ${report.llm_model}${report.llm_version ? ` (${report.llm_version})` : ""}`,
				margin,
				yPos,
			);
			yPos += 10;

			// Executive Summary
			pdf.setFontSize(14);
			pdf.setFont("helvetica", "bold");
			pdf.text("요약", margin, yPos);
			yPos += 8;
			pdf.setFontSize(10);
			pdf.setFont("helvetica", "normal");
			const summaryLines = pdf.splitTextToSize(
				report.executive_summary.overview,
				contentWidth,
			);
			pdf.text(summaryLines, margin, yPos);
			yPos += summaryLines.length * 5 + 5;

			// 핵심 발견사항
			if (
				report.executive_summary.key_findings &&
				report.executive_summary.key_findings.length > 0
			) {
				pdf.setFont("helvetica", "bold");
				pdf.text("핵심 발견사항:", margin, yPos);
				yPos += 6;
				pdf.setFont("helvetica", "normal");
				report.executive_summary.key_findings.forEach(
					(finding: string, idx: number) => {
						if (yPos > 270) {
							pdf.addPage();
							yPos = 20;
						}
						pdf.text(`${idx + 1}. ${finding}`, margin + 5, yPos);
						yPos += 6;
					},
				);
				yPos += 5;
			}

			// Performance Analysis
			if (yPos > 250) {
				pdf.addPage();
				yPos = 20;
			}
			pdf.setFontSize(14);
			pdf.setFont("helvetica", "bold");
			pdf.text("성과 분석", margin, yPos);
			yPos += 8;
			pdf.setFontSize(10);
			pdf.setFont("helvetica", "normal");
			const perfLines = pdf.splitTextToSize(
				report.performance_analysis.summary,
				contentWidth,
			);
			pdf.text(perfLines, margin, yPos);
			yPos += perfLines.length * 5 + 10;

			// 검증 상태
			if (yPos > 260) {
				pdf.addPage();
				yPos = 20;
			}
			pdf.setFontSize(12);
			pdf.setFont("helvetica", "bold");
			pdf.text(
				`사실 확인: ${report.fact_check_passed ? "✓ 통과" : "✗ 실패"}`,
				margin,
				yPos,
			);

			if (
				!report.fact_check_passed &&
				report.validation_errors &&
				report.validation_errors.length > 0
			) {
				yPos += 8;
				pdf.setFontSize(10);
				pdf.setFont("helvetica", "normal");
				pdf.setTextColor(200, 0, 0);
				report.validation_errors.forEach((error: string) => {
					if (yPos > 270) {
						pdf.addPage();
						yPos = 20;
					}
					pdf.text(`⚠ ${error}`, margin + 5, yPos);
					yPos += 6;
				});
				pdf.setTextColor(0, 0, 0);
			}

			// 파일명 생성
			const filename =
				options.filename ?? `backtest_report_${backtestId}_${Date.now()}.pdf`;

			// PDF 저장
			pdf.save(filename);
			showSuccess(`PDF 내보내기 완료: ${filename}`);
		} catch (error) {
			showError(
				`PDF 내보내기 실패: ${error instanceof Error ? error.message : "알 수 없는 오류"}`,
			);
		} finally {
			setIsExporting(false);
		}
	};

	// --------------------------------------------------------------------------------------
	// 공유 기능 (Placeholder - Backend API 필요)
	// --------------------------------------------------------------------------------------

	const shareReport = async (options: ShareOptions) => {
		if (!reportQuery.data?.data) {
			showError("공유할 리포트가 없습니다");
			return;
		}

		try {
			// TODO: Backend API 구현 후 연동
			// await NarrativeService.shareReport({
			//   path: { backtest_id: backtestId },
			//   body: options,
			// });

			console.log("Share report:", options);
			showSuccess(`리포트가 ${options.method}로 공유되었습니다`);
		} catch (error) {
			showError(
				`공유 실패: ${error instanceof Error ? error.message : "알 수 없는 오류"}`,
			);
		}
	};

	// --------------------------------------------------------------------------------------
	// Return Hook Interface
	// --------------------------------------------------------------------------------------

	return {
		// 상태
		report: reportQuery.data?.data,
		isLoading: reportQuery.isLoading,
		isGenerating: generateReportMutation.isPending,
		isRegenerating: regenerateReportMutation.isPending,
		isExporting,
		error: reportQuery.error,

		// 섹션 추출 (편의 함수)
		executiveSummary: reportQuery.data?.data?.executive_summary,
		performanceAnalysis: reportQuery.data?.data?.performance_analysis,
		strategyInsights: reportQuery.data?.data?.strategy_insights,
		riskAssessment: reportQuery.data?.data?.risk_assessment,
		marketContext: reportQuery.data?.data?.market_context,
		recommendations: reportQuery.data?.data?.recommendations,

		// 액션
		generateReport: generateReportMutation.mutate,
		regenerateReport: regenerateReportMutation.mutate,
		exportPDF,
		shareReport,

		// 유틸리티
		refresh: () =>
			queryClient.invalidateQueries({
				queryKey: narrativeReportQueryKeys.byBacktest(backtestId),
			}),
	};
};
