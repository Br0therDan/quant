/**
 * useRegimeDetection Hook
 *
 * 시장 국면 감지 API를 TanStack Query v5로 래핑한 커스텀 훅
 *
 * **주요 기능**:
 * - 현재 시장 국면 조회 (bullish, bearish, volatile, sideways)
 * - 국면 신뢰도 및 확률 분포 제공
 * - 국면별 정량 지표 (수익률, 변동성, 낙폭, 모멘텀)
 * - 자동 캐싱 및 stale 관리 (5분 TTL)
 * - 수동 새로고침 지원 (refresh 파라미터)
 *
 * **사용 예시**:
 * ```tsx
 * const { currentRegime, isLoading, refresh } = useRegimeDetection("AAPL");
 *
 * if (currentRegime) {
 *   console.log(currentRegime.regime); // "bullish"
 *   console.log(currentRegime.confidence); // 0.85
 * }
 *
 * // 수동 새로고침
 * await refresh.mutateAsync();
 * ```
 *
 * @module hooks/useRegimeDetection
 */

import type {
	MarketRegimeResponse,
	MarketRegimeSnapshot,
	MarketRegimeType,
	RegimeMetrics,
} from "@/client";
import { MarketDataService } from "@/client";
import { useSnackbar } from "@/contexts/SnackbarContext";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

// ============================================================================
// Query Keys (Hierarchical Structure)
// ============================================================================

/**
 * TanStack Query v5 쿼리 키 팩토리
 *
 * **계층 구조**:
 * - `["regime"]`: 모든 국면 쿼리
 * - `["regime", "current", symbol]`: 특정 심볼 현재 국면
 * - `["regime", "current", symbol, lookback]`: 특정 심볼 + Lookback
 */
export const regimeQueryKeys = {
	all: ["regime"] as const,
	current: (symbol: string) =>
		[...regimeQueryKeys.all, "current", symbol] as const,
	currentWithLookback: (symbol: string, lookbackDays: number) =>
		[...regimeQueryKeys.all, "current", symbol, lookbackDays] as const,
};

// ============================================================================
// Hook: useCurrentRegime (현재 시장 국면 조회)
// ============================================================================

/**
 * useCurrentRegime 파라미터
 */
export interface UseCurrentRegimeParams {
	/** 심볼 (예: "AAPL", "TSLA") */
	symbol: string;
	/** Lookback 기간 (일수, 기본값: 60) */
	lookbackDays?: number;
	/** 쿼리 자동 실행 여부 (기본값: true) */
	enabled?: boolean;
}

/**
 * 현재 시장 국면을 조회하는 Query Hook
 *
 * **기능**:
 * - 최신 국면 스냅샷 조회 (regime, confidence, probabilities, metrics)
 * - 자동 캐싱 (5분 staleTime)
 * - 에러 처리 (Snackbar)
 *
 * **반환값**:
 * - `currentRegime`: 국면 스냅샷 (MarketRegimeSnapshot | null)
 * - `isLoading`: 로딩 상태
 * - `error`: 에러 객체
 * - `refetch`: 수동 재조회 함수
 *
 * @param params - 조회 파라미터 (symbol, lookbackDays, enabled)
 * @returns TanStack Query 결과 객체 + 추가 헬퍼
 */
export const useCurrentRegime = ({
	symbol,
	lookbackDays = 60,
	enabled = true,
}: UseCurrentRegimeParams) => {
	const { showError } = useSnackbar();

	const query = useQuery({
		queryKey: regimeQueryKeys.currentWithLookback(symbol, lookbackDays),
		queryFn: async () => {
			const response = await MarketDataService.getMarketRegime({
				query: { symbol, lookback_days: lookbackDays },
			});
			return response.data as MarketRegimeResponse;
		},
		enabled: enabled && !!symbol,
		staleTime: 1000 * 60 * 5, // 5분
		gcTime: 1000 * 60 * 10, // 10분 (구 cacheTime)
		retry: 2,
		retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
	});

	// 에러 처리
	if (query.error) {
		showError(`국면 감지 실패: ${query.error.message}`);
	}

	return {
		currentRegime: query.data?.data ?? null,
		isLoading: query.isLoading,
		error: query.error,
		refetch: query.refetch,
		queryKey: regimeQueryKeys.currentWithLookback(symbol, lookbackDays),
	};
};

// ============================================================================
// Hook: useRefreshRegime (수동 새로고침)
// ============================================================================

/**
 * useRefreshRegime 파라미터
 */
export interface UseRefreshRegimeParams {
	/** 심볼 (예: "AAPL") */
	symbol: string;
	/** Lookback 기간 (일수, 기본값: 60) */
	lookbackDays?: number;
}

/**
 * 시장 국면을 수동으로 새로고침하는 Mutation Hook
 *
 * **기능**:
 * - refresh=true 파라미터로 강제 재계산
 * - 성공 시 쿼리 무효화 (자동 재조회)
 * - Snackbar 피드백
 *
 * **사용 예시**:
 * ```tsx
 * const refresh = useRefreshRegime({ symbol: "AAPL" });
 * await refresh.mutateAsync();
 * ```
 *
 * @param params - 새로고침 파라미터 (symbol, lookbackDays)
 * @returns TanStack Mutation 객체
 */
