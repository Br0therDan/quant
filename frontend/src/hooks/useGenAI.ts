/**
 * useGenAI Hook
 *
 * GenAI 관련 기능 통합 훅
 * - Prompt Governance (템플릿 관리, 승인, 평가)
 * - ChatOps (세션 관리, 전략 비교)
 * - Narrative Reports
 * - Strategy Generation
 *
 * Phase: 5 (Frontend Enhancement)
 * 작성일: 2025-10-16
 */

import { GenAiService } from "@/client";
import type {
    PromptEvaluationRequest,
    PromptTemplateCreate,
    PromptTemplateUpdate,
    PromptUsageLogCreate,
} from "@/client/types.gen";
import { useSnackbar } from "@/contexts/SnackbarContext";
import {
    useMutation,
    useQuery,
    useQueryClient,
} from "@tanstack/react-query";

// ========================================================================================
// Query Keys
// ========================================================================================

export const genAiQueryKeys = {
    all: ["genAI"] as const,
    promptTemplates: () => [...genAiQueryKeys.all, "promptTemplates"] as const,
    promptTemplate: (promptId: string, version: number) =>
        [...genAiQueryKeys.all, "promptTemplate", promptId, version] as const,
    promptAuditLogs: (promptId: string, version: number) =>
        [...genAiQueryKeys.all, "auditLogs", promptId, version] as const,
};

// ========================================================================================
// Main Hook
// ========================================================================================

