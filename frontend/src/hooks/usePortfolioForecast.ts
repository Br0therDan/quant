/**
 * usePortfolioForecast Hook
 *
 * 포트폴리오 예측 데이터 조회 및 분석을 위한 Custom Hook
 *
 * Features:
 * - 확률적 포트폴리오 가치 예측 (percentile bands)
 * - 다양한 예측 기간 (7-120일)
 * - 예측 메트릭 (예상 수익률, 변동성)
 * - 시나리오 분석 (Bull/Base/Bear)
 *
 * @author GitHub Copilot
 * @created 2025-01-16
 */

import type {
	ForecastPercentileBand,
	PortfolioForecastDistribution,
	PortfolioForecastResponse,
} from "@/client";
import { DashboardService } from "@/client";
import { useSnackbar } from "@/contexts/SnackbarContext";
import { useQuery, type UseQueryResult } from "@tanstack/react-query";

// ============================================================================
// Query Keys (Hierarchical Pattern)
// ============================================================================

export const portfolioForecastQueryKeys = {
	/**
	 * 모든 포트폴리오 예측 쿼리의 Base Key
	 */
	all: ["portfolio-forecast"] as const,

	/**
	 * 기본 예측 조회 (30일)
	 */
	forecast: () => [...portfolioForecastQueryKeys.all, "forecast"] as const,

	/**
	 * 특정 기간 예측 조회
	 * @param horizonDays - 예측 기간 (7-120일)
	 */
	forecastWithHorizon: (horizonDays: number) =>
		[...portfolioForecastQueryKeys.all, "forecast", horizonDays] as const,
};

// ============================================================================
// Types
// ============================================================================

/**
 * 포트폴리오 예측 훅 옵션
 */
export interface UsePortfolioForecastOptions {
	/** 예측 기간 (일, 7-120일) */
	horizonDays?: number;
	/** 자동 조회 활성화 */
	enabled?: boolean;
	/** 데이터 갱신 주기 (ms, 기본 5분) */
	staleTime?: number;
}

/**
 * 시나리오 타입 (백분위 기반)
 */
export type ScenarioType = "bull" | "base" | "bear";

/**
 * 시나리오 분석 결과
 */
export interface ScenarioAnalysis {
	scenario: ScenarioType;
	label: string;
	percentile: number;
	projectedValue: number;
	returnPct: number;
	probability: number;
	color: string;
}

// ============================================================================
// Query Hooks
// ============================================================================

/**
 * 포트폴리오 예측 조회
 *
 * @example
 * ```tsx
 * const { data, isLoading } = usePortfolioForecast({ horizonDays: 30 });
 * if (data?.data) {
 *   console.log(data.data.expected_return_pct);
 * }
 * ```
 *
 * @param options - 훅 옵션 (예측 기간, 활성화 여부)
 * @returns Query 결과 (data, isLoading, error, refetch 등)
 */
export function usePortfolioForecastQuery(
	options?: UsePortfolioForecastOptions,
): UseQueryResult<PortfolioForecastResponse | undefined, Error> {
	const { showError } = useSnackbar();
	const horizonDays = options?.horizonDays ?? 30;

	return useQuery({
		queryKey: portfolioForecastQueryKeys.forecastWithHorizon(horizonDays),
		queryFn: async () => {
			const response = await DashboardService.getPortfolioForecast({
				query: {
					horizon_days: horizonDays,
				},
			});
			return response.data;
		},
		staleTime: options?.staleTime ?? 1000 * 60 * 5, // 5분
		enabled: options?.enabled ?? true,
		meta: {
			onError: (error: Error) => {
				showError(`포트폴리오 예측 조회 실패: ${error.message}`);
			},
		},
	});
} // ============================================================================
// Helper Functions
// ============================================================================

/**
 * 특정 백분위 밴드 조회
 *
 * @example
 * ```tsx
 * const band = getPercentileBand(data.data.percentile_bands, 50);
 * console.log(band?.projected_value);
 * ```
 *
 * @param bands - 백분위 밴드 배열
 * @param percentile - 조회할 백분위 (0-100)
 * @returns 백분위 밴드 또는 undefined
 */
export function getPercentileBand(
	bands: ForecastPercentileBand[],
	percentile: number,
): ForecastPercentileBand | undefined {
	return bands.find((band) => band.percentile === percentile);
}

/**
 * 백분위를 사람이 읽기 쉬운 형식으로 포맷
 *
 * @example
 * ```tsx
 * formatPercentile(5);   // "5th"
 * formatPercentile(50);  // "50th"
 * formatPercentile(95);  // "95th"
 * ```
 *
 * @param percentile - 백분위 (0-100)
 * @returns 포맷된 백분위 문자열
 */
export function formatPercentile(percentile: number): string {
	const suffix =
		percentile === 1
			? "st"
			: percentile === 2
				? "nd"
				: percentile === 3
					? "rd"
					: "th";
	return `${percentile}${suffix}`;
}

/**
 * 예상 포트폴리오 가치 계산 (특정 백분위)
 *
 * @example
 * ```tsx
 * const value = calculateExpectedValue(100000, 0.05);
 * console.log(value); // 105000
 * ```
 *
 * @param currentValue - 현재 포트폴리오 가치
 * @param returnPct - 예상 수익률 (비율, 0.05 = 5%)
 * @returns 예상 포트폴리오 가치
 */
export function calculateExpectedValue(
	currentValue: number,
	returnPct: number,
): number {
	return currentValue * (1 + returnPct);
}

/**
 * 시나리오별 분석 수행
 *
 * @example
 * ```tsx
 * const scenarios = analyzeScenarios(data.data);
 * scenarios.forEach(s => console.log(s.label, s.returnPct));
 * ```
 *
 * @param forecastData - 포트폴리오 예측 데이터
 * @returns 시나리오 분석 결과 배열 (Bull/Base/Bear)
 */
