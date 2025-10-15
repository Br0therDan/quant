/**
 * usePromptGovernance Hook
 *
 * LLM 프롬프트 템플릿 거버넌스를 위한 커스텀 훅
 *
 * 주요 기능:
 * - 프롬프트 템플릿 생성/수정/조회
 * - 버전 관리 및 승인 워크플로우 (Draft → Under Review → Approved/Rejected)
 * - 사용 로그 추적 및 분석
 * - 품질 평가 (토큰 수, 복잡도, 명확성 등)
 *
 * @author AI MLOps Team
 * @since Phase 4 - Day 9
 */

import type {
	PromptEvaluationRequest,
	PromptEvaluationResponse,
	PromptTemplateCreate,
	PromptTemplateUpdate,
	PromptUsageLogCreate,
	PromptUsageLogResponse,
	PromptWorkflowAction,
} from "@/client";
import { PromptGovernanceService } from "@/client";
import { useSnackbar } from "@/contexts/SnackbarContext";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

// ============================================================================
// Query Keys
// ============================================================================

export const promptGovernanceQueryKeys = {
	all: ["promptGovernance"] as const,
	templatesList: (params?: { status?: string; tag?: string }) =>
		[...promptGovernanceQueryKeys.all, "templatesList", params] as const,
	templateDetail: (promptId: string, version: string) =>
		[
			...promptGovernanceQueryKeys.all,
			"templateDetail",
			promptId,
			version,
		] as const,
	usageLogs: (promptId: string, version: string) =>
		[...promptGovernanceQueryKeys.all, "usageLogs", promptId, version] as const,
	auditLogs: (promptId: string, version: string) =>
		[...promptGovernanceQueryKeys.all, "auditLogs", promptId, version] as const,
};

// ============================================================================
// Hook Parameters
// ============================================================================

export interface UsePromptGovernanceParams {
	status?: string;
	tag?: string;
}

// ============================================================================
// Main Hook
// ============================================================================

