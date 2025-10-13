// MarketData - Crypto Module API
// TanStack Query (v5.9) 기반 Query 및 Mutation 활용 상태관리 및 데이터 패칭 훅
// 성능 최적화 및 캐싱, 에러 핸들링, 로딩 상태 관리 포함
// Hook은 useCrypto 단일/통합 사용 (별도의 추가 훅 생성 불필요)
// Hey-API 기반: @/client/sdk.gen.ts 의 각 엔드포인트별 서비스클래스 및 @/client/types.gen.ts 의 타입정의 활용(엔드포인트의 스키마명칭과 호환)

import { CryptoService } from "@/client";
import { useQuery } from "@tanstack/react-query";
import { useMemo } from "react";

export const cryptoQueryKeys = {
    all: ["crypto"] as const,
    exchangeRate: () => [...cryptoQueryKeys.all, "exchangeRate"] as const,
    exchangeRatePair: (fromCurrency: string, toCurrency: string) =>
        [...cryptoQueryKeys.exchangeRate(), fromCurrency, toCurrency] as const,
    bulkExchangeRates: () =>
        [...cryptoQueryKeys.all, "bulkExchangeRates"] as const,
    bulkExchangeRatesPair: (
        fromCurrency: string,
        toCurrencies: string[],
    ) =>
        [
            ...cryptoQueryKeys.bulkExchangeRates(),
            fromCurrency,
            ...toCurrencies.sort(),
        ] as const,
    dailyPrices: () => [...cryptoQueryKeys.all, "dailyPrices"] as const,
    dailyPricesSymbol: (
        symbol: string,
        market: string,
        options?: { startDate?: string; endDate?: string },
    ) => {
        const key = [...cryptoQueryKeys.dailyPrices(), symbol, market] as const;
        const params: Record<string, string> = {};
        if (options?.startDate) params.startDate = options.startDate;
        if (options?.endDate) params.endDate = options.endDate;
        return Object.keys(params).length > 0
            ? ([...key, params] as const)
            : key;
    },
    weeklyPrices: () => [...cryptoQueryKeys.all, "weeklyPrices"] as const,
    weeklyPricesSymbol: (
        symbol: string,
        market: string,
        options?: { startDate?: string; endDate?: string },
    ) => {
        const key = [
            ...cryptoQueryKeys.weeklyPrices(),
            symbol,
            market,
        ] as const;
        const params: Record<string, string> = {};
        if (options?.startDate) params.startDate = options.startDate;
        if (options?.endDate) params.endDate = options.endDate;
        return Object.keys(params).length > 0
            ? ([...key, params] as const)
            : key;
    },
    monthlyPrices: () => [...cryptoQueryKeys.all, "monthlyPrices"] as const,
    monthlyPricesSymbol: (
        symbol: string,
        market: string,
        options?: { startDate?: string; endDate?: string },
    ) => {
        const key = [
            ...cryptoQueryKeys.monthlyPrices(),
            symbol,
            market,
        ] as const;
        const params: Record<string, string> = {};
        if (options?.startDate) params.startDate = options.startDate;
        if (options?.endDate) params.endDate = options.endDate;
        return Object.keys(params).length > 0
            ? ([...key, params] as const)
            : key;
    },
    bitcoinPrice: () => [...cryptoQueryKeys.all, "bitcoinPrice"] as const,
    bitcoinPriceMarket: (market: string) =>
        [...cryptoQueryKeys.bitcoinPrice(), market] as const,
    ethereumPrice: () => [...cryptoQueryKeys.all, "ethereumPrice"] as const,
    ethereumPriceMarket: (market: string) =>
        [...cryptoQueryKeys.ethereumPrice(), market] as const,
};

export function useCrypto() {
    return useMemo(
        () => ({
            queryKeys: cryptoQueryKeys,
        }),
        [],
    );
}

