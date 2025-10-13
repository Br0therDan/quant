// MarketData - Technical Indicator Module API
// TanStack Query (v5.9) 기반 Query 및 Mutation 활용 상태관리 및 데이터 패칭 훅
// 성능 최적화 및 캐싱, 에러 핸들링, 로딩 상태 관리 포함
// Hook은 useTechnicalIndicator 단일/통합 사용 (별도의 추가 훅 생성 불필요)
// Hey-API 기반: @/client/sdk.gen.ts 의 각 엔드포인트별 서비스클래스 및 @/client/types.gen.ts 의 타입정의 활용(엔드포인트의 스키마명칭과 호환)

import { TechnicalIndicatorService } from "@/client";
import { useQuery } from "@tanstack/react-query";
import { useMemo } from "react";

export const technicalIndicatorQueryKeys = {
	all: ["technicalIndicator"] as const,
	indicatorList: () =>
		[...technicalIndicatorQueryKeys.all, "indicatorList"] as const,
	sma: () => [...technicalIndicatorQueryKeys.all, "sma"] as const,
	smaSymbol: (
		symbol: string,
		options?: {
			interval?: string;
			timePeriod?: number;
			seriesType?: string;
		},
	) => {
		const key = [...technicalIndicatorQueryKeys.sma(), symbol] as const;
		const params: Record<string, string | number> = {};
		if (options?.interval) params.interval = options.interval;
		if (options?.timePeriod) params.timePeriod = options.timePeriod;
		if (options?.seriesType) params.seriesType = options.seriesType;
		return Object.keys(params).length > 0 ? ([...key, params] as const) : key;
	},
	wma: () => [...technicalIndicatorQueryKeys.all, "wma"] as const,
	wmaSymbol: (
		symbol: string,
		options?: {
			interval?: string;
			timePeriod?: number;
			seriesType?: string;
		},
	) => {
		const key = [...technicalIndicatorQueryKeys.wma(), symbol] as const;
		const params: Record<string, string | number> = {};
		if (options?.interval) params.interval = options.interval;
		if (options?.timePeriod) params.timePeriod = options.timePeriod;
		if (options?.seriesType) params.seriesType = options.seriesType;
		return Object.keys(params).length > 0 ? ([...key, params] as const) : key;
	},
	dema: () => [...technicalIndicatorQueryKeys.all, "dema"] as const,
	demaSymbol: (
		symbol: string,
		options?: {
			interval?: string;
			timePeriod?: number;
			seriesType?: string;
		},
	) => {
		const key = [...technicalIndicatorQueryKeys.dema(), symbol] as const;
		const params: Record<string, string | number> = {};
		if (options?.interval) params.interval = options.interval;
		if (options?.timePeriod) params.timePeriod = options.timePeriod;
		if (options?.seriesType) params.seriesType = options.seriesType;
		return Object.keys(params).length > 0 ? ([...key, params] as const) : key;
	},
	tema: () => [...technicalIndicatorQueryKeys.all, "tema"] as const,
	temaSymbol: (
		symbol: string,
		options?: {
			interval?: string;
			timePeriod?: number;
			seriesType?: string;
		},
	) => {
		const key = [...technicalIndicatorQueryKeys.tema(), symbol] as const;
		const params: Record<string, string | number> = {};
		if (options?.interval) params.interval = options.interval;
		if (options?.timePeriod) params.timePeriod = options.timePeriod;
		if (options?.seriesType) params.seriesType = options.seriesType;
		return Object.keys(params).length > 0 ? ([...key, params] as const) : key;
	},
	ema: () => [...technicalIndicatorQueryKeys.all, "ema"] as const,
	emaSymbol: (
		symbol: string,
		options?: {
			interval?: string;
			timePeriod?: number;
			seriesType?: string;
		},
	) => {
		const key = [...technicalIndicatorQueryKeys.ema(), symbol] as const;
		const params: Record<string, string | number> = {};
		if (options?.interval) params.interval = options.interval;
		if (options?.timePeriod) params.timePeriod = options.timePeriod;
		if (options?.seriesType) params.seriesType = options.seriesType;
		return Object.keys(params).length > 0 ? ([...key, params] as const) : key;
	},
	rsi: () => [...technicalIndicatorQueryKeys.all, "rsi"] as const,
	rsiSymbol: (
		symbol: string,
		options?: {
			interval?: string;
			timePeriod?: number;
			seriesType?: string;
		},
	) => {
		const key = [...technicalIndicatorQueryKeys.rsi(), symbol] as const;
		const params: Record<string, string | number> = {};
		if (options?.interval) params.interval = options.interval;
		if (options?.timePeriod) params.timePeriod = options.timePeriod;
		if (options?.seriesType) params.seriesType = options.seriesType;
		return Object.keys(params).length > 0 ? ([...key, params] as const) : key;
	},
	macd: () => [...technicalIndicatorQueryKeys.all, "macd"] as const,
	macdSymbol: (
		symbol: string,
		options?: {
			interval?: string;
			seriesType?: string;
			fastPeriod?: number;
			slowPeriod?: number;
			signalPeriod?: number;
		},
	) => {
		const key = [...technicalIndicatorQueryKeys.macd(), symbol] as const;
		const params: Record<string, string | number> = {};
		if (options?.interval) params.interval = options.interval;
		if (options?.seriesType) params.seriesType = options.seriesType;
		if (options?.fastPeriod) params.fastPeriod = options.fastPeriod;
		if (options?.slowPeriod) params.slowPeriod = options.slowPeriod;
		if (options?.signalPeriod) params.signalPeriod = options.signalPeriod;
		return Object.keys(params).length > 0 ? ([...key, params] as const) : key;
	},
	bbands: () => [...technicalIndicatorQueryKeys.all, "bbands"] as const,
	bbandsSymbol: (
		symbol: string,
		options?: {
			interval?: string;
			timePeriod?: number;
			seriesType?: string;
			nbdevup?: number;
			nbdevdn?: number;
		},
	) => {
		const key = [...technicalIndicatorQueryKeys.bbands(), symbol] as const;
		const params: Record<string, string | number> = {};
		if (options?.interval) params.interval = options.interval;
		if (options?.timePeriod) params.timePeriod = options.timePeriod;
		if (options?.seriesType) params.seriesType = options.seriesType;
		if (options?.nbdevup) params.nbdevup = options.nbdevup;
		if (options?.nbdevdn) params.nbdevdn = options.nbdevdn;
		return Object.keys(params).length > 0 ? ([...key, params] as const) : key;
	},
	adx: () => [...technicalIndicatorQueryKeys.all, "adx"] as const,
	adxSymbol: (
		symbol: string,
		options?: {
			interval?: string;
			timePeriod?: number;
		},
	) => {
		const key = [...technicalIndicatorQueryKeys.adx(), symbol] as const;
		const params: Record<string, string | number> = {};
		if (options?.interval) params.interval = options.interval;
		if (options?.timePeriod) params.timePeriod = options.timePeriod;
		return Object.keys(params).length > 0 ? ([...key, params] as const) : key;
	},
	atr: () => [...technicalIndicatorQueryKeys.all, "atr"] as const,
	atrSymbol: (
		symbol: string,
		options?: {
			interval?: string;
			timePeriod?: number;
		},
	) => {
		const key = [...technicalIndicatorQueryKeys.atr(), symbol] as const;
		const params: Record<string, string | number> = {};
		if (options?.interval) params.interval = options.interval;
		if (options?.timePeriod) params.timePeriod = options.timePeriod;
		return Object.keys(params).length > 0 ? ([...key, params] as const) : key;
	},
	stoch: () => [...technicalIndicatorQueryKeys.all, "stoch"] as const,
	stochSymbol: (
		symbol: string,
		options?: {
			interval?: string;
			fastkPeriod?: number;
			slowkPeriod?: number;
			slowdPeriod?: number;
			slowkMaType?: number;
			slowdMaType?: number;
		},
	) => {
		const key = [...technicalIndicatorQueryKeys.stoch(), symbol] as const;
		const params: Record<string, string | number> = {};
		if (options?.interval) params.interval = options.interval;
		if (options?.fastkPeriod) params.fastkPeriod = options.fastkPeriod;
		if (options?.slowkPeriod) params.slowkPeriod = options.slowkPeriod;
		if (options?.slowdPeriod) params.slowdPeriod = options.slowdPeriod;
		if (options?.slowkMaType) params.slowkMaType = options.slowkMaType;
		if (options?.slowdMaType) params.slowdMaType = options.slowdMaType;
		return Object.keys(params).length > 0 ? ([...key, params] as const) : key;
	},
};