export const usePromptGovernance = (params?: UsePromptGovernanceParams) => {
	const queryClient = useQueryClient();
	const { showSuccess, showError } = useSnackbar();

	// ============================================================================
	// Queries
	// ============================================================================

	// 템플릿 목록 조회
	const templatesListQuery = useQuery({
		queryKey: promptGovernanceQueryKeys.templatesList(params),
		queryFn: async () => {
			const response = await PromptGovernanceService.listPromptTemplates({
				query: {
					status: params?.status ?? null,
					tag: params?.tag ?? null,
				},
			});
			return response.data;
		},
		staleTime: 1000 * 60 * 5, // 5분
	});

	// ============================================================================
	// Mutations
	// ============================================================================

	// 새 템플릿 생성
	const createTemplateMutation = useMutation({
		mutationFn: async (data: PromptTemplateCreate) => {
			const response = await PromptGovernanceService.createPromptTemplate({
				body: data,
			});
			return response.data;
		},
		onSuccess: (data) => {
			queryClient.invalidateQueries({
				queryKey: promptGovernanceQueryKeys.templatesList(),
			});
			if (data) {
				showSuccess(
					`프롬프트 템플릿 '${data.name}' v${data.version}이 생성되었습니다.`,
				);
			}
		},
		onError: (error: Error) => {
			showError(`템플릿 생성 실패: ${error.message}`);
		},
	});

	// 템플릿 수정
	const updateTemplateMutation = useMutation({
		mutationFn: async ({
			promptId,
			version,
			data,
		}: {
			promptId: string;
			version: string;
			data: PromptTemplateUpdate;
		}) => {
			const response = await PromptGovernanceService.updatePromptTemplate({
				path: { prompt_id: promptId, version },
				body: data,
			});
			return response.data;
		},
		onSuccess: (data) => {
			queryClient.invalidateQueries({
				queryKey: promptGovernanceQueryKeys.templatesList(),
			});
			if (data) {
				queryClient.invalidateQueries({
					queryKey: promptGovernanceQueryKeys.templateDetail(
						data.prompt_id,
						data.version,
					),
				});
				showSuccess(`템플릿 v${data.version}이 수정되었습니다.`);
			}
		},
		onError: (error: Error) => {
			showError(`템플릿 수정 실패: ${error.message}`);
		},
	});

	// 검토 요청 (Draft → Under Review)
	const submitForReviewMutation = useMutation({
		mutationFn: async ({
			promptId,
			version,
			action,
		}: {
			promptId: string;
			version: string;
			action: PromptWorkflowAction;
		}) => {
			const response = await PromptGovernanceService.submitPromptForReview({
				path: { prompt_id: promptId, version },
				body: action,
			});
			return response.data;
		},
		onSuccess: (data) => {
			queryClient.invalidateQueries({
				queryKey: promptGovernanceQueryKeys.templatesList(),
			});
			if (data) {
				queryClient.invalidateQueries({
					queryKey: promptGovernanceQueryKeys.templateDetail(
						data.prompt_id,
						data.version,
					),
				});
			}
			showSuccess("검토 요청이 제출되었습니다.");
		},
		onError: (error: Error) => {
			showError(`검토 요청 실패: ${error.message}`);
		},
	});

	// 템플릿 승인 (Under Review → Approved)
	const approveTemplateMutation = useMutation({
		mutationFn: async ({
			promptId,
			version,
			action,
		}: {
			promptId: string;
			version: string;
			action: PromptWorkflowAction;
		}) => {
			const response = await PromptGovernanceService.approvePrompt({
				path: { prompt_id: promptId, version },
				body: action,
			});
			return response.data;
		},
		onSuccess: (data) => {
			queryClient.invalidateQueries({
				queryKey: promptGovernanceQueryKeys.templatesList(),
			});
			if (data) {
				queryClient.invalidateQueries({
					queryKey: promptGovernanceQueryKeys.templateDetail(
						data.prompt_id,
						data.version,
					),
				});
				showSuccess(`템플릿 v${data.version}이 승인되었습니다.`);
			}
		},
		onError: (error: Error) => {
			showError(`승인 실패: ${error.message}`);
		},
	});

	// 템플릿 거부 (Under Review → Rejected)
	const rejectTemplateMutation = useMutation({
		mutationFn: async ({
			promptId,
			version,
			action,
		}: {
			promptId: string;
			version: string;
			action: PromptWorkflowAction;
		}) => {
			const response = await PromptGovernanceService.rejectPrompt({
				path: { prompt_id: promptId, version },
				body: action,
			});
			return response.data;
		},
		onSuccess: (data) => {
			queryClient.invalidateQueries({
				queryKey: promptGovernanceQueryKeys.templatesList(),
			});
			if (data) {
				queryClient.invalidateQueries({
					queryKey: promptGovernanceQueryKeys.templateDetail(
						data.prompt_id,
						data.version,
					),
				});
			}
			showSuccess("템플릿이 거부되었습니다.");
		},
		onError: (error: Error) => {
			showError(`거부 처리 실패: ${error.message}`);
		},
	});

	// 프롬프트 품질 평가
	const evaluatePromptMutation = useMutation({
		mutationFn: async (request: PromptEvaluationRequest) => {
			const response = await PromptGovernanceService.evaluatePrompt({
				body: request,
			});
			return response.data;
		},
		onSuccess: () => {
			showSuccess("프롬프트 평가가 완료되었습니다.");
		},
		onError: (error: Error) => {
			showError(`평가 실패: ${error.message}`);
		},
	});

	// 사용 로그 기록
	const logUsageMutation = useMutation({
		mutationFn: async ({
			promptId,
			version,
			log,
		}: {
			promptId: string;
			version: string;
			log: PromptUsageLogCreate;
		}) => {
			const response = await PromptGovernanceService.logPromptUsage({
				path: { prompt_id: promptId, version },
				body: log,
			});
			return response.data;
		},
		onSuccess: (_, variables) => {
			queryClient.invalidateQueries({
				queryKey: promptGovernanceQueryKeys.usageLogs(
					variables.promptId,
					variables.version,
				),
			});
		},
		onError: (error: Error) => {
			showError(`사용 로그 기록 실패: ${error.message}`);
		},
	});

	// ============================================================================
	// Return
	// ============================================================================

	return {
		// Queries
		templatesList: templatesListQuery.data ?? [],
		isLoadingTemplates: templatesListQuery.isLoading,
		templatesError: templatesListQuery.error,

		// Mutations
		createTemplate: createTemplateMutation.mutateAsync,
		isCreatingTemplate: createTemplateMutation.isPending,

		updateTemplate: updateTemplateMutation.mutateAsync,
		isUpdatingTemplate: updateTemplateMutation.isPending,

		submitForReview: submitForReviewMutation.mutateAsync,
		isSubmittingForReview: submitForReviewMutation.isPending,

		approveTemplate: approveTemplateMutation.mutateAsync,
		isApprovingTemplate: approveTemplateMutation.isPending,

		rejectTemplate: rejectTemplateMutation.mutateAsync,
		isRejectingTemplate: rejectTemplateMutation.isPending,

		evaluatePrompt: evaluatePromptMutation.mutateAsync,
		isEvaluatingPrompt: evaluatePromptMutation.isPending,
		evaluationResult: evaluatePromptMutation.data as
			| PromptEvaluationResponse
			| undefined,

		logUsage: logUsageMutation.mutateAsync,
		isLoggingUsage: logUsageMutation.isPending,

		// Helpers
		findTemplate: (promptId: string, version: string) =>
			templatesListQuery.data?.find(
				(t) => t.prompt_id === promptId && t.version === version,
			) ?? null,
	};
};

