"use client";

import type { ChartType, IndicatorConfig } from "./ReactFinancialChart";

const STORAGE_KEY_PREFIX = "react-financial-chart";

export interface ChartSettings {
	chartType: ChartType["type"];
	indicators: IndicatorConfig;
	dateRange?: {
		start: string | null;
		end: string | null;
	};
	interval?: string;
	adjusted?: boolean;
}

/**
 * 심볼별 차트 설정을 localStorage에 저장
 */
export function saveChartSettings(
	symbol: string,
	settings: ChartSettings,
): void {
	if (typeof window === "undefined") return;

	try {
		const key = `${STORAGE_KEY_PREFIX}:${symbol}`;
		localStorage.setItem(key, JSON.stringify(settings));
	} catch (error) {
		console.error("Failed to save chart settings:", error);
	}
}

/**
 * 심볼별 차트 설정을 localStorage에서 불러오기
 */
export function loadChartSettings(symbol: string): ChartSettings | null {
	if (typeof window === "undefined") return null;

	try {
		const key = `${STORAGE_KEY_PREFIX}:${symbol}`;
		const stored = localStorage.getItem(key);

		if (!stored) return null;

		return JSON.parse(stored) as ChartSettings;
	} catch (error) {
		console.error("Failed to load chart settings:", error);
		return null;
	}
}

/**
 * 심볼별 차트 설정 삭제
 */
export function clearChartSettings(symbol: string): void {
	if (typeof window === "undefined") return;

	try {
		const key = `${STORAGE_KEY_PREFIX}:${symbol}`;
		localStorage.removeItem(key);
	} catch (error) {
		console.error("Failed to clear chart settings:", error);
	}
}

/**
 * 모든 심볼의 차트 설정 목록 가져오기
 */
export function getAllChartSettings(): Record<string, ChartSettings> {
	if (typeof window === "undefined") return {};

	try {
		const settings: Record<string, ChartSettings> = {};
		const prefix = `${STORAGE_KEY_PREFIX}:`;

		for (let i = 0; i < localStorage.length; i++) {
			const key = localStorage.key(i);
			if (key?.startsWith(prefix)) {
				const symbol = key.replace(prefix, "");
				const stored = localStorage.getItem(key);
				if (stored) {
					settings[symbol] = JSON.parse(stored);
				}
			}
		}

		return settings;
	} catch (error) {
		console.error("Failed to get all chart settings:", error);
		return {};
	}
}
