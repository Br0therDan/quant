// MarketData - Fundamental Module API
// TanStack Query (v5.9) 기반 Query 및 및 Mutation 활용 상태관리 및 데이터 패칭 훅
// 성능 최적화 및 캐싱, 에러 핸들링, 로딩 상태 관리 포함
// Hook은 useFundamental 단일/통합 사용 (별도의 추가 훅 생성 불필요)
// Hey-API 기반: @/client/sdk.gen.ts 의 각 엔드포인트별 서비스클래스 및 @/client/types.gen.ts 의 타입정의 활용(엔드포인트의 스키마명칭과 호환)

import { MarketDataService } from "@/client";
import { useQuery } from "@tanstack/react-query";
import { useMemo } from "react";

export const fundamentalQueryKeys = {
	all: ["fundamental"] as const,
	companyOverview: () =>
		[...fundamentalQueryKeys.all, "companyOverview"] as const,
	companyOverviewSymbol: (symbol: string) =>
		[...fundamentalQueryKeys.companyOverview(), symbol] as const,
	incomeStatement: () =>
		[...fundamentalQueryKeys.all, "incomeStatement"] as const,
	incomeStatementSymbol: (symbol: string) =>
		[...fundamentalQueryKeys.incomeStatement(), symbol] as const,
	balanceSheet: () => [...fundamentalQueryKeys.all, "balanceSheet"] as const,
	balanceSheetSymbol: (symbol: string) =>
		[...fundamentalQueryKeys.balanceSheet(), symbol] as const,
	cashFlow: () => [...fundamentalQueryKeys.all, "cashFlow"] as const,
	cashFlowSymbol: (symbol: string) =>
		[...fundamentalQueryKeys.cashFlow(), symbol] as const,
	earnings: () => [...fundamentalQueryKeys.all, "earnings"] as const,
	earningsSymbol: (symbol: string) =>
		[...fundamentalQueryKeys.earnings(), symbol] as const,
};

export function useFundamental() {
	return useMemo(
		() => ({
			queryKeys: fundamentalQueryKeys,
		}),
		[],
	);
}

// Individual hook functions for specific symbols
export const useFundamentalCompanyOverview = (symbol: string) => {
	return useQuery({
		queryKey: fundamentalQueryKeys.companyOverviewSymbol(symbol),
		queryFn: async () => {
			const response = await MarketDataService.getCompanyOverview({
				path: { symbol },
			});
			return response.data;
		},
		enabled: !!symbol,
		staleTime: 1000 * 60 * 60 * 24, // 24 hours (company overview doesn't change frequently)
		gcTime: 7 * 24 * 60 * 60 * 1000, // 7 days
	});
};

export const useFundamentalIncomeStatement = (symbol: string) => {
	return useQuery({
		queryKey: fundamentalQueryKeys.incomeStatementSymbol(symbol),
		queryFn: async () => {
			const response = await MarketDataService.getIncomeStatement({
				path: { symbol },
			});
			return response.data;
		},
		enabled: !!symbol,
		staleTime: 1000 * 60 * 60 * 6, // 6 hours (financial statements update quarterly)
		gcTime: 24 * 60 * 60 * 1000, // 24 hours
	});
};

export const useFundamentalBalanceSheet = (symbol: string) => {
	return useQuery({
		queryKey: fundamentalQueryKeys.balanceSheetSymbol(symbol),
		queryFn: async () => {
			const response = await MarketDataService.getBalanceSheet({
				path: { symbol },
			});
			return response.data;
		},
		enabled: !!symbol,
		staleTime: 1000 * 60 * 60 * 6, // 6 hours
		gcTime: 24 * 60 * 60 * 1000, // 24 hours
	});
};

export const useFundamentalCashFlow = (symbol: string) => {
	return useQuery({
		queryKey: fundamentalQueryKeys.cashFlowSymbol(symbol),
		queryFn: async () => {
			const response = await MarketDataService.getCashFlow({
				path: { symbol },
			});
			return response.data;
		},
		enabled: !!symbol,
		staleTime: 1000 * 60 * 60 * 6, // 6 hours
		gcTime: 24 * 60 * 60 * 1000, // 24 hours
	});
};

export const useFundamentalEarnings = (symbol: string) => {
	return useQuery({
		queryKey: fundamentalQueryKeys.earningsSymbol(symbol),
		queryFn: async () => {
			const response = await MarketDataService.getEarnings({
				path: { symbol },
			});
			return response.data;
		},
		enabled: !!symbol,
		staleTime: 1000 * 60 * 60 * 2, // 2 hours (earnings can change more frequently)
		gcTime: 12 * 60 * 60 * 1000, // 12 hours
	});
};
