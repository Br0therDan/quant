/**
 * useMLModel Hook
 *
 * Phase 1 Day 2-3: ML Model Management
 * - Query: List models, Get model details, Compare models
 * - Mutation: Train model, Delete model
 * - TanStack Query v5 pattern
 */

import type {
	MlCompareModelsData,
	MlDeleteModelData,
	MlGetModelInfoData,
	MlListModelsData,
	MlTrainModelData,
} from "@/client";
import { MlService } from "@/client";
import { useSnackbar } from "@/contexts/SnackbarContext";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

// ============================================================================
// Query Keys (Hierarchical)
// ============================================================================

export const mlModelQueryKeys = {
	all: ["ml-models"] as const,
	lists: () => [...mlModelQueryKeys.all, "list"] as const,
	detail: (version: string) =>
		[...mlModelQueryKeys.all, "detail", version] as const,
	comparison: (metric: string, versions?: string[]) =>
		[
			...mlModelQueryKeys.all,
			"comparison",
			metric,
			versions?.sort().join(","),
		] as const,
};

// ============================================================================
// Queries (Read Operations)
// ============================================================================

/**
 * 모든 ML 모델 목록 조회
 *
 * @returns useQuery result with model list
 *
 * @example
 * ```tsx
 * const { modelList, isLoading, error } = useMLModel();
 * ```
 */
export const useModelList = () => {
	const modelListQuery = useQuery({
		queryKey: mlModelQueryKeys.lists(),
		queryFn: async () => {
			const response = await MlService.listModels();
			return response.data;
		},
		staleTime: 1000 * 60 * 5, // 5분 (모델 목록은 자주 변경되지 않음)
		gcTime: 1000 * 60 * 10, // 10분 (구 cacheTime)
	});

	return {
		modelList: modelListQuery.data,
		isLoading: modelListQuery.isLoading,
		error: modelListQuery.error,
		refetch: modelListQuery.refetch,
	};
};

/**
 * 특정 버전의 ML 모델 상세 정보 조회
 *
 * @param version - Model version (e.g., "v1", "v2")
 * @param enabled - Query enabled flag (default: true if version exists)
 * @returns useQuery result with model details
 *
 * @example
 * ```tsx
 * const { modelDetail } = useModelDetail("v1");
 * ```
 */
export const useModelDetail = (version?: string, enabled = true) => {
	const modelDetailQuery = useQuery({
		queryKey: mlModelQueryKeys.detail(version || ""),
		queryFn: async () => {
			if (!version) throw new Error("Version is required");
			const response = await MlService.getModelInfo({ path: { version } });
			return response.data;
		},
		enabled: !!version && enabled,
		staleTime: 1000 * 60 * 10, // 10분 (모델 상세는 변경되지 않음)
		gcTime: 1000 * 60 * 20, // 20분
	});

	return {
		modelDetail: modelDetailQuery.data,
		isLoading: modelDetailQuery.isLoading,
		error: modelDetailQuery.error,
		refetch: modelDetailQuery.refetch,
	};
};

/**
 * 여러 모델 버전을 특정 지표로 비교
 *
 * @param metric - Comparison metric (accuracy, precision, recall, f1_score)
 * @param versions - Model versions to compare (optional, compares all if omitted)
 * @param enabled - Query enabled flag
 * @returns useQuery result with comparison data
 *
 * @example
 * ```tsx
 * const { comparison } = useModelComparison("accuracy", ["v1", "v2", "v3"]);
 * ```
 */
export const useModelComparison = (
	metric: string,
	versions?: string[],
	enabled = true,
) => {
	const comparisonQuery = useQuery({
		queryKey: mlModelQueryKeys.comparison(metric, versions),
		queryFn: async () => {
			const response = await MlService.compareModels({
				path: { metric },
				query: versions ? { versions: versions.join(",") } : undefined,
			});
			return response.data;
		},
		enabled: !!metric && enabled,
		staleTime: 1000 * 60 * 5, // 5분
		gcTime: 1000 * 60 * 10, // 10분
	});

	return {
		comparison: comparisonQuery.data,
		isLoading: comparisonQuery.isLoading,
		error: comparisonQuery.error,
		refetch: comparisonQuery.refetch,
	};
};

