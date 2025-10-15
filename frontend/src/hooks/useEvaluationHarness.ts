/**
 * Evaluation Harness Management Hook
 *
 * Manages model evaluation scenarios and runs for MLOps platform.
 * Provides comprehensive model assessment and comparison capabilities.
 *
 * @module hooks/useEvaluationHarness
 */

import type {
    EvaluationRequest,
    EvaluationRunResponse,
    EvaluationStatus,
    ScenarioCreate,
    ScenarioResponse,
    ScenarioUpdate,
} from "@/client";
import { EvaluationHarnessService } from "@/client";
import { useSnackbar } from "@/contexts/SnackbarContext";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";


// ============================================================================
// Types (using backend-generated types)
// ============================================================================

export type Scenario = ScenarioResponse;
export type EvaluationRun = EvaluationRunResponse;

// Create/Update DTOs
export type ScenarioCreateDTO = ScenarioCreate;
export type ScenarioUpdateDTO = ScenarioUpdate;

// Re-export enums for convenience
export type { EvaluationStatus };

// ============================================================================
// Query Keys
// ============================================================================

export const evaluationHarnessQueryKeys = {
    all: ["evaluationHarness"] as const,
    scenarios: () => [...evaluationHarnessQueryKeys.all, "scenarios"] as const,
    scenarioDetail: (name: string) =>
        [...evaluationHarnessQueryKeys.scenarios(), "detail", name] as const,
    runs: () => [...evaluationHarnessQueryKeys.all, "runs"] as const,
    runDetail: (runId: string) =>
        [...evaluationHarnessQueryKeys.runs(), "detail", runId] as const,
};

// ============================================================================
// Hook Implementation
// ============================================================================

export const useEvaluationHarness = () => {
    const queryClient = useQueryClient();
    const { showSuccess, showError } = useSnackbar();

    // ============================================================================
    // Queries
    // ============================================================================

    /**
     * Query: Scenarios List
     * Fetches list of all evaluation scenarios
     */
    const scenariosQuery = useQuery({
        queryKey: evaluationHarnessQueryKeys.scenarios(),
        queryFn: async (): Promise<Scenario[]> => {
            const response = await EvaluationHarnessService.listScenarios();
            return response.data ?? [];
        },
        staleTime: 1000 * 60 * 5, // 5 minutes
    });

    /**
     * Query: Evaluation Runs List
     * Fetches list of evaluation runs
     */
    const runsQuery = useQuery({
        queryKey: evaluationHarnessQueryKeys.runs(),
        queryFn: async (): Promise<EvaluationRun[]> => {
            const response = await EvaluationHarnessService.listEvaluationRuns();
            return response.data ?? [];
        },
        staleTime: 1000 * 60 * 2, // 2 minutes
    });

    // ============================================================================
    // Mutations
    // ============================================================================

    /**
     * Mutation: Create Scenario
     * Creates a new evaluation scenario
     */
    const createScenarioMutation = useMutation({
        mutationFn: async (data: ScenarioCreate): Promise<Scenario> => {
            const response = await EvaluationHarnessService.registerScenario({
                body: data,
            });
            if (!response.data) {
                throw new Error("Scenario creation failed");
            }
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({
                queryKey: evaluationHarnessQueryKeys.scenarios(),
            });
            showSuccess("시나리오가 성공적으로 생성되었습니다");
        },
        onError: (error: Error) => {
            showError(`시나리오 생성 실패: ${error.message}`);
        },
    });

    /**
     * Mutation: Update Scenario
     * Updates an existing scenario
     */
    const updateScenarioMutation = useMutation({
        mutationFn: async ({
            name,
            data,
        }: {
            name: string;
            data: ScenarioUpdate;
        }): Promise<Scenario> => {
            const response = await EvaluationHarnessService.updateScenario({
                path: { name },
                body: data,
            });
            if (!response.data) {
                throw new Error("Scenario update failed");
            }
            return response.data;
        },
        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({
                queryKey: evaluationHarnessQueryKeys.scenarios(),
            });
            queryClient.invalidateQueries({
                queryKey: evaluationHarnessQueryKeys.scenarioDetail(variables.name),
            });
            showSuccess("시나리오가 성공적으로 업데이트되었습니다");
        },
        onError: (error: Error) => {
            showError(`시나리오 업데이트 실패: ${error.message}`);
        },
    });

    /**
     * Mutation: Run Evaluation
     * Starts a new evaluation run
     */
    const runEvaluationMutation = useMutation({
        mutationFn: async (data: EvaluationRequest): Promise<EvaluationRun> => {
            const response = await EvaluationHarnessService.runEvaluation({
                body: data,
            });
            if (!response.data) {
                throw new Error("Evaluation run failed");
            }
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({
                queryKey: evaluationHarnessQueryKeys.runs(),
            });
            showSuccess("평가가 성공적으로 시작되었습니다");
        },
        onError: (error: Error) => {
            showError(`평가 실행 실패: ${error.message}`);
        },
    });

    // ============================================================================
    // Return Hook Interface
    // ============================================================================

    return {
        // Queries
        scenariosList: scenariosQuery.data || [],
        isLoadingScenarios: scenariosQuery.isLoading,
        scenariosError: scenariosQuery.error,

        runsList: runsQuery.data || [],
        isLoadingRuns: runsQuery.isLoading,
        runsError: runsQuery.error,

        // Mutations
        createScenario: createScenarioMutation.mutateAsync,
        isCreatingScenario: createScenarioMutation.isPending,

        updateScenario: (name: string, data: ScenarioUpdate) =>
            updateScenarioMutation.mutateAsync({ name, data }),
        isUpdatingScenario: updateScenarioMutation.isPending,

        runEvaluation: runEvaluationMutation.mutateAsync,
        isRunningEvaluation: runEvaluationMutation.isPending,

        // Refetch functions
        refetchScenarios: scenariosQuery.refetch,
        refetchRuns: runsQuery.refetch,
    };
};

// ============================================================================
// Additional Hooks for Detail Views
// ============================================================================

/**
 * Hook: Evaluation Run Detail
 * Fetches detailed report for a specific evaluation run
 */
export const useEvaluationRunDetail = (runId: string | null) => {
    const runDetailQuery = useQuery({
        queryKey: evaluationHarnessQueryKeys.runDetail(runId || ""),
        queryFn: async () => {
            if (!runId) {
                throw new Error("Run ID is required");
            }
            const response = await EvaluationHarnessService.getEvaluationReport({
                path: { run_id: runId },
            });
            return response.data;
        },
        enabled: !!runId,
        staleTime: 1000 * 60 * 5,
    });

    return {
        runDetail: runDetailQuery.data,
        isLoading: runDetailQuery.isLoading,
        error: runDetailQuery.error,
        refetch: runDetailQuery.refetch,
    };
};
