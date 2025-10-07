"use client";

import { Box } from "@mui/material";
import { LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { useQuery } from "@tanstack/react-query";
import dayjs, { type Dayjs } from "dayjs";
import "dayjs/locale/ko";
import React from "react";

import {
  marketDataGetAvailableSymbolsOptions,
  marketDataGetMarketDataOptions,
} from "@/client/@tanstack/react-query.gen";
import CandlestickChart from "@/components/market-data/CandlestickChart";
import ChartControls from "@/components/market-data/ChartControls";
import MarketDataHeader from "@/components/market-data/MarketDataHeader";
import WatchList from "@/components/market-data/WatchList";

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
  const [interval, setInterval] = React.useState<string>("1d");
  const [chartType, setChartType] = React.useState("candlestick");
  const [forceRefresh, setForceRefresh] = React.useState<boolean>(false);

  // 사용 가능한 심볼 목록 조회
  const { data: availableSymbols, isLoading: symbolsLoading } = useQuery(
    marketDataGetAvailableSymbolsOptions()
  );

  // 선택된 심볼의 마켓 데이터 조회
  const {
    data: marketData,
    isLoading: dataLoading,
    refetch: refetchMarketData,
  } = useQuery({
    ...marketDataGetMarketDataOptions({
      path: { symbol: selectedSymbol },
      query: {
        start_date: startDate?.toDate() || dayjs().toDate(),
        end_date: endDate?.toDate() || dayjs().toDate(),
        force_refresh: forceRefresh,
      },
    }),
    enabled: !!selectedSymbol && !!startDate && !!endDate,
  });

  // 첫 번째 심볼 자동 선택
  React.useEffect(() => {
    if (availableSymbols && availableSymbols.length > 0 && !selectedSymbol) {
      setSelectedSymbol(availableSymbols[0]);
    }
  }, [availableSymbols, selectedSymbol]);

  const handleRefresh = React.useCallback(() => {
    setForceRefresh(true);
    refetchMarketData().finally(() => {
      setForceRefresh(false);
    });
  }, [refetchMarketData]);

  const handleSymbolChange = React.useCallback((symbol: string) => {
    setSelectedSymbol(symbol);
  }, []);

  // 마켓 데이터를 차트 데이터로 변환
  const chartData: CandlestickData[] = React.useMemo(() => {
    if (!marketData || !Array.isArray(marketData)) return [];

    return (marketData as any[])
      .map((item) => ({
        time: dayjs(item.date).format("YYYY-MM-DD"),
        open: item.open,
        high: item.high,
        low: item.low,
        close: item.close,
        volume: item.volume || 0,
      }))
      .sort((a, b) => a.time.localeCompare(b.time));
  }, [marketData]);

  // 요약 데이터 생성
  const summaryData = React.useMemo(() => {
    if (!chartData.length) return null;

    const latestData = chartData[chartData.length - 1];
    const previousData = chartData[chartData.length - 2];

    if (!latestData || !previousData) return null;

    const change = latestData.close - previousData.close;
    const changePercent = (change / previousData.close) * 100;

    return {
      symbol: selectedSymbol,
      currentPrice: latestData.close,
      change,
      changePercent,
      volume: latestData.volume,
      high: latestData.high,
      low: latestData.low,
      open: latestData.open,
      previousClose: previousData.close,
    };
  }, [chartData, selectedSymbol]);

  const isLoading = symbolsLoading || dataLoading;

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