export function useTechnicalIndicator() {
	return useMemo(
		() => ({
			queryKeys: technicalIndicatorQueryKeys,
		}),
		[],
	);
}

// Get indicator list
export const useIndicatorList = (options?: { enabled?: boolean }) => {
	return useQuery({
		queryKey: technicalIndicatorQueryKeys.indicatorList(),
		queryFn: async () => {
			console.log("🌐 API Call - Indicator List");
			const response = await TechnicalIndicatorService.getIndicatorList();
			console.log("✅ API Response - Indicator List:", {
				response: response.data,
			});
			return response.data;
		},
		enabled: options?.enabled !== false,
		staleTime: 1000 * 60 * 60, // 1 hour (indicator list is stable)
		gcTime: 1000 * 60 * 60 * 24, // 24 hours
	});
};

// SMA (Simple Moving Average)
export const useSMA = (
	symbol: string,
	options?: {
		interval?: string;
		timePeriod?: number;
		seriesType?: string;
		enabled?: boolean;
	},
) => {
	const queryKey = technicalIndicatorQueryKeys.smaSymbol(symbol, {
		interval: options?.interval,
		timePeriod: options?.timePeriod,
		seriesType: options?.seriesType,
	});

	return useQuery({
		queryKey,
		queryFn: async () => {
			console.log("🌐 API Call - SMA:", {
				symbol,
				interval: options?.interval,
				timePeriod: options?.timePeriod,
				seriesType: options?.seriesType,
				queryKey,
			});
			const response = await TechnicalIndicatorService.getSma({
				path: { symbol },
				query: {
					interval: options?.interval,
					time_period: options?.timePeriod,
					series_type: options?.seriesType,
				} as any,
			});
			console.log("✅ API Response - SMA:", {
				symbol,
				dataLength: (response.data as any)?.data?.length || 0,
				response: response.data,
			});
			return response.data;
		},
		enabled: options?.enabled !== undefined ? options.enabled : !!symbol,
		staleTime: 1000 * 60 * 5, // 5 minutes
		gcTime: 1000 * 60 * 30, // 30 minutes
	});
};

