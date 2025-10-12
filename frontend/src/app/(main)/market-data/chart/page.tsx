"use client";

import { Box } from "@mui/material";
import { LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import dayjs, { type Dayjs } from "dayjs";
import "dayjs/locale/ko";
import React from "react";
import LightWeightChart from '@/components/market-data/LightweightChart';

import ChartControls from "@/components/market-data/ChartControls";
import MarketDataHeader from "@/components/market-data/MarketDataHeader";
import {
  useStockDailyPrices,
  useStockIntraday,
  useStockMonthlyPrices,
  useStockQuote,
  useStockWeeklyPrices,
} from "@/hooks/useStocks";
import { useWatchlist } from "@/hooks/useWatchList";

// 한국어 로케일 설정
dayjs.locale("ko");

interface CandlestickData {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export default function MarketDataChartPage() {
  const [selectedSymbol, setSelectedSymbol] = React.useState<string>("");
  const [startDate, setStartDate] = React.useState<Dayjs | null>(
    dayjs().subtract(1, "month")
  );
  const [endDate, setEndDate] = React.useState<Dayjs | null>(dayjs());
  const [interval, setInterval] = React.useState<string>("daily"); // 기본값: 일봉
  const [chartType, setChartType] = React.useState("candlestick");
  const [adjusted, setAdjusted] = React.useState(true); // Adjusted prices 기본값

  // 워치리스트 데이터 가져오기
  const {
    watchlistList,
    isLoading: { watchlistList: watchlistLoading },
  } = useWatchlist();

  // API 응답 구조 처리: { user_id, watchlists: [...] }
  const watchlists = React.useMemo(() => {
    if (!watchlistList) return [];

    if (Array.isArray(watchlistList)) {
      return watchlistList;
    }

    if (typeof watchlistList === "object" && "watchlists" in watchlistList) {
      return Array.isArray((watchlistList as any).watchlists)
        ? (watchlistList as any).watchlists
        : [];
    }

    return [];
  }, [watchlistList]);

  // 첫 번째 워치리스트의 첫 번째 심볼을 기본값으로 설정
  React.useEffect(() => {
    if (watchlists.length > 0 && !selectedSymbol) {
      const firstWatchlist = watchlists[0];
      const firstSymbol = firstWatchlist?.symbols?.[0];
      if (firstSymbol) {
        setSelectedSymbol(firstSymbol);
      }
    }
  }, [watchlists, selectedSymbol]);

  // 기간에 따른 적절한 API 선택
  const apiType = React.useMemo(() => {
    // interval 값으로 API 결정
    // 분봉: 1min, 5min, 15min, 30min, 60min
    if (["1min", "5min", "15min", "30min", "60min"].includes(interval)) {
      return "intraday";
    }
    // 주봉
    if (interval === "weekly") {
      return "weekly";
    }
    // 월봉
    if (interval === "monthly") {
      return "monthly";
    }
    // 일봉 (기본값)
    return "daily";
  }, [interval]);

  // 실시간 Quote (항상 필요)
  const { data: currentQuote, isLoading: quoteLoading } =
    useStockQuote(selectedSymbol);

  // Intraday API
  const { data: intradayData, isLoading: intradayLoading } = useStockIntraday(
    selectedSymbol,
    {
      interval: interval as "1min" | "5min" | "15min" | "30min" | "60min",
      enabled: apiType === "intraday" && !!selectedSymbol,
    }
  );

  // Daily API
  const { data: dailyPrices, isLoading: dailyLoading } = useStockDailyPrices(
    selectedSymbol,
    {
      outputsize: "full",
      adjusted,
      startDate: startDate?.format("YYYY-MM-DD"),
      endDate: endDate?.format("YYYY-MM-DD"),
      enabled: apiType === "daily" && !!selectedSymbol,
    }
  );

  // Weekly API
  const { data: weeklyPrices, isLoading: weeklyLoading } = useStockWeeklyPrices(
    selectedSymbol,
    {
      outputsize: "full",
      adjusted,
      startDate: startDate?.format("YYYY-MM-DD"),
      endDate: endDate?.format("YYYY-MM-DD"),
      enabled: apiType === "weekly" && !!selectedSymbol,
    }
  );

  // Monthly API
  const { data: monthlyPrices, isLoading: monthlyLoading } =
    useStockMonthlyPrices(selectedSymbol, {
      outputsize: "full",
      adjusted,
      startDate: startDate?.format("YYYY-MM-DD"),
      endDate: endDate?.format("YYYY-MM-DD"),
      enabled: apiType === "monthly" && !!selectedSymbol,
    });

  // 디버깅: API 호출 조건 확인
  React.useEffect(() => {
    console.log("🔍 API Call Conditions:", {
      selectedSymbol,
      interval,
      apiType,
      startDate: startDate?.format("YYYY-MM-DD"),
      endDate: endDate?.format("YYYY-MM-DD"),
      enabledConditions: {
        intraday: apiType === "intraday" && !!selectedSymbol,
        daily: apiType === "daily" && !!selectedSymbol,
        weekly: apiType === "weekly" && !!selectedSymbol,
        monthly: apiType === "monthly" && !!selectedSymbol,
      },
    });
  }, [selectedSymbol, apiType, interval, startDate, endDate]);

  const handleSymbolChange = React.useCallback((symbol: string) => {
    setSelectedSymbol(symbol);
  }, []);

  // 디버깅: 데이터 상태 확인
  React.useEffect(() => {
    console.log("📊 Chart Data Debug:", {
      selectedSymbol,
      apiType,
      interval,
      intradayData: intradayData
        ? Array.isArray(intradayData)
          ? `Array[${intradayData.length}]`
          : "Object"
        : "null",
      dailyPrices: dailyPrices
        ? Array.isArray(dailyPrices)
          ? `Array[${dailyPrices.length}]`
          : "Object"
        : "null",
      weeklyPrices: weeklyPrices
        ? Array.isArray(weeklyPrices)
          ? `Array[${weeklyPrices.length}]`
          : "Object"
        : "null",
      monthlyPrices: monthlyPrices
        ? Array.isArray(monthlyPrices)
          ? `Array[${monthlyPrices.length}]`
          : "Object"
        : "null",
      isLoading: {
        intradayLoading,
        dailyLoading,
        weeklyLoading,
        monthlyLoading,
      },
    });
  }, [
    selectedSymbol,
    apiType,
    interval,
    intradayData,
    dailyPrices,
    weeklyPrices,
    monthlyPrices,
    intradayLoading,
    dailyLoading,
    weeklyLoading,
    monthlyLoading,
  ]);

  // 차트 데이터 결정 - apiType에 따라 적절한 데이터 선택
  const rawData = React.useMemo(() => {
    if (apiType === "intraday") return intradayData;
    if (apiType === "daily") return dailyPrices;
    if (apiType === "weekly") return weeklyPrices;
    if (apiType === "monthly") return monthlyPrices;
    return null;
  }, [apiType, intradayData, dailyPrices, weeklyPrices, monthlyPrices]);

  // 마켓 데이터를 차트 데이터로 변환
  const chartData: CandlestickData[] = React.useMemo(() => {
    if (!rawData) {
      console.log("📈 No rawData");
      return [];
    }

    console.log("📈 Raw data structure:", rawData);

    // rawData가 배열인지 확인
    let dataArray: any[] = [];

    if (Array.isArray(rawData)) {
      dataArray = rawData;
    } else if (typeof rawData === "object") {
      // 백엔드 응답 구조: { symbol, data: [...], count, start_date, end_date, frequency }
      if ("data" in rawData && Array.isArray((rawData as any).data)) {
        dataArray = (rawData as any).data;
        console.log("📈 Extracted data array from response:", {
          symbol: (rawData as any).symbol,
          count: (rawData as any).count,
          dataLength: dataArray.length,
        });
      } else if (
        "prices" in rawData &&
        Array.isArray((rawData as any).prices)
      ) {
        dataArray = (rawData as any).prices;
      } else if (
        "time_series" in rawData &&
        Array.isArray((rawData as any).time_series)
      ) {
        dataArray = (rawData as any).time_series;
      } else {
        console.warn("❌ Unknown data structure:", rawData);
        return [];
      }
    }

    if (dataArray.length === 0) {
      console.log("⚠️ Data array is empty");
      return [];
    }

    console.log("📈 Processing chart data:", {
      dataArrayLength: dataArray.length,
      firstItem: dataArray[0],
      lastItem: dataArray[dataArray.length - 1],
    });

    const processed = dataArray
      .map((item) => {
        const dateStr = item.date || item.timestamp || item.time;

        // 인트라데이 데이터인 경우 시간 정보를 포함한 ISO 형식 유지
        // 일별 데이터인 경우 날짜만 추출
        const hasTimeInfo = dateStr?.includes("T") || dateStr?.includes(":");
        const timeValue = hasTimeInfo
          ? dateStr // ISO 8601 형식 유지 (2025-10-07T10:30:00)
          : dayjs(dateStr).format("YYYY-MM-DD"); // 일별 데이터 (2025-10-07)

        return {
          time: timeValue,
          open: Number(item.open) || 0,
          high: Number(item.high) || 0,
          low: Number(item.low) || 0,
          close: Number(item.close) || 0,
          volume: Number(item.volume) || 0,
        };
      })
      .filter(
        (item) =>
          item.open > 0 && item.high > 0 && item.low > 0 && item.close > 0
      )
      .sort((a, b) => {
        // 시간 정보가 있는 경우 ISO 문자열 비교, 없는 경우 날짜 문자열 비교
        return a.time.localeCompare(b.time);
      });

    console.log("✅ Processed chart data:", {
      count: processed.length,
      firstItem: processed[0],
      lastItem: processed[processed.length - 1],
    });

    return processed;
  }, [rawData]);

  // chartData 변경 감지
  React.useEffect(() => {
    console.log("📊 ChartData Changed:", {
      chartDataLength: chartData.length,
      hasData: chartData.length > 0,
      firstItem: chartData[0],
      lastItem: chartData[chartData.length - 1],
    });
  }, [chartData]);

  // 요약 데이터 생성 (실시간 호가 + 차트 데이터 조합)
  const summaryData = React.useMemo(() => {
    if (!chartData.length && !currentQuote) return null;

    const latestChartData = chartData[chartData.length - 1];
    const previousChartData = chartData[chartData.length - 2];

    // 실시간 호가 정보가 있으면 우선 사용
    if (currentQuote) {
      const currentPrice =
        Number((currentQuote as any)?.price) || latestChartData?.close || 0;
      const previousClose =
        Number((currentQuote as any)?.previous_close) ||
        previousChartData?.close ||
        0;
      const change = currentPrice - previousClose;
      const changePercent =
        previousClose > 0 ? (change / previousClose) * 100 : 0;

      return {
        symbol: selectedSymbol,
        currentPrice,
        change,
        changePercent,
        volume:
          Number((currentQuote as any)?.volume) || latestChartData?.volume || 0,
        high: Number((currentQuote as any)?.high) || latestChartData?.high || 0,
        low: Number((currentQuote as any)?.low) || latestChartData?.low || 0,
        open: Number((currentQuote as any)?.open) || latestChartData?.open || 0,
        previousClose,
        marketCap: (currentQuote as any)?.market_cap,
        peRatio: (currentQuote as any)?.pe_ratio,
      };
    } // 차트 데이터만 있는 경우
    if (latestChartData && previousChartData) {
      const change = latestChartData.close - previousChartData.close;
      const changePercent = (change / previousChartData.close) * 100;

      return {
        symbol: selectedSymbol,
        currentPrice: latestChartData.close,
        change,
        changePercent,
        volume: latestChartData.volume,
        high: latestChartData.high,
        low: latestChartData.low,
        open: latestChartData.open,
        previousClose: previousChartData.close,
      };
    }

    return null;
  }, [chartData, currentQuote, selectedSymbol]);

  const isLoading = React.useMemo(() => {
    let dataLoading = false;
    if (apiType === "intraday") dataLoading = intradayLoading;
    else if (apiType === "daily") dataLoading = dailyLoading;
    else if (apiType === "weekly") dataLoading = weeklyLoading;
    else if (apiType === "monthly") dataLoading = monthlyLoading;

    return watchlistLoading || quoteLoading || dataLoading;
  }, [
    watchlistLoading,
    quoteLoading,
    apiType,
    intradayLoading,
    dailyLoading,
    weeklyLoading,
    monthlyLoading,
  ]);

  return (
    <LocalizationProvider dateAdapter={AdapterDayjs} adapterLocale="ko">
      <Box sx={{ height: "100vh", display: "flex", flexDirection: "column" }}>
        {/* 상단 헤더 - 심볼 정보 및 가격 */}
        <MarketDataHeader data={summaryData} isLoading={isLoading} />

        {/* 메인 컨텐츠 영역 */}
        <Box sx={{ flexGrow: 1, display: "flex" }}>
          {/* 왼쪽 - 차트 영역 */}
          <Box sx={{ flexGrow: 1, display: "flex", flexDirection: "column" }}>
            {/* 차트 */}
            <Box sx={{ flexGrow: 1, p: 2 }}>
              {!selectedSymbol ? (
                <Box
                  display="flex"
                  alignItems="center"
                  justifyContent="center"
                  height="100%"
                  sx={{
                    border: 1,
                    borderColor: "divider",
                    borderRadius: 1,
                    backgroundColor: "background.paper",
                  }}
                >
                  <Box textAlign="center">
                    워치리스트에서 종목을 선택해주세요
                  </Box>
                </Box>
              ) : chartData.length > 0 ? (
                <LightWeightChart
                  data={chartData}
                  symbol={selectedSymbol}
                  height={
                    typeof window !== "undefined"
                      ? window.innerHeight - 300
                      : 600
                  }
                  showVolume={true}
                />
              ) : (
                <Box
                  display="flex"
                  alignItems="center"
                  justifyContent="center"
                  height="100%"
                  sx={{
                    border: 1,
                    borderColor: "divider",
                    borderRadius: 1,
                    backgroundColor: "background.paper",
                  }}
                >
                  <Box textAlign="center">
                    {isLoading
                      ? "차트 데이터를 로딩 중입니다..."
                      : "차트 데이터가 없습니다"}
                  </Box>
                </Box>
              )}
            </Box>

            {/* 차트 컨트롤 */}
            <ChartControls
              startDate={startDate}
              endDate={endDate}
              onStartDateChange={setStartDate}
              onEndDateChange={setEndDate}
              interval={interval}
              onIntervalChange={setInterval}
              isLoading={isLoading}
              chartType={chartType}
              onChartTypeChange={setChartType}
              adjusted={adjusted}
              onAdjustedChange={setAdjusted}
            />
          </Box>
        </Box>
      </Box>
    </LocalizationProvider>
  );
}