// Individual hook functions for specific crypto operations
export const useCryptoExchangeRate = (
    fromCurrency: string,
    toCurrency: string,
    options?: { enabled?: boolean },
) => {
    const queryKey = cryptoQueryKeys.exchangeRatePair(
        fromCurrency,
        toCurrency,
    );

    return useQuery({
        queryKey,
        queryFn: async () => {
            console.log("🌐 API Call - Crypto Exchange Rate:", {
                fromCurrency,
                toCurrency,
                queryKey,
            });
            const response = await CryptoService.getExchangeRate({
                path: { from_currency: fromCurrency, to_currency: toCurrency },
            });
            console.log("✅ API Response - Crypto Exchange Rate:", {
                fromCurrency,
                toCurrency,
                response: response.data,
            });
            return response.data;
        },
        enabled:
            options?.enabled !== undefined
                ? options.enabled
                : !!(fromCurrency && toCurrency),
        staleTime: 1000 * 30, // 30 seconds (real-time rates)
        gcTime: 2 * 60 * 1000, // 2 minutes
        refetchInterval: 1000 * 60, // Refetch every 60 seconds
    });
};

export const useCryptoBulkExchangeRates = (
    fromCurrency: string,
    toCurrencies: string[],
    options?: { enabled?: boolean },
) => {
    const queryKey = cryptoQueryKeys.bulkExchangeRatesPair(
        fromCurrency,
        toCurrencies,
    );

    return useQuery({
        queryKey,
        queryFn: async () => {
            console.log("🌐 API Call - Crypto Bulk Exchange Rates:", {
                fromCurrency,
                toCurrencies,
                queryKey,
            });
            const response = await CryptoService.getBulkExchangeRates({
                query: {
                    crypto_symbols: toCurrencies,
                    target_currency: fromCurrency
                },
            });
            console.log("✅ API Response - Crypto Bulk Exchange Rates:", {
                fromCurrency,
                toCurrencies,
                response: response.data,
            });
            return response.data;
        },
        enabled:
            options?.enabled !== undefined
                ? options.enabled
                : !!(fromCurrency && toCurrencies.length > 0),
        staleTime: 1000 * 30, // 30 seconds
        gcTime: 2 * 60 * 1000, // 2 minutes
        refetchInterval: 1000 * 60, // Refetch every 60 seconds
    });
};

export const useCryptoDailyPrices = (
    symbol: string,
    market: string,
    options?: {
        startDate?: string;
        endDate?: string;
        enabled?: boolean;
    },
) => {
    const queryKey = cryptoQueryKeys.dailyPricesSymbol(symbol, market, {
        startDate: options?.startDate,
        endDate: options?.endDate,
    });

    return useQuery({
        queryKey,
        queryFn: async () => {
            console.log("🌐 API Call - Crypto Daily Prices:", {
                symbol,
                market,
                start_date: options?.startDate,
                end_date: options?.endDate,
                queryKey,
            });
            const response = await CryptoService.getDailyPrices({
                path: { symbol },
                query: {
                    market,
                    start_date: options?.startDate,
                    end_date: options?.endDate,
                } as any,
            });
            console.log("✅ API Response - Crypto Daily Prices:", {
                symbol,
                market,
                dataLength: (response.data as any)?.data?.length || 0,
                response: response.data,
            });
            return response.data;
        },
        enabled:
            options?.enabled !== undefined
                ? options.enabled
                : !!(symbol && market),
        staleTime: 0, // 캐싱 제거: 항상 stale로 간주
        gcTime: 0, // 캐싱 제거: 즉시 가비지 컬렉션
        refetchOnMount: true, // 마운트 시 항상 refetch
        refetchOnWindowFocus: false, // 윈도우 포커스 시 refetch 비활성화
    });
};

export const useCryptoWeeklyPrices = (
    symbol: string,
    market: string,
    options?: {
        startDate?: string;
        endDate?: string;
        enabled?: boolean;
    },
) => {
    const queryKey = cryptoQueryKeys.weeklyPricesSymbol(symbol, market, {
        startDate: options?.startDate,
        endDate: options?.endDate,
    });

    return useQuery({
        queryKey,
        queryFn: async () => {
            console.log("🌐 API Call - Crypto Weekly Prices:", {
                symbol,
                market,
                start_date: options?.startDate,
                end_date: options?.endDate,
                queryKey,
            });
            const response = await CryptoService.getWeeklyPrices({
                path: { symbol },
                query: {
                    market,
                    start_date: options?.startDate,
                    end_date: options?.endDate,
                } as any,
            });
            console.log("✅ API Response - Crypto Weekly Prices:", {
                symbol,
                market,
                dataLength: (response.data as any)?.data?.length || 0,
                response: response.data,
            });
            return response.data;
        },
        enabled:
            options?.enabled !== undefined
                ? options.enabled
                : !!(symbol && market),
        staleTime: 0, // 캐싱 제거: 항상 stale로 간주
        gcTime: 0, // 캐싱 제거: 즉시 가비지 컬렉션
        refetchOnMount: true, // 마운트 시 항상 refetch
        refetchOnWindowFocus: false, // 윈도우 포커스 시 refetch 비활성화
    });
};

