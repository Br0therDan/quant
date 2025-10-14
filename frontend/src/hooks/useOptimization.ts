import { BacktestService } from "@/client";
import type {
	OptimizationProgress,
	OptimizationRequest,
	OptimizationResponse,
	StudyListResponse,
} from "@/client/types.gen";
import { useSnackbar } from "@/contexts/SnackbarContext";
import {
	useMutation,
	useQuery,
	useQueryClient,
	type UseMutateFunction,
} from "@tanstack/react-query";
import { useMemo } from "react";

// Query Keys for Optimization
export const optimizationQueryKeys = {
	all: ["optimization"] as const,
	studies: () => [...optimizationQueryKeys.all, "studies"] as const,
	study: (studyName: string) =>
		[...optimizationQueryKeys.studies(), studyName] as const,
	progress: (studyName: string) =>
		[...optimizationQueryKeys.study(studyName), "progress"] as const,
	result: (studyName: string) =>
		[...optimizationQueryKeys.study(studyName), "result"] as const,
} as const;

// Mutation Function Types
type CreateOptimizationFn = UseMutateFunction<
	Awaited<ReturnType<typeof BacktestService.createOptimizationStudy>>["data"],
	unknown,
	OptimizationRequest,
	unknown
>;

/**
 * useOptimization Hook
 *
 * Provides optimization study management functionality:
 * - List optimization studies with filters
 * - Create and start new optimization studies
 * - Track optimization status
 *
 * @example
 * ```tsx
 * const {
 *   studies,
 *   isLoading,
 *   createOptimization,
 *   isOptimizing,
 * } = useOptimization();
 *
 * // Create optimization study
 * createOptimization({
 *   strategy_name: "MyStrategy",
 *   symbol: "AAPL",
 *   param_space: {
 *     rsi_period: [10, 30],
 *     threshold: [0.01, 0.05],
 *   },
 *   n_trials: 100,
 * });
 * ```
 */
export function useOptimization() {
	const queryClient = useQueryClient();
	const { showSuccess, showError } = useSnackbar();

	// Query: List optimization studies
	const studiesQuery = useQuery({
		queryKey: optimizationQueryKeys.studies(),
		queryFn: async () => {
			const response = await BacktestService.listOptimizationStudies({
				query: {
					symbol: undefined,
					strategy_name: undefined,
					status: undefined,
					limit: 100,
				},
			});
			return response.data as StudyListResponse;
		},
		staleTime: 1000 * 60 * 5, // 5 minutes
		gcTime: 30 * 60 * 1000, // 30 minutes
	});

	// Mutation: Create optimization study
	const createOptimizationMutation = useMutation({
		mutationFn: async (config: OptimizationRequest) => {
			const response = await BacktestService.createOptimizationStudy({
				body: config,
			});
			return response.data as OptimizationResponse;
		},
		onSuccess: (data) => {
			queryClient.invalidateQueries({
				queryKey: optimizationQueryKeys.studies(),
			});
			showSuccess(
				`최적화 스터디 "${data.study_name || "새 스터디"}"가 시작되었습니다`,
			);
		},
		onError: (error) => {
			console.error("최적화 시작 실패:", error);
			showError(
				error instanceof Error ? error.message : "최적화 시작에 실패했습니다",
			);
		},
	});

	return useMemo(
		() => ({
			// Data
			studies: studiesQuery.data,

			// Loading States
			isLoading: studiesQuery.isLoading,
			isOptimizing: createOptimizationMutation.isPending,

			// Errors
			error: studiesQuery.error,

			// Actions
			createOptimization:
				createOptimizationMutation.mutate as CreateOptimizationFn,
			createOptimizationAsync: createOptimizationMutation.mutateAsync,

			// Refetch
			refetch: studiesQuery.refetch,
		}),
		[studiesQuery, createOptimizationMutation],
	);
}

/**
 * useOptimizationStudy Hook
 *
 * Provides individual optimization study tracking with real-time progress updates.
 *
 * @param studyName - Study identifier
 * @param options - Configuration options
 * @param options.pollInterval - Poll interval in milliseconds (default: 5000)
 * @param options.enabled - Whether to enable queries (default: true)
 *
 * @example
 * ```tsx
 * const {
 *   progress,
 *   result,
 *   progressPercent,
 *   isCompleted,
 * } = useOptimizationStudy("study_123", {
 *   pollInterval: 5000, // Poll every 5 seconds
 * });
 *
 * if (isCompleted) {
 *   console.log("Best params:", result.best_params);
 *   console.log("Best value:", result.best_value);
 * }
 * ```
 */
