// Backtest Module API
// TanStack Query (v5.9) 기반 Query 및 및 Mutation 활용 상태관리 및 데이터 패칭 훅
// 성능 최적화 및 캐싱, 에러 핸들링, 로딩 상태 관리 포함
// Hook은 useBacktest 단일/통합 사용 (별도의 추가 훅 생성 불필요)
// Hey-API 기반: @/client/sdk.gen.ts 의 각 엔드포인트별 서비스클래스 및 @/client/types.gen.ts 의 타입정의 활용(엔드포인트의 스키마명칭과 호환)
// MUI Snackbar 활용 알림(토스트) 기능 포함

import type { BacktestCreate } from "@/client";
import { BacktestService } from "@/client";
import { useSnackbar } from "@/contexts/SnackbarContext";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo } from 'react';
export const backtestQueryKeys = {
    all: ["backtest"] as const,
    lists: () => [...backtestQueryKeys.all, "list"] as const,
    list: (filters: string) => [...backtestQueryKeys.lists(), { filters }] as const,
    details: () => [...backtestQueryKeys.all, "detail"] as const,
    detail: (id: string) => [...backtestQueryKeys.details(), id] as const,
    results: () => [...backtestQueryKeys.all, "result"] as const,
    result: (id: string) => [...backtestQueryKeys.results(), id] as const,
    analytics: () => [...backtestQueryKeys.all, "analytics"] as const,
    performanceState: () => [...backtestQueryKeys.analytics(), "performanceState"] as const,
    tradeState: () => [...backtestQueryKeys.analytics(), "tradeState"] as const,
    summaryState: () => [...backtestQueryKeys.analytics(), "summaryState"] as const,
    healthState: () => [...backtestQueryKeys.all, "healthState"] as const,
};