export const useCryptoMonthlyPrices = (
    symbol: string,
    market: string,
    options?: {
        startDate?: string;
        endDate?: string;
        enabled?: boolean;
    },
) => {
    const queryKey = cryptoQueryKeys.monthlyPricesSymbol(symbol, market, {
        startDate: options?.startDate,
        endDate: options?.endDate,
    });

    return useQuery({
        queryKey,
        queryFn: async () => {
            console.log("🌐 API Call - Crypto Monthly Prices:", {
                symbol,
                market,
                start_date: options?.startDate,
                end_date: options?.endDate,
                queryKey,
            });
            const response = await CryptoService.getMonthlyPrices({
                path: { symbol },
                query: {
                    market,
                    start_date: options?.startDate,
                    end_date: options?.endDate,
                } as any,
            });
            console.log("✅ API Response - Crypto Monthly Prices:", {
                symbol,
                market,
                dataLength: (response.data as any)?.data?.length || 0,
                response: response.data,
            });
            return response.data;
        },
        enabled:
            options?.enabled !== undefined
                ? options.enabled
                : !!(symbol && market),
        staleTime: 0, // 캐싱 제거: 항상 stale로 간주
        gcTime: 0, // 캐싱 제거: 즉시 가비지 컬렉션
        refetchOnMount: true, // 마운트 시 항상 refetch
        refetchOnWindowFocus: false, // 윈도우 포커스 시 refetch 비활성화
    });
};

export const useBitcoinPrice = (
    period: "daily" | "weekly" | "monthly" = "daily",
    market = "USD",
    options?: {
        startDate?: string;
        endDate?: string;
        enabled?: boolean
    },
) => {
    const queryKey = cryptoQueryKeys.bitcoinPriceMarket(market);

    return useQuery({
        queryKey,
        queryFn: async () => {
            console.log("🌐 API Call - Bitcoin Price:", {
                period,
                market,
                start_date: options?.startDate,
                end_date: options?.endDate,
                queryKey,
            });
            const response = await CryptoService.getBitcoinPrice({
                path: { period },
                query: {
                    market,
                    start_date: options?.startDate,
                    end_date: options?.endDate,
                } as any,
            });
            console.log("✅ API Response - Bitcoin Price:", {
                period,
                market,
                response: response.data,
            });
            return response.data;
        },
        enabled: options?.enabled !== undefined ? options.enabled : !!market,
        staleTime: 1000 * 30, // 30 seconds (real-time price)
        gcTime: 2 * 60 * 1000, // 2 minutes
        refetchInterval: 1000 * 60, // Refetch every 60 seconds
    });
};

export const useEthereumPrice = (
    period: "daily" | "weekly" | "monthly" = "daily",
    market = "USD",
    options?: {
        startDate?: string;
        endDate?: string;
        enabled?: boolean
    },
) => {
    const queryKey = cryptoQueryKeys.ethereumPriceMarket(market);

    return useQuery({
        queryKey,
        queryFn: async () => {
            console.log("🌐 API Call - Ethereum Price:", {
                period,
                market,
                start_date: options?.startDate,
                end_date: options?.endDate,
                queryKey,
            });
            const response = await CryptoService.getEthereumPrice({
                path: { period },
                query: {
                    market,
                    start_date: options?.startDate,
                    end_date: options?.endDate,
                } as any,
            });
            console.log("✅ API Response - Ethereum Price:", {
                period,
                market,
                response: response.data,
            });
            return response.data;
        },
        enabled: options?.enabled !== undefined ? options.enabled : !!market,
        staleTime: 1000 * 30, // 30 seconds (real-time price)
        gcTime: 2 * 60 * 1000, // 2 minutes
        refetchInterval: 1000 * 60, // Refetch every 60 seconds
    });
};
