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
    dailyPricesSymbol: (symbol: string, options?: { startDate?: string; endDate?: string }) => {
        const key = [...stockQueryKeys.dailyPrices(), symbol] as const;
        // undefined 값을 제거하여 일관된 키 생성
        const params: Record<string, string> = {};
        if (options?.startDate) params.startDate = options.startDate;
        if (options?.endDate) params.endDate = options.endDate;
        return Object.keys(params).length > 0 ? [...key, params] as const : key;
    },
    weeklyPrices: () => [...stockQueryKeys.all, "weeklyPrices"] as const,
    weeklyPricesSymbol: (symbol: string, options?: { startDate?: string; endDate?: string }) => {
        const key = [...stockQueryKeys.weeklyPrices(), symbol] as const;
        const params: Record<string, string> = {};
        if (options?.startDate) params.startDate = options.startDate;
        if (options?.endDate) params.endDate = options.endDate;
        return Object.keys(params).length > 0 ? [...key, params] as const : key;
    },
    monthlyPrices: () => [...stockQueryKeys.all, "monthlyPrices"] as const,
    monthlyPricesSymbol: (symbol: string, options?: { startDate?: string; endDate?: string }) => {
        const key = [...stockQueryKeys.monthlyPrices(), symbol] as const;
        const params: Record<string, string> = {};
        if (options?.startDate) params.startDate = options.startDate;
        if (options?.endDate) params.endDate = options.endDate;
        return Object.keys(params).length > 0 ? [...key, params] as const : key;
    },
    quote: () => [...stockQueryKeys.all, "quote"] as const,
    quoteSymbol: (symbol: string) => [...stockQueryKeys.quote(), symbol] as const,
    intraday: () => [...stockQueryKeys.all, "intraday"] as const,
    intradaySymbol: (symbol: string, interval?: string) => {
        const key = [...stockQueryKeys.intraday(), symbol] as const;
        return interval ? [...key, { interval }] as const : key;
    },
    historical: () => [...stockQueryKeys.all, "historical"] as const,
    historicalSymbol: (symbol: string, period?: string) => {
        const key = [...stockQueryKeys.historical(), symbol] as const;
        return period ? [...key, { period }] as const : key;
    },
    search: () => [...stockQueryKeys.all, "search"] as const,
    searchSymbols: (keywords: string) => [...stockQueryKeys.search(), keywords] as const,
};

export function useStocks() {
    return useMemo(() => ({
        queryKeys: stockQueryKeys,
    }), []);
}

// Individual hook functions for specific symbols
export const useStockDailyPrices = (
    symbol: string,
    options?: {
        outputsize?: "compact" | "full";
        startDate?: string;
        endDate?: string;
        enabled?: boolean;
    }
) => {
    const queryKey = stockQueryKeys.dailyPricesSymbol(symbol, {
        startDate: options?.startDate,
        endDate: options?.endDate,
    });

    return useQuery({
        queryKey,
        queryFn: async () => {
            console.log("🌐 API Call - Daily Prices:", {
                symbol,
                outputsize: options?.outputsize || "full",
                start_date: options?.startDate,
                end_date: options?.endDate,
                queryKey,
            });
            const response = await StockService.getDailyPrices({
                path: { symbol },
                query: {
                    outputsize: options?.outputsize || "full",
                    start_date: options?.startDate,
                    end_date: options?.endDate,
                } as any // Type assertion to bypass type checking for query params
            });
            console.log("✅ API Response - Daily Prices:", {
                symbol,
                dataLength: (response.data as any)?.data?.length || 0,
                response: response.data,
            });
            return response.data;
        },
        enabled: options?.enabled !== undefined ? options.enabled : !!symbol,
        staleTime: 0, // 캐싱 제거: 항상 stale로 간주
        gcTime: 0, // 캐싱 제거: 즉시 가비지 컬렉션
        refetchOnMount: true, // 마운트 시 항상 refetch
        refetchOnWindowFocus: false, // 윈도우 포커스 시 refetch 비활성화
    });
}; export const useStockWeeklyPrices = (
    symbol: string,
    options?: {
        outputsize?: "compact" | "full";
        startDate?: string;
        endDate?: string;
        enabled?: boolean;
    }
) => {
    const queryKey = stockQueryKeys.weeklyPricesSymbol(symbol, {
        startDate: options?.startDate,
        endDate: options?.endDate,
    });

    return useQuery({
        queryKey,
        queryFn: async () => {
            console.log("🌐 API Call - Weekly Prices:", {
                symbol,
                outputsize: options?.outputsize || "full",
                start_date: options?.startDate,
                end_date: options?.endDate,
                queryKey,
            });
            const response = await StockService.getWeeklyPrices({
                path: { symbol },
                query: {
                    outputsize: options?.outputsize || "full",
                    start_date: options?.startDate,
                    end_date: options?.endDate,
                } as any
            });
            console.log("✅ API Response - Weekly Prices:", {
                symbol,
                dataLength: (response.data as any)?.data?.length || 0,
                response: response.data,
            });
            return response.data;
        },
        enabled: options?.enabled !== undefined ? options.enabled : !!symbol,
        staleTime: 0, // 캐싱 제거: 항상 stale로 간주
        gcTime: 0, // 캐싱 제거: 즉시 가비지 컬렉션
        refetchOnMount: true, // 마운트 시 항상 refetch
        refetchOnWindowFocus: false, // 윈도우 포커스 시 refetch 비활성화
    });
};