export function useGenAI() {
    const queryClient = useQueryClient();
    const { showSuccess, showError } = useSnackbar();

    // --------------------------------------------------------------------------------------
    // Query: List Prompt Templates
    // --------------------------------------------------------------------------------------

    const promptTemplatesQuery = useQuery({
        queryKey: genAiQueryKeys.promptTemplates(),
        queryFn: async () => {
            const response = await GenAiService.listPromptTemplates();
            return response.data;
        },
        staleTime: 1000 * 60 * 5, // 5분
        gcTime: 1000 * 60 * 30, // 30분
    });

    // --------------------------------------------------------------------------------------
    // Query: Prompt Audit Logs
    // --------------------------------------------------------------------------------------

    const usePromptAuditLogs = (promptId: string, version: number) => {
        return useQuery({
            queryKey: genAiQueryKeys.promptAuditLogs(promptId, version),
            queryFn: async () => {
                const response = await GenAiService.listPromptAuditLogs({
                    path: { prompt_id: promptId, version: String(version) },
                });
                return response.data;
            },
            enabled: !!promptId && version > 0,
            staleTime: 1000 * 60, // 1분
        });
    };

    // --------------------------------------------------------------------------------------
    // Mutation: Create Prompt Template
    // --------------------------------------------------------------------------------------

    const createPromptTemplateMutation = useMutation({
        mutationFn: async (data: PromptTemplateCreate) => {
            const response = await GenAiService.createPromptTemplate({
                body: data,
            });
            return response.data;
        },
        onSuccess: (data) => {
            queryClient.invalidateQueries({
                queryKey: genAiQueryKeys.promptTemplates(),
            });
            if (data) {
                showSuccess(`프롬프트 템플릿이 생성되었습니다: ${data.prompt_id}`);
            } else {
                showSuccess("프롬프트 템플릿이 생성되었습니다");
            }
        },
        onError: (error: Error) => {
            showError(`템플릿 생성 실패: ${error.message}`);
        },
    });

    // --------------------------------------------------------------------------------------
    // Mutation: Update Prompt Template
    // --------------------------------------------------------------------------------------

    const updatePromptTemplateMutation = useMutation({
        mutationFn: async ({
            promptId,
            version,
            data,
        }: {
            promptId: string;
            version: number;
            data: PromptTemplateUpdate;
        }) => {
            const response = await GenAiService.updatePromptTemplate({
                path: { prompt_id: promptId, version: String(version) },
                body: data,
            });
            return response.data;
        },
        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({
                queryKey: genAiQueryKeys.promptTemplates(),
            });
            queryClient.invalidateQueries({
                queryKey: genAiQueryKeys.promptTemplate(
                    variables.promptId,
                    variables.version,
                ),
            });
            showSuccess("프롬프트 템플릿이 업데이트되었습니다");
        },
        onError: (error: Error) => {
            showError(`템플릿 업데이트 실패: ${error.message}`);
        },
    });

    // --------------------------------------------------------------------------------------
    // Mutation: Submit Prompt for Review
    // --------------------------------------------------------------------------------------

    const submitPromptForReviewMutation = useMutation({
        mutationFn: async ({
            promptId,
            version,
            reviewer,
            notes,
        }: {
            promptId: string;
            version: number;
            reviewer: string;
            notes?: string;
        }) => {
            const response = await GenAiService.submitPromptForReview({
                path: { prompt_id: promptId, version: String(version) },
                body: { reviewer, notes },
            });
            return response.data;
        },
        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({
                queryKey: genAiQueryKeys.promptTemplates(),
            });
            queryClient.invalidateQueries({
                queryKey: genAiQueryKeys.promptTemplate(
                    variables.promptId,
                    variables.version,
                ),
            });
            showSuccess("검토 요청이 제출되었습니다");
        },
        onError: (error: Error) => {
            showError(`검토 요청 실패: ${error.message}`);
        },
    });

    // --------------------------------------------------------------------------------------
    // Mutation: Approve Prompt
    // --------------------------------------------------------------------------------------

    const approvePromptMutation = useMutation({
        mutationFn: async ({
            promptId,
            version,
            reviewer,
            notes,
        }: {
            promptId: string;
            version: number;
            reviewer: string;
            notes?: string;
        }) => {
            const response = await GenAiService.approvePrompt({
                path: { prompt_id: promptId, version: String(version) },
                body: { reviewer, notes },
            });
            return response.data;
        },
        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({
                queryKey: genAiQueryKeys.promptTemplates(),
            });
            queryClient.invalidateQueries({
                queryKey: genAiQueryKeys.promptAuditLogs(
                    variables.promptId,
                    variables.version,
                ),
            });
            showSuccess("프롬프트가 승인되었습니다");
        },
        onError: (error: Error) => {
            showError(`승인 실패: ${error.message}`);
        },
    });

    // --------------------------------------------------------------------------------------
    // Mutation: Reject Prompt
    // --------------------------------------------------------------------------------------

    const rejectPromptMutation = useMutation({
        mutationFn: async ({
            promptId,
            version,
            reviewer,
            notes,
        }: {
            promptId: string;
            version: number;
            reviewer: string;
            notes?: string;
        }) => {
            const response = await GenAiService.rejectPrompt({
                path: { prompt_id: promptId, version: String(version) },
                body: { reviewer, notes },
            });
            return response.data;
        },
        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({
                queryKey: genAiQueryKeys.promptTemplates(),
            });
            queryClient.invalidateQueries({
                queryKey: genAiQueryKeys.promptAuditLogs(
                    variables.promptId,
                    variables.version,
                ),
            });
            showSuccess("프롬프트가 거부되었습니다");
        },
        onError: (error: Error) => {
            showError(`거부 실패: ${error.message}`);
        },
    });

    // --------------------------------------------------------------------------------------
    // Mutation: Evaluate Prompt
    // --------------------------------------------------------------------------------------

    const evaluatePromptMutation = useMutation({
        mutationFn: async (data: PromptEvaluationRequest) => {
            const response = await GenAiService.evaluatePrompt({
                body: data,
            });
            return response.data;
        },
        onSuccess: () => {
            showSuccess("프롬프트 평가가 완료되었습니다");
        },
        onError: (error: Error) => {
            showError(`평가 실패: ${error.message}`);
        },
    });

    // --------------------------------------------------------------------------------------
    // Mutation: Log Prompt Usage
    // --------------------------------------------------------------------------------------

    const logPromptUsageMutation = useMutation({
        mutationFn: async ({
            promptId,
            version,
            data,
        }: {
            promptId: string;
            version: number;
            data: PromptUsageLogCreate;
        }) => {
            const response = await GenAiService.logPromptUsage({
                path: { prompt_id: promptId, version: String(version) },
                body: data,
            });
            return response.data;
        },
        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({
                queryKey: genAiQueryKeys.promptAuditLogs(
                    variables.promptId,
                    variables.version,
                ),
            });
        },
        onError: (error: Error) => {
            console.error("Usage log failed:", error.message);
        },
    });

    // --------------------------------------------------------------------------------------
    // Return Values
    // --------------------------------------------------------------------------------------

    return {
        // Queries
        promptTemplatesList: promptTemplatesQuery.data,
        isLoadingTemplates: promptTemplatesQuery.isLoading,
        isFetchingTemplates: promptTemplatesQuery.isFetching,
        templatesError: promptTemplatesQuery.error,

        // Derived Queries
        usePromptAuditLogs,

        // Mutations
        createPromptTemplate: createPromptTemplateMutation.mutate,
        isCreatingTemplate: createPromptTemplateMutation.isPending,

        updatePromptTemplate: updatePromptTemplateMutation.mutate,
        isUpdatingTemplate: updatePromptTemplateMutation.isPending,

        submitPromptForReview: submitPromptForReviewMutation.mutate,
        isSubmittingForReview: submitPromptForReviewMutation.isPending,

        approvePrompt: approvePromptMutation.mutate,
        isApprovingPrompt: approvePromptMutation.isPending,

        rejectPrompt: rejectPromptMutation.mutate,
        isRejectingPrompt: rejectPromptMutation.isPending,

        evaluatePrompt: evaluatePromptMutation.mutate,
        isEvaluatingPrompt: evaluatePromptMutation.isPending,
        evaluationResult: evaluatePromptMutation.data,

        logPromptUsage: logPromptUsageMutation.mutate,
    };
}

// ========================================================================================
// Export Types
// ========================================================================================

export type UseGenAIReturn = ReturnType<typeof useGenAI>;
