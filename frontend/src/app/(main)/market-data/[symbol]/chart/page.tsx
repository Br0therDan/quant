"use client";

import LoadingSpinner from "@/components/common/LoadingSpinner";
import ReactFinancialChart, {
  ChartFooter,
  ChartHeader,
} from "@/components/market-data/ReactFinancialChart";
import type { IndicatorConfig } from "@/components/market-data/ReactFinancialChart/ReactFinancialChart";
import { useChartSettings } from "@/components/market-data/ReactFinancialChart/useChartSettings";
import {
  useStockDailyPrices,
  useStockMonthlyPrices,
  useStockWeeklyPrices,
} from "@/hooks/useStocks";
import { Box } from "@mui/material";
import type { Dayjs } from "dayjs";
import dayjs from "dayjs";
import { useParams } from "next/navigation";
import { useEffect, useMemo, useRef, useState } from "react";

export default function SymbolChartPage() {
  const params = useParams();
  const symbol = (params.symbol as string)?.toUpperCase();
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 800 });

  // 차트 상태
  const [chartType, setChartType] = useState<
    | "candlestick"
    | "ohlc"
    | "line"
    | "area"
    | "scatter"
    | "heikinAshi"
    | "renko"
    | "kagi"
    | "pointAndFigure"
  >("candlestick");
  const [interval, setInterval] = useState<string>("daily");
  const [adjusted, setAdjusted] = useState(true);
  const [startDate, setStartDate] = useState<Dayjs | null>(
    dayjs().subtract(1, "year")
  );
  const [endDate, setEndDate] = useState<Dayjs | null>(dayjs());

  // 인디케이터 상태
  const [indicators, setIndicators] = useState<IndicatorConfig>({
    ema: [],
    sma: [],
    wma: [],
    tma: [],
    bollingerBand: false,
    atr: false,
    sar: false,
    macd: false,
    rsi: false,
    stochastic: null,
    forceIndex: false,
    elderRay: false,
    elderImpulse: false,
  });

  // localStorage 훅 (심볼별 설정 관리)
  const { loadSettings, saveSettings } = useChartSettings({
    symbol,
    autoSave: true,
    debounceMs: 500,
  });

  // 컴포넌트 마운트 시 저장된 설정 복원
  useEffect(() => {
    const loaded = loadSettings();
    if (loaded) {
      setChartType(loaded.chartType);
      setIndicators(loaded.indicators);
      if (loaded.interval) setInterval(loaded.interval);
      if (loaded.adjusted !== undefined) setAdjusted(loaded.adjusted);
      if (loaded.dateRange?.start) setStartDate(dayjs(loaded.dateRange.start));
      if (loaded.dateRange?.end) setEndDate(dayjs(loaded.dateRange.end));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [loadSettings]);

  // 차트 크기 계산
  useEffect(() => {
    const updateDimensions = () => {
      if (chartContainerRef.current) {
        setDimensions({
          width: chartContainerRef.current.clientWidth,
          height: window.innerHeight - 120,
        });
      }
    };

    updateDimensions();
    window.addEventListener("resize", updateDimensions);
    return () => window.removeEventListener("resize", updateDimensions);
  }, []);

  // 설정 변경 시 자동 저장 (디바운싱)
  useEffect(() => {
    saveSettings({
      chartType,
      indicators,
      interval,
      adjusted,
      dateRange: {
        start: startDate?.format("YYYY-MM-DD") || null,
        end: endDate?.format("YYYY-MM-DD") || null,
      },
    });
  }, [
    chartType,
    indicators,
    interval,
    adjusted,
    startDate,
    endDate,
    saveSettings,
  ]);

  // 날짜 문자열 변환
  const dateRange = useMemo(() => {
    return {
      startDate: startDate?.format("YYYY-MM-DD") || "",
      endDate: endDate?.format("YYYY-MM-DD") || "",
    };
  }, [startDate, endDate]);

  // 데이터 fetching (interval에 따라 다른 hook 사용)
  const shouldFetchDaily = interval === "daily";
  const shouldFetchWeekly = interval === "weekly";
  const shouldFetchMonthly = interval === "monthly";

  const { data: dailyData, isLoading: dailyLoading } = useStockDailyPrices(
    symbol,
    shouldFetchDaily
      ? {
          outputsize: "full",
          adjusted,
          ...dateRange,
        }
      : undefined
  );

  const { data: weeklyData, isLoading: weeklyLoading } = useStockWeeklyPrices(
    symbol,
    shouldFetchWeekly
      ? {
          adjusted,
          ...dateRange,
        }
      : undefined
  );

  const { data: monthlyData, isLoading: monthlyLoading } =
    useStockMonthlyPrices(
      symbol,
      shouldFetchMonthly
        ? {
            adjusted,
            ...dateRange,
          }
        : undefined
    );

  const isLoading = dailyLoading || weeklyLoading || monthlyLoading;

  // 현재 interval에 맞는 데이터 선택
  const currentData = useMemo(() => {
    switch (interval) {
      case "daily":
        return dailyData;
      case "weekly":
        return weeklyData;
      case "monthly":
        return monthlyData;
      default:
        return dailyData;
    }
  }, [interval, dailyData, weeklyData, monthlyData]);

  // 차트 데이터 변환
  const candlestickData = useMemo(() => {
    if (
      !currentData ||
      typeof currentData !== "object" ||
      !("data" in currentData)
    ) {
      return [];
    }

    const dataArray = Array.isArray(currentData.data) ? currentData.data : [];

    return dataArray
      .map((item: any) => ({
        time: item.date,
        open: Number(item.open) || 0,
        high: Number(item.high) || 0,
        low: Number(item.low) || 0,
        close: Number(item.close) || 0,
        volume: Number(item.volume) || 0,
      }))
      .filter((item) => item.open > 0 && item.close > 0);
  }, [currentData]);

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        overflow: "hidden",
      }}
    >
      {/* Chart Header */}
      <ChartHeader
        symbol={symbol}
        interval={interval}
        onIntervalChange={setInterval}
        chartType={chartType}
        onChartTypeChange={setChartType}
        indicators={indicators}
        onIndicatorsChange={setIndicators}
      />

      {/* Chart Canvas */}
      <Box
        ref={chartContainerRef}
        sx={{ flex: 1, overflow: "hidden", position: "relative" }}
      >
        {isLoading ? (
          <LoadingSpinner
            variant="chart"
            height="100%"
            message="차트 데이터를 불러오는 중..."
          />
        ) : candlestickData.length > 0 && dimensions.width > 0 ? (
          <ReactFinancialChart
            data={candlestickData}
            symbol={symbol}
            height={dimensions.height}
            width={dimensions.width}
            chartType={chartType}
            indicators={indicators}
          />
        ) : (
          <Box
            display="flex"
            alignItems="center"
            justifyContent="center"
            height="100%"
          >
            <Box textAlign="center">
              <Box
                component="span"
                sx={{ fontSize: "0.875rem", color: "text.secondary" }}
              >
                차트 데이터를 불러올 수 없습니다
              </Box>
            </Box>
          </Box>
        )}
      </Box>

      {/* Chart Footer */}
      <ChartFooter
        onStartDateChange={setStartDate}
        onEndDateChange={setEndDate}
        onIntervalChange={setInterval}
      />
    </Box>
  );
}
