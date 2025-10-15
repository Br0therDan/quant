/**
 * Feature Store Management Hook
 *
 * Manages feature engineering data, versions, and datasets for MLOps platform.
 * Provides CRUD operations for features and dataset exploration capabilities.
 *
 * @module hooks/useFeatureStore
 */

import { useSnackbar } from "@/contexts/SnackbarContext";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

// ============================================================================
// Types (temporary - will be replaced by generated client types)
// ============================================================================

export interface Feature {
	id: string;
	name: string;
	type: "numerical" | "categorical" | "binary" | "text" | "datetime";
	description: string;
	tags: string[];
	created_by: string;
	created_at: string;
	updated_at: string;
	usage_count: number;
	version: number;
}

export interface FeatureDetail extends Feature {
	statistics: {
		mean?: number;
		median?: number;
		std?: number;
		min?: number;
		max?: number;
		missing_ratio?: number;
		unique_count?: number;
		distribution?: { value: string | number; count: number }[];
	};
	source_dataset: string;
	transformation_code: string;
	dependencies: string[];
}

export interface FeatureVersion {
	id: string;
	version: number;
	feature_id: string;
	description: string;
	changes: string;
	created_by: string;
	created_at: string;
	transformation_code: string;
}

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

export interface FeatureCreate {
	name: string;
	type: Feature["type"];
	description: string;
	tags: string[];
	source_dataset: string;
	transformation_code: string;
}

export interface FeatureUpdate {
	description?: string;
	tags?: string[];
	transformation_code?: string;
}

export interface FeaturesQueryParams {
	type?: Feature["type"];
	tags?: string[];
	search?: string;
	sort_by?: "name" | "created_at" | "usage_count";
	sort_order?: "asc" | "desc";
	page?: number;
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
			// TODO: Replace with actual API call after pnpm gen:client
			// const response = await FeatureStoreService.getFeatures({ query: params });
			// return response.data;

			// Mock data for now
			await new Promise((resolve) => setTimeout(resolve, 500));
			return {
				features: [],
				total: 0,
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
			// TODO: Replace with actual API call
			// const response = await FeatureStoreService.createFeature({ body: data });
			// return response.data;

			await new Promise((resolve) => setTimeout(resolve, 1000));
			return {
				id: `feature_${Date.now()}`,
				name: data.name,
				type: data.type,
				description: data.description,
				tags: data.tags,
				created_by: "current_user",
				created_at: new Date().toISOString(),
				updated_at: new Date().toISOString(),
				usage_count: 0,
				version: 1,
			};
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
			featureId,
			data,
		}: {
			featureId: string;
			data: FeatureUpdate;
		}): Promise<Feature> => {
			// TODO: Replace with actual API call
			// const response = await FeatureStoreService.updateFeature({
			//   path: { feature_id: featureId },
			//   body: data
			// });
			// return response.data;

			await new Promise((resolve) => setTimeout(resolve, 1000));
			return {
				id: featureId,
				name: "Updated Feature",
				type: "numerical",
				description: data.description || "",
				tags: data.tags || [],
				created_by: "current_user",
				created_at: new Date().toISOString(),
				updated_at: new Date().toISOString(),
				usage_count: 0,
				version: 2,
			};
		},
		onSuccess: (_, variables) => {
			queryClient.invalidateQueries({
				queryKey: featureStoreQueryKeys.features(),
			});
			queryClient.invalidateQueries({
				queryKey: featureStoreQueryKeys.featureDetail(variables.featureId),
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
		mutationFn: async (_featureId: string): Promise<void> => {
			// TODO: Replace with actual API call
			// await FeatureStoreService.deleteFeature({ path: { feature_id: featureId } });

			await new Promise((resolve) => setTimeout(resolve, 1000));
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

		updateFeature: (featureId: string, data: FeatureUpdate) =>
			updateFeatureMutation.mutateAsync({ featureId, data }),
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
export const useFeatureDetail = (featureId: string | null) => {
	const featureDetailQuery = useQuery({
		queryKey: featureStoreQueryKeys.featureDetail(featureId || ""),
		queryFn: async (): Promise<FeatureDetail> => {
			// TODO: Replace with actual API call
			// const response = await FeatureStoreService.getFeature({
			//   path: { feature_id: featureId! }
			// });
			// return response.data;

			await new Promise((resolve) => setTimeout(resolve, 500));
			return {
				id: featureId || "",
				name: "Sample Feature",
				type: "numerical",
				description: "Sample feature description",
				tags: ["technical", "price"],
				created_by: "user123",
				created_at: new Date().toISOString(),
				updated_at: new Date().toISOString(),
				usage_count: 10,
				version: 1,
				statistics: {
					mean: 50.5,
					median: 48.2,
					std: 12.3,
					min: 10.0,
					max: 100.0,
					missing_ratio: 0.05,
					unique_count: 85,
				},
				source_dataset: "dataset_123",
				transformation_code:
					"df['new_feature'] = df['price'].rolling(20).mean()",
				dependencies: ["price"],
			};
		},
		enabled: !!featureId,
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
export const useFeatureVersions = (featureId: string | null) => {
	const versionsQuery = useQuery({
		queryKey: featureStoreQueryKeys.versions(featureId || ""),
		queryFn: async (): Promise<FeatureVersion[]> => {
			// TODO: Replace with actual API call
			// const response = await FeatureStoreService.getFeatureVersions({
			//   path: { feature_id: featureId! }
			// });
			// return response.data;

			await new Promise((resolve) => setTimeout(resolve, 500));
			return [];
		},
		enabled: !!featureId,
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
