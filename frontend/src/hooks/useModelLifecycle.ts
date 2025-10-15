/**
 * Model Lifecycle Management Hook
 *
 * Manages ML model experiments, registry, and deployments for MLOps platform.
 * Provides experiment tracking, model versioning, and deployment pipeline management.
 *
 * @module hooks/useModelLifecycle
 */

import { useSnackbar } from "@/contexts/SnackbarContext";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

// ============================================================================
// Types (temporary - will be replaced by generated client types)
// ============================================================================

export interface Experiment {
    id: string;
    name: string;
    description: string;
    status: "running" | "completed" | "failed" | "cancelled";
    metrics: Record<string, number>;
    hyperparameters: Record<string, unknown>;
    created_by: string;
    created_at: string;
    completed_at?: string;
    duration_seconds?: number;
}

export interface ExperimentDetail extends Experiment {
    logs: string[];
    artifacts: {
        name: string;
        type: string;
        size: number;
        path: string;
    }[];
    model_id?: string;
}

export interface Model {
    id: string;
    name: string;
    version: string;
    experiment_id: string;
    status: "draft" | "registered" | "staging" | "production" | "archived";
    accuracy: number;
    created_by: string;
    created_at: string;
    updated_at: string;
    tags: string[];
}

export interface ModelDetail extends Model {
    description: string;
    framework: string;
    hyperparameters: Record<string, unknown>;
    metrics: Record<string, number>;
    size_mb: number;
    artifact_path: string;
    deployment_count: number;
}

export interface Deployment {
    id: string;
    model_id: string;
    model_name: string;
    model_version: string;
    status: "pending" | "validating" | "deploying" | "active" | "failed" | "rollback";
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

export interface ExperimentCreate {
    name: string;
    description: string;
    hyperparameters: Record<string, unknown>;
}

export interface ModelRegister {
    experiment_id: string;
    name: string;
    version: string;
    description: string;
    tags: string[];
}

export interface ModelDeploy {
    model_id: string;
    environment: Deployment["environment"];
}

export interface ExperimentsQueryParams {
    status?: Experiment["status"];
    date_from?: string;
    date_to?: string;
    sort_by?: "created_at" | "name" | "duration";
    sort_order?: "asc" | "desc";
    page?: number;
    limit?: number;
}

export interface ModelsQueryParams {
    status?: Model["status"];
    tags?: string[];
    sort_by?: "created_at" | "name" | "accuracy";
    sort_order?: "asc" | "desc";
    page?: number;
    limit?: number;
}

// ============================================================================
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
    deployments: () =>
        [...modelLifecycleQueryKeys.all, "deployments"] as const,
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
        queryFn: async (): Promise<{
            experiments: Experiment[];
            total: number;
        }> => {
            // TODO: Replace with actual API call after pnpm gen:client
            // const response = await ModelLifecycleService.getExperiments({ query: params });
            // return response.data;

            // Mock data for now
            await new Promise((resolve) => setTimeout(resolve, 500));
            return {
                experiments: [],
                total: 0,
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
     * Creates a new ML experiment
     */
    const createExperimentMutation = useMutation({
        mutationFn: async (data: ExperimentCreate): Promise<Experiment> => {
            // TODO: Replace with actual API call
            // const response = await ModelLifecycleService.createExperiment({ body: data });
            // return response.data;

            await new Promise((resolve) => setTimeout(resolve, 1000));
            return {
                id: `exp_${Date.now()}`,
                name: data.name,
                description: data.description,
                status: "running",
                metrics: {},
                hyperparameters: data.hyperparameters,
                created_by: "current_user",
                created_at: new Date().toISOString(),
            };
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
     * Registers a model from an experiment to the model registry
     */
    const registerModelMutation = useMutation({
        mutationFn: async (data: ModelRegister): Promise<Model> => {
            // TODO: Replace with actual API call
            // const response = await ModelLifecycleService.registerModel({ body: data });
            // return response.data;

            await new Promise((resolve) => setTimeout(resolve, 1000));
            return {
                id: `model_${Date.now()}`,
                name: data.name,
                version: data.version,
                experiment_id: data.experiment_id,
                status: "registered",
                accuracy: 0.85,
                created_by: "current_user",
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString(),
                tags: data.tags,
            };
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
            // TODO: Replace with actual API call
            // const response = await ModelLifecycleService.getModels({ query: params });
            // return response.data;

            await new Promise((resolve) => setTimeout(resolve, 500));
            return {
                models: [],
                total: 0,
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
                logs: ["Deployment started", "Validation passed", "Deployed successfully"],
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