// WMA (Weighted Moving Average)
export const useWMA = (
	symbol: string,
	options?: {
		interval?: string;
		timePeriod?: number;
		seriesType?: string;
		enabled?: boolean;
	},
) => {
	const queryKey = technicalIndicatorQueryKeys.wmaSymbol(symbol, {
		interval: options?.interval,
		timePeriod: options?.timePeriod,
		seriesType: options?.seriesType,
	});

	return useQuery({
		queryKey,
		queryFn: async () => {
			console.log("🌐 API Call - WMA:", {
				symbol,
				interval: options?.interval,
				timePeriod: options?.timePeriod,
				seriesType: options?.seriesType,
				queryKey,
			});
			const response = await TechnicalIndicatorService.getWma({
				path: { symbol },
				query: {
					interval: options?.interval,
					time_period: options?.timePeriod,
					series_type: options?.seriesType,
				} as any,
			});
			console.log("✅ API Response - WMA:", {
				symbol,
				dataLength: (response.data as any)?.data?.length || 0,
				response: response.data,
			});
			return response.data;
		},
		enabled: options?.enabled !== undefined ? options.enabled : !!symbol,
		staleTime: 1000 * 60 * 5, // 5 minutes
		gcTime: 1000 * 60 * 30, // 30 minutes
	});
};

