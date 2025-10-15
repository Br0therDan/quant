/**
 * Feature Store Management Hook
 *
 * Manages feature engineering data, versions, and datasets for MLOps platform.
 * Provides CRUD operations for features and dataset exploration capabilities.
 *
 * @module hooks/useFeatureStore
 */

import type {
	DataType,
	FeatureCreate,
	FeatureLineageResponse,
	FeatureResponse,
	FeatureStatisticsResponse,
	FeatureStatus,
	FeatureType,
	FeatureUpdate,
	FeatureUsageCreate,
	FeatureVersionCreate,
	FeatureVersionResponse,
} from "@/client";
import { FeatureStoreService } from "@/client";
import { useSnackbar } from "@/contexts/SnackbarContext";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

// ============================================================================
// Types (using backend-generated types)
// ============================================================================

export type Feature = FeatureResponse;
export type FeatureDetail = FeatureResponse; // Backend provides full detail
export type FeatureVersion = FeatureVersionResponse;
export type FeatureLineage = FeatureLineageResponse;
export type FeatureStatistics = FeatureStatisticsResponse;

// Create/Update DTOs
export type FeatureCreateDTO = FeatureCreate;
export type FeatureUpdateDTO = FeatureUpdate;
export type FeatureVersionCreateDTO = FeatureVersionCreate;
export type FeatureUsageDTO = FeatureUsageCreate;

// Re-export enums for convenience
export type { DataType, FeatureStatus, FeatureType };

// Dataset interface (if not in backend types, keep custom)
export interface Dataset {
	id: string;
	name: string;
	description: string;
	features: string[];
	row_count: number;
	created_at: string;
	updated_at: string;
	sample_data?: Record<string, unknown>[];
	correlation_matrix?: {
		feature1: string;
		feature2: string;
		correlation: number;
	}[];
}

// Query parameters (frontend-specific)
export interface FeaturesQueryParams {
	feature_type?: FeatureType;
	status?: FeatureStatus;
	owner?: string;
	tags?: string[];
	search?: string;
	sort_by?: "feature_name" | "created_at" | "usage_count";
	sort_order?: "asc" | "desc";
	skip?: number;
	limit?: number;
}

// ============================================================================
// Query Keys
// ============================================================================

export const featureStoreQueryKeys = {
	all: ["featureStore"] as const,
	features: () => [...featureStoreQueryKeys.all, "features"] as const,
	featuresList: (params?: FeaturesQueryParams) =>
		[...featureStoreQueryKeys.features(), "list", params] as const,
	featureDetail: (featureId: string) =>
		[...featureStoreQueryKeys.features(), "detail", featureId] as const,
	versions: (featureId: string) =>
		[...featureStoreQueryKeys.all, "versions", featureId] as const,
	datasets: () => [...featureStoreQueryKeys.all, "datasets"] as const,
	datasetDetail: (datasetId: string) =>
		[...featureStoreQueryKeys.datasets(), "detail", datasetId] as const,
};

// ============================================================================
// Hook Implementation
// ============================================================================

