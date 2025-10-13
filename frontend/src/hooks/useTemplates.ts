// Strategy Template Module API
// TanStack Query (v5.9) 기반 Query 및 및 Mutation 활용 상태관리 및 데이터 패칭 훅
// 성능 최적화 및 캐싱, 에러 핸들링, 로딩 상태 관리 포함
// Hook은 useTemplate 단일/통합 사용 (별도의 추가 훅 생성 불필요)
// Hey-API 기반: @/client/sdk.gen.ts 의 각 엔드포인트별 서비스클래스 및 @/client/types.gen.ts 의 타입정의 활용(엔드포인트의 스키마명칭과 호환)

import { TemplateService, type TemplateUpdate } from "@/client";
import { useSnackbar } from "@/contexts/SnackbarContext";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo } from "react";

export const templateQueryKeys = {
	all: ["template"] as const,
	lists: () => [...templateQueryKeys.all, "list"] as const,
	details: () => [...templateQueryKeys.all, "detail"] as const,
	detail: (id: string) => [...templateQueryKeys.details(), id] as const,
	analytics: () => [...templateQueryKeys.all, "analytics"] as const,
	usageStats: () => [...templateQueryKeys.analytics(), "usage-stats"] as const,
};

export function useTemplates() {
	const queryClient = useQueryClient();
	const { showSuccess, showError } = useSnackbar();

	// Queries
	const templateListQuery = useQuery({
		queryKey: templateQueryKeys.lists(),
		queryFn: async () => {
			const response = await TemplateService.getTemplates();
			return response.data;
		},
		staleTime: 1000 * 60 * 30, // 30 minutes (templates don't change frequently)
		gcTime: 2 * 60 * 60 * 1000, // 2 hours
	});

	const templateUsageStatsQuery = useQuery({
		queryKey: templateQueryKeys.usageStats(),
		queryFn: async () => {
			const response = await TemplateService.getTemplateUsageStats();
			return response.data;
		},
		staleTime: 1000 * 60 * 15, // 15 minutes
		gcTime: 60 * 60 * 1000, // 1 hour
	});

	// Mutations
	const createTemplateMutation = useMutation({
		mutationFn: async (data: any) => {
			const response = await TemplateService.createTemplate({
				body: data,
			});
			return response.data;
		},
		onSuccess: (data) => {
			queryClient.invalidateQueries({ queryKey: templateQueryKeys.lists() });
			queryClient.invalidateQueries({
				queryKey: templateQueryKeys.usageStats(),
			});
			showSuccess(
				`템플릿 "${data?.name || "새 템플릿"}"이 성공적으로 생성되었습니다`,
			);
		},
		onError: (error) => {
			console.error("템플릿 생성 실패:", error);
			showError(
				error instanceof Error ? error.message : "템플릿 생성에 실패했습니다",
			);
		},
	});

	const updateTemplateMutation = useMutation({
		mutationFn: async ({ id, data }: { id: string; data: TemplateUpdate }) => {
			const response = await TemplateService.updateTemplate({
				path: { template_id: id },
				body: data,
			});
			return response.data;
		},
		onSuccess: (data) => {
			queryClient.invalidateQueries({ queryKey: templateQueryKeys.lists() });
			queryClient.invalidateQueries({
				queryKey: templateQueryKeys.detail(data?.id || ""),
			});
			showSuccess(
				`템플릿 "${data?.name || "템플릿"}"이 성공적으로 업데이트되었습니다`,
			);
		},
		onError: (error) => {
			console.error("템플릿 업데이트 실패:", error);
			showError(
				error instanceof Error
					? error.message
					: "템플릿 업데이트에 실패했습니다",
			);
		},
	});

	const deleteTemplateMutation = useMutation({
		mutationFn: async (id: string) => {
			const response = await TemplateService.deleteTemplate({
				path: { template_id: id },
			});
			return response.data;
		},
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: templateQueryKeys.lists() });
			queryClient.invalidateQueries({
				queryKey: templateQueryKeys.usageStats(),
			});
			showSuccess("템플릿이 성공적으로 삭제되었습니다");
		},
		onError: (error) => {
			console.error("템플릿 삭제 실패:", error);
			showError(
				error instanceof Error ? error.message : "템플릿 삭제에 실패했습니다",
			);
		},
	});

	const createStrategyFromTemplateMutation = useMutation({
		mutationFn: async (data: { templateId: string; strategyData: any }) => {
			const response = await TemplateService.createStrategyFromTemplate({
				path: { template_id: data.templateId },
				body: data.strategyData,
			});
			return response.data;
		},
		onSuccess: (data) => {
			queryClient.invalidateQueries({ queryKey: ["strategy", "list"] }); // Invalidate strategy list
			queryClient.invalidateQueries({
				queryKey: templateQueryKeys.usageStats(),
			});
			showSuccess(
				`템플릿에서 전략 "${data?.name || "새 전략"}"이 성공적으로 생성되었습니다`,
			);
		},
		onError: (error) => {
			console.error("템플릿에서 전략 생성 실패:", error);
			showError(
				error instanceof Error
					? error.message
					: "템플릿에서 전략 생성에 실패했습니다",
			);
		},
	});

	return useMemo(
		() => ({
			// Data
			templates: templateListQuery.data?.templates,
			templateUsageStats: templateUsageStatsQuery.data,

			// Status
			isError: {
				templates: templateListQuery.isError,
				templateUsageStats: templateUsageStatsQuery.isError,
			},
			isLoading: {
				templates: templateListQuery.isLoading,
				templateUsageStats: templateUsageStatsQuery.isLoading,
			},
			error: {
				templates: templateListQuery.error,
				templateUsageStats: templateUsageStatsQuery.error,
			},

			// Actions
			refetch: {
				templateList: templateListQuery.refetch,
				templateUsageStats: templateUsageStatsQuery.refetch,
			},

			// Mutations
			createTemplate: createTemplateMutation.mutateAsync,
			updateTemplate: updateTemplateMutation.mutateAsync,
			deleteTemplate: deleteTemplateMutation.mutateAsync,
			createStrategyFromTemplate:
				createStrategyFromTemplateMutation.mutateAsync,

			// Mutation Status
			isMutating: {
				createTemplate: createTemplateMutation.isPending,
				updateTemplate: updateTemplateMutation.isPending,
				deleteTemplate: deleteTemplateMutation.isPending,
				createStrategyFromTemplate:
					createStrategyFromTemplateMutation.isPending,
			},
		}),
		[
			templateListQuery,
			templateUsageStatsQuery,
			createTemplateMutation,
			updateTemplateMutation,
			deleteTemplateMutation,
			createStrategyFromTemplateMutation,
		],
	);
}

// Individual hook for template detail
export const useTemplateDetail = (id: string) => {
	return useQuery({
		queryKey: templateQueryKeys.detail(id),
		queryFn: async () => {
			const response = await TemplateService.getTemplate({
				path: { template_id: id },
			});
			return response.data;
		},
		enabled: !!id,
		staleTime: 1000 * 60 * 30, // 30 minutes
		gcTime: 2 * 60 * 60 * 1000, // 2 hours
	});
};
