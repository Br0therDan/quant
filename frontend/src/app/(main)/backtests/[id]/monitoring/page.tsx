"use client";

import PageContainer from "@/components/layout/PageContainer";
import { useBacktest, useBacktestDetail } from "@/hooks/useBacktests";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Container,
  FormControlLabel,
  LinearProgress,
  Paper,
  Stack,
  Switch,
  Typography,
} from "@mui/material";
import Grid from "@mui/material/Unstable_Grid2";
import { Refresh, Schedule, TrendingUp } from "@mui/icons-material";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { backtestUtils } from "../../utils";

export default function BacktestMonitoringPage() {
  const params = useParams();
  const backtestId = params.id as string;
  const [autoRefresh, setAutoRefresh] = useState(true);
  const refreshInterval = 5000;

  const {
    data: backtest,
    isLoading,
    refetch,
  } = useBacktestDetail(backtestId);
  const { isMutating } = useBacktest();

  useEffect(() => {
    if (!autoRefresh || !backtest || !backtestUtils.isRunning(backtest.status)) {
      return;
    }
    const timer = setInterval(() => {
      refetch();
    }, refreshInterval);
    return () => clearInterval(timer);
  }, [autoRefresh, backtest, refreshInterval, refetch]);

  if (isLoading) {
    return (
      <PageContainer
        title="백테스트 모니터링"
        breadcrumbs={[{ title: "백테스트" }, { title: "모니터링" }]}
      >
        <Box sx={{ mt: 4 }}>
          <LinearProgress />
        </Box>
      </PageContainer>
    );
  }

  if (!backtest) {
    return (
      <PageContainer
        title="백테스트 모니터링"
        breadcrumbs={[{ title: "백테스트" }, { title: "모니터링" }]}
      >
        <Alert severity="error">백테스트 정보를 불러올 수 없습니다.</Alert>
      </PageContainer>
    );
  }

  const performance = backtest.performance;

  return (
    <PageContainer
      title={`${backtest.name} 실시간 모니터링`}
      breadcrumbs={[{ title: "백테스트" }, { title: backtest.name }, { title: "모니터링" }]}
    >
      <Container maxWidth="lg">
        <Stack spacing={3} sx={{ mb: 4 }}>
          <Stack direction="row" justifyContent="space-between" alignItems="center">
            <Stack spacing={1}>
              <Typography variant="h4">{backtest.name}</Typography>
              <Stack direction="row" spacing={1} alignItems="center">
                <Chip
                  label={backtestUtils.formatStatus(backtest.status)}
                  sx={{
                    backgroundColor: backtestUtils.getStatusColor(backtest.status),
                    color: "white",
                  }}
                />
                <Typography variant="body2" color="text.secondary">
                  마지막 업데이트: {backtestUtils.formatDate(backtest.updated_at)}
                </Typography>
              </Stack>
            </Stack>
            <Stack direction="row" spacing={2} alignItems="center">
              <FormControlLabel
                control={
                  <Switch
                    checked={autoRefresh}
                    onChange={(event) => setAutoRefresh(event.target.checked)}
                  />
                }
                label="자동 새로고침"
              />
              <Button
                variant="outlined"
                startIcon={<Refresh />}
                onClick={() => refetch()}
                disabled={isMutating.updateBacktest}
              >
                새로고침
              </Button>
            </Stack>
          </Stack>

          {backtestUtils.isRunning(backtest.status) ? (
            <Alert severity="info">
              백테스트가 실행 중입니다. 실시간 상태는 {refreshInterval / 1000}초마다 자동으로 업데이트됩니다.
            </Alert>
          ) : (
            <Alert severity="success">백테스트가 완료되었습니다.</Alert>
          )}
        </Stack>

        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid xs={12} md={4}>
            <Card variant="outlined">
              <CardContent>
                <Stack spacing={1}>
                  <TrendingUp color="success" />
                  <Typography variant="h5">
                    {backtestUtils.formatPercentage(performance?.total_return)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    총 수익률
                  </Typography>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
          <Grid xs={12} md={4}>
            <Card variant="outlined">
              <CardContent>
                <Stack spacing={1}>
                  <Schedule color="primary" />
                  <Typography variant="h5">
                    {backtestUtils.formatDuration(backtest.start_time, backtest.end_time)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    실행 시간
                  </Typography>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
          <Grid xs={12} md={4}>
            <Card variant="outlined">
              <CardContent>
                <Stack spacing={1}>
                  <Typography variant="overline" color="text.secondary">
                    진행 상태
                  </Typography>
                  <LinearProgress
                    variant={backtestUtils.isRunning(backtest.status) ? "indeterminate" : "determinate"}
                    value={backtestUtils.isRunning(backtest.status) ? undefined : 100}
                  />
                  <Typography variant="caption" color="text.secondary">
                    상태: {backtestUtils.formatStatus(backtest.status)}
                  </Typography>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            구성 정보
          </Typography>
          <Grid container spacing={2}>
            <Grid xs={12} md={6}>
              <Typography variant="subtitle2" gutterBottom>
                심볼
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {backtestUtils.extractSymbols(backtest)}
              </Typography>
            </Grid>
            <Grid xs={12} md={6}>
              <Typography variant="subtitle2" gutterBottom>
                기간
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {backtest.config
                  ? `${backtestUtils.formatDate(backtest.config.start_date)} ~ ${backtestUtils.formatDate(backtest.config.end_date)}`
                  : "-"}
              </Typography>
            </Grid>
            <Grid xs={12} md={6}>
              <Typography variant="subtitle2" gutterBottom>
                초기 자본
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {backtestUtils.formatCurrency(backtest.config?.initial_cash ?? undefined)}
              </Typography>
            </Grid>
            <Grid xs={12} md={6}>
              <Typography variant="subtitle2" gutterBottom>
                리밸런싱 주기
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {backtest.config?.rebalance_frequency ?? "-"}
              </Typography>
            </Grid>
          </Grid>
        </Paper>
      </Container>
    </PageContainer>
  );
}