export function useBacktest() {
    const queryClient = useQueryClient();
    const { showSuccess, showError } = useSnackbar();

    // Queries
    const backtestListQuery = useQuery({
        queryKey: backtestQueryKeys.lists(),
        queryFn: async () => {
            const response = await BacktestService.getBacktests();
            return response.data;
        },
        staleTime: 1000 * 60 * 5, // 5 minutes
        gcTime: 30 * 60 * 1000, // 30 minutes
    });

    const backtestResultsQuery = useQuery({
        queryKey: backtestQueryKeys.results(),
        queryFn: async () => {
            const response = await BacktestService.getBacktestResults();
            return response.data;
        },
        staleTime: 1000 * 60 * 5, // 5 minutes
        gcTime: 30 * 60 * 1000, // 30 minutes
    });

    const backtestPerformanceAnalyticsQuery = useQuery({
        queryKey: backtestQueryKeys.performanceState(),
        queryFn: async () => {
            const response = await BacktestService.getPerformanceAnalytics();
            return response.data;
        },
        staleTime: 1000 * 60 * 5, // 5 minutes
        gcTime: 30 * 60 * 1000, // 30 minutes
    });

    const backtestTradeAnalyticsQuery = useQuery({
        queryKey: backtestQueryKeys.tradeState(),
        queryFn: async () => {
            const response = await BacktestService.getTradesAnalytics();
            return response.data;
        },
        staleTime: 1000 * 60 * 5, // 5 minutes
        gcTime: 30 * 60 * 1000, // 30 minutes
    });

    const backtestSummaryAnalyticsQuery = useQuery({
        queryKey: [...backtestQueryKeys.analytics(), "summary"],
        queryFn: async () => {
            const response = await BacktestService.getBacktestSummaryAnalytics();
            return response.data;
        },
        staleTime: 1000 * 60 * 5, // 5 minutes
        gcTime: 30 * 60 * 1000, // 30 minutes
    });

    const backtestHealthCheckQuery = useQuery({
        queryKey: backtestQueryKeys.healthState(),
        queryFn: async () => {
            const response = await BacktestService.healthCheck();
            return response.data;
        },
        staleTime: 1000 * 60 * 5, // 5 minutes
        gcTime: 30 * 60 * 1000, // 30 minutes
    });

    // Mutations
    const createBacktestMutation = useMutation({
        mutationFn: async (data: BacktestCreate) => {
            const response = await BacktestService.createBacktest({ body: data });
            return response.data;
        },
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: backtestQueryKeys.lists() });
            showSuccess(`백테스트 "${data?.name || '새 백테스트'}"가 성공적으로 생성되었습니다`);
        },
        onError: (error) => {
            console.error("백테스트 생성 실패:", error);
            showError(error instanceof Error ? error.message : '백테스트 생성에 실패했습니다');
        }
    });

    const updateBacktestMutation = useMutation({
        mutationFn: async (data: { id: string; updateData: Partial<BacktestCreate> }) => {
            const response = await BacktestService.updateBacktest({ path: { backtest_id: data.id }, body: data.updateData });
            return response.data;
        },
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: backtestQueryKeys.lists() });
            showSuccess(`백테스트 "${data?.name || '백테스트'}"가 성공적으로 업데이트되었습니다`);
        },
        onError: (error) => {
            console.error("백테스트 업데이트 실패:", error);
            showError(error instanceof Error ? error.message : '백테스트 업데이트에 실패했습니다');
        }
    });

    const deleteBacktestMutation = useMutation({
        mutationFn: async (id: string) => {
            const response = await BacktestService.deleteBacktest({ path: { backtest_id: id } });
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: backtestQueryKeys.lists() });
            showSuccess('백테스트가 성공적으로 삭제되었습니다');
        },
        onError: (error) => {
            console.error("백테스트 삭제 실패:", error);
            showError(error instanceof Error ? error.message : '백테스트 삭제에 실패했습니다');
        }
    });

    return useMemo(() => ({

        // Data
        backtestList: backtestListQuery.data,
        backtestResults: backtestResultsQuery.data,
        backtestPerformanceAnalytics: backtestPerformanceAnalyticsQuery.data,
        backtestTradeAnalytics: backtestTradeAnalyticsQuery.data,
        backtestSummaryAnalytics: backtestSummaryAnalyticsQuery.data,
        backtestHealthCheck: backtestHealthCheckQuery.data,
        // Status
        isError: {
            backtestList: backtestListQuery.isError,
            backtestResults: backtestResultsQuery.isError,
            backtestPerformanceAnalytics: backtestPerformanceAnalyticsQuery.isError,
            backtestTradeAnalytics: backtestTradeAnalyticsQuery.isError,
            backtestSummaryAnalytics: backtestSummaryAnalyticsQuery.isError,
            backtestHealthCheck: backtestHealthCheckQuery.isError,
        },

        // Mutations
        createBacktest: createBacktestMutation.mutate,
        updateBacktest: updateBacktestMutation.mutate,
        deleteBacktest: deleteBacktestMutation.mutate,


        // Loading States
        isMutating: {
            createBacktest: createBacktestMutation.isPending,
            updateBacktest: updateBacktestMutation.isPending,
            deleteBacktest: deleteBacktestMutation.isPending,
        },

        isLoading: {
            backtestList: backtestListQuery.isLoading,
            backtestResults: backtestResultsQuery.isLoading,
            backtestPerformanceAnalytics: backtestPerformanceAnalyticsQuery.isLoading,
            backtestTradeAnalytics: backtestTradeAnalyticsQuery.isLoading,
            backtestSummaryAnalytics: backtestSummaryAnalyticsQuery.isLoading,
            backtestHealthCheck: backtestHealthCheckQuery.isLoading,
        },
    }),
        [
            backtestListQuery,
            backtestResultsQuery,
            backtestPerformanceAnalyticsQuery,
            backtestTradeAnalyticsQuery,
            backtestSummaryAnalyticsQuery,
            backtestHealthCheckQuery,
            createBacktestMutation,
            updateBacktestMutation,
            deleteBacktestMutation,
        ]);


}


export const useBacktestDetail = (id: string) => {
    return useQuery({
        queryKey: backtestQueryKeys.detail(id),
        queryFn: async () => {
            const response = await BacktestService.getBacktest({ path: { backtest_id: id } });
            return response.data;
        },
        enabled: !!id,
        staleTime: 1000 * 60 * 5, // 5 minutes
        gcTime: 30 * 60 * 1000, // 30 minutes
    });
};