export function useOptimizationStudy(
	studyName: string,
	options?: {
		pollInterval?: number;
		enabled?: boolean;
	},
) {
	const enabled = options?.enabled ?? true;
	const pollInterval = options?.pollInterval ?? 5000; // 5 seconds default

	// Query: Get optimization progress (with polling)
	const progressQuery = useQuery({
		queryKey: optimizationQueryKeys.progress(studyName),
		queryFn: async () => {
			const response = await BacktestService.getOptimizationProgress({
				path: { study_name: studyName },
			});
			return response.data as OptimizationResponse;
		},
		enabled: enabled && !!studyName,
		staleTime: 1000 * 5, // 5 seconds (fast refresh for progress)
		gcTime: 30 * 60 * 1000, // 30 minutes
		refetchInterval: (query) => {
			// Stop polling if status is completed or failed
			const status = query.state.data?.status;
			if (status === "completed" || status === "failed") {
				return false;
			}
			return pollInterval;
		},
	});

	// Query: Get optimization result (only if completed)
	const resultQuery = useQuery({
		queryKey: optimizationQueryKeys.result(studyName),
		queryFn: async () => {
			const response = await BacktestService.getOptimizationResult({
				path: { study_name: studyName },
			});
			return response.data as OptimizationResponse;
		},
		enabled:
			enabled && !!studyName && progressQuery.data?.status === "completed",
		staleTime: 1000 * 60 * 5, // 5 minutes
		gcTime: 30 * 60 * 1000, // 30 minutes
	});

	// Calculate progress percentage
	const progressPercent = useMemo(() => {
		const data = progressQuery.data?.data as OptimizationProgress | undefined;
		if (!data) return 0;
		const { n_trials, trials_completed } = data;
		if (!n_trials || !trials_completed) return 0;
		return Math.round((trials_completed / n_trials) * 100);
	}, [progressQuery.data]);

	// Check if completed
	const isCompleted = useMemo(() => {
		const data = progressQuery.data?.data as OptimizationProgress | undefined;
		return data?.status === "completed";
	}, [progressQuery.data]);

	// Check if failed
	const isFailed = useMemo(() => {
		const data = progressQuery.data?.data as OptimizationProgress | undefined;
		return data?.status === "failed";
	}, [progressQuery.data]);

	// Check if running
	const isRunning = useMemo(() => {
		const data = progressQuery.data?.data as OptimizationProgress | undefined;
		return data?.status === "running";
	}, [progressQuery.data]);

	return useMemo(
		() => ({
			// Data
			progress: progressQuery.data,
			result: resultQuery.data,

			// Computed States
			progressPercent,
			isCompleted,
			isFailed,
			isRunning,

			// Loading States
			isLoading: progressQuery.isLoading,
			isLoadingResult: resultQuery.isLoading,

			// Errors
			error: progressQuery.error || resultQuery.error,

			// Refetch
			refetch: {
				progress: progressQuery.refetch,
				result: resultQuery.refetch,
			},
		}),
		[
			progressQuery,
			resultQuery,
			progressPercent,
			isCompleted,
			isFailed,
			isRunning,
		],
	);
}

/**
 * useOptimizationStudies Hook (with filters)
 *
 * Provides filtered optimization study list.
 *
 * @param filters - Filter options
 *
 * @example
 * ```tsx
 * const { studies, isLoading } = useOptimizationStudies({
 *   symbol: "AAPL",
 *   status: "completed",
 * });
 * ```
 */
export function useOptimizationStudies(filters?: {
	symbol?: string;
	strategy_name?: string;
	status?: string;
	limit?: number;
}) {
	return useQuery({
		queryKey: [
			...optimizationQueryKeys.studies(),
			"filtered",
			filters?.symbol,
			filters?.strategy_name,
			filters?.status,
			filters?.limit,
		],
		queryFn: async () => {
			const response = await BacktestService.listOptimizationStudies({
				query: {
					symbol: filters?.symbol,
					strategy_name: filters?.strategy_name,
					status: filters?.status,
					limit: filters?.limit || 100,
				},
			});
			return response.data as StudyListResponse;
		},
		staleTime: 1000 * 60 * 5, // 5 minutes
		gcTime: 30 * 60 * 1000, // 30 minutes
	});
}
