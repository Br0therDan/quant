// Watchlist Module API
// TanStack Query (v5.9) 기반 Query 및 및 Mutation 활용 상태관리 및 데이터 패칭 훅
// 성능 최적화 및 캐싱, 에러 핸들링, 로딩 상태 관리 포함
// Hook은 useWatchlist 단일/통합 사용 (별도의 추가 훅 생성 불필요)
// Hey-API 기반: @/client/sdk.gen.ts 의 각 엔드포인트별 서비스클래스 및 @/client/types.gen.ts 의 타입정의 활용(엔드포인트의 스키마명칭과 호환)

import { WatchlistService } from "@/client";
import type { WatchlistCreate, WatchlistUpdate } from "@/client";
import { useSnackbar } from "@/contexts/SnackbarContext";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo } from "react";

export const watchlistQueryKeys = {
    all: ["watchlist"] as const,
    lists: () => [...watchlistQueryKeys.all, "list"] as const,
    details: () => [...watchlistQueryKeys.all, "detail"] as const,
    detail: (name: string) => [...watchlistQueryKeys.details(), name] as const,
    coverage: () => [...watchlistQueryKeys.all, "coverage"] as const,
    watchlistCoverage: (name: string) => [...watchlistQueryKeys.coverage(), name] as const,
};

