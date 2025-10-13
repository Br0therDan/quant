"use client";

import { useCallback, useEffect, useRef } from "react";
import type { ChartSettings } from "./chartStorage";
import { loadChartSettings, saveChartSettings } from "./chartStorage";

interface UseChartSettingsOptions {
	symbol: string;
	autoSave?: boolean;
	debounceMs?: number;
}

/**
 * 차트 설정을 localStorage에 자동으로 저장/복원하는 커스텀 훅
 *
 * @example
 * ```tsx
 * const { loadSettings, saveSettings } = useChartSettings({
 *   symbol,
 *   autoSave: true,
 *   debounceMs: 500
 * });
 *
 * // 컴포넌트 마운트 시 자동 로드
 * useEffect(() => {
 *   const loaded = loadSettings();
 *   if (loaded) {
 *     setChartType(loaded.chartType);
 *     setIndicators(loaded.indicators);
 *   }
 * }, [symbol]);
 *
 * // 설정 변경 시 자동 저장 (디바운싱)
 * saveSettings({ chartType, indicators, dateRange, interval });
 * ```
 */
export function useChartSettings(options: UseChartSettingsOptions) {
	const { symbol, autoSave = true, debounceMs = 500 } = options;
	const saveTimerRef = useRef<NodeJS.Timeout | null>(null);

	/**
	 * 설정 불러오기 (즉시 실행)
	 */
	const loadSettings = useCallback((): ChartSettings | null => {
		return loadChartSettings(symbol);
	}, [symbol]);

	/**
	 * 설정 저장하기 (디바운싱 적용)
	 */
	const saveSettings = useCallback(
		(settings: ChartSettings) => {
			if (!autoSave) {
				saveChartSettings(symbol, settings);
				return;
			}

			// 기존 타이머 취소
			if (saveTimerRef.current) {
				clearTimeout(saveTimerRef.current);
			}

			// 디바운싱된 저장
			saveTimerRef.current = setTimeout(() => {
				saveChartSettings(symbol, settings);
			}, debounceMs);
		},
		[symbol, autoSave, debounceMs],
	);

	/**
	 * 컴포넌트 언마운트 시 타이머 정리
	 */
	useEffect(() => {
		return () => {
			if (saveTimerRef.current) {
				clearTimeout(saveTimerRef.current);
			}
		};
	}, []);

	return {
		loadSettings,
		saveSettings,
	};
}
