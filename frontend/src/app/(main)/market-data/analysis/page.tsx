"use client";

import {
  Alert,
  Box,
  Button,
  Container,
  Skeleton,
  Typography,
} from "@mui/material";
import { LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { useQuery } from "@tanstack/react-query";
import dayjs, { Dayjs } from "dayjs";
import React from "react";

import PageContainer from "@/components/layout/PageContainer";
import MarketDataControls from "@/components/market-data/MarketDataControls";
import TechnicalIndicators from "@/components/market-data/TechnicalIndicators";

import {
  marketDataGetAvailableSymbolsOptions,
  marketDataGetMarketDataOptions,
} from "@/client/@tanstack/react-query.gen";

interface CandlestickData {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export default function TechnicalAnalysisPage() {
  const [selectedSymbol, setSelectedSymbol] = React.useState<string>("");
  const [startDate, setStartDate] = React.useState<Dayjs | null>(
    dayjs().subtract(6, "month")
  );
  const [endDate, setEndDate] = React.useState<Dayjs | null>(dayjs());
  const [interval, setInterval] = React.useState<string>("1d");
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
    error,
  } = useQuery({
    ...marketDataGetMarketDataOptions({
      path: { symbol: selectedSymbol },
      query: {
        start_date: new Date(
          startDate?.format("YYYY-MM-DD") || dayjs().format("YYYY-MM-DD")
        ),
        end_date: new Date(
          endDate?.format("YYYY-MM-DD") || dayjs().format("YYYY-MM-DD")
        ),
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

  const handleRefresh = () => {
    setForceRefresh(true);
    refetchMarketData().finally(() => {
      setForceRefresh(false);
    });
  };

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

  const isLoading = symbolsLoading || dataLoading;

  if (error) {
    return (
      <LocalizationProvider dateAdapter={AdapterDayjs}>
        <PageContainer
          title="기술적 분석"
          breadcrumbs={[
            { title: "데이터 관리" },
            { title: "마켓 데이터" },
            { title: "기술적 분석" },
          ]}
        >
          <Container maxWidth="xl">
            <Alert severity="error" sx={{ mb: 2 }}>
              데이터를 불러오는 중 오류가 발생했습니다:{" "}
              {error.message || String(error)}
            </Alert>
            <Button variant="outlined" onClick={handleRefresh}>
              다시 시도
            </Button>
          </Container>
        </PageContainer>
      </LocalizationProvider>
    );
  }

  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <PageContainer
        title="기술적 분석"
        breadcrumbs={[
          { title: "데이터 관리" },
          { title: "마켓 데이터" },
          { title: "기술적 분석" },
        ]}
        actions={
          <Button
            variant="contained"
            onClick={handleRefresh}
            disabled={isLoading}
          >
            새로고침
          </Button>
        }
      >
        <Container maxWidth="xl">
          <Box mb={4}>
            <Typography variant="h4" component="h1" gutterBottom>
              기술적 지표 분석
            </Typography>
            <Typography variant="subtitle1" color="text.secondary">
              RSI, MACD, 볼린저 밴드 등의 기술적 지표로 주식을 분석합니다.
            </Typography>
          </Box>

          <Box display="flex" flexDirection="column" gap={3}>
            <Box display="flex" gap={3}>
              {/* 좌측 컨트롤 패널 */}
              <Box width={300} flexShrink={0}>
                {isLoading ? (
                  <Skeleton variant="rectangular" height={400} />
                ) : (
                  <MarketDataControls
                    selectedSymbol={selectedSymbol}
                    onSymbolChange={setSelectedSymbol}
                    availableSymbols={(availableSymbols as string[]) || []}
                    startDate={startDate}
                    endDate={endDate}
                    onStartDateChange={setStartDate}
                    onEndDateChange={setEndDate}
                    interval={interval}
                    onIntervalChange={setInterval}
                    onRefresh={handleRefresh}
                    isLoading={isLoading}
                  />
                )}
              </Box>

              {/* 우측 지표 분석 영역 */}
              <Box flexGrow={1}>
                {chartData.length > 0 ? (
                  <TechnicalIndicators
                    data={chartData}
                    symbol={selectedSymbol}
                    height={400}
                  />
                ) : (
                  <Box
                    display="flex"
                    alignItems="center"
                    justifyContent="center"
                    height={400}
                    border={1}
                    borderColor="divider"
                    borderRadius={1}
                  >
                    <Typography variant="h6" color="text.secondary">
                      {isLoading
                        ? "기술적 지표를 로딩 중입니다..."
                        : "종목을 선택하면 기술적 지표가 표시됩니다"}
                    </Typography>
                  </Box>
                )}
              </Box>
            </Box>

            {/* 지표 설명 섹션 */}
            {chartData.length > 0 && (
              <Box mt={4}>
                <Typography variant="h5" gutterBottom>
                  기술적 지표 해석 가이드
                </Typography>
                <Box
                  display="grid"
                  gridTemplateColumns="repeat(auto-fit, minmax(300px, 1fr))"
                  gap={3}
                >
                  <Box p={3} border={1} borderColor="divider" borderRadius={1}>
                    <Typography variant="h6" gutterBottom color="primary">
                      RSI (상대강도지수)
                    </Typography>
                    <Typography variant="body2" paragraph>
                      • <strong>과매수:</strong> RSI 70 이상 (매도 신호)
                    </Typography>
                    <Typography variant="body2" paragraph>
                      • <strong>과매도:</strong> RSI 30 이하 (매수 신호)
                    </Typography>
                    <Typography variant="body2">
                      • <strong>중립:</strong> RSI 30-70 (추세 지속)
                    </Typography>
                  </Box>

                  <Box p={3} border={1} borderColor="divider" borderRadius={1}>
                    <Typography variant="h6" gutterBottom color="secondary">
                      MACD
                    </Typography>
                    <Typography variant="body2" paragraph>
                      • <strong>골든크로스:</strong> MACD선이 시그널선 위로
                      (매수 신호)
                    </Typography>
                    <Typography variant="body2" paragraph>
                      • <strong>데드크로스:</strong> MACD선이 시그널선 아래로
                      (매도 신호)
                    </Typography>
                    <Typography variant="body2">
                      • <strong>히스토그램:</strong> 모멘텀 강도 (0선 돌파 주목)
                    </Typography>
                  </Box>

                  <Box p={3} border={1} borderColor="divider" borderRadius={1}>
                    <Typography variant="h6" gutterBottom color="warning.main">
                      볼린저 밴드
                    </Typography>
                    <Typography variant="body2" paragraph>
                      • <strong>상단 밴드 터치:</strong> 과매수 가능성 (매도
                      고려)
                    </Typography>
                    <Typography variant="body2" paragraph>
                      • <strong>하단 밴드 터치:</strong> 과매도 가능성 (매수
                      고려)
                    </Typography>
                    <Typography variant="body2">
                      • <strong>밴드 수축/확장:</strong> 변동성 변화 신호
                    </Typography>
                  </Box>
                </Box>
              </Box>
            )}
          </Box>
        </Container>
      </PageContainer>
    </LocalizationProvider>
  );
}