// DEMA (Double Exponential Moving Average)
export const useDEMA = (
	symbol: string,
	options?: {
		interval?: string;
		timePeriod?: number;
		seriesType?: string;
		enabled?: boolean;
	},
) => {
	const queryKey = technicalIndicatorQueryKeys.demaSymbol(symbol, {
		interval: options?.interval,
		timePeriod: options?.timePeriod,
		seriesType: options?.seriesType,
	});

	return useQuery({
		queryKey,
		queryFn: async () => {
			console.log("🌐 API Call - DEMA:", {
				symbol,
				interval: options?.interval,
				timePeriod: options?.timePeriod,
				seriesType: options?.seriesType,
				queryKey,
			});
			const response = await TechnicalIndicatorService.getDema({
				path: { symbol },
				query: {
					interval: options?.interval,
					time_period: options?.timePeriod,
					series_type: options?.seriesType,
				} as any,
			});
			console.log("✅ API Response - DEMA:", {
				symbol,
				dataLength: (response.data as any)?.data?.length || 0,
				response: response.data,
			});
			return response.data;
		},
		enabled: options?.enabled !== undefined ? options.enabled : !!symbol,
		staleTime: 1000 * 60 * 5, // 5 minutes
		gcTime: 1000 * 60 * 30, // 30 minutes
	});
};

// TEMA (Triple Exponential Moving Average)
export const useTEMA = (
	symbol: string,
	options?: {
		interval?: string;
		timePeriod?: number;
		seriesType?: string;
		enabled?: boolean;
	},
) => {
	const queryKey = technicalIndicatorQueryKeys.temaSymbol(symbol, {
		interval: options?.interval,
		timePeriod: options?.timePeriod,
		seriesType: options?.seriesType,
	});

	return useQuery({
		queryKey,
		queryFn: async () => {
			console.log("🌐 API Call - TEMA:", {
				symbol,
				interval: options?.interval,
				timePeriod: options?.timePeriod,
				seriesType: options?.seriesType,
				queryKey,
			});
			const response = await TechnicalIndicatorService.getTema({
				path: { symbol },
				query: {
					interval: options?.interval,
					time_period: options?.timePeriod,
					series_type: options?.seriesType,
				} as any,
			});
			console.log("✅ API Response - TEMA:", {
				symbol,
				dataLength: (response.data as any)?.data?.length || 0,
				response: response.data,
			});
			return response.data;
		},
		enabled: options?.enabled !== undefined ? options.enabled : !!symbol,
		staleTime: 1000 * 60 * 5, // 5 minutes
		gcTime: 1000 * 60 * 30, // 30 minutes
	});
};

// EMA (Exponential Moving Average)
export const useEMA = (
	symbol: string,
	options?: {
		interval?: string;
		timePeriod?: number;
		seriesType?: string;
		enabled?: boolean;
	},
) => {
	const queryKey = technicalIndicatorQueryKeys.emaSymbol(symbol, {
		interval: options?.interval,
		timePeriod: options?.timePeriod,
		seriesType: options?.seriesType,
	});

	return useQuery({
		queryKey,
		queryFn: async () => {
			console.log("🌐 API Call - EMA:", {
				symbol,
				interval: options?.interval,
				timePeriod: options?.timePeriod,
				seriesType: options?.seriesType,
				queryKey,
			});
			const response = await TechnicalIndicatorService.getEma({
				path: { symbol },
				query: {
					interval: options?.interval,
					time_period: options?.timePeriod,
					series_type: options?.seriesType,
				} as any,
			});
			console.log("✅ API Response - EMA:", {
				symbol,
				dataLength: (response.data as any)?.data?.length || 0,
				response: response.data,
			});
			return response.data;
		},
		enabled: options?.enabled !== undefined ? options.enabled : !!symbol,
		staleTime: 1000 * 60 * 5, // 5 minutes
		gcTime: 1000 * 60 * 30, // 30 minutes
	});
};

