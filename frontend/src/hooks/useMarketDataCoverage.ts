/**
 * useMarketDataCoverage - 종목별 데이터 커버리지 정보
 *
 * Epic 2: Story 2.2 - 데이터 수집 상태 모니터링
 */

import { MarketDataService } from "@/client";
import { useSnackbar } from "@/contexts/SnackbarContext";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

export const coverageQueryKeys = {
    all: ["coverage"] as const,
    symbol: (symbol: string) => [...coverageQueryKeys.all, symbol] as const,
};

export function useMarketDataCoverage(symbol: string) {
    const queryClient = useQueryClient();
    const { showSuccess, showError } = useSnackbar();

    // Coverage 정보 조회
    const coverageQuery = useQuery({
        queryKey: coverageQueryKeys.symbol(symbol),
        queryFn: async () => {
            const response = await MarketDataService.getDataCoverage({
                path: { symbol },
            });
            return response.data;
        },
        staleTime: 1000 * 60 * 5, // 5분
        gcTime: 10 * 60 * 1000, // 10분
        enabled: !!symbol,
    });

    // 기업 정보 수집
    const collectCompanyInfoMutation = useMutation({
        mutationFn: async (symbolToCollect: string) => {
            const response = await MarketDataService.collectCompanyInfo({
                path: { symbol: symbolToCollect },
            });
            return response.data;
        },
        onSuccess: (_, symbolCollected) => {
            queryClient.invalidateQueries({
                queryKey: coverageQueryKeys.symbol(symbolCollected),
            });
            showSuccess(`${symbolCollected} 기업 정보 수집이 완료되었습니다`);
        },
        onError: (error, symbolCollected) => {
            console.error("기업 정보 수집 실패:", error);
            showError(
                `${symbolCollected} 기업 정보 수집에 실패했습니다: ${error instanceof Error ? error.message : "알 수 없는 오류"}`
            );
        },
    });

    // 주가 데이터 수집
    const collectMarketDataMutation = useMutation({
        mutationFn: async (symbolToCollect: string) => {
            const response = await MarketDataService.collectMarketData({
                path: { symbol: symbolToCollect },
            });
            return response.data;
        },
        onSuccess: (_, symbolCollected) => {
            queryClient.invalidateQueries({
                queryKey: coverageQueryKeys.symbol(symbolCollected),
            });
            showSuccess(`${symbolCollected} 주가 데이터 수집이 완료되었습니다`);
        },
        onError: (error, symbolCollected) => {
            console.error("주가 데이터 수집 실패:", error);
            showError(
                `${symbolCollected} 주가 데이터 수집에 실패했습니다: ${error instanceof Error ? error.message : "알 수 없는 오류"}`
            );
        },
    });

    // 전체 데이터 수집 (기업 정보 + 주가 데이터)
    const collectAllDataMutation = useMutation({
        mutationFn: async (symbolToCollect: string) => {
            // 순차적으로 실행
            await collectCompanyInfoMutation.mutateAsync(symbolToCollect);
            await collectMarketDataMutation.mutateAsync(symbolToCollect);
        },
        onSuccess: (_, symbolCollected) => {
            queryClient.invalidateQueries({
                queryKey: coverageQueryKeys.symbol(symbolCollected),
            });
            showSuccess(`${symbolCollected} 전체 데이터 수집이 완료되었습니다`);
        },
        onError: (error, symbolCollected) => {
            console.error("전체 데이터 수집 실패:", error);
            showError(
                `${symbolCollected} 데이터 수집에 실패했습니다: ${error instanceof Error ? error.message : "알 수 없는 오류"}`
            );
        },
    });

    return {
        // Data
        coverage: coverageQuery.data,

        // Status
        isLoading: coverageQuery.isLoading,
        isError: coverageQuery.isError,
        error: coverageQuery.error,

        // Actions
        refetch: coverageQuery.refetch,
        collectCompanyInfo: collectCompanyInfoMutation.mutate,
        collectMarketData: collectMarketDataMutation.mutate,
        collectAllData: collectAllDataMutation.mutate,

        // Mutation status
        isCollecting:
            collectCompanyInfoMutation.isPending ||
            collectMarketDataMutation.isPending ||
            collectAllDataMutation.isPending,
    };
}
