// Strategy Module API
// TanStack Query (v5.9) 기반 Query 및 및 Mutation 활용 상태관리 및 데이터 패칭 훅
// 성능 최적화 및 캐싱, 에러 핸들링, 로딩 상태 관리 포함
// Hook은 useStrategy 단일/통합 사용 (별도의 추가 훅 생성 불필요)
// Hey-API 기반: @/client/sdk.gen.ts 의 각 엔드포인트별 서비스클래스 및 @/client/types.gen.ts 의 타입정의 활용(엔드포인트의 스키마명칭과 호환)

import { StrategyService } from "@/client";
import type { StrategyCreateRequest, StrategyExecuteRequest } from "@/client/types.gen";
import { useSnackbar } from "@/contexts/SnackbarContext";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo } from "react";

export const strategyQueryKeys = {
    all: ["strategy"] as const,
    lists: () => [...strategyQueryKeys.all, "list"] as const,
    list: (filters: string) => [...strategyQueryKeys.lists(), { filters }] as const,
    details: () => [...strategyQueryKeys.all, "detail"] as const,
    detail: (id: string) => [...strategyQueryKeys.details(), id] as const,
    executions: () => [...strategyQueryKeys.all, "executions"] as const,
    strategyExecutions: (id: string) => [...strategyQueryKeys.executions(), id] as const,
    performance: () => [...strategyQueryKeys.all, "performance"] as const,
    strategyPerformance: (id: string) => [...strategyQueryKeys.performance(), id] as const,
};

export function useStrategy() {
    const queryClient = useQueryClient();
    const { showSuccess, showError } = useSnackbar();

    // Queries
    const strategyListQuery = useQuery({
        queryKey: strategyQueryKeys.lists(),
        queryFn: async () => {
            const response = await StrategyService.getStrategies();
            return response.data;
        },
        staleTime: 1000 * 60 * 5, // 5 minutes
        gcTime: 30 * 60 * 1000, // 30 minutes
    });

    // Mutations
    const createStrategyMutation = useMutation({
        mutationFn: async (data: StrategyCreateRequest) => {
            const response = await StrategyService.createStrategy({
                body: data
            });
            return response.data;
        },
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: strategyQueryKeys.lists() });
            showSuccess(`전략 "${data?.name || '새 전략'}"이 성공적으로 생성되었습니다`);
        },
        onError: (error) => {
            console.error("전략 생성 실패:", error);
            showError(error instanceof Error ? error.message : '전략 생성에 실패했습니다');
        },
    });

    const updateStrategyMutation = useMutation({
        mutationFn: async (data: { id: string; updateData: Partial<StrategyCreateRequest> }) => {
            const response = await StrategyService.updateStrategy({
                path: { strategy_id: data.id },
                body: data.updateData
            });
            return response.data;
        },
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: strategyQueryKeys.lists() });
            queryClient.invalidateQueries({ queryKey: strategyQueryKeys.detail(data?.id || '') });
            showSuccess(`전략 "${data?.name || '전략'}"이 성공적으로 업데이트되었습니다`);
        },
        onError: (error) => {
            console.error("전략 업데이트 실패:", error);
            showError(error instanceof Error ? error.message : '전략 업데이트에 실패했습니다');
        },
    });

    const deleteStrategyMutation = useMutation({
        mutationFn: async (id: string) => {
            const response = await StrategyService.deleteStrategy({
                path: { strategy_id: id }
            });
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: strategyQueryKeys.lists() });
            showSuccess('전략이 성공적으로 삭제되었습니다');
        },
        onError: (error) => {
            console.error("전략 삭제 실패:", error);
            showError(error instanceof Error ? error.message : '전략 삭제에 실패했습니다');
        },
    });

    const executeStrategyMutation = useMutation({
        mutationFn: async ({id, data}: { id: string; data: StrategyExecuteRequest }) => {
            const response = await StrategyService.executeStrategy({
                path: { strategy_id: id },
                body: data
            });
            return response.data;
        },
        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({ queryKey: strategyQueryKeys.strategyExecutions(variables.id) });
            queryClient.invalidateQueries({ queryKey: strategyQueryKeys.strategyPerformance(variables.id) });
            showSuccess('전략이 성공적으로 실행되었습니다');
        },
        onError: (error) => {
            console.error("전략 실행 실패:", error);
            showError(error instanceof Error ? error.message : '전략 실행에 실패했습니다');
        },
    });

    return useMemo(() => ({

        // Data
        strategyList: strategyListQuery.data?.strategies,
        // Actions
        refetch: {
            strategyList: strategyListQuery.refetch,
        },
        // Mutations
        createStrategy: createStrategyMutation.mutate,
        updateStrategy: updateStrategyMutation.mutate,
        deleteStrategy: deleteStrategyMutation.mutate,
        executeStrategy: executeStrategyMutation.mutate,
        // Status
        isError: {
            strategyList: strategyListQuery.isError,
        },
        isLoading: {
            strategyList: strategyListQuery.isLoading,
        },
        isPending: {
            createStrategy: createStrategyMutation.isPending,
            updateStrategy: updateStrategyMutation.isPending,
            deleteStrategy: deleteStrategyMutation.isPending,
            executeStrategy: executeStrategyMutation.isPending,
        },
        error: {
            strategyList: strategyListQuery.error,
        },
        isMutating: {
            createStrategy: createStrategyMutation.isPending,
            updateStrategy: updateStrategyMutation.isPending,
            deleteStrategy: deleteStrategyMutation.isPending,
            executeStrategy: executeStrategyMutation.isPending,
        },

    }), [
        strategyListQuery,
        createStrategyMutation,
        updateStrategyMutation,
        deleteStrategyMutation,
        executeStrategyMutation,
    ]);
}

// Individual hook for strategy detail
export const useStrategyDetail = (id: string) => {
    return useQuery({
        queryKey: strategyQueryKeys.detail(id),
        queryFn: async () => {
            const response = await StrategyService.getStrategy({
                path: { strategy_id: id }
            });
            return response.data;
        },
        enabled: !!id,
        staleTime: 1000 * 60 * 5, // 5 minutes
        gcTime: 30 * 60 * 1000, // 30 minutes
    });
};

// Individual hook for strategy executions
export const useStrategyExecutions = (id: string) => {
    return useQuery({
        queryKey: strategyQueryKeys.strategyExecutions(id),
        queryFn: async () => {
            const response = await StrategyService.getStrategyExecutions({
                path: { strategy_id: id }
            });
            return response.data;
        },
        enabled: !!id,
        staleTime: 1000 * 60 * 2, // 2 minutes
        gcTime: 10 * 60 * 1000, // 10 minutes
    });
};

// Individual hook for strategy performance
export const useStrategyPerformance = (id: string) => {
    return useQuery({
        queryKey: strategyQueryKeys.strategyPerformance(id),
        queryFn: async () => {
            const response = await StrategyService.getStrategyPerformance({
                path: { strategy_id: id }
            });
            return response.data;
        },
        enabled: !!id,
        staleTime: 1000 * 60 * 5, // 5 minutes
        gcTime: 30 * 60 * 1000, // 30 minutes
    });
};
