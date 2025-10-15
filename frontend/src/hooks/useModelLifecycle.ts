/**
 * Model Lifecycle Management Hook
 *
 * Manages ML model experiments, registry, and deployments for MLOps platform.
 * Provides experiment tracking, model versioning, and deployment pipeline management.
 *
 * @module hooks/useModelLifecycle
 */

import type {
	DeploymentCreate,
	DeploymentEnvironment,
	DeploymentResponse,
	DeploymentStatus,
	DeploymentUpdate,
	DriftEventCreate,
	DriftEventResponse,
	DriftSeverity,
	ExperimentCreate,
	ExperimentResponse,
	ExperimentStatus,
	ExperimentUpdate,
	ModelStage,
	ModelVersionCreate,
	ModelVersionResponse,
	RunCreate,
	RunResponse,
	RunStatus,
	RunUpdate,
} from "@/client";
import { ModelLifecycleService } from "@/client";
import { useSnackbar } from "@/contexts/SnackbarContext";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

// ============================================================================
// Re-export Backend Types (No local interface duplication)
// ============================================================================

// All types imported from generated backend schema
export type {
	DeploymentCreate,
	DeploymentEnvironment,
	DeploymentResponse,
	DeploymentStatus,
	DeploymentUpdate,
	DriftEventCreate,
	DriftEventResponse,
	DriftSeverity,
	ExperimentCreate,
	ExperimentResponse,
	ExperimentStatus,
	ExperimentUpdate,
	ModelStage,
	ModelVersionCreate,
	ModelVersionResponse,
	RunCreate,
	RunResponse,
	RunStatus,
	RunUpdate,
};

// Type aliases for convenience (avoid duplication, use backend types)
export type Experiment = ExperimentResponse;
export type ExperimentDetail = ExperimentResponse;
export type Run = RunResponse;
export type Model = ModelVersionResponse;
export type ModelDetail = ModelVersionResponse;
export type Deployment = DeploymentResponse;
export type DriftEvent = DriftEventResponse;

// Query parameter interfaces (frontend-specific, not in backend schema)
export interface ExperimentsQueryParams {
	status?: ExperimentStatus;
	owner?: string;
	tags?: string[];
	sort_by?: "created_at" | "name";
	sort_order?: "asc" | "desc";
	page?: number;
	limit?: number;
}

export interface ModelsQueryParams {
	stage?: ModelStage;
	experiment_id?: string;
	tags?: string[];
	sort_by?: "created_at" | "name";
	sort_order?: "asc" | "desc";
	page?: number;
	limit?: number;
}

export interface RunsQueryParams {
	experiment_id?: string;
	status?: RunStatus;
	sort_by?: "created_at" | "start_time";
	sort_order?: "asc" | "desc";
	page?: number;
	limit?: number;
} // ============================================================================
// Query Keys
// ============================================================================

export const modelLifecycleQueryKeys = {
	all: ["modelLifecycle"] as const,
	experiments: () => [...modelLifecycleQueryKeys.all, "experiments"] as const,
	experimentsList: (params?: ExperimentsQueryParams) =>
		[...modelLifecycleQueryKeys.experiments(), "list", params] as const,
	experimentDetail: (experimentId: string) =>
		[...modelLifecycleQueryKeys.experiments(), "detail", experimentId] as const,
	models: () => [...modelLifecycleQueryKeys.all, "models"] as const,
	modelsList: (params?: ModelsQueryParams) =>
		[...modelLifecycleQueryKeys.models(), "list", params] as const,
	modelDetail: (modelId: string) =>
		[...modelLifecycleQueryKeys.models(), "detail", modelId] as const,
	deployments: () => [...modelLifecycleQueryKeys.all, "deployments"] as const,
	deploymentsList: () =>
		[...modelLifecycleQueryKeys.deployments(), "list"] as const,
	deploymentDetail: (deploymentId: string) =>
		[...modelLifecycleQueryKeys.deployments(), "detail", deploymentId] as const,
};

// ============================================================================
// Hook Implementation
// ============================================================================

