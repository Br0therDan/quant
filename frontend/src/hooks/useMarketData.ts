// MarketData - Management/Info/Health 엔드포인트 Module API
// TanStack Query (v5.9) 기반 Query 및 및 Mutation 활용 상태관리 및 데이터 패칭 훅
// 성능 최적화 및 캐싱, 에러 핸들링, 로딩 상태 관리 포함
// Hook은 useMarketData 단일/통합 사용 (별도의 추가 훅 생성 불필요)
// Hey-API 기반: @/client/sdk.gen.ts 의 각 엔드포인트별 서비스클래스 및 @/client/types.gen.ts 의 타입정의 활용(엔드포인트의 스키마명칭과 호환)

import { MarketDataService } from "@/client";
import { useSnackbar } from "@/contexts/SnackbarContext";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo } from "react";

export const marketDataQueryKeys = {
    all: ["marketData"] as const,
    info: () => [...marketDataQueryKeys.all, "info"] as const,
    health: () => [...marketDataQueryKeys.all, "health"] as const,
    systemStatus: () => [...marketDataQueryKeys.all, "systemStatus"] as const,
    coverage: () => [...marketDataQueryKeys.all, "coverage"] as const,
    coverageSymbol: (symbol: string) => [...marketDataQueryKeys.coverage(), symbol] as const,
    collection: () => [...marketDataQueryKeys.all, "collection"] as const,
};

export function useMarketData() {
    const queryClient = useQueryClient();
    const { showSuccess, showError } = useSnackbar();

    // Queries
    const marketDataInfoQuery = useQuery({
        queryKey: marketDataQueryKeys.info(),
        queryFn: async () => {
            const response = await MarketDataService.getMarketDataInfo();
            return response.data;
        },
        staleTime: 1000 * 60 * 30, // 30 minutes (info doesn't change often)
        gcTime: 2 * 60 * 60 * 1000, // 2 hours
    });

    const healthCheckQuery = useQuery({
        queryKey: marketDataQueryKeys.health(),
        queryFn: async () => {
            const response = await MarketDataService.healthCheck();
            return response.data;
        },
        staleTime: 1000 * 30, // 30 seconds (health status should be fresh)
        gcTime: 2 * 60 * 1000, // 2 minutes
        refetchInterval: 1000 * 60, // Refetch every minute
    });

    const systemStatusQuery = useQuery({
        queryKey: marketDataQueryKeys.systemStatus(),
        queryFn: async () => {
            const response = await MarketDataService.getSystemStatus();
            return response.data;
        },
        staleTime: 1000 * 60, // 1 minute
        gcTime: 10 * 60 * 1000, // 10 minutes
    });

    // Mutations
    const collectCompanyInfoMutation = useMutation({
        mutationFn: async (symbol: string) => {
            const response = await MarketDataService.collectCompanyInfo({
                path: { symbol }
            });
            return response.data;
        },
        onSuccess: (_, symbol) => {
            queryClient.invalidateQueries({ queryKey: marketDataQueryKeys.coverageSymbol(symbol) });
            queryClient.invalidateQueries({ queryKey: marketDataQueryKeys.systemStatus() });
            showSuccess(`${symbol} 기업 정보 수집이 완료되었습니다`);
        },
        onError: (error, symbol) => {
            console.error("기업 정보 수집 실패:", error);
            showError(`${symbol} 기업 정보 수집에 실패했습니다: ${error instanceof Error ? error.message : '알 수 없는 오류'}`);
        },
    });

    const collectMarketDataMutation = useMutation({
        mutationFn: async (symbol: string) => {
            const response = await MarketDataService.collectMarketData({
                path: { symbol }
            });
            return response.data;
        },
        onSuccess: (_, symbol) => {
            queryClient.invalidateQueries({ queryKey: marketDataQueryKeys.coverageSymbol(symbol) });
            queryClient.invalidateQueries({ queryKey: marketDataQueryKeys.systemStatus() });
            showSuccess(`${symbol} 주가 데이터 수집이 완료되었습니다`);
        },
        onError: (error, symbol) => {
            console.error("주가 데이터 수집 실패:", error);
            showError(`${symbol} 주가 데이터 수집에 실패했습니다: ${error instanceof Error ? error.message : '알 수 없는 오류'}`);
        },
    });

    const collectBulkDataMutation = useMutation({
        mutationFn: async (symbols: string[]) => {
            const response = await MarketDataService.collectBulkData({
                query: { symbols }
            });
            return response.data;
        },
        onSuccess: (_, symbols) => {
            queryClient.invalidateQueries({ queryKey: marketDataQueryKeys.coverage() });
            queryClient.invalidateQueries({ queryKey: marketDataQueryKeys.systemStatus() });
            showSuccess(`${symbols.length}개 종목의 데이터 수집이 시작되었습니다`);
        },
        onError: (error) => {
            console.error("대량 데이터 수집 실패:", error);
            showError(`대량 데이터 수집에 실패했습니다: ${error instanceof Error ? error.message : '알 수 없는 오류'}`);
        },
    });

    return useMemo(() => ({

        // Data
        marketDataInfo: marketDataInfoQuery.data,
        healthCheck: healthCheckQuery.data,
        systemStatus: systemStatusQuery.data,

        // Status
        isError: {
            marketDataInfo: marketDataInfoQuery.isError,
            healthCheck: healthCheckQuery.isError,
            systemStatus: systemStatusQuery.isError,
        },
        isLoading: {
            marketDataInfo: marketDataInfoQuery.isLoading,
            healthCheck: healthCheckQuery.isLoading,
            systemStatus: systemStatusQuery.isLoading,
        },
        isPending: {
            marketDataInfo: marketDataInfoQuery.isPending,
            healthCheck: healthCheckQuery.isPending,
            systemStatus: systemStatusQuery.isPending,
        },
        error: {
            marketDataInfo: marketDataInfoQuery.error,
            healthCheck: healthCheckQuery.error,
            systemStatus: systemStatusQuery.error,
        },

        // Actions
        refetch: {
            marketDataInfo: marketDataInfoQuery.refetch,
            healthCheck: healthCheckQuery.refetch,
            systemStatus: systemStatusQuery.refetch,
        },

        // Mutations
        collectCompanyInfo: collectCompanyInfoMutation.mutate,
        collectMarketData: collectMarketDataMutation.mutate,
        collectBulkData: collectBulkDataMutation.mutate,

        // Mutation Status
        isCollecting: {
            companyInfo: collectCompanyInfoMutation.isPending,
            marketData: collectMarketDataMutation.isPending,
            bulkData: collectBulkDataMutation.isPending,
        },

        // Query Objects (if needed for advanced usage)
        queries: {
            marketDataInfoQuery,
            healthCheckQuery,
            systemStatusQuery,
        },
        mutations: {
            collectCompanyInfoMutation,
            collectMarketDataMutation,
            collectBulkDataMutation,
        },

    }), [
        marketDataInfoQuery,
        healthCheckQuery,
        systemStatusQuery,
        collectCompanyInfoMutation,
        collectMarketDataMutation,
        collectBulkDataMutation,
    ]);
}

// Individual hook for data coverage by symbol
export const useMarketDataCoverage = (symbol: string) => {
    return useQuery({
        queryKey: marketDataQueryKeys.coverageSymbol(symbol),
        queryFn: async () => {
            const response = await MarketDataService.getDataCoverage({
                path: { symbol }
            });
            return response.data;
        },
        enabled: !!symbol,
        staleTime: 1000 * 60 * 5, // 5 minutes
        gcTime: 30 * 60 * 1000, // 30 minutes
    });
};
