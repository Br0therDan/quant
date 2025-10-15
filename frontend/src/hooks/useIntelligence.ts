// MarketData - AlphaVantage Intelligence Module API
// TanStack Query (v5.9) 기반 Query 및 및 Mutation 활용 상태관리 및 데이터 패칭 훅
// 성능 최적화 및 캐싱, 에러 핸들링, 로딩 상태 관리 포함
// Hook은 useIntelligence 단일/통합 사용 (별도의 추가 훅 생성 불필요)
// Hey-API 기반: @/client/sdk.gen.ts 의 각 엔드포인트별 서비스클래스 및 @/client/types.gen.ts 의 타입정의 활용(엔드포인트의 스키마명칭과 호환)

import { MarketDataService } from "@/client";
import { useQuery } from "@tanstack/react-query";
import { useMemo } from "react";

export const intelligenceQueryKeys = {
	all: ["intelligence"] as const,
	news: () => [...intelligenceQueryKeys.all, "news"] as const,
	newsSymbol: (symbol: string) =>
		[...intelligenceQueryKeys.news(), symbol] as const,
	sentiment: () => [...intelligenceQueryKeys.all, "sentiment"] as const,
	sentimentSymbol: (symbol: string) =>
		[...intelligenceQueryKeys.sentiment(), symbol] as const,
	analyst: () => [...intelligenceQueryKeys.all, "analyst"] as const,
	analystRecommendations: (symbol: string) =>
		[...intelligenceQueryKeys.analyst(), "recommendations", symbol] as const,
	social: () => [...intelligenceQueryKeys.all, "social"] as const,
	socialSentiment: (symbol: string) =>
		[...intelligenceQueryKeys.social(), "sentiment", symbol] as const,
};

export function useIntelligence() {
	return useMemo(
		() => ({
			queryKeys: intelligenceQueryKeys,
		}),
		[],
	);
}

// Individual hook functions for specific symbols
export const useIntelligenceNews = (symbol: string) => {
	return useQuery({
		queryKey: intelligenceQueryKeys.newsSymbol(symbol),
		queryFn: async () => {
			const response = await MarketDataService.getNews({
				path: { symbol },
			});
			return response.data;
		},
		enabled: !!symbol,
		staleTime: 1000 * 60 * 10, // 10 minutes
		gcTime: 30 * 60 * 1000, // 30 minutes
	});
};

export const useIntelligenceSentiment = (symbol: string) => {
	return useQuery({
		queryKey: intelligenceQueryKeys.sentimentSymbol(symbol),
		queryFn: async () => {
			const response = await MarketDataService.getSentimentAnalysis({
				path: { symbol },
			});
			return response.data;
		},
		enabled: !!symbol,
		staleTime: 1000 * 60 * 15, // 15 minutes
		gcTime: 15 * 60 * 1000, // 1 hour
	});
};

export const useIntelligenceAnalyst = (symbol: string) => {
	return useQuery({
		queryKey: intelligenceQueryKeys.analystRecommendations(symbol),
		queryFn: async () => {
			const response = await MarketDataService.getAnalystRecommendations({
				path: { symbol },
			});
			return response.data;
		},
		enabled: !!symbol,
		staleTime: 1000 * 60 * 60, // 1 hour
		gcTime: 4 * 60 * 60 * 1000, // 4 hours
	});
};

export const useIntelligenceSocial = (symbol: string) => {
	return useQuery({
		queryKey: intelligenceQueryKeys.socialSentiment(symbol),
		queryFn: async () => {
			const response = await MarketDataService.getSocialSentiment({
				path: { symbol },
			});
			return response.data;
		},
		enabled: !!symbol,
		staleTime: 1000 * 60 * 5, // 5 minutes
		gcTime: 15 * 60 * 1000, // 15 minutes
	});
};
