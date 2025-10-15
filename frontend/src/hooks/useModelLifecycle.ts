/**
 * Model Lifecycle Management Hook
 *
 * Manages ML model experiments, registry, and deployments for MLOps platform.
 * Provides experiment tracking, model versioning, and deployment pipeline management.
 *
 * @module hooks/useModelLifecycle
 */

import type {
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
    RunUpdate
} from "@/client";
import { ModelLifecycleService } from "@/client";
import { useSnackbar } from "@/contexts/SnackbarContext";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

// ============================================================================
// Types (using backend-generated types)
// ============================================================================

export type Experiment = ExperimentResponse;
export type ExperimentDetail = ExperimentResponse; // Backend provides full detail
export type Run = RunResponse;
export type Model = ModelVersionResponse;
export type ModelDetail = ModelVersionResponse; // Backend provides full detail
export type DriftEvent = DriftEventResponse;

// Create/Update DTOs aligned with backend
export type ExperimentCreateDTO = ExperimentCreate;
export type ExperimentUpdateDTO = ExperimentUpdate;
export type RunCreateDTO = RunCreate;
export type RunUpdateDTO = RunUpdate;
export type ModelCreateDTO = ModelVersionCreate;
export type DriftEventCreateDTO = DriftEventCreate;

// Re-export enums for convenience
export type { DriftSeverity, ExperimentStatus, ModelStage, RunStatus };

// Deployment interface (if not in backend types, keep custom)
export interface Deployment {
    id: string;
    model_id: string;
    model_name: string;
    model_version: string;
    status:
    | "pending"
    | "validating"
    | "deploying"
    | "active"
    | "failed"
    | "rollback";
    environment: "development" | "staging" | "production";
    endpoint: string;
    created_by: string;
    deployed_at?: string;
    created_at: string;
}

export interface DeploymentDetail extends Deployment {
    logs: string[];
    health_status: "healthy" | "degraded" | "unhealthy";
    request_count: number;
    error_rate: number;
    avg_latency_ms: number;
}

// Query parameters aligned with backend
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
}// ============================================================================
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
            // TODO: Replace with actual API call
            // const response = await ModelLifecycleService.getDeployments();
            // return response.data;

            await new Promise((resolve) => setTimeout(resolve, 500));
            return [];
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
        mutationFn: async (data: ModelDeploy): Promise<Deployment> => {
            // TODO: Replace with actual API call
            // const response = await ModelLifecycleService.deployModel({ body: data });
            // return response.data;

            await new Promise((resolve) => setTimeout(resolve, 2000));
            return {
                id: `deploy_${Date.now()}`,
                model_id: data.model_id,
                model_name: "Sample Model",
                model_version: "v1.0.0",
                status: "deploying",
                environment: data.environment,
                endpoint: `https://api.example.com/models/${data.model_id}`,
                created_by: "current_user",
                created_at: new Date().toISOString(),
            };
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
export const useExperimentDetail = (experimentId: string | null) => {
    const experimentDetailQuery = useQuery({
        queryKey: modelLifecycleQueryKeys.experimentDetail(experimentId || ""),
        queryFn: async (): Promise<ExperimentDetail> => {
            // TODO: Replace with actual API call
            // const response = await ModelLifecycleService.getExperiment({
            //   path: { experiment_id: experimentId! }
            // });
            // return response.data;

            await new Promise((resolve) => setTimeout(resolve, 500));
            return {
                id: experimentId || "",
                name: "Sample Experiment",
                description: "Sample experiment description",
                status: "completed",
                metrics: {
                    accuracy: 0.85,
                    f1_score: 0.82,
                    precision: 0.88,
                    recall: 0.79,
                },
                hyperparameters: {
                    learning_rate: 0.001,
                    batch_size: 32,
                    epochs: 100,
                },
                created_by: "user123",
                created_at: new Date().toISOString(),
                completed_at: new Date().toISOString(),
                duration_seconds: 3600,
                logs: ["Starting experiment...", "Training completed"],
                artifacts: [],
            };
        },
        enabled: !!experimentId,
        staleTime: 1000 * 60 * 5,
    });

    return {
        experimentDetail: experimentDetailQuery.data,
        isLoading: experimentDetailQuery.isLoading,
        error: experimentDetailQuery.error,
        refetch: experimentDetailQuery.refetch,
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
 * Fetches detailed information for a specific model
 */
export const useModelDetail = (modelId: string | null) => {
    const modelDetailQuery = useQuery({
        queryKey: modelLifecycleQueryKeys.modelDetail(modelId || ""),
        queryFn: async (): Promise<ModelDetail> => {
            // TODO: Replace with actual API call
            // const response = await ModelLifecycleService.getModel({
            //   path: { model_id: modelId! }
            // });
            // return response.data;

            await new Promise((resolve) => setTimeout(resolve, 500));
            return {
                id: modelId || "",
                name: "Sample Model",
                version: "v1.0.0",
                experiment_id: "exp_123",
                status: "production",
                accuracy: 0.85,
                created_by: "user123",
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString(),
                tags: ["classification", "production"],
                description: "Sample model description",
                framework: "scikit-learn",
                hyperparameters: {
                    learning_rate: 0.001,
                    batch_size: 32,
                },
                metrics: {
                    accuracy: 0.85,
                    f1_score: 0.82,
                },
                size_mb: 125.5,
                artifact_path: "/models/sample_model_v1.pkl",
                deployment_count: 2,
            };
        },
        enabled: !!modelId,
        staleTime: 1000 * 60 * 5,
    });

    return {
        modelDetail: modelDetailQuery.data,
        isLoading: modelDetailQuery.isLoading,
        error: modelDetailQuery.error,
        refetch: modelDetailQuery.refetch,
    };
};

/**
 * Hook: Deployment Detail
 * Fetches detailed information for a specific deployment
 */
export const useDeploymentDetail = (deploymentId: string | null) => {
    const deploymentDetailQuery = useQuery({
        queryKey: modelLifecycleQueryKeys.deploymentDetail(deploymentId || ""),
        queryFn: async (): Promise<DeploymentDetail> => {
            // TODO: Replace with actual API call
            // const response = await ModelLifecycleService.getDeployment({
            //   path: { deployment_id: deploymentId! }
            // });
            // return response.data;

            await new Promise((resolve) => setTimeout(resolve, 500));
            return {
                id: deploymentId || "",
                model_id: "model_123",
                model_name: "Sample Model",
                model_version: "v1.0.0",
                status: "active",
                environment: "production",
                endpoint: "https://api.example.com/models/sample",
                created_by: "user123",
                deployed_at: new Date().toISOString(),
                created_at: new Date().toISOString(),
                logs: [
                    "Deployment started",
                    "Validation passed",
                    "Deployed successfully",
                ],
                health_status: "healthy",
                request_count: 10523,
                error_rate: 0.02,
                avg_latency_ms: 45,
            };
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
