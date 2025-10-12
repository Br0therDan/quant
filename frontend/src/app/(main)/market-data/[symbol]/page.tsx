"use client";

import LoadingSpinner from "@/components/common/LoadingSpinner";
import LightWeightChart from '@/components/market-data/LightweightChart';

import { useStockIntraday, useStockQuote } from "@/hooks/useStocks";
import {
  useFundamentalBalanceSheet,
  useFundamentalCompanyOverview,
  useFundamentalEarnings,
  useFundamentalIncomeStatement,
} from "@/hooks/ussFundamental";
import {
  ShowChart as ChartIcon,
  VerifiedUser as VerifiedIcon,
} from "@mui/icons-material";
import {
  Box,
  Button,
  Chip,
  Divider,
  Grid,
  Paper,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import dayjs from "dayjs";
import { useParams, useRouter } from "next/navigation";
import { useMemo } from "react";

export default function SymbolOverviewPage() {
  const params = useParams();
  const router = useRouter();
  const symbol = (params.symbol as string)?.toUpperCase();

  // 데이터 fetching
  const { data: companyResponse, isLoading: companyLoading } =
    useFundamentalCompanyOverview(symbol);
  const { data: quoteData, isLoading: quoteLoading } = useStockQuote(symbol);
  const { data: earningsResponse } = useFundamentalEarnings(symbol);
  const { data: incomeResponse, isLoading: incomeLoading } =
    useFundamentalIncomeStatement(symbol);
  const { data: balanceResponse, isLoading: balanceLoading } =
    useFundamentalBalanceSheet(symbol);

  // Intraday 차트 데이터 (오늘/최근 거래일)
  const { data: chartData, isLoading: chartLoading } = useStockIntraday(
    symbol,
    {
      interval: "5min", // 5분 간격
    }
  );

  const companyData = companyResponse?.data;
  const earningsData = earningsResponse?.data?.[0]; // 배열의 첫 번째 요소
  const incomeData = incomeResponse?.data?.[0]; // 배열의 첫 번째 요소
  const balanceData = balanceResponse?.data?.[0]; // 배열의 첫 번째 요소

  // 가격 정보
  const currentPrice = quoteData?.price ? Number(quoteData.price) : 0;
  const priceChange = quoteData?.change ? Number(quoteData.change) : 0;
  const priceChangePercent = quoteData?.change_percent
    ? Number(quoteData.change_percent)
    : 0;
  const isPositive = priceChange >= 0;

  // 차트 데이터 변환
  const candlestickData = useMemo(() => {
    if (!chartData || typeof chartData !== "object" || !("data" in chartData)) {
      return [];
    }

    const dataArray = Array.isArray(chartData.data) ? chartData.data : [];

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
  }, [chartData]);

  // 숫자 포맷팅 헬퍼
  const formatBillion = (value: any) => {
    if (!value || value === "None") return "—";
    const num = Number(value);
    if (Number.isNaN(num)) return "—";
    return `${(num / 1e9).toFixed(2)}B`;
  };

  const formatMillion = (value: any) => {
    if (!value || value === "None") return "—";
    const num = Number(value);
    if (Number.isNaN(num)) return "—";
    return `${(num / 1e6).toFixed(2)}M`;
  };

  return (
    <Box sx={{ maxWidth: 1400, mx: "auto" }}>
      {/* 헤더: 회사명 & 가격 정보 */}
      <Box sx={{ p: 3, pb: 0 }}>
        <Box
          display="flex"
          justifyContent="space-between"
          alignItems="flex-start"
          mb={2}
        >
          {/* 왼쪽: 회사명 & 메타 정보 */}
          <Box>
            {companyLoading ? (
              <Skeleton width={300} height={40} />
            ) : (
              <>
                <Typography variant="h4" fontWeight="600" gutterBottom>
                  {companyData?.name || symbol}
                </Typography>
                <Box display="flex" gap={1} alignItems="center">
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    fontWeight="500"
                  >
                    {symbol}
                  </Typography>
                  <VerifiedIcon
                    sx={{ fontSize: 16, color: "primary.main" }}
                    titleAccess="Nasdaq Stock Market"
                  />
                  <Chip
                    label={companyData?.exchange || "Nasdaq Stock Market"}
                    size="small"
                    variant="outlined"
                    sx={{ height: 20 }}
                  />
                </Box>
              </>
            )}
          </Box>

          {/* 오른쪽: 현재가 & 변동 */}
          <Box textAlign="right">
            {quoteLoading ? (
              <Skeleton width={200} height={60} />
            ) : (
              <>
                <Box display="flex" alignItems="baseline" gap={1}>
                  <Typography variant="h3" fontWeight="700">
                    {currentPrice.toFixed(2)}
                  </Typography>
                  <Typography variant="h6" color="text.secondary">
                    USD
                  </Typography>
                </Box>
                <Box
                  display="flex"
                  alignItems="center"
                  justifyContent="flex-end"
                  gap={0.5}
                  mt={0.5}
                >
                  <Typography
                    variant="h6"
                    fontWeight="600"
                    color={isPositive ? "error.main" : "success.main"}
                  >
                    {isPositive ? "−" : "+"}
                    {Math.abs(priceChange).toFixed(2)}
                  </Typography>
                  <Typography
                    variant="h6"
                    fontWeight="600"
                    color={isPositive ? "error.main" : "success.main"}
                  >
                    {isPositive ? "−" : "+"}
                    {Math.abs(priceChangePercent).toFixed(2)}%
                  </Typography>
                </Box>
                <Typography
                  variant="caption"
                  color="text.secondary"
                  display="block"
                  mt={0.5}
                >
                  {dayjs().format("M월 D일 HH:mm")} GMT+9 에 마감 때
                </Typography>
              </>
            )}
          </Box>
        </Box>
      </Box>

      <Grid container spacing={3} sx={{ p: 3 }}>
        {/* 차트 섹션 */}
        <Grid size={12}>
          <Paper sx={{ p: 3 }}>
            <Box
              display="flex"
              justifyContent="space-between"
              alignItems="center"
              mb={2}
            >
              <Typography variant="h6" fontWeight="600">
                {symbol} 차트
              </Typography>
              <Button
                variant="outlined"
                size="small"
                startIcon={<ChartIcon />}
                onClick={() => router.push(`/market-data/${symbol}/chart`)}
              >
                전체 차트
              </Button>
            </Box>
            {chartLoading ? (
              <LoadingSpinner
                variant="chart"
                height={400}
                message="차트 로딩 중..."
              />
            ) : candlestickData.length > 0 ? (
              <LightWeightChart
                data={candlestickData}
                symbol={symbol}
                height={400}
                showVolume={true}
              />
            ) : (
              <Box
                height={400}
                display="flex"
                alignItems="center"
                justifyContent="center"
              >
                <Typography color="text.secondary">
                  차트 데이터를 불러올 수 없습니다
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* 예정된 실적 발표 섹션 */}
        <Grid size={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" fontWeight="600" gutterBottom>
              {symbol} 예정된 실적 발표
            </Typography>
            <Divider sx={{ my: 2 }} />
            <Grid container spacing={3}>
              <Grid size={{ xs: 12, sm: 4 }}>
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    다음 리포트 날짜
                  </Typography>
                  <Typography variant="body1" fontWeight="500">
                    {earningsData?.reported_date
                      ? dayjs(earningsData.reported_date).format(
                          "YYYY년 M월 D일"
                        )
                      : "—"}
                  </Typography>
                </Box>
              </Grid>
              <Grid size={{ xs: 12, sm: 4 }}>
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    리포트 기간
                  </Typography>
                  <Typography variant="body1" fontWeight="500">
                    {earningsData?.fiscal_date_ending
                      ? dayjs(earningsData.fiscal_date_ending).format(
                          "YYYY Q[Q]"
                        )
                      : "—"}
                  </Typography>
                </Box>
              </Grid>
              <Grid size={{ xs: 12, sm: 4 }}>
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    추정 EPS
                  </Typography>
                  <Typography variant="body1" fontWeight="500">
                    {earningsData?.estimated_eps
                      ? `${Number(earningsData.estimated_eps).toFixed(2)} USD`
                      : companyData?.eps
                      ? `${Number(companyData.eps).toFixed(2)} USD`
                      : "—"}
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* 주요 통계 섹션 */}
        <Grid size={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" fontWeight="600" gutterBottom>
              주요 통계
            </Typography>
            <Divider sx={{ my: 2 }} />
            <Grid container spacing={3}>
              <Grid size={{ xs: 12, md: 6 }}>
                <Box display="flex" flexDirection="column" gap={2}>
                  <StatRow
                    label="시가총액"
                    value={formatBillion(companyData?.market_capitalization)}
                  />
                  <StatRow
                    label="기본 EPS (TTM)"
                    value={
                      companyData?.eps
                        ? `${Number(companyData.eps).toFixed(2)} USD`
                        : "—"
                    }
                  />
                  <StatRow label="베타 (5Y)" value={companyData?.beta || "—"} />
                </Box>
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <Box display="flex" flexDirection="column" gap={2}>
                  <StatRow
                    label="주가 수익 비율 (TTM)"
                    value={companyData?.pe_ratio || "—"}
                  />
                  <StatRow
                    label="순수익 (FY)"
                    value={formatMillion(companyData?.revenue_ttm)}
                  />
                  <StatRow
                    label="매출 (회계연도)"
                    value={formatBillion(companyData?.revenue_ttm)}
                  />
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* 재무제표 섹션 - 손익계산서 & 대차대조표 */}
        <Grid size={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" fontWeight="600" gutterBottom>
              재무제표
            </Typography>
            <Divider sx={{ my: 2 }} />

            {/* 부채 수준 및 범위 */}
            <Box mb={4}>
              <Typography variant="subtitle1" fontWeight="600" gutterBottom>
                부채 수준 및 범위
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 600 }}>항목</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 600 }}>
                        금액
                      </TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    <TableRow>
                      <TableCell>총 부채</TableCell>
                      <TableCell align="right">
                        {balanceLoading ? (
                          <Skeleton width={100} />
                        ) : (
                          formatBillion(balanceData?.total_liabilities)
                        )}
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>유동 부채</TableCell>
                      <TableCell align="right">
                        {balanceLoading ? (
                          <Skeleton width={100} />
                        ) : (
                          formatBillion(balanceData?.total_current_liabilities)
                        )}
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>장기 부채</TableCell>
                      <TableCell align="right">
                        {balanceLoading ? (
                          <Skeleton width={100} />
                        ) : (
                          formatBillion(balanceData?.long_term_debt)
                        )}
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>

            {/* 여백 (마진) */}
            <Box>
              <Typography variant="subtitle1" fontWeight="600" gutterBottom>
                여백
              </Typography>
              <Grid container spacing={2}>
                <Grid size={{ xs: 12, sm: 4 }}>
                  <StatRow
                    label="영업 이익"
                    value={
                      incomeLoading ? (
                        <Skeleton width={80} />
                      ) : (
                        formatBillion(incomeData?.operating_income)
                      )
                    }
                  />
                </Grid>
                <Grid size={{ xs: 12, sm: 4 }}>
                  <StatRow
                    label="매출총이익"
                    value={
                      incomeLoading ? (
                        <Skeleton width={80} />
                      ) : (
                        formatBillion(incomeData?.gross_profit)
                      )
                    }
                  />
                </Grid>
                <Grid size={{ xs: 12, sm: 4 }}>
                  <StatRow
                    label="세전 이익"
                    value={
                      incomeLoading ? (
                        <Skeleton width={80} />
                      ) : (
                        formatBillion(incomeData?.income_before_tax)
                      )
                    }
                  />
                </Grid>
              </Grid>
            </Box>
          </Paper>
        </Grid>

        {/* 회사 정보 */}
        <Grid size={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" fontWeight="600" gutterBottom>
              {companyData?.name || symbol} 정보
            </Typography>
            <Divider sx={{ my: 2 }} />

            <Grid container spacing={3} mb={3}>
              <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    섹터
                  </Typography>
                  <Typography variant="body1" fontWeight="500">
                    {companyData?.sector || "—"}
                  </Typography>
                </Box>
              </Grid>
              <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    산업
                  </Typography>
                  <Typography variant="body1" fontWeight="500">
                    {companyData?.industry || "—"}
                  </Typography>
                </Box>
              </Grid>
              <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    본부
                  </Typography>
                  <Typography variant="body1" fontWeight="500">
                    {companyData?.country || "—"}
                  </Typography>
                </Box>
              </Grid>
              <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    회계연도 종료
                  </Typography>
                  <Typography variant="body1" fontWeight="500">
                    {companyData?.fiscal_year_end || "—"}
                  </Typography>
                </Box>
              </Grid>
            </Grid>

            <Divider sx={{ my: 2 }} />

            <Typography variant="h6" fontWeight="600" gutterBottom>
              관련 주식
            </Typography>
            <Typography variant="body2" color="text.secondary" mb={2}>
              {symbol}과 같은 업계의 다른 유명 인사들을 확인해 보세요.
            </Typography>
            <Typography variant="body2" color="text.secondary">
              관련 주식 정보는 준비 중입니다.
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

// Helper component for statistics rows
function StatRow({
  label,
  value,
}: {
  label: string;
  value: string | number | React.ReactNode;
}) {
  return (
    <Box
      display="flex"
      justifyContent="space-between"
      alignItems="center"
      py={0.5}
    >
      <Typography variant="body2" color="text.secondary">
        {label}
      </Typography>
      <Typography variant="body2" fontWeight="500">
        {value}
      </Typography>
    </Box>
  );
}
