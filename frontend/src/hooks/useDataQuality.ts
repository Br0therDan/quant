// Data Quality Module API
// TanStack Query (v5.9) 기반 Query 활용 상태관리 및 데이터 패칭 훅
// 데이터 품질 모니터링, 이상 알림, 심각도 통계 조회
// Dashboard Summary API의 data_quality 필드 활용

import { DashboardService } from "@/client";
import type {
	DataQualityAlert,
	DataQualitySeverity,
	DataQualitySummary,
} from "@/client/types.gen";
import { useQuery } from "@tanstack/react-query";
import { useMemo } from "react";

export const dataQualityQueryKeys = {
	all: ["dataQuality"] as const,
	summary: () => [...dataQualityQueryKeys.all, "summary"] as const,
	alerts: (severity?: DataQualitySeverity) =>
		[...dataQualityQueryKeys.all, "alerts", { severity }] as const,
	severityStats: () => [...dataQualityQueryKeys.all, "severityStats"] as const,
};

/**
 * useDataQuality Hook
 *
 * 데이터 품질 모니터링을 위한 Custom Hook
 *
 * Features:
 * - 데이터 품질 요약 조회 (총 이벤트, 심각도별 카운트)
 * - 최근 알림 목록 조회 (심각도 필터링 가능)
 * - 심각도 통계 계산 (PieChart용)
 * - 자동 새로고침 (1분 간격)
 *
 * @example
 * ```tsx
 * const { qualitySummary, recentAlerts, severityStats, isLoading, error } = useDataQuality();
 *
 * if (isLoading) return <CircularProgress />;
 * if (error) return <Alert severity="error">{error.message}</Alert>;
 *
 * return (
 *   <Box>
 *     <Typography>총 이벤트: {qualitySummary?.total_alerts}</Typography>
 *     <SeverityPieChart data={severityStats} />
 *     <AlertTimeline alerts={recentAlerts} />
 *   </Box>
 * );
 * ```
 */
export function useDataQuality(severity?: DataQualitySeverity) {
	// Query: Dashboard Summary (data_quality 필드 포함)
	const dashboardSummaryQuery = useQuery({
		queryKey: dataQualityQueryKeys.summary(),
		queryFn: async () => {
			const response = await DashboardService.getDashboardSummary();
			return response.data;
		},
		staleTime: 1000 * 60, // 1분
		gcTime: 1000 * 60 * 5, // 5분
		refetchInterval: 1000 * 60, // 1분 자동 새로고침
	});

	// Derived data: Quality Summary
	const qualitySummary: DataQualitySummary | null | undefined = useMemo(() => {
		return dashboardSummaryQuery.data?.data?.data_quality;
	}, [dashboardSummaryQuery.data]);

	// Derived data: Recent Alerts (severity 필터링)
	const recentAlerts: DataQualityAlert[] = useMemo(() => {
		const alerts = qualitySummary?.recent_alerts || [];

		if (!severity) {
			return alerts;
		}

		return alerts.filter((alert) => alert.severity === severity);
	}, [qualitySummary, severity]);

	// Derived data: Severity Stats (PieChart용)
	const severityStats = useMemo(() => {
		if (!qualitySummary?.severity_breakdown) {
			return [];
		}

		const breakdown = qualitySummary.severity_breakdown;

		return Object.entries(breakdown).map(([severity, count]) => ({
			severity: severity as DataQualitySeverity,
			count: count || 0,
			name: getSeverityLabel(severity as DataQualitySeverity),
			color: getSeverityColor(severity as DataQualitySeverity),
		}));
	}, [qualitySummary]);

	// Derived data: Anomaly Details (Table용)
	const anomalyDetails = useMemo(() => {
		return (
			recentAlerts.map((alert) => ({
				id: `${alert.symbol}-${alert.occurred_at}`,
				date: alert.occurred_at,
				symbol: alert.symbol,
				dataType: alert.data_type,
				severity: alert.severity,
				isoScore: alert.iso_score,
				prophetScore: alert.prophet_score,
				priceChangePct: alert.price_change_pct,
				volumeZScore: alert.volume_z_score,
				message: alert.message,
			})) || []
		);
	}, [recentAlerts]);

	// Derived data: Total Events by Severity
	const totalEventsBySeverity = useMemo(() => {
		const breakdown = qualitySummary?.severity_breakdown || {};
		return {
			critical: breakdown.critical || 0,
			high: breakdown.high || 0,
			medium: breakdown.medium || 0,
			low: breakdown.low || 0,
			normal: breakdown.normal || 0,
		};
	}, [qualitySummary]);

	return useMemo(
		() => ({
			// Data
			qualitySummary,
			recentAlerts,
			severityStats,
			anomalyDetails,
			totalEventsBySeverity,

			// Status
			isLoading: dashboardSummaryQuery.isLoading,
			isError: dashboardSummaryQuery.isError,
			error: dashboardSummaryQuery.error,

			// Actions
			refetch: dashboardSummaryQuery.refetch,

			// Query Object (advanced usage)
			query: dashboardSummaryQuery,
		}),
		[
			qualitySummary,
			recentAlerts,
			severityStats,
			anomalyDetails,
			totalEventsBySeverity,
			dashboardSummaryQuery,
		],
	);
}

/**
 * 심각도별 한글 라벨 반환
 */
function getSeverityLabel(severity: DataQualitySeverity): string {
	const labels: Record<DataQualitySeverity, string> = {
		critical: "긴급",
		high: "높음",
		medium: "중간",
		low: "낮음",
		normal: "정상",
	};

	return labels[severity] || severity;
}

/**
 * 심각도별 색상 코드 반환 (Material-UI theme 색상)
 */
function getSeverityColor(severity: DataQualitySeverity): string {
	const colors: Record<DataQualitySeverity, string> = {
		critical: "#d32f2f", // error.dark
		high: "#f44336", // error.main
		medium: "#ff9800", // warning.main
		low: "#2196f3", // info.main
		normal: "#4caf50", // success.main
	};

	return colors[severity] || "#9e9e9e";
}