export const useModelLifecycle = (params?: ExperimentsQueryParams) => {
	const queryClient = useQueryClient();
	const { showSuccess, showError } = useSnackbar();

	// ============================================================================
	// Queries
	// ============================================================================

	/**
	 * Query: Experiments List
	 * Fetches paginated list of experiments with optional filtering
	 */
	const experimentsQuery = useQuery({
		queryKey: modelLifecycleQueryKeys.experimentsList(params),
		queryFn: async () => {
			const response = await ModelLifecycleService.listExperiments({
				query: {
					owner: params?.owner,
					status: params?.status,
				},
			});
			const experiments = response.data ?? [];
			return {
				experiments,
				total: experiments.length,
			};
		},
		staleTime: 1000 * 60 * 5, // 5 minutes
	});

	/**
	 * Query: Deployments List
	 * Fetches list of all deployments
	 */
	const deploymentsQuery = useQuery({
		queryKey: modelLifecycleQueryKeys.deploymentsList(),
		queryFn: async (): Promise<Deployment[]> => {
			const response = await ModelLifecycleService.listDeployments();
			return response.data as Deployment[];
		},
		staleTime: 1000 * 60 * 2, // 2 minutes
	});

	// ============================================================================
	// Mutations
	// ============================================================================

	/**
	 * Mutation: Create Experiment
	 * Creates a new ML experiment for tracking
	 */
	const createExperimentMutation = useMutation({
		mutationFn: async (data: ExperimentCreate): Promise<Experiment> => {
			const response = await ModelLifecycleService.createExperiment({
				body: data,
			});
			if (!response.data) {
				throw new Error("Experiment creation failed");
			}
			return response.data;
		},
		onSuccess: () => {
			queryClient.invalidateQueries({
				queryKey: modelLifecycleQueryKeys.experiments(),
			});
			showSuccess("실험이 성공적으로 생성되었습니다");
		},
		onError: (error: Error) => {
			showError(`실험 생성 실패: ${error.message}`);
		},
	});

	/**
	 * Mutation: Register Model
	 * Registers a model version to the model registry
	 */
	const registerModelMutation = useMutation({
		mutationFn: async (data: ModelVersionCreate): Promise<Model> => {
			const response = await ModelLifecycleService.registerModelVersion({
				body: data,
			});
			if (!response.data) {
				throw new Error("Model registration failed");
			}
			return response.data;
		},
		onSuccess: () => {
			queryClient.invalidateQueries({
				queryKey: modelLifecycleQueryKeys.models(),
			});
			showSuccess("모델이 성공적으로 등록되었습니다");
		},
		onError: (error: Error) => {
			showError(`모델 등록 실패: ${error.message}`);
		},
	});

	/**
	 * Mutation: Deploy Model
	 * Deploys a model to a specific environment
	 */
	const deployModelMutation = useMutation({
		mutationFn: async (data: DeploymentCreate): Promise<Deployment> => {
			const response = await ModelLifecycleService.createDeployment({
				body: data,
			});
			return response.data as Deployment;
		},
		onSuccess: () => {
			queryClient.invalidateQueries({
				queryKey: modelLifecycleQueryKeys.deployments(),
			});
			showSuccess("모델 배포가 시작되었습니다");
		},
		onError: (error: Error) => {
			showError(`모델 배포 실패: ${error.message}`);
		},
	});

	// ============================================================================
	// Return Hook Interface
	// ============================================================================

	return {
		// Queries
		experimentsList: experimentsQuery.data?.experiments || [],
		experimentsTotal: experimentsQuery.data?.total || 0,
		isLoadingExperiments: experimentsQuery.isLoading,
		isFetchingExperiments: experimentsQuery.isFetching,
		experimentsError: experimentsQuery.error,

		deploymentsList: deploymentsQuery.data || [],
		isLoadingDeployments: deploymentsQuery.isLoading,
		deploymentsError: deploymentsQuery.error,

		// Mutations
		createExperiment: createExperimentMutation.mutateAsync,
		isCreatingExperiment: createExperimentMutation.isPending,

		registerModel: registerModelMutation.mutateAsync,
		isRegisteringModel: registerModelMutation.isPending,

		deployModel: deployModelMutation.mutateAsync,
		isDeployingModel: deployModelMutation.isPending,

		// Refetch functions
		refetchExperiments: experimentsQuery.refetch,
		refetchDeployments: deploymentsQuery.refetch,
	};
};