export const useRefreshRegime = ({
	symbol,
	lookbackDays = 60,
}: UseRefreshRegimeParams) => {
	const queryClient = useQueryClient();
	const { showSuccess, showError } = useSnackbar();

	return useMutation({
		mutationFn: async () => {
			const response = await MarketDataService.getMarketRegime({
				query: { symbol, refresh: true, lookback_days: lookbackDays },
			});
			return response.data as MarketRegimeResponse;
		},
		onSuccess: () => {
			// 모든 국면 쿼리 무효화 (자동 재조회)
			queryClient.invalidateQueries({
				queryKey: regimeQueryKeys.all,
			});
			showSuccess("시장 국면이 갱신되었습니다");
		},
		onError: (error: Error) => {
			showError(`국면 갱신 실패: ${error.message}`);
		},
	});
};

// ============================================================================
// Main Hook: useRegimeDetection (통합 인터페이스)
// ============================================================================

/**
 * useRegimeDetection 파라미터
 */
export interface UseRegimeDetectionParams {
	/** 심볼 (예: "AAPL") */
	symbol: string;
	/** Lookback 기간 (일수, 기본값: 60) */
	lookbackDays?: number;
	/** 쿼리 자동 실행 여부 (기본값: true) */
	enabled?: boolean;
}

/**
 * 시장 국면 감지 통합 Hook
 *
 * **제공 기능**:
 * - `currentRegime`: 현재 국면 스냅샷 (regime, confidence, metrics 포함)
 * - `isLoading`: 로딩 상태
 * - `refresh`: 수동 새로고침 Mutation
 * - `isRefreshing`: 새로고침 진행 중 여부
 * - `getRegimeColor`: 국면별 색상 헬퍼 함수
 * - `getRegimeLabel`: 국면별 한글 라벨 헬퍼 함수
 *
 * **사용 예시**:
 * ```tsx
 * const {
 *   currentRegime,
 *   isLoading,
 *   refresh,
 *   getRegimeColor,
 *   getRegimeLabel,
 * } = useRegimeDetection({ symbol: "AAPL" });
 *
 * return (
 *   <div>
 *     <Chip
 *       label={getRegimeLabel(currentRegime?.regime)}
 *       sx={{ bgcolor: getRegimeColor(currentRegime?.regime) }}
 *     />
 *     <Typography>신뢰도: {currentRegime?.confidence}%</Typography>
 *     <Button onClick={() => refresh.mutate()} disabled={isRefreshing}>
 *       새로고침
 *     </Button>
 *   </div>
 * );
 * ```
 *
 * @param params - 파라미터 (symbol, lookbackDays, enabled)
 * @returns 통합 API 인터페이스
 */
export const useRegimeDetection = ({
	symbol,
	lookbackDays = 60,
	enabled = true,
}: UseRegimeDetectionParams) => {
	// 현재 국면 조회
	const { currentRegime, isLoading, error, refetch, queryKey } =
		useCurrentRegime({
			symbol,
			lookbackDays,
			enabled,
		});

	// 수동 새로고침
	const refresh = useRefreshRegime({ symbol, lookbackDays });

	// ========================================
	// 헬퍼 함수: 국면별 색상
	// ========================================
	const getRegimeColor = (regime?: MarketRegimeType): string => {
		switch (regime) {
			case "bullish":
				return "#4caf50"; // Green
			case "bearish":
				return "#f44336"; // Red
			case "volatile":
				return "#ff9800"; // Orange
			case "sideways":
				return "#9e9e9e"; // Gray
			default:
				return "#e0e0e0"; // Light Gray
		}
	};

	// ========================================
	// 헬퍼 함수: 국면별 한글 라벨
	// ========================================
	const getRegimeLabel = (regime?: MarketRegimeType): string => {
		switch (regime) {
			case "bullish":
				return "상승장";
			case "bearish":
				return "하락장";
			case "volatile":
				return "변동장";
			case "sideways":
				return "횡보장";
			default:
				return "알 수 없음";
		}
	};

	// ========================================
	// 헬퍼 함수: 신뢰도 퍼센트 포맷
	// ========================================
	const formatConfidence = (confidence?: number): string => {
		if (confidence === undefined) return "N/A";
		return `${(confidence * 100).toFixed(1)}%`;
	};

	// ========================================
	// 헬퍼 함수: 메트릭 포맷
	// ========================================
	const formatMetric = (value?: number, suffix = "%"): string => {
		if (value === undefined) return "N/A";
		return `${value.toFixed(2)}${suffix}`;
	};

	return {
		// 데이터
		currentRegime,
		regime: currentRegime?.regime,
		confidence: currentRegime?.confidence,
		probabilities: currentRegime?.probabilities,
		metrics: currentRegime?.metrics,
		notes: currentRegime?.notes,

		// 상태
		isLoading,
		error,
		isRefreshing: refresh.isPending,

		// 액션
		refresh,
		refetch,

		// 헬퍼
		getRegimeColor,
		getRegimeLabel,
		formatConfidence,
		formatMetric,

		// 메타데이터
		queryKey,
	};
};

// ============================================================================
// 타입 재Export (편의성)
// ============================================================================
export type {
	MarketRegimeResponse,
	MarketRegimeSnapshot,
	MarketRegimeType,
	RegimeMetrics
};