// ============================================================================
// Mutations (Write Operations)
// ============================================================================

/**
 * 새로운 ML 모델 학습
 *
 * @returns useMutation result
 *
 * @example
 * ```tsx
 * const { trainModel, isTraining } = useTrainModel();
 *
 * await trainModel.mutateAsync({
 *   body: {
 *     symbols: ["AAPL", "MSFT"],
 *     lookback_days: 500,
 *     test_size: 0.2,
 *     num_boost_round: 100,
 *   }
 * });
 * ```
 */
export const useTrainModel = () => {
	const queryClient = useQueryClient();
	const { showSuccess, showError } = useSnackbar();

	const trainModelMutation = useMutation({
		mutationFn: async (data: MlTrainModelData) => {
			const response = await MlService.trainModel(data);
			return response.data;
		},
		onSuccess: (data) => {
			// Invalidate model list to show new model
			queryClient.invalidateQueries({ queryKey: mlModelQueryKeys.lists() });
			if (data) {
				showSuccess(
					`모델 학습이 시작되었습니다. ${data.message || "백그라운드에서 처리 중입니다."}`,
				);
			} else {
				showSuccess("모델 학습이 시작되었습니다.");
			}
		},
		onError: (error: Error) => {
			showError(`모델 학습 실패: ${error.message}`);
		},
	});

	return {
		trainModel: trainModelMutation,
		isTraining: trainModelMutation.isPending,
		error: trainModelMutation.error,
	};
};

/**
 * ML 모델 삭제
 *
 * @returns useMutation result
 *
 * @example
 * ```tsx
 * const { deleteModel } = useDeleteModel();
 *
 * await deleteModel.mutateAsync({ path: { version: "v1" } });
 * ```
 */
export const useDeleteModel = () => {
	const queryClient = useQueryClient();
	const { showSuccess, showError } = useSnackbar();

	const deleteModelMutation = useMutation({
		mutationFn: async (data: MlDeleteModelData) => {
			const response = await MlService.deleteModel(data);
			return response.data;
		},
		onSuccess: (_, variables) => {
			// Invalidate model list and specific detail
			queryClient.invalidateQueries({ queryKey: mlModelQueryKeys.lists() });
			queryClient.invalidateQueries({
				queryKey: mlModelQueryKeys.detail(variables.path.version),
			});
			showSuccess(`모델 "${variables.path.version}"이(가) 삭제되었습니다.`);
		},
		onError: (error: Error) => {
			showError(`모델 삭제 실패: ${error.message}`);
		},
	});

	return {
		deleteModel: deleteModelMutation,
		isDeleting: deleteModelMutation.isPending,
		error: deleteModelMutation.error,
	};
};

// ============================================================================
// Combined Hook (All-in-One Interface)
// ============================================================================

/**
 * 통합 ML 모델 관리 훅
 *
 * @returns All ML model operations in one object
 *
 * @example
 * ```tsx
 * const {
 *   modelList,
 *   trainModel,
 *   deleteModel,
 *   isLoading,
 * } = useMLModel();
 * ```
 */
export const useMLModel = () => {
	const {
		modelList,
		isLoading: isListLoading,
		error: listError,
	} = useModelList();
	const { trainModel, isTraining } = useTrainModel();
	const { deleteModel, isDeleting } = useDeleteModel();

	return {
		// Queries
		modelList,
		isLoading: isListLoading,
		error: listError,

		// Mutations
		trainModel,
		deleteModel,

		// Loading states
		isTraining,
		isDeleting,
	};
};

// ============================================================================
// Type Exports for External Use
// ============================================================================

export type {
	MlCompareModelsData,
	MlDeleteModelData,
	MlGetModelInfoData,
	MlListModelsData,
	MlTrainModelData,
};
