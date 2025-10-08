"use client";

import { Box } from "@mui/material";
import { LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import dayjs, { type Dayjs } from "dayjs";
import "dayjs/locale/ko";
import React from "react";

import CandlestickChart from "@/components/market-data/CandlestickChart";
import ChartControls from "@/components/market-data/ChartControls";
import MarketDataHeader from "@/components/market-data/MarketDataHeader";
import WatchList from "@/components/market-data/WatchList";
import {
  useStockDailyPrices,
  useStockHistorical,
  useStockQuote,
} from "@/hooks/useStocks";
import { useWatchlist, useWatchlistDetail } from "@/hooks/useWatchList";

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
  const [selectedSymbol, setSelectedSymbol] = React.useState<string>("AAPL");
  const [startDate, setStartDate] = React.useState<Dayjs | null>(
    dayjs().subtract(1, "month")
  );
  const [endDate, setEndDate] = React.useState<Dayjs | null>(dayjs());
  const [interval, setInterval] = React.useState<string>("1d");
  const [chartType, setChartType] = React.useState("candlestick");

  // 새로운 훅들 사용
  const {
    isLoading: { watchlistList: watchlistLoading },
  } = useWatchlist();
  const { data: watchlistDetail } = useWatchlistDetail("default");

  // 선택된 심볼의 데이터 조회
  const {
    data: dailyPrices,
    isLoading: dailyLoading,
    refetch: refetchDaily,
  } = useStockDailyPrices(selectedSymbol);
  const { data: currentQuote, isLoading: quoteLoading } =
    useStockQuote(selectedSymbol);
  const {
    data: historicalData,
    isLoading: historicalLoading,
    refetch: refetchHistorical,
  } = useStockHistorical(selectedSymbol, {
    startDate: startDate?.format("YYYY-MM-DD"),
    endDate: endDate?.format("YYYY-MM-DD"),
    frequency: interval === "1d" ? "daily" : interval,
  });

  // 사용 가능한 심볼들 (워치리스트에서 가져오기)
  const availableSymbols = React.useMemo(() => {
    const watchlistSymbols = (watchlistDetail as any)?.symbols || [];
    const defaultSymbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "NVDA"];
    return watchlistSymbols.length > 0 ? watchlistSymbols : defaultSymbols;
  }, [watchlistDetail]);

  // 첫 번째 심볼 자동 선택
  React.useEffect(() => {
    if (
      availableSymbols &&
      availableSymbols.length > 0 &&
      !availableSymbols.includes(selectedSymbol)
    ) {
      setSelectedSymbol(availableSymbols[0]);
    }
  }, [availableSymbols, selectedSymbol]);

  const handleRefresh = React.useCallback(() => {
    refetchDaily();
    refetchHistorical();
  }, [refetchDaily, refetchHistorical]);

  const handleSymbolChange = React.useCallback((symbol: string) => {
    setSelectedSymbol(symbol);
  }, []);

  // 차트 데이터 결정 (히스토리컬 데이터 우선, 없으면 일일 데이터)
  const rawData = historicalData || dailyPrices;

  // 마켓 데이터를 차트 데이터로 변환
  const chartData: CandlestickData[] = React.useMemo(() => {
    if (!rawData || !Array.isArray(rawData)) return [];

    return (rawData as any[])
      .map((item) => ({
        time: dayjs(item.date || item.timestamp).format("YYYY-MM-DD"),
        open: Number(item.open) || 0,
        high: Number(item.high) || 0,
        low: Number(item.low) || 0,
        close: Number(item.close) || 0,
        volume: Number(item.volume) || 0,
      }))
      .filter(
        (item) =>
          item.open > 0 && item.high > 0 && item.low > 0 && item.close > 0
      )
      .sort((a, b) => a.time.localeCompare(b.time));
  }, [rawData]);

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

  const isLoading =
    watchlistLoading || dailyLoading || quoteLoading || historicalLoading;

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
              {chartData.length > 0 ? (
                <CandlestickChart
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
                      : "종목을 선택하면 차트가 표시됩니다"}
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
              onRefresh={handleRefresh}
              isLoading={isLoading}
              chartType={chartType}
              onChartTypeChange={setChartType}
            />
          </Box>

          {/* 오른쪽 - 워치리스트 */}
          <Box sx={{ width: 320, p: 2, borderLeft: 1, borderColor: "divider" }}>
            <WatchList
              selectedSymbol={selectedSymbol}
              onSymbolChange={handleSymbolChange}
            />
          </Box>
        </Box>
      </Box>
    </LocalizationProvider>
  );
}