// RSI (Relative Strength Index)
export const useRSI = (
	symbol: string,
	options?: {
		interval?: string;
		timePeriod?: number;
		seriesType?: string;
		enabled?: boolean;
	},
) => {
	const queryKey = technicalIndicatorQueryKeys.rsiSymbol(symbol, {
		interval: options?.interval,
		timePeriod: options?.timePeriod,
		seriesType: options?.seriesType,
	});

	return useQuery({
		queryKey,
		queryFn: async () => {
			console.log("🌐 API Call - RSI:", {
				symbol,
				interval: options?.interval,
				timePeriod: options?.timePeriod,
				seriesType: options?.seriesType,
				queryKey,
			});
			const response = await TechnicalIndicatorService.getRsi({
				path: { symbol },
				query: {
					interval: options?.interval,
					time_period: options?.timePeriod,
					series_type: options?.seriesType,
				} as any,
			});
			console.log("✅ API Response - RSI:", {
				symbol,
				dataLength: (response.data as any)?.data?.length || 0,
				response: response.data,
			});
			return response.data;
		},
		enabled: options?.enabled !== undefined ? options.enabled : !!symbol,
		staleTime: 1000 * 60 * 5, // 5 minutes
		gcTime: 1000 * 60 * 30, // 30 minutes
	});
};

// MACD (Moving Average Convergence Divergence)
export const useMACD = (
	symbol: string,
	options?: {
		interval?: string;
		seriesType?: string;
		fastPeriod?: number;
		slowPeriod?: number;
		signalPeriod?: number;
		enabled?: boolean;
	},
) => {
	const queryKey = technicalIndicatorQueryKeys.macdSymbol(symbol, {
		interval: options?.interval,
		seriesType: options?.seriesType,
		fastPeriod: options?.fastPeriod,
		slowPeriod: options?.slowPeriod,
		signalPeriod: options?.signalPeriod,
	});

	return useQuery({
		queryKey,
		queryFn: async () => {
			console.log("🌐 API Call - MACD:", {
				symbol,
				interval: options?.interval,
				seriesType: options?.seriesType,
				fastPeriod: options?.fastPeriod,
				slowPeriod: options?.slowPeriod,
				signalPeriod: options?.signalPeriod,
				queryKey,
			});
			const response = await TechnicalIndicatorService.getMacd({
				path: { symbol },
				query: {
					interval: options?.interval,
					series_type: options?.seriesType,
					fastperiod: options?.fastPeriod,
					slowperiod: options?.slowPeriod,
					signalperiod: options?.signalPeriod,
				} as any,
			});
			console.log("✅ API Response - MACD:", {
				symbol,
				dataLength: (response.data as any)?.data?.length || 0,
				response: response.data,
			});
			return response.data;
		},
		enabled: options?.enabled !== undefined ? options.enabled : !!symbol,
		staleTime: 1000 * 60 * 5, // 5 minutes
		gcTime: 1000 * 60 * 30, // 30 minutes
	});
};

// BBANDS (Bollinger Bands)
export const useBBANDS = (
	symbol: string,
	options?: {
		interval?: string;
		timePeriod?: number;
		seriesType?: string;
		nbdevup?: number;
		nbdevdn?: number;
		enabled?: boolean;
	},
) => {
	const queryKey = technicalIndicatorQueryKeys.bbandsSymbol(symbol, {
		interval: options?.interval,
		timePeriod: options?.timePeriod,
		seriesType: options?.seriesType,
		nbdevup: options?.nbdevup,
		nbdevdn: options?.nbdevdn,
	});

	return useQuery({
		queryKey,
		queryFn: async () => {
			console.log("🌐 API Call - BBANDS:", {
				symbol,
				interval: options?.interval,
				timePeriod: options?.timePeriod,
				seriesType: options?.seriesType,
				nbdevup: options?.nbdevup,
				nbdevdn: options?.nbdevdn,
				queryKey,
			});
			const response = await TechnicalIndicatorService.getBbands({
				path: { symbol },
				query: {
					interval: options?.interval,
					time_period: options?.timePeriod,
					series_type: options?.seriesType,
					nbdevup: options?.nbdevup,
					nbdevdn: options?.nbdevdn,
				} as any,
			});
			console.log("✅ API Response - BBANDS:", {
				symbol,
				dataLength: (response.data as any)?.data?.length || 0,
				response: response.data,
			});
			return response.data;
		},
		enabled: options?.enabled !== undefined ? options.enabled : !!symbol,
		staleTime: 1000 * 60 * 5, // 5 minutes
		gcTime: 1000 * 60 * 30, // 30 minutes
	});
};