export function analyzeScenarios(
	forecastData: PortfolioForecastDistribution,
): ScenarioAnalysis[] {
	const { last_portfolio_value, percentile_bands } = forecastData;

	// 각 시나리오 백분위 매핑
	const scenarioMap: Array<{
		scenario: ScenarioType;
		label: string;
		percentile: number;
		color: string;
	}> = [
		{
			scenario: "bull",
			label: "강세 시나리오",
			percentile: 95,
			color: "#4caf50",
		},
		{
			scenario: "base",
			label: "기본 시나리오",
			percentile: 50,
			color: "#2196f3",
		},
		{
			scenario: "bear",
			label: "약세 시나리오",
			percentile: 5,
			color: "#f44336",
		},
	];

	return scenarioMap.map(({ scenario, label, percentile, color }) => {
		const band = getPercentileBand(percentile_bands, percentile);
		const projectedValue = band?.projected_value ?? last_portfolio_value;
		const returnPct =
			((projectedValue - last_portfolio_value) / last_portfolio_value) * 100;

		// 확률 계산 (간단한 근사)
		let probability: number;
		if (percentile === 95) {
			probability = 5; // 상위 5%
		} else if (percentile === 50) {
			probability = 50; // 중간 50%
		} else {
			probability = 5; // 하위 5%
		}

		return {
			scenario,
			label,
			percentile,
			projectedValue,
			returnPct,
			probability,
			color,
		};
	});
}

/**
 * 리스크 조정 수익률 계산 (샤프 비율 근사)
 *
 * @example
 * ```tsx
 * const sharpe = calculateRiskAdjustedReturn(10, 15, 2);
 * console.log(sharpe); // (10 - 2) / 15 = 0.53
 * ```
 *
 * @param expectedReturnPct - 예상 수익률 (%)
 * @param volatilityPct - 변동성 (%)
 * @param riskFreeRate - 무위험 수익률 (%, 기본 2%)
 * @returns 샤프 비율 (리스크 조정 수익률)
 */
export function calculateRiskAdjustedReturn(
	expectedReturnPct: number,
	volatilityPct: number,
	riskFreeRate = 2,
): number {
	if (volatilityPct === 0) return 0;
	return (expectedReturnPct - riskFreeRate) / volatilityPct;
}

/**
 * 신뢰 구간 레벨 판단
 *
 * @example
 * ```tsx
 * getConfidenceLevel(10, 5);  // "high"
 * getConfidenceLevel(5, 15);  // "low"
 * ```
 *
 * @param expectedReturnPct - 예상 수익률 (%)
 * @param volatilityPct - 변동성 (%)
 * @returns 신뢰도 레벨 ("high", "medium", "low")
 */
export function getConfidenceLevel(
	expectedReturnPct: number,
	volatilityPct: number,
): "high" | "medium" | "low" {
	const sharpe = calculateRiskAdjustedReturn(expectedReturnPct, volatilityPct);

	if (sharpe > 1) return "high";
	if (sharpe > 0.5) return "medium";
	return "low";
}

/**
 * 예측 지표 포맷팅 (퍼센트)
 *
 * @example
 * ```tsx
 * formatForecastMetric(10.5234);    // "+10.52%"
 * formatForecastMetric(-5.123);     // "-5.12%"
 * formatForecastMetric(0.123, 3);   // "+0.123%"
 * ```
 *
 * @param value - 메트릭 값 (%)
 * @param decimals - 소수점 자릿수 (기본 2)
 * @returns 포맷된 문자열
 */
export function formatForecastMetric(value: number, decimals = 2): string {
	const sign = value >= 0 ? "+" : "";
	return `${sign}${value.toFixed(decimals)}%`;
}

// ============================================================================
// Main Hook (Aggregation)
// ============================================================================

/**
 * 포트폴리오 예측 통합 Hook
 *
 * @example
 * ```tsx
 * const {
 *   forecast,
 *   scenarios,
 *   isLoading,
 *   formatMetric,
 * } = usePortfolioForecast({ horizonDays: 30 });
 *
 * if (forecast?.data) {
 *   console.log(forecast.data.expected_return_pct);
 *   scenarios.forEach(s => console.log(s.label, s.returnPct));
 * }
 * ```
 *
 * @param options - 훅 옵션 (예측 기간, 활성화 여부)
 * @returns 예측 데이터, 시나리오 분석, 헬퍼 함수
 */
export function usePortfolioForecast(options?: UsePortfolioForecastOptions) {
	const forecastQuery = usePortfolioForecastQuery(options);

	// 시나리오 분석 (데이터 있을 때만)
	const scenarios = forecastQuery.data?.data
		? analyzeScenarios(forecastQuery.data.data)
		: [];

	return {
		// Query 결과
		forecast: forecastQuery.data,
		forecastData: forecastQuery.data?.data,
		isLoading: forecastQuery.isLoading,
		isError: forecastQuery.isError,
		error: forecastQuery.error,
		refetch: forecastQuery.refetch,

		// 분석 결과
		scenarios,

		// 헬퍼 함수
		getPercentileBand: (percentile: number) =>
			forecastQuery.data?.data
				? getPercentileBand(
						forecastQuery.data.data.percentile_bands,
						percentile,
					)
				: undefined,
		formatPercentile,
		calculateExpectedValue,
		calculateRiskAdjustedReturn,
		getConfidenceLevel: () =>
			forecastQuery.data?.data
				? getConfidenceLevel(
						forecastQuery.data.data.expected_return_pct,
						forecastQuery.data.data.expected_volatility_pct,
					)
				: "low",
		formatMetric: formatForecastMetric,
	};
}
