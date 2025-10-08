// MarketData - Economic Indicators Module API
// TanStack Query (v5.9) 기반 Query 및 및 Mutation 활용 상태관리 및 데이터 패칭 훅
// 성능 최적화 및 캐싱, 에러 핸들링, 로딩 상태 관리 포함
// Hook은 useEconomic 단일/통합 사용 (별도의 추가 훅 생성 불필요)
// Hey-API 기반: @/client/sdk.gen.ts 의 각 엔드포인트별 서비스클래스 및 @/client/types.gen.ts 의 타입정의 활용(엔드포인트의 스키마명칭과 호환)

import { EconomicService } from "@/client";
import { useQuery } from "@tanstack/react-query";
import { useMemo } from "react";

export const economicQueryKeys = {
    all: ["economic"] as const,
    gdp: () => [...economicQueryKeys.all, "gdp"] as const,
    inflation: () => [...economicQueryKeys.all, "inflation"] as const,
    interestRates: () => [...economicQueryKeys.all, "interest-rates"] as const,
    employment: () => [...economicQueryKeys.all, "employment"] as const,
    consumerSentiment: () => [...economicQueryKeys.all, "consumer-sentiment"] as const,
};

export function useEconomic() {

    // Queries
    const gdpDataQuery = useQuery({
        queryKey: economicQueryKeys.gdp(),
        queryFn: async () => {
            const response = await EconomicService.getGdpData();
            return response.data;
        },
        staleTime: 1000 * 60 * 60, // 1 hour (economic data updates infrequently)
        gcTime: 4 * 60 * 60 * 1000, // 4 hours
    });

    const inflationDataQuery = useQuery({
        queryKey: economicQueryKeys.inflation(),
        queryFn: async () => {
            const response = await EconomicService.getInflationData();
            return response.data;
        },
        staleTime: 1000 * 60 * 60, // 1 hour
        gcTime: 4 * 60 * 60 * 1000, // 4 hours
    });

    const interestRatesQuery = useQuery({
        queryKey: economicQueryKeys.interestRates(),
        queryFn: async () => {
            const response = await EconomicService.getInterestRates();
            return response.data;
        },
        staleTime: 1000 * 60 * 30, // 30 minutes (interest rates can change more frequently)
        gcTime: 2 * 60 * 60 * 1000, // 2 hours
    });

    const employmentDataQuery = useQuery({
        queryKey: economicQueryKeys.employment(),
        queryFn: async () => {
            const response = await EconomicService.getEmploymentData();
            return response.data;
        },
        staleTime: 1000 * 60 * 60, // 1 hour
        gcTime: 4 * 60 * 60 * 1000, // 4 hours
    });

    const consumerSentimentQuery = useQuery({
        queryKey: economicQueryKeys.consumerSentiment(),
        queryFn: async () => {
            const response = await EconomicService.getConsumerSentiment();
            return response.data;
        },
        staleTime: 1000 * 60 * 60, // 1 hour
        gcTime: 4 * 60 * 60 * 1000, // 4 hours
    });

    return useMemo(() => ({

        // Data
        gdpData: gdpDataQuery.data,
        inflationData: inflationDataQuery.data,
        interestRates: interestRatesQuery.data,
        employmentData: employmentDataQuery.data,
        consumerSentiment: consumerSentimentQuery.data,

        // Status
        isError: {
            gdpData: gdpDataQuery.isError,
            inflationData: inflationDataQuery.isError,
            interestRates: interestRatesQuery.isError,
            employmentData: employmentDataQuery.isError,
            consumerSentiment: consumerSentimentQuery.isError,
        },
        isLoading: {
            gdpData: gdpDataQuery.isLoading,
            inflationData: inflationDataQuery.isLoading,
            interestRates: interestRatesQuery.isLoading,
            employmentData: employmentDataQuery.isLoading,
            consumerSentiment: consumerSentimentQuery.isLoading,
        },
        isPending: {
            gdpData: gdpDataQuery.isPending,
            inflationData: inflationDataQuery.isPending,
            interestRates: interestRatesQuery.isPending,
            employmentData: employmentDataQuery.isPending,
            consumerSentiment: consumerSentimentQuery.isPending,
        },
        error: {
            gdpData: gdpDataQuery.error,
            inflationData: inflationDataQuery.error,
            interestRates: interestRatesQuery.error,
            employmentData: employmentDataQuery.error,
            consumerSentiment: consumerSentimentQuery.error,
        },

        // Actions
        refetch: {
            gdpData: gdpDataQuery.refetch,
            inflationData: inflationDataQuery.refetch,
            interestRates: interestRatesQuery.refetch,
            employmentData: employmentDataQuery.refetch,
            consumerSentiment: consumerSentimentQuery.refetch,
        },

        // Query Objects (if needed for advanced usage)
        queries: {
            gdpDataQuery,
            inflationDataQuery,
            interestRatesQuery,
            employmentDataQuery,
            consumerSentimentQuery,
        },

    }), [
        gdpDataQuery,
        inflationDataQuery,
        interestRatesQuery,
        employmentDataQuery,
        consumerSentimentQuery,
    ]);
}