export const useStockMonthlyPrices = (
    symbol: string,
    options?: {
        outputsize?: "compact" | "full";
        startDate?: string;
        endDate?: string;
        enabled?: boolean;
    }
) => {
    const queryKey = stockQueryKeys.monthlyPricesSymbol(symbol, {
        startDate: options?.startDate,
        endDate: options?.endDate,
    });

    return useQuery({
        queryKey,
        queryFn: async () => {
            console.log("🌐 API Call - Monthly Prices:", {
                symbol,
                outputsize: options?.outputsize || "full",
                start_date: options?.startDate,
                end_date: options?.endDate,
                queryKey,
            });
            const response = await StockService.getMonthlyPrices({
                path: { symbol },
                query: {
                    outputsize: options?.outputsize || "full",
                    start_date: options?.startDate,
                    end_date: options?.endDate,
                } as any
            });
            console.log("✅ API Response - Monthly Prices:", {
                symbol,
                dataLength: (response.data as any)?.data?.length || 0,
                response: response.data,
            });
            return response.data;
        },
        enabled: options?.enabled !== undefined ? options.enabled : !!symbol,
        staleTime: 0, // 캐싱 제거: 항상 stale로 간주
        gcTime: 0, // 캐싱 제거: 즉시 가비지 컬렉션
        refetchOnMount: true, // 마운트 시 항상 refetch
        refetchOnWindowFocus: false, // 윈도우 포커스 시 refetch 비활성화
    });
};

export const useStockQuote = (symbol: string) => {
    return useQuery({
        queryKey: stockQueryKeys.quoteSymbol(symbol),
        queryFn: async () => {
            const response = await StockService.getQuote({
                path: { symbol }
            });
            return response.data?.data;
        },
        enabled: !!symbol,
        staleTime: 1000 * 15, // 15 seconds (real-time quotes)
        gcTime: 2 * 60 * 1000, // 2 minutes
        refetchInterval: 1000 * 30, // Refetch every 30 seconds during market hours
    });
};

export const useStockIntraday = (
    symbol: string,
    options?: {
        interval?: "1min" | "5min" | "15min" | "30min" | "60min";
        enabled?: boolean;
    }
) => {
    const queryKey = stockQueryKeys.intradaySymbol(symbol, options?.interval);

    return useQuery({
        queryKey,
        queryFn: async () => {
            console.log("🌐 API Call - Intraday:", {
                symbol,
                interval: options?.interval,
                queryKey,
            });
            const response = await StockService.getIntradayData({
                path: { symbol },
                query: options?.interval ? { interval: options.interval } : undefined
            });
            console.log("✅ API Response - Intraday:", {
                symbol,
                dataLength: (response.data as any)?.data?.length || 0,
                response: response.data,
            });
            return response.data;
        },
        enabled: options?.enabled !== undefined ? options.enabled : !!symbol,
        staleTime: 0, // Always fetch fresh data for debugging
        gcTime: 5 * 60 * 1000, // 5 minutes
    });
};

export const useStockHistorical = (symbol: string, options?: {
    startDate?: string;
    endDate?: string;
    frequency?: string;
}, queryOptions?: { enabled?: boolean }) => {
    return useQuery({
        queryKey: stockQueryKeys.historicalSymbol(symbol, options?.frequency),
        queryFn: async () => {
            // 임시로 dailyPrices를 사용 (실제 historical API가 없는 경우)
            const response = await StockService.getDailyPrices({
                path: { symbol }
            });
            return response.data;
        },
        enabled: queryOptions?.enabled !== false && !!symbol,
        staleTime: 1000 * 60 * 10, // 10 minutes
        gcTime: 30 * 60 * 1000, // 30 minutes
    });
};

export const useStockSearchSymbols = (keywords: string) => {
    return useQuery({
        queryKey: stockQueryKeys.searchSymbols(keywords),
        queryFn: async () => {
            const response = await StockService.searchStockSymbols({
                query: { keywords }
            });
            return response.data;
        },
        enabled: !!keywords && keywords.length >= 2, // 최소 2글자 이상
        staleTime: 1000 * 60 * 5, // 5 minutes (search results are relatively stable)
        gcTime: 15 * 60 * 1000, // 15 minutes
        // placeholderData 제거 - 이전 데이터 유지가 문제를 일으킬 수 있음
    });
};