// ============================================================================
// Additional Hooks for Detail Views
// ============================================================================

/**
 * Hook: Experiment Detail
 * Fetches detailed information for a specific experiment
 */
export const useExperimentDetail = (experimentName: string | null) => {
	const experimentDetailQuery = useQuery({
		queryKey: modelLifecycleQueryKeys.experimentDetail(experimentName || ""),
		queryFn: async (): Promise<ExperimentDetail> => {
			if (!experimentName) {
				throw new Error("Experiment name is required");
			}
			const response = await ModelLifecycleService.getExperiment({
				path: { name: experimentName },
			});
			if (!response.data) {
				throw new Error("Experiment not found");
			}
			return response.data;
		},
		enabled: !!experimentName,
	});

	return {
		experimentDetail: experimentDetailQuery.data,
		isLoading: experimentDetailQuery.isLoading,
		isError: experimentDetailQuery.isError,
		error: experimentDetailQuery.error,
	};
};

/**
 * Hook: Models List
 * Fetches list of registered models with filtering
 */
export const useModels = (params?: ModelsQueryParams) => {
	const modelsQuery = useQuery({
		queryKey: modelLifecycleQueryKeys.modelsList(params),
		queryFn: async (): Promise<{ models: Model[]; total: number }> => {
			const response = await ModelLifecycleService.listModelVersions({
				query: {
					stage: params?.stage,
				},
			});
			const models = response.data ?? [];
			return {
				models,
				total: models.length,
			};
		},
		staleTime: 1000 * 60 * 5,
	});

	return {
		modelsList: modelsQuery.data?.models || [],
		modelsTotal: modelsQuery.data?.total || 0,
		isLoading: modelsQuery.isLoading,
		isFetching: modelsQuery.isFetching,
		error: modelsQuery.error,
		refetch: modelsQuery.refetch,
	};
};

/**
 * Hook: Model Detail
 * Fetches detailed information for a specific model version
 */
export const useModelDetail = (
	modelName: string | null,
	version: string | null,
) => {
	const modelDetailQuery = useQuery({
		queryKey: modelLifecycleQueryKeys.modelDetail(
			modelName && version ? `${modelName}/${version}` : "",
		),
		queryFn: async (): Promise<ModelDetail> => {
			if (!modelName || !version) {
				throw new Error("Model name and version are required");
			}
			const response = await ModelLifecycleService.getModelVersion({
				path: { model_name: modelName, version },
			});
			if (!response.data) {
				throw new Error("Model version not found");
			}
			return response.data;
		},
		enabled: !!(modelName && version),
	});

	return {
		modelDetail: modelDetailQuery.data,
		isLoading: modelDetailQuery.isLoading,
		isError: modelDetailQuery.isError,
		error: modelDetailQuery.error,
	};
};

/**
 * Hook: Deployment Detail
 * Fetches detailed information for a specific deployment
 */
export const useDeploymentDetail = (deploymentId: string | null) => {
	const deploymentDetailQuery = useQuery({
		queryKey: modelLifecycleQueryKeys.deploymentDetail(deploymentId || ""),
		queryFn: async (): Promise<Deployment> => {
			if (!deploymentId) throw new Error("Deployment ID required");
			const response = await ModelLifecycleService.getDeployment({
				path: { deployment_id: deploymentId },
			});
			return response.data as Deployment;
		},
		enabled: !!deploymentId,
		staleTime: 1000 * 60 * 2, // 2 minutes for deployment metrics
		refetchInterval: (query) => {
			// Auto-refresh if deployment is in progress
			const status = query.state.data?.status;
			return status === "pending" ||
				status === "validating" ||
				status === "deploying"
				? 5000
				: false;
		},
	});

	return {
		deploymentDetail: deploymentDetailQuery.data,
		isLoading: deploymentDetailQuery.isLoading,
		error: deploymentDetailQuery.error,
		refetch: deploymentDetailQuery.refetch,
	};
};