export const useFeatureStore = (params?: FeaturesQueryParams) => {
	const queryClient = useQueryClient();
	const { showSuccess, showError } = useSnackbar();

	// ============================================================================
	// Queries
	// ============================================================================

	/**
	 * Query: Feature List
	 * Fetches paginated list of features with optional filtering
	 */
	const featuresQuery = useQuery({
		queryKey: featureStoreQueryKeys.featuresList(params),
		queryFn: async (): Promise<{ features: Feature[]; total: number }> => {
			const response = await FeatureStoreService.listFeatures({
				query: {
					owner: params?.owner,
					feature_type: params?.feature_type,
					status: params?.status,
					tags: params?.tags?.join(","),
					skip: params?.skip,
					limit: params?.limit,
				},
			});
			if (!response.data) {
				return { features: [], total: 0 };
			}
			return {
				features: response.data.features,
				total: response.data.total,
			};
		},
		staleTime: 1000 * 60 * 5, // 5 minutes
	});

	/**
	 * Query: Datasets List
	 * Fetches list of available datasets
	 */
	const datasetsQuery = useQuery({
		queryKey: featureStoreQueryKeys.datasets(),
		queryFn: async (): Promise<Dataset[]> => {
			// TODO: Replace with actual API call
			// const response = await FeatureStoreService.getDatasets();
			// return response.data;

			await new Promise((resolve) => setTimeout(resolve, 500));
			return [];
		},
		staleTime: 1000 * 60 * 10, // 10 minutes
	});

	// ============================================================================
	// Mutations
	// ============================================================================

	/**
	 * Mutation: Create Feature
	 * Creates a new feature in the store
	 */
	const createFeatureMutation = useMutation({
		mutationFn: async (data: FeatureCreate): Promise<Feature> => {
			const response = await FeatureStoreService.createFeature({
				body: data,
			});
			if (!response.data) {
				throw new Error("Feature creation failed");
			}
			return response.data;
		},
		onSuccess: () => {
			queryClient.invalidateQueries({
				queryKey: featureStoreQueryKeys.features(),
			});
			showSuccess("피처가 성공적으로 생성되었습니다");
		},
		onError: (error: Error) => {
			showError(`피처 생성 실패: ${error.message}`);
		},
	});

	/**
	 * Mutation: Update Feature
	 * Updates an existing feature
	 */
	const updateFeatureMutation = useMutation({
		mutationFn: async ({
			feature_name,
			data,
		}: {
			feature_name: string;
			data: FeatureUpdate;
		}): Promise<Feature> => {
			const response = await FeatureStoreService.updateFeature({
				path: { feature_name },
				body: data,
			});
			if (!response.data) {
				throw new Error("Feature update failed");
			}
			return response.data;
		},
		onSuccess: (_, variables) => {
			queryClient.invalidateQueries({
				queryKey: featureStoreQueryKeys.features(),
			});
			queryClient.invalidateQueries({
				queryKey: featureStoreQueryKeys.featureDetail(variables.feature_name),
			});
			showSuccess("피처가 성공적으로 업데이트되었습니다");
		},
		onError: (error: Error) => {
			showError(`피처 업데이트 실패: ${error.message}`);
		},
	});

	/**
	 * Mutation: Delete Feature
	 * Deletes a feature from the store
	 */
	const deleteFeatureMutation = useMutation({
		mutationFn: async (feature_name: string): Promise<void> => {
			await FeatureStoreService.deleteFeature({
				path: { feature_name },
			});
		},
		onSuccess: () => {
			queryClient.invalidateQueries({
				queryKey: featureStoreQueryKeys.features(),
			});
			showSuccess("피처가 성공적으로 삭제되었습니다");
		},
		onError: (error: Error) => {
			showError(`피처 삭제 실패: ${error.message}`);
		},
	});

	// ============================================================================
	// Return Hook Interface
	// ============================================================================

	return {
		// Queries
		featuresList: featuresQuery.data?.features || [],
		featuresTotal: featuresQuery.data?.total || 0,
		isLoadingFeatures: featuresQuery.isLoading,
		isFetchingFeatures: featuresQuery.isFetching,
		featuresError: featuresQuery.error,

		datasetsList: datasetsQuery.data || [],
		isLoadingDatasets: datasetsQuery.isLoading,
		datasetsError: datasetsQuery.error,

		// Mutations
		createFeature: createFeatureMutation.mutateAsync,
		isCreatingFeature: createFeatureMutation.isPending,

		updateFeature: (feature_name: string, data: FeatureUpdate) =>
			updateFeatureMutation.mutateAsync({ feature_name, data }),
		isUpdatingFeature: updateFeatureMutation.isPending,

		deleteFeature: deleteFeatureMutation.mutateAsync,
		isDeletingFeature: deleteFeatureMutation.isPending,

		// Refetch functions
		refetchFeatures: featuresQuery.refetch,
		refetchDatasets: datasetsQuery.refetch,
	};
};

// ============================================================================
// Additional Hooks for Detail Views
// ============================================================================

/**
 * Hook: Feature Detail
 * Fetches detailed information for a specific feature
 */
export const useFeatureDetail = (feature_name: string | null) => {
	const featureDetailQuery = useQuery({
		queryKey: featureStoreQueryKeys.featureDetail(feature_name || ""),
		queryFn: async (): Promise<FeatureDetail> => {
			if (!feature_name) {
				throw new Error("Feature name is required");
			}
			const response = await FeatureStoreService.getFeature({
				path: { feature_name },
			});
			if (!response.data) {
				throw new Error("Feature not found");
			}
			return response.data;
		},
		enabled: !!feature_name,
		staleTime: 1000 * 60 * 5,
	});

	return {
		featureDetail: featureDetailQuery.data,
		isLoading: featureDetailQuery.isLoading,
		error: featureDetailQuery.error,
		refetch: featureDetailQuery.refetch,
	};
};

/**
 * Hook: Feature Versions
 * Fetches version history for a specific feature
 */
export const useFeatureVersions = (feature_name: string | null) => {
	const versionsQuery = useQuery({
		queryKey: featureStoreQueryKeys.versions(feature_name || ""),
		queryFn: async (): Promise<FeatureVersion[]> => {
			if (!feature_name) {
				return [];
			}
			const response = await FeatureStoreService.getFeatureVersions({
				path: { feature_name },
			});
			return response.data?.versions ?? [];
		},
		enabled: !!feature_name,
		staleTime: 1000 * 60 * 10,
	});

	return {
		versions: versionsQuery.data || [],
		isLoading: versionsQuery.isLoading,
		error: versionsQuery.error,
		refetch: versionsQuery.refetch,
	};
};

/**
 * Hook: Dataset Detail
 * Fetches detailed information for a specific dataset
 */
export const useDatasetDetail = (datasetId: string | null) => {
	const datasetDetailQuery = useQuery({
		queryKey: featureStoreQueryKeys.datasetDetail(datasetId || ""),
		queryFn: async (): Promise<Dataset> => {
			// TODO: Replace with actual API call
			// const response = await FeatureStoreService.getDataset({
			//   path: { dataset_id: datasetId! }
			// });
			// return response.data;

			await new Promise((resolve) => setTimeout(resolve, 500));
			return {
				id: datasetId || "",
				name: "Sample Dataset",
				description: "Sample dataset description",
				features: ["feature1", "feature2", "feature3"],
				row_count: 10000,
				created_at: new Date().toISOString(),
				updated_at: new Date().toISOString(),
				sample_data: [],
				correlation_matrix: [],
			};
		},
		enabled: !!datasetId,
		staleTime: 1000 * 60 * 10,
	});

	return {
		dataset: datasetDetailQuery.data,
		isLoading: datasetDetailQuery.isLoading,
		error: datasetDetailQuery.error,
		refetch: datasetDetailQuery.refetch,
	};
};
