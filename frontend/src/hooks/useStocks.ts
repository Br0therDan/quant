// MarketData - Stock Module API
// TanStack Query (v5.9) 기반 Query 및 및 Mutation 활용 상태관리 및 데이터 패칭 훅
// 성능 최적화 및 캐싱, 에러 핸들링, 로딩 상태 관리 포함
// Hook은 useStock 단일/통합 사용 (별도의 추가 훅 생성 불필요)
// Hey-API 기반: @/client/sdk.gen.ts 의 각 엔드포인트별 서비스클래스 및 @/client/types.gen.ts 의 타입정의 활용(엔드포인트의 스키마명칭과 호환)

import { StockService } from "@/client";
import { useQuery } from "@tanstack/react-query";
import { useMemo } from "react";

export const stockQueryKeys = {
    all: ["stock"] as const,
    dailyPrices: () => [...stockQueryKeys.all, "dailyPrices"] as const,
    dailyPricesSymbol: (symbol: string) => [...stockQueryKeys.dailyPrices(), symbol] as const,
    quote: () => [...stockQueryKeys.all, "quote"] as const,
    quoteSymbol: (symbol: string) => [...stockQueryKeys.quote(), symbol] as const,
    intraday: () => [...stockQueryKeys.all, "intraday"] as const,
    intradaySymbol: (symbol: string, interval?: string) => [...stockQueryKeys.intraday(), symbol, { interval }] as const,
    historical: () => [...stockQueryKeys.all, "historical"] as const,
    historicalSymbol: (symbol: string, period?: string) => [...stockQueryKeys.historical(), symbol, { period }] as const,
};

export function useStocks() {
    return useMemo(() => ({
        queryKeys: stockQueryKeys,
    }), []);
}

// Individual hook functions for specific symbols
export const useStockDailyPrices = (symbol: string) => {
    return useQuery({
        queryKey: stockQueryKeys.dailyPricesSymbol(symbol),
        queryFn: async () => {
            const response = await StockService.getDailyPrices({
                path: { symbol }
            });
            return response.data;
        },
        enabled: !!symbol,
        staleTime: 1000 * 60 * 5, // 5 minutes (daily prices don't change during trading day)
        gcTime: 30 * 60 * 1000, // 30 minutes
    });
};

export const useStockQuote = (symbol: string) => {
    return useQuery({
        queryKey: stockQueryKeys.quoteSymbol(symbol),
        queryFn: async () => {
            const response = await StockService.getQuote({
                path: { symbol }
            });
            return response.data;
        },
        enabled: !!symbol,
        staleTime: 1000 * 15, // 15 seconds (real-time quotes)
        gcTime: 2 * 60 * 1000, // 2 minutes
        refetchInterval: 1000 * 30, // Refetch every 30 seconds during market hours
    });
};

export const useStockIntraday = (symbol: string, interval?: string) => {
    return useQuery({
        queryKey: stockQueryKeys.intradaySymbol(symbol, interval),
        queryFn: async () => {
            const response = await StockService.getIntradayData({
                path: { symbol },
                query: interval ? { interval } : undefined
            });
            return response.data;
        },
        enabled: !!symbol,
        staleTime: 1000 * 60, // 1 minute
        gcTime: 5 * 60 * 1000, // 5 minutes
    });
};

export const useStockHistorical = (symbol: string, options?: { startDate?: string; endDate?: string; frequency?: string }) => {
    return useQuery({
        queryKey: stockQueryKeys.historicalSymbol(symbol, options?.frequency),
        queryFn: async () => {
            const response = await StockService.getHistoricalData({
                path: { symbol },
                query: options ? {
                    start_date: options.startDate,
                    end_date: options.endDate,
                    frequency: options.frequency
                } : undefined
            });
            return response.data;
        },
        enabled: !!symbol,
        staleTime: 1000 * 60 * 60, // 1 hour (historical data doesn't change frequently)
        gcTime: 4 * 60 * 60 * 1000, // 4 hours
    });
};
