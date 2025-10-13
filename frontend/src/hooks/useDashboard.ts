// Dashboard Module API
// TanStack Query (v5.9) 기반 Query 및 및 Mutation 활용 상태관리 및 데이터 패칭 훅
// 성능 최적화 및 캐싱, 에러 핸들링, 로딩 상태 관리 포함
// Hook은 useDashboard 단일/통합 사용 (별도의 추가 훅 생성 불필요)
// Hey-API 기반: @/client/sdk.gen.ts 의 각 엔드포인트별 서비스클래스 및 @/client/types.gen.ts 의 타입정의 활용(엔드포인트의 스키마명칭과 호환)

import { DashboardService } from "@/client";
import { useQuery } from "@tanstack/react-query";
import { useMemo } from "react";

export const dashboardQueryKeys = {
	all: ["dashboard"] as const,
	summary: () => [...dashboardQueryKeys.all, "summary"] as const,
	portfolio: () => [...dashboardQueryKeys.all, "portfolio"] as const,
	portfolioPerformance: (period?: string) =>
		[...dashboardQueryKeys.portfolio(), "performance", { period }] as const,
	strategies: () => [...dashboardQueryKeys.all, "strategies"] as const,
	strategyComparison: () =>
		[...dashboardQueryKeys.strategies(), "comparison"] as const,
	trades: () => [...dashboardQueryKeys.all, "trades"] as const,
	recentTrades: (limit?: number) =>
		[...dashboardQueryKeys.trades(), "recent", { limit }] as const,
	watchlist: () => [...dashboardQueryKeys.all, "watchlist"] as const,
	watchlistQuotes: () => [...dashboardQueryKeys.watchlist(), "quotes"] as const,
	news: () => [...dashboardQueryKeys.all, "news"] as const,
	newsFeed: (limit?: number) =>
		[...dashboardQueryKeys.news(), "feed", { limit }] as const,
	economic: () => [...dashboardQueryKeys.all, "economic"] as const,
	economicCalendar: (days?: number) =>
		[...dashboardQueryKeys.economic(), "calendar", { days }] as const,
};

export function useDashboard() {
	// Queries
	const dashboardSummaryQuery = useQuery({
		queryKey: dashboardQueryKeys.summary(),
		queryFn: async () => {
			const response = await DashboardService.getDashboardSummary();
			return response.data;
		},
		staleTime: 1000 * 60 * 5, // 5 minutes
		gcTime: 30 * 60 * 1000, // 30 minutes
	});

	const portfolioPerformanceQuery = useQuery({
		queryKey: dashboardQueryKeys.portfolioPerformance(),
		queryFn: async () => {
			const response = await DashboardService.getPortfolioPerformance();
			return response.data;
		},
		staleTime: 1000 * 60 * 5, // 5 minutes
		gcTime: 30 * 60 * 1000, // 30 minutes
	});

	const strategyComparisonQuery = useQuery({
		queryKey: dashboardQueryKeys.strategyComparison(),
		queryFn: async () => {
			const response = await DashboardService.getStrategyComparison();
			return response.data;
		},
		staleTime: 1000 * 60 * 5, // 5 minutes
		gcTime: 30 * 60 * 1000, // 30 minutes
	});

	const recentTradesQuery = useQuery({
		queryKey: dashboardQueryKeys.recentTrades(),
		queryFn: async () => {
			const response = await DashboardService.getRecentTrades();
			return response.data;
		},
		staleTime: 1000 * 60 * 5, // 5 minutes
		gcTime: 30 * 60 * 1000, // 30 minutes
	});

	const watchlistQuotesQuery = useQuery({
		queryKey: dashboardQueryKeys.watchlistQuotes(),
		queryFn: async () => {
			const response = await DashboardService.getWatchlistQuotes();
			return response.data;
		},
		staleTime: 1000 * 30, // 30 seconds (real-time data)
		gcTime: 5 * 60 * 1000, // 5 minutes
	});

	const newsFeedQuery = useQuery({
		queryKey: dashboardQueryKeys.newsFeed(),
		queryFn: async () => {
			const response = await DashboardService.getNewsFeed();
			return response.data;
		},
		staleTime: 1000 * 60 * 10, // 10 minutes
		gcTime: 30 * 60 * 1000, // 30 minutes
	});

	const economicCalendarQuery = useQuery({
		queryKey: dashboardQueryKeys.economicCalendar(),
		queryFn: async () => {
			const response = await DashboardService.getEconomicCalendar();
			return response.data;
		},
		staleTime: 1000 * 60 * 30, // 30 minutes
		gcTime: 15 * 60 * 1000, // 1 hour
	});

	return useMemo(
		() => ({
			// Data
			dashboardSummary: dashboardSummaryQuery.data,
			portfolioPerformance: portfolioPerformanceQuery.data,
			strategyComparison: strategyComparisonQuery.data,
			recentTrades: recentTradesQuery.data,
			watchlistQuotes: watchlistQuotesQuery.data,
			newsFeed: newsFeedQuery.data,
			economicCalendar: economicCalendarQuery.data,

			// Status
			isError: {
				dashboardSummary: dashboardSummaryQuery.isError,
				portfolioPerformance: portfolioPerformanceQuery.isError,
				strategyComparison: strategyComparisonQuery.isError,
				recentTrades: recentTradesQuery.isError,
				watchlistQuotes: watchlistQuotesQuery.isError,
				newsFeed: newsFeedQuery.isError,
				economicCalendar: economicCalendarQuery.isError,
			},
			isLoading: {
				dashboardSummary: dashboardSummaryQuery.isLoading,
				portfolioPerformance: portfolioPerformanceQuery.isLoading,
				strategyComparison: strategyComparisonQuery.isLoading,
				recentTrades: recentTradesQuery.isLoading,
				watchlistQuotes: watchlistQuotesQuery.isLoading,
				newsFeed: newsFeedQuery.isLoading,
				economicCalendar: economicCalendarQuery.isLoading,
			},
			error: {
				dashboardSummary: dashboardSummaryQuery.error,
				portfolioPerformance: portfolioPerformanceQuery.error,
				strategyComparison: strategyComparisonQuery.error,
				recentTrades: recentTradesQuery.error,
				watchlistQuotes: watchlistQuotesQuery.error,
				newsFeed: newsFeedQuery.error,
				economicCalendar: economicCalendarQuery.error,
			},

			// Actions
			refetch: {
				dashboardSummary: dashboardSummaryQuery.refetch,
				portfolioPerformance: portfolioPerformanceQuery.refetch,
				strategyComparison: strategyComparisonQuery.refetch,
				recentTrades: recentTradesQuery.refetch,
				watchlistQuotes: watchlistQuotesQuery.refetch,
				newsFeed: newsFeedQuery.refetch,
				economicCalendar: economicCalendarQuery.refetch,
			},

			// Query Objects (if needed for advanced usage)
			queries: {
				dashboardSummaryQuery,
				portfolioPerformanceQuery,
				strategyComparisonQuery,
				recentTradesQuery,
				watchlistQuotesQuery,
				newsFeedQuery,
				economicCalendarQuery,
			},
		}),
		[
			dashboardSummaryQuery,
			portfolioPerformanceQuery,
			strategyComparisonQuery,
			recentTradesQuery,
			watchlistQuotesQuery,
			newsFeedQuery,
			economicCalendarQuery,
		],
	);
}