export function useWatchlist() {
    const queryClient = useQueryClient();
    const { showSuccess, showError } = useSnackbar();

    // Queries
    const watchlistListQuery = useQuery({
        queryKey: watchlistQueryKeys.lists(),
        queryFn: async () => {
            const response = await WatchlistService.listWatchlists();
            return response.data;
        },
        staleTime: 1000 * 60 * 5, // 5 minutes
        gcTime: 30 * 60 * 1000, // 30 minutes
    });

    // Mutations
    const createWatchlistMutation = useMutation({
        mutationFn: async (data: any) => {
            const response = await WatchlistService.createWatchlist({
                body: data
            });
            return response.data;
        },
        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({ queryKey: watchlistQueryKeys.lists() });
            showSuccess(`워치리스트 "${variables?.name || '새 워치리스트'}"가 성공적으로 생성되었습니다`);
        },
        onError: (error) => {
            console.error("워치리스트 생성 실패:", error);
            showError(error instanceof Error ? error.message : '워치리스트 생성에 실패했습니다');
        },
    });

    const createOrUpdateWatchlistMutation = useMutation({
        mutationFn: async (data: WatchlistCreate) => {
            const response = await WatchlistService.createOrUpdateWatchlist({
                body: data
            });
            return response.data;
        },
        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({ queryKey: watchlistQueryKeys.lists() });
            if (variables?.name) {
                queryClient.invalidateQueries({ queryKey: watchlistQueryKeys.detail(variables.name) });
            }
            showSuccess(`워치리스트 "${variables?.name || 'default'}"가 성공적으로 저장되었습니다`);
        },
        onError: (error) => {
            console.error("워치리스트 저장 실패:", error);
            showError(error instanceof Error ? error.message : '워치리스트 저장에 실패했습니다');
        },
    });

    const updateWatchlistMutation = useMutation({
        mutationFn: async ({name, updateData}: { name: string; updateData: WatchlistUpdate }) => {
            const response = await WatchlistService.updateWatchlist({
                path: { name },
                body: updateData
            });
            return response.data;
        },
        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({ queryKey: watchlistQueryKeys.lists() });
            queryClient.invalidateQueries({ queryKey: watchlistQueryKeys.detail(variables.name) });
            showSuccess(`워치리스트 "${variables.name}"가 성공적으로 업데이트되었습니다`);
        },
        onError: (error, variables) => {
            console.error("워치리스트 업데이트 실패:", error);
            showError(`워치리스트 "${variables.name}" 업데이트에 실패했습니다: ${error instanceof Error ? error.message : '알 수 없는 오류'}`);
        },
    });

    const deleteWatchlistMutation = useMutation({
        mutationFn: async (name: string) => {
            const response = await WatchlistService.deleteWatchlist({
                path: { name }
            });
            return response.data;
        },
        onSuccess: (_, name) => {
            queryClient.invalidateQueries({ queryKey: watchlistQueryKeys.lists() });
            queryClient.removeQueries({ queryKey: watchlistQueryKeys.detail(name) });
            showSuccess(`워치리스트 "${name}"가 성공적으로 삭제되었습니다`);
        },
        onError: (error, name) => {
            console.error("워치리스트 삭제 실패:", error);
            showError(`워치리스트 "${name}" 삭제에 실패했습니다: ${error instanceof Error ? error.message : '알 수 없는 오류'}`);
        },
    });

    const setupDefaultWatchlistMutation = useMutation({
        mutationFn: async () => {
            const response = await WatchlistService.setupDefaultWatchlist();
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: watchlistQueryKeys.lists() });
            queryClient.invalidateQueries({ queryKey: watchlistQueryKeys.detail('default') });
            showSuccess('기본 워치리스트가 성공적으로 설정되었습니다');
        },
        onError: (error) => {
            console.error("기본 워치리스트 설정 실패:", error);
            showError(error instanceof Error ? error.message : '기본 워치리스트 설정에 실패했습니다');
        },
    });

    return useMemo(() => ({

        // Data
        watchlistList: watchlistListQuery.data,

        // Status
        isError: {
            watchlistList: watchlistListQuery.isError,
        },
        isLoading: {
            watchlistList: watchlistListQuery.isLoading,
        },
        isPending: {
            watchlistList: watchlistListQuery.isPending,
        },
        error: {
            watchlistList: watchlistListQuery.error,
        },

        // Actions
        refetch: {
            watchlistList: watchlistListQuery.refetch,
        },

        // Mutations
        createWatchlist: createWatchlistMutation.mutate,
        createOrUpdateWatchlist: createOrUpdateWatchlistMutation.mutate,
        updateWatchlist: updateWatchlistMutation.mutate,
        deleteWatchlist: deleteWatchlistMutation.mutate,
        setupDefaultWatchlist: setupDefaultWatchlistMutation.mutate,

        // Mutation Status
        isMutating: {
            createWatchlist: createWatchlistMutation.isPending,
            createOrUpdateWatchlist: createOrUpdateWatchlistMutation.isPending,
            updateWatchlist: updateWatchlistMutation.isPending,
            deleteWatchlist: deleteWatchlistMutation.isPending,
            setupDefaultWatchlist: setupDefaultWatchlistMutation.isPending,
        },

        // Query Objects (if needed for advanced usage)
        queries: {
            watchlistListQuery,
        },
        mutations: {
            createWatchlistMutation,
            createOrUpdateWatchlistMutation,
            updateWatchlistMutation,
            deleteWatchlistMutation,
            setupDefaultWatchlistMutation,
        },

    }), [
        watchlistListQuery,
        createWatchlistMutation,
        createOrUpdateWatchlistMutation,
        updateWatchlistMutation,
        deleteWatchlistMutation,
        setupDefaultWatchlistMutation,
    ]);
}

// Individual hook for watchlist detail
export const useWatchlistDetail = (name: string) => {
    return useQuery({
        queryKey: watchlistQueryKeys.detail(name),
        queryFn: async () => {
            const response = await WatchlistService.getWatchlist({
                path: { name }
            });
            return response.data;
        },
        enabled: !!name,
        staleTime: 1000 * 60 * 2, // 2 minutes (watchlist data can change frequently)
        gcTime: 10 * 60 * 1000, // 10 minutes
    });
};

// Individual hook for watchlist coverage
export const useWatchlistCoverage = (name: string) => {
    return useQuery({
        queryKey: watchlistQueryKeys.watchlistCoverage(name),
        queryFn: async () => {
            const response = await WatchlistService.getWatchlistCoverage({
                path: { name }
            });
            return response.data;
        },
        enabled: !!name,
        staleTime: 1000 * 60 * 5, // 5 minutes
        gcTime: 30 * 60 * 1000, // 30 minutes
    });
};
