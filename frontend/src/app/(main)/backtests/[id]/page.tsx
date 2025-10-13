"use client";

import PageContainer from "@/components/layout/PageContainer";
import { useBacktest, useBacktestDetail } from "@/hooks/useBacktests";
import {
  ArrowBack,
  Assessment,
  Delete,
  Download,
  Edit,
  Refresh,
  ShowChart,
  TableChart,
  Timeline,
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
  Container,
  Divider,
  Grid,
  IconButton,
  LinearProgress,
  Paper,
  Stack,
  Tab,
  Tabs,
  Tooltip,
  Typography,
} from "@mui/material";
import { useParams, useRouter } from "next/navigation";
import { useMemo, useState } from "react";
import { backtestUtils } from "../utils";

type TabIndex = 0 | 1 | 2;

function TabPanel({ value, index, children }: { value: number; index: number; children: React.ReactNode }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`backtest-tabpanel-${index}`}
      aria-labelledby={`backtest-tab-${index}`}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

export default function BacktestDetailPage() {
  const params = useParams();
  const router = useRouter();
  const backtestId = params.id as string;
  const [activeTab, setActiveTab] = useState<TabIndex>(0);

  const {
    data: backtest,
    isLoading: detailLoading,
    error: detailError,
    refetch: refetchBacktest,
  } = useBacktestDetail(backtestId);

  const { deleteBacktest, isMutating } = useBacktest();

  const performance = backtest?.performance;

  const handleDelete = () => {
    if (!backtestId) return;
    if (confirm("정말로 이 백테스트를 삭제하시겠습니까?")) {
      deleteBacktest(backtestId, {
        onSuccess: () => {
          router.push("/backtests");
        },
      });
    }
  };

  const handleRefresh = () => {
    refetchBacktest();
  };

  const overviewItems = useMemo(
    () => [
      {
        label: "상태",
        value: backtestUtils.formatStatus(backtest?.status),
      },
      {
        label: "기간",
        value: backtest?.config
          ? `${backtestUtils.formatDate(backtest.config.start_date)} ~ ${backtestUtils.formatDate(backtest.config.end_date)}`
          : "-",
      },
      {
        label: "심볼",
        value: backtestUtils.extractSymbols(backtest ?? undefined),
      },
      {
        label: "초기 자본",
        value: backtestUtils.formatCurrency(backtest?.config?.initial_cash ?? undefined),
      },
      {
        label: "최대 포지션",
        value: backtestUtils.formatPercentage(backtest?.config?.max_position_size ?? undefined),
      },
      {
        label: "수수료율",
        value: backtestUtils.formatPercentage(backtest?.config?.commission_rate ?? undefined, 3),
      },
      {
        label: "슬리피지",
        value: backtestUtils.formatPercentage(backtest?.config?.slippage_rate ?? undefined, 3),
      },
      {
        label: "리밸런싱 주기",
        value: backtest?.config?.rebalance_frequency ?? "-",
      },
    ],
    [backtest],
  );

  if (detailLoading) {
    return (
      <PageContainer title="백테스트 상세" breadcrumbs={[{ title: "백테스트" }, { title: "상세" }]}>
        <Box sx={{ mt: 4 }}>
          <LinearProgress />
        </Box>
      </PageContainer>
    );
  }

  if (detailError || !backtest) {
    return (
      <PageContainer title="백테스트 상세" breadcrumbs={[{ title: "백테스트" }, { title: "상세" }]}>
        <Alert severity="error">백테스트를 찾을 수 없거나 불러오는 중 오류가 발생했습니다.</Alert>
      </PageContainer>
    );
  }

  return (
    <PageContainer
      title={backtest.name}
      breadcrumbs={[{ title: "백테스트" }, { title: backtest.name }]}
    >
      <Container maxWidth="lg">
        <Box sx={{ mb: 4 }}>
          <Button startIcon={<ArrowBack />} onClick={() => router.push("/backtests")}>
            목록으로 돌아가기
          </Button>
        </Box>

        <Paper sx={{ p: 3, mb: 4 }}>
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              flexWrap: "wrap",
              gap: 2,
            }}
          >
            <Stack spacing={1}>
              <Typography variant="h4" component="h1">
                {backtest.name}
              </Typography>
              <Stack direction="row" spacing={1} alignItems="center">
                <Chip
                  label={backtestUtils.formatStatus(backtest.status)}
                  sx={{
                    backgroundColor: backtestUtils.getStatusColor(backtest.status),
                    color: "white",
                  }}
                />
                <Typography variant="body2" color="text.secondary">
                  생성일: {backtestUtils.formatDate(backtest.created_at)}
                </Typography>
              </Stack>
              {backtest.description && (
                <Typography variant="body2" color="text.secondary">
                  {backtest.description}
                </Typography>
              )}
            </Stack>

            <Stack direction="row" spacing={1}>
              <Tooltip title="새로고침">
                <span>
                  <IconButton onClick={handleRefresh}>
                    <Refresh />
                  </IconButton>
                </span>
              </Tooltip>
              <Tooltip title="설정 다운로드">
                <span>
                  <IconButton disabled>
                    <Download />
                  </IconButton>
                </span>
              </Tooltip>
              <Tooltip title="수정">
                <span>
                  <IconButton onClick={() => router.push(`/backtests/${backtestId}/edit`)}>
                    <Edit />
                  </IconButton>
                </span>
              </Tooltip>
              <Tooltip title="삭제">
                <span>
                  <IconButton color="error" disabled={isMutating.deleteBacktest} onClick={handleDelete}>
                    <Delete />
                  </IconButton>
                </span>
              </Tooltip>
            </Stack>
          </Box>
        </Paper>

        {backtestUtils.isRunning(backtest.status) && (
          <Alert severity="info" sx={{ mb: 4 }}>
            백테스트가 실행 중입니다. 진행 상황은 자동으로 업데이트됩니다.
          </Alert>
        )}

        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid size={12} >
            <Card variant="outlined">
              <CardContent>
                <Stack spacing={1} alignItems="flex-start">
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
          <Grid size={12} >
            <Card variant="outlined">
              <CardContent>
                <Stack spacing={1} alignItems="flex-start">
                  <Assessment color="primary" />
                  <Typography variant="h5">
                    {backtestUtils.formatNumber(performance?.sharpe_ratio)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    샤프 비율
                  </Typography>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
          <Grid size={12} >
            <Card variant="outlined">
              <CardContent>
                <Stack spacing={1} alignItems="flex-start">
                  <TrendingDown color="error" />
                  <Typography variant="h5" color="error">
                    {backtestUtils.formatPercentage(
                      performance?.max_drawdown ? Math.abs(performance?.max_drawdown) : performance?.max_drawdown,
                    )}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    최대 낙폭
                  </Typography>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
          <Grid size={12} >
            <Card variant="outlined">
              <CardContent>
                <Stack spacing={1} alignItems="flex-start">
                  <ShowChart color="primary" />
                  <Typography variant="h5">
                    {backtestUtils.formatPercentage(performance?.win_rate)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    승률
                  </Typography>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Paper>
          <Tabs
            value={activeTab}
            onChange={(_, newValue) => setActiveTab(newValue as TabIndex)}
            variant="scrollable"
            allowScrollButtonsMobile
          >
            <Tab icon={<Assessment />} iconPosition="start" label="개요" />
            <Tab icon={<Timeline />} iconPosition="start" label="성과" />
            <Tab icon={<TableChart />} iconPosition="start" label="거래 내역" />
          </Tabs>

          <TabPanel value={activeTab} index={0}>
            <Grid container spacing={3}>
              <Grid size={12} >
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      기본 정보
                    </Typography>
                    <Divider sx={{ my: 2 }} />
                    <Stack spacing={1.5}>
                      {overviewItems.map((item) => (
                        <Box key={item.label}>
                          <Typography variant="body2" color="text.secondary">
                            {item.label}
                          </Typography>
                          <Typography variant="body1">{item.value}</Typography>
                        </Box>
                      ))}
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
              <Grid size={12} >
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      실행 정보
                    </Typography>
                    <Divider sx={{ my: 2 }} />
                    <Stack spacing={1.5}>
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          시작 시간
                        </Typography>
                        <Typography variant="body1">
                          {backtestUtils.formatDate(backtest.start_time)}
                        </Typography>
                      </Box>
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          종료 시간
                        </Typography>
                        <Typography variant="body1">
                          {backtestUtils.formatDate(backtest.end_time)}
                        </Typography>
                      </Box>
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          실행 소요 시간
                        </Typography>
                        <Typography variant="body1">
                          {backtestUtils.formatDuration(backtest.start_time, backtest.end_time)}
                        </Typography>
                      </Box>
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </TabPanel>

          <TabPanel value={activeTab} index={1}>
            {performance ? (
              <Grid container spacing={3}>
                <Grid size={12} >
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle1" gutterBottom>
                        수익률
                      </Typography>
                      <Stack spacing={1}>
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            연환산 수익률
                          </Typography>
                          <Typography variant="body1">
                            {backtestUtils.formatPercentage(performance.annualized_return)}
                          </Typography>
                        </Box>
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            변동성
                          </Typography>
                          <Typography variant="body1">
                            {backtestUtils.formatPercentage(performance.volatility)}
                          </Typography>
                        </Box>
                      </Stack>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid size={12} >
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle1" gutterBottom>
                        거래 통계
                      </Typography>
                      <Stack spacing={1}>
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            총 거래 수
                          </Typography>
                          <Typography variant="body1">
                            {performance.total_trades ?? "-"}
                          </Typography>
                        </Box>
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            승/패 거래
                          </Typography>
                          <Typography variant="body1">
                            {performance.winning_trades} 승 · {performance.losing_trades} 패
                          </Typography>
                        </Box>
                      </Stack>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            ) : (
              <Alert severity="info">성과 데이터가 아직 생성되지 않았습니다.</Alert>
            )}
          </TabPanel>

          <TabPanel value={activeTab} index={2}>
            <Alert severity="info">
              거래 내역 데이터는 아직 제공되지 않습니다. 백테스트 실행이 완료되면 거래
              내역이 표시됩니다.
            </Alert>
          </TabPanel>
        </Paper>
      </Container>
    </PageContainer>
  );
}
