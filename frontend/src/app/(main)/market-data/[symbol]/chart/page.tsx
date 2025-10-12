"use client";

import LoadingSpinner from "@/components/common/LoadingSpinner";
import LightWeightChart from "@/components/market-data/LightweightChart";
import ChartControls from "@/components/market-data/ChartControls";
import {
  useStockDailyPrices,
  useStockMonthlyPrices,
  useStockWeeklyPrices,
} from "@/hooks/useStocks";
import {
  Box,
  Card,
  CardContent,
  Container,
  Paper,
  Typography,
} from "@mui/material";
import type { Dayjs } from "dayjs";
import dayjs from "dayjs";
import { useParams } from "next/navigation";
import { useMemo, useState } from "react";

export default function SymbolChartPage() {
  const params = useParams();
  const symbol = (params.symbol as string)?.toUpperCase();

  // 차트 상태
  const [chartType, setChartType] = useState<string>("candlestick");
  const [interval, setInterval] = useState<string>("daily");
  const [adjusted, setAdjusted] = useState(true);
  const [startDate, setStartDate] = useState<Dayjs | null>(
    dayjs().subtract(1, "year")
  );
  const [endDate, setEndDate] = useState<Dayjs | null>(dayjs());

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
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box display="flex" flexDirection="column" gap={3}>
        {/* 헤더 */}
        <Box>
          <Typography variant="h4" gutterBottom>
            {symbol} - Chart Analysis
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Interactive price chart with technical analysis tools
          </Typography>
        </Box>

        {/* 차트 컨트롤 */}
        <Paper elevation={1} sx={{ p: 2 }}>
          <ChartControls
            startDate={startDate}
            endDate={endDate}
            onStartDateChange={setStartDate}
            onEndDateChange={setEndDate}
            interval={interval}
            onIntervalChange={setInterval}
            chartType={chartType}
            onChartTypeChange={setChartType}
            adjusted={adjusted}
            onAdjustedChange={setAdjusted}
            isLoading={isLoading}
          />
        </Paper>

        {/* 차트 */}
        <Card>
          <CardContent>
            {isLoading ? (
              <LoadingSpinner
                variant="chart"
                height={600}
                message="차트 데이터를 불러오는 중..."
              />
            ) : candlestickData.length > 0 ? (
              <LightWeightChart
                data={candlestickData}
                symbol={symbol}
                height={600}
                showVolume={true}
              />
            ) : (
              <Box
                height={600}
                display="flex"
                alignItems="center"
                justifyContent="center"
              >
                <Typography color="text.secondary">
                  차트 데이터를 불러올 수 없습니다
                </Typography>
              </Box>
            )}
          </CardContent>
        </Card>

        {/* 차트 정보 */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Chart Information
            </Typography>
            <Box display="flex" flexDirection="column" gap={1}>
              <InfoRow label="Symbol" value={symbol} />
              <InfoRow label="Interval" value={interval.toUpperCase()} />
              <InfoRow label="Data Points" value={candlestickData.length} />
              <InfoRow
                label="Adjusted Prices"
                value={adjusted ? "Yes" : "No"}
              />
              <InfoRow
                label="Date Range"
                value={`${dateRange.startDate} ~ ${dateRange.endDate}`}
              />
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Container>
  );
}

// Helper component
function InfoRow({ label, value }: { label: string; value: string | number }) {
  return (
    <Box display="flex" justifyContent="space-between">
      <Typography variant="body2" color="text.secondary">
        {label}
      </Typography>
      <Typography variant="body2" fontWeight="medium">
        {value}
      </Typography>
    </Box>
  );
}