// ============================================================================
// Sub-Hook: Template Detail
// ============================================================================

export const usePromptTemplateDetail = (promptId: string, version: string) => {
	const { findTemplate } = usePromptGovernance();

	const templateDetailQuery = useQuery({
		queryKey: promptGovernanceQueryKeys.templateDetail(promptId, version),
		queryFn: () => {
			const template = findTemplate(promptId, version);
			if (!template) {
				throw new Error("Template not found");
			}
			return template;
		},
		enabled: !!promptId && !!version,
		staleTime: 1000 * 60 * 5,
	});

	return {
		template: templateDetailQuery.data,
		isLoading: templateDetailQuery.isLoading,
		error: templateDetailQuery.error,
	};
};

// ============================================================================
// Sub-Hook: Usage Logs
// ============================================================================

export const usePromptUsageLogs = (promptId: string, version: string) => {
	const usageLogsQuery = useQuery({
		queryKey: promptGovernanceQueryKeys.usageLogs(promptId, version),
		queryFn: async () => {
			// Backend API에 usage logs 엔드포인트가 없으므로
			// 현재는 빈 배열 반환 (향후 구현 예정)
			return [] as PromptUsageLogResponse[];
		},
		enabled: !!promptId && !!version,
		staleTime: 1000 * 60,
	});

	return {
		usageLogs: usageLogsQuery.data ?? [],
		isLoading: usageLogsQuery.isLoading,
		error: usageLogsQuery.error,
	};
};

// ============================================================================
// Sub-Hook: Audit Logs
// ============================================================================

export const usePromptAuditLogs = (promptId: string, version: string) => {
	const auditLogsQuery = useQuery({
		queryKey: promptGovernanceQueryKeys.auditLogs(promptId, version),
		queryFn: async () => {
			const response = await PromptGovernanceService.listPromptAuditLogs({
				path: { prompt_id: promptId, version },
			});
			return response.data;
		},
		enabled: !!promptId && !!version,
		staleTime: 1000 * 60,
	});

	return {
		auditLogs: auditLogsQuery.data ?? [],
		isLoading: auditLogsQuery.isLoading,
		error: auditLogsQuery.error,
	};
};
