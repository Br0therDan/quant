"use client";

import {
  ArrowBack,
  Assessment,
  ShowChart,
  TableChart,
  TrendingDown,
  TrendingUp,
} from "@mui/icons-material";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tabs,
  Typography,
} from "@mui/material";
import { useParams, useRouter } from "next/navigation";
import type React from "react";
import { useState } from "react";

import PageContainer from "@/components/layout/PageContainer";
import StrategyPerformanceSummary from "@/components/strategies/StrategyPerformanceSummary";

import {
  useStrategyDetail,
  useStrategyExecutions,
  useStrategyPerformance,
} from "@/hooks/useStrategy";

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function CustomTabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

export default function StrategyPerformancePage() {
  const router = useRouter();
  const params = useParams();
  const strategyId = params.id as string;

  const [tabValue, setTabValue] = useState(0);
  const [selectedPeriod, setSelectedPeriod] = useState("1Y");

  // 전략 데이터 조회
  const {
    strategy,
    isLoading: strategyLoading,
    error: strategyError,
  } = useStrategyDetail(strategyId);

  // 전략 성과 데이터 조회
  const {
    data: performanceData,
    isLoading: performanceLoading,
    error: performanceError,
  } = useStrategyPerformance(strategyId);

  // 전략 실행 내역 조회
  const {
    data: executionsData,
    isLoading: executionsLoading,
    error: executionsError,
  } = useStrategyExecutions(strategyId);

  // 백테스트 결과는 모의 데이터 사용 (실제 API 구현 시 교체)
  const backtestsLoading = false;
  const backtestsError = null;

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleBack = () => {
    router.push(`/strategies/${strategyId}`);
  };

  // 로딩 및 에러 상태 통합
  const isLoading =
    strategyLoading ||
    backtestsLoading ||
    performanceLoading ||
    executionsLoading;
  const hasError =
    strategyError || backtestsError || performanceError || executionsError;

  if (isLoading) {
    return (
      <PageContainer
        title="성과 분석"
        breadcrumbs={[
          { title: "Strategy Center" },
          { title: "Strategies" },
          { title: "Performance" },
        ]}
      >
        <Box sx={{ display: "flex", justifyContent: "center", py: 4 }}>
          <CircularProgress />
        </Box>
      </PageContainer>
    );
  }

  if (hasError || !strategy) {
    return (
      <PageContainer
        title="성과 분석"
        breadcrumbs={[
          { title: "Strategy Center" },
          { title: "Strategies" },
          { title: "Performance" },
        ]}
      >
        <Alert severity="error">
          데이터를 불러오는 중 오류가 발생했습니다:{" "}
          {
            (
              strategyError ||
              backtestsError ||
              performanceError ||
              executionsError ||
              (hasError as any)
            )?.message
          }
        </Alert>
      </PageContainer>
    );
  }

  // 실제 성과 데이터 (없으면 기본값)
  const performance = performanceData || {
    total_return: 0,
    sharpe_ratio: 0,
    max_drawdown: 0,
    volatility: 0,
    win_rate: 0,
    total_signals: 0,
    buy_signals: 0,
    sell_signals: 0,
  };

  // 실제 실행 내역 (없으면 빈 배열)
  const executions = executionsData?.executions || [];

  // 거래 내역 변환 (Execution → Trade format)
  const trades = executions.map((exec, index) => {
    const metadata = exec.metadata || {};
    const quantity =
      typeof metadata.quantity === "number" ? metadata.quantity : 0;
    const pnl = typeof metadata.pnl === "number" ? metadata.pnl : 0;

    return {
      id: index + 1,
      date: new Date(exec.timestamp).toLocaleDateString("ko-KR"),
      type: exec.signal_type,
      symbol: exec.symbol,
      quantity,
      price: exec.price,
      pnl,
      status: "FILLED" as const,
    };
  });

  // 월별 수익률 계산 (실행 내역 기반)
  const monthlyReturnsMap = executions.reduce((acc, exec) => {
    const month = new Date(exec.timestamp).toISOString().slice(0, 7); // YYYY-MM
    if (!acc[month]) {
      const metadata = exec.metadata || {};
      const totalReturn =
        typeof metadata.total_return === "number" ? metadata.total_return : 0;

      acc[month] = {
        month,
        return: totalReturn * 100,
      };
    }
    return acc;
  }, {} as Record<string, { month: string; return: number }>);

  const monthlyReturns = Object.values(monthlyReturnsMap).sort((a, b) =>
    a.month.localeCompare(b.month)
  );

  // 성과 요약 데이터 (StrategyPerformanceSummary 호환 형식)
  const latestBacktest = {
    id: strategyId,
    total_return: (performance.total_return || 0) * 100, // 퍼센트로 변환
    annual_return: ((performance.total_return || 0) * 100) / 1, // 1년 기준
    sharpe_ratio: performance.sharpe_ratio || 0,
    max_drawdown: (performance.max_drawdown || 0) * 100,
    volatility: (performance.volatility || 0) * 100,
    win_rate: (performance.win_rate || 0) * 100,
    total_trades: performance.total_signals || 0,
    profit_factor: 1.0, // metadata에서 계산 필요
    start_date: executions[executions.length - 1]?.timestamp
      ? new Date(executions[executions.length - 1].timestamp)
          .toISOString()
          .slice(0, 10)
      : "N/A",
    end_date: executions[0]?.timestamp
      ? new Date(executions[0].timestamp).toISOString().slice(0, 10)
      : "N/A",
  };

  return (
    <PageContainer
      title={`${strategy.name} - 성과 분석`}
      breadcrumbs={[
        { title: "Strategy Center" },
        { title: "Strategies" },
        { title: strategy.name },
        { title: "Performance" },
      ]}
      actions={[
        <Button
          key="back"
          variant="outlined"
          startIcon={<ArrowBack />}
          onClick={handleBack}
        >
          전략으로 돌아가기
        </Button>,
      ]}
    >
      <Grid container spacing={3}>
        {/* 성과 요약 */}
        <Grid size={{ xs: 12, lg: 4 }}>
          <StrategyPerformanceSummary
            strategyName={strategy.name}
            strategyType={strategy.strategy_type}
            performance={latestBacktest}
            period={selectedPeriod}
          />

          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                분석 기간
              </Typography>
              <FormControl fullWidth>
                <InputLabel>기간 선택</InputLabel>
                <Select
                  value={selectedPeriod}
                  label="기간 선택"
                  onChange={(e) => setSelectedPeriod(e.target.value)}
                >
                  <MenuItem value="1M">1개월</MenuItem>
                  <MenuItem value="3M">3개월</MenuItem>
                  <MenuItem value="6M">6개월</MenuItem>
                  <MenuItem value="1Y">1년</MenuItem>
                  <MenuItem value="3Y">3년</MenuItem>
                  <MenuItem value="5Y">5년</MenuItem>
                  <MenuItem value="ALL">전체</MenuItem>
                </Select>
              </FormControl>
            </CardContent>
          </Card>
        </Grid>

        {/* 상세 분석 */}
        <Grid size={{ xs: 12, lg: 8 }}>
          <Card>
            <CardContent>
              <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
                <Tabs value={tabValue} onChange={handleTabChange}>
                  <Tab
                    icon={<ShowChart />}
                    label="수익률 차트"
                    iconPosition="start"
                  />
                  <Tab
                    icon={<TableChart />}
                    label="거래 내역"
                    iconPosition="start"
                  />
                  <Tab
                    icon={<Assessment />}
                    label="월별 수익률"
                    iconPosition="start"
                  />
                </Tabs>
              </Box>

              <CustomTabPanel value={tabValue} index={0}>
                <Box
                  sx={{
                    height: 400,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                >
                  <Typography variant="h6" color="text.secondary">
                    수익률 차트가 여기에 표시됩니다
                  </Typography>
                </Box>
              </CustomTabPanel>

              <CustomTabPanel value={tabValue} index={1}>
                <TableContainer component={Paper} variant="outlined">
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>날짜</TableCell>
                        <TableCell>유형</TableCell>
                        <TableCell>종목</TableCell>
                        <TableCell align="right">수량</TableCell>
                        <TableCell align="right">가격</TableCell>
                        <TableCell align="right">손익</TableCell>
                        <TableCell>상태</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {trades.map((trade) => (
                        <TableRow key={trade.id}>
                          <TableCell>{trade.date}</TableCell>
                          <TableCell>
                            <Chip
                              label={trade.type}
                              color={
                                trade.type === "BUY" ? "primary" : "secondary"
                              }
                              size="small"
                              icon={
                                trade.type === "BUY" ? (
                                  <TrendingUp />
                                ) : (
                                  <TrendingDown />
                                )
                              }
                            />
                          </TableCell>
                          <TableCell>{trade.symbol}</TableCell>
                          <TableCell align="right">
                            {trade.quantity.toLocaleString()}
                          </TableCell>
                          <TableCell align="right">
                            ${trade.price.toFixed(2)}
                          </TableCell>
                          <TableCell
                            align="right"
                            sx={{
                              color:
                                trade.pnl > 0
                                  ? "success.main"
                                  : trade.pnl < 0
                                  ? "error.main"
                                  : "text.primary",
                            }}
                          >
                            {trade.pnl !== 0 ? `$${trade.pnl.toFixed(2)}` : "-"}
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={trade.status}
                              color="success"
                              size="small"
                            />
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CustomTabPanel>

              <CustomTabPanel value={tabValue} index={2}>
                <TableContainer component={Paper} variant="outlined">
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>월</TableCell>
                        <TableCell align="right">수익률 (%)</TableCell>
                        <TableCell align="center">상태</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {monthlyReturns.map((item) => (
                        <TableRow key={item.month}>
                          <TableCell>{item.month}</TableCell>
                          <TableCell
                            align="right"
                            sx={{
                              color:
                                item.return > 0
                                  ? "success.main"
                                  : item.return < 0
                                  ? "error.main"
                                  : "text.primary",
                            }}
                          >
                            {item.return > 0 ? "+" : ""}
                            {item.return.toFixed(1)}%
                          </TableCell>
                          <TableCell align="center">
                            {item.return > 0 ? (
                              <TrendingUp color="success" />
                            ) : item.return < 0 ? (
                              <TrendingDown color="error" />
                            ) : (
                              "-"
                            )}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CustomTabPanel>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </PageContainer>
  );
}