// ADX (Average Directional Index)
export const useADX = (
	symbol: string,
	options?: {
		interval?: string;
		timePeriod?: number;
		enabled?: boolean;
	},
) => {
	const queryKey = technicalIndicatorQueryKeys.adxSymbol(symbol, {
		interval: options?.interval,
		timePeriod: options?.timePeriod,
	});

	return useQuery({
		queryKey,
		queryFn: async () => {
			console.log("🌐 API Call - ADX:", {
				symbol,
				interval: options?.interval,
				timePeriod: options?.timePeriod,
				queryKey,
			});
			const response = await TechnicalIndicatorService.getAdx({
				path: { symbol },
				query: {
					interval: options?.interval,
					time_period: options?.timePeriod,
				} as any,
			});
			console.log("✅ API Response - ADX:", {
				symbol,
				dataLength: (response.data as any)?.data?.length || 0,
				response: response.data,
			});
			return response.data;
		},
		enabled: options?.enabled !== undefined ? options.enabled : !!symbol,
		staleTime: 1000 * 60 * 5, // 5 minutes
		gcTime: 1000 * 60 * 30, // 30 minutes
	});
};

// ATR (Average True Range)
export const useATR = (
	symbol: string,
	options?: {
		interval?: string;
		timePeriod?: number;
		enabled?: boolean;
	},
) => {
	const queryKey = technicalIndicatorQueryKeys.atrSymbol(symbol, {
		interval: options?.interval,
		timePeriod: options?.timePeriod,
	});

	return useQuery({
		queryKey,
		queryFn: async () => {
			console.log("🌐 API Call - ATR:", {
				symbol,
				interval: options?.interval,
				timePeriod: options?.timePeriod,
				queryKey,
			});
			const response = await TechnicalIndicatorService.getAtr({
				path: { symbol },
				query: {
					interval: options?.interval,
					time_period: options?.timePeriod,
				} as any,
			});
			console.log("✅ API Response - ATR:", {
				symbol,
				dataLength: (response.data as any)?.data?.length || 0,
				response: response.data,
			});
			return response.data;
		},
		enabled: options?.enabled !== undefined ? options.enabled : !!symbol,
		staleTime: 1000 * 60 * 5, // 5 minutes
		gcTime: 1000 * 60 * 30, // 30 minutes
	});
};

// STOCH (Stochastic Oscillator)
export const useSTOCH = (
	symbol: string,
	options?: {
		interval?: string;
		fastkPeriod?: number;
		slowkPeriod?: number;
		slowdPeriod?: number;
		slowkMaType?: number;
		slowdMaType?: number;
		enabled?: boolean;
	},
) => {
	const queryKey = technicalIndicatorQueryKeys.stochSymbol(symbol, {
		interval: options?.interval,
		fastkPeriod: options?.fastkPeriod,
		slowkPeriod: options?.slowkPeriod,
		slowdPeriod: options?.slowdPeriod,
		slowkMaType: options?.slowkMaType,
		slowdMaType: options?.slowdMaType,
	});

	return useQuery({
		queryKey,
		queryFn: async () => {
			console.log("🌐 API Call - STOCH:", {
				symbol,
				interval: options?.interval,
				fastkPeriod: options?.fastkPeriod,
				slowkPeriod: options?.slowkPeriod,
				slowdPeriod: options?.slowdPeriod,
				slowkMaType: options?.slowkMaType,
				slowdMaType: options?.slowdMaType,
				queryKey,
			});
			const response = await TechnicalIndicatorService.getStoch({
				path: { symbol },
				query: {
					interval: options?.interval,
					fastkperiod: options?.fastkPeriod,
					slowkperiod: options?.slowkPeriod,
					slowdperiod: options?.slowdPeriod,
					slowkmatype: options?.slowkMaType,
					slowdmatype: options?.slowdMaType,
				} as any,
			});
			console.log("✅ API Response - STOCH:", {
				symbol,
				dataLength: (response.data as any)?.data?.length || 0,
				response: response.data,
			});
			return response.data;
		},
		enabled: options?.enabled !== undefined ? options.enabled : !!symbol,
		staleTime: 1000 * 60 * 5, // 5 minutes
		gcTime: 1000 * 60 * 30, // 30 minutes
	});
};
