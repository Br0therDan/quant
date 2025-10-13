"use client";

import PageContainer from "@/components/layout/PageContainer";
import { useBacktest, useBacktestDetail } from "@/hooks/useBacktest";
import {
  ArrowBack,
  Assessment,
  Delete,
  Download,
  Edit,
  PlayArrow,
  Refresh,
  Share,
  Stop,
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
import type React from "react";
import { useState } from "react";

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`backtest-tabpanel-${index}`}
      aria-labelledby={`backtest-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

export default function BacktestDetailPage() {
  const params = useParams();
  const router = useRouter();
  const backtestId = params.id as string;
  const [activeTab, setActiveTab] = useState(0);

  // Use useBacktestDetail hook
  const {
    data: backtest,
    isLoading: backtestLoading,
    error: backtestError,
    refetch: refetchBacktest,
  } = useBacktestDetail(backtestId);

  // Use useBacktest for mutations
  const { deleteBacktest } = useBacktest();

  const handleExecute = async () => {
    console.log("Execute backtest:", backtestId);
    // TODO: Implement execute functionality
    refetchBacktest();
  };

  const handleDelete = async () => {
    if (confirm("정말로 이 백테스트를 삭제하시겠습니까?")) {
      deleteBacktest(backtestId);
      router.push("/backtests");
    }
  };
  const getReturnColor = (value?: number) => {
    if (value === undefined || value === null) return "text.secondary";
    return value >= 0 ? "success.main" : "error.main";
  };

  const getReturnIcon = (value?: number) => {
    if (value === undefined || value === null) return null;
    return value >= 0 ? <TrendingUp /> : <TrendingDown />;
  };

  if (backtestLoading) {
    return (
      <PageContainer
        title="백테스트 상세"
        breadcrumbs={[{ title: "상세 보기" }]}
      >
        <Box sx={{ mt: 4 }}>
          <LinearProgress />
        </Box>
      </PageContainer>
    );
  }

  if (backtestError || !backtest) {
    return (
      <PageContainer
        title="백테스트 상세"
        breadcrumbs={[{ title: "백테스트" }]}
      >
        <Alert severity="error">
          백테스트를 찾을 수 없거나 불러오는 중 오류가 발생했습니다.
        </Alert>
      </PageContainer>
    );
  }

  return (
    <PageContainer
      title={backtest.name}
      breadcrumbs={[
        { title: "백테스트" },
        { title: backtest?.name || "상세 보기" },
      ]}
    >
      <Container maxWidth="lg">
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              mb: 2,
            }}
          >
            <Button
              startIcon={<ArrowBack />}
              onClick={() => router.push("/backtests")}
            >
              백테스트 목록으로
            </Button>

            <Stack direction="row" spacing={1}>
              <Tooltip title="새로고침">
                <IconButton onClick={() => refetchBacktest()}>
                  <Refresh />
                </IconButton>
              </Tooltip>
              <Tooltip title="공유">
                <IconButton>
                  <Share />
                </IconButton>
              </Tooltip>
              <Tooltip title="다운로드">
                <IconButton>
                  <Download />
                </IconButton>
              </Tooltip>
              <Tooltip title="수정">
                <IconButton
                  onClick={() => router.push(`/backtests/${backtestId}/edit`)}
                >
                  <Edit />
                </IconButton>
              </Tooltip>
              <Tooltip title="삭제">
                <IconButton color="error" onClick={handleDelete}>
                  <Delete />
                </IconButton>
              </Tooltip>
            </Stack>
          </Box>

          <Box sx={{ display: "flex", alignItems: "center", gap: 2, mb: 2 }}>
            <Chip
              label={backtestUtils.formatStatus(backtest.status as any)}
              size="medium"
              sx={{
                backgroundColor: backtestUtils.getStatusColor(
                  backtest.status as any
                ),
                color: "white",
              }}
            />
            {(backtest as any)?.tags?.map((tag: string) => (
              <Chip key={tag} label={tag} size="small" variant="outlined" />
            ))}
          </Box>

          {backtest.description && (
            <Typography variant="body1" color="text.secondary" gutterBottom>
              {backtest.description}
            </Typography>
          )}
        </Box>

        {/* Running Progress */}
        {backtestUtils.isRunning(backtest.status as any) && (
          <Alert severity="info" sx={{ mb: 3 }}>
            <Box
              sx={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
              }}
            >
              <Box>
                <Typography variant="subtitle2">
                  백테스트가 실행 중입니다...
                </Typography>
                <Typography variant="body2">
                  현재 상태:{" "}
                  {backtestUtils.formatStatus(backtest.status as any)}
                </Typography>
              </Box>
              <Button
                variant="outlined"
                color="error"
                startIcon={<Stop />}
                size="small"
              >
                중단
              </Button>
            </Box>
            <LinearProgress sx={{ mt: 2 }} />
          </Alert>
        )}

        {/* Quick Stats */}
        {backtestUtils.isCompleted(backtest.status as any) && results && (
          <Grid container spacing={3} sx={{ mb: 3 }}>
            <Grid size={12}>
              <Card>
                <CardContent sx={{ textAlign: "center" }}>
                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      mb: 1,
                    }}
                  >
                    {getReturnIcon((results as any)?.total_return)}
                  </Box>
                  <Typography
                    variant="h4"
                    sx={{
                      color: getReturnColor((results as any)?.total_return),
                    }}
                  >
                    {(results as any)?.total_return
                      ? backtestUtils.formatPercentage(
                          (results as any).total_return
                        )
                      : "-"}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    총 수익률
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid size={12}>
              <Card>
                <CardContent sx={{ textAlign: "center" }}>
                  <Assessment sx={{ mb: 1, fontSize: 40 }} />
                  <Typography variant="h4">
                    {(results as any)?.sharpe_ratio
                      ? backtestUtils.formatNumber(
                          (results as any).sharpe_ratio
                        )
                      : "-"}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    샤프 비율
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid size={12}>
              <Card>
                <CardContent sx={{ textAlign: "center" }}>
                  <TrendingDown
                    sx={{ mb: 1, fontSize: 40, color: "error.main" }}
                  />
                  <Typography variant="h4" color="error">
                    {(results as any)?.max_drawdown
                      ? backtestUtils.formatPercentage(
                          Math.abs((results as any).max_drawdown)
                        )
                      : "-"}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    최대 낙폭
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid size={12}>
              <Card>
                <CardContent sx={{ textAlign: "center" }}>
                  <Timeline sx={{ mb: 1, fontSize: 40 }} />
                  <Typography variant="h4">
                    {(results as any)?.volatility
                      ? backtestUtils.formatPercentage(
                          (results as any).volatility
                        )
                      : "-"}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    변동성
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        {/* Main Content Tabs */}
        <Paper sx={{ mb: 3 }}>
          <Tabs
            value={activeTab}
            onChange={(_, newValue) => setActiveTab(newValue)}
            aria-label="백테스트 탭"
          >
            <Tab label="개요" icon={<Assessment />} iconPosition="start" />
            <Tab
              label="성과 분석"
              icon={<Timeline />}
              iconPosition="start"
              disabled={!backtestUtils.isCompleted(backtest.status as any)}
            />
            <Tab
              label="거래 내역"
              icon={<TableChart />}
              iconPosition="start"
              disabled={!backtestUtils.isCompleted(backtest.status as any)}
            />
          </Tabs>

          {/* Overview Tab */}
          <TabPanel value={activeTab} index={0}>
            <Grid container spacing={3}>
              <Grid size={12}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      기본 정보
                    </Typography>
                    <Divider sx={{ mb: 2 }} />
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary">
                        상태
                      </Typography>
                      <Typography variant="body1">
                        {backtestUtils.formatStatus(backtest.status as any)}
                      </Typography>
                    </Box>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary">
                        전략
                      </Typography>
                      <Typography variant="body1">
                        {(backtest as any)?.strategy_name || "N/A"}
                      </Typography>
                    </Box>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary">
                        생성일
                      </Typography>
                      <Typography variant="body1">
                        {new Date(backtest.created_at).toLocaleString("ko-KR")}
                      </Typography>
                    </Box>
                    {(backtest as any)?.completed_at && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" color="text.secondary">
                          완료일
                        </Typography>
                        <Typography variant="body1">
                          {new Date(
                            (backtest as any).completed_at
                          ).toLocaleString("ko-KR")}
                        </Typography>
                      </Box>
                    )}
                    {(backtest as any)?.duration && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" color="text.secondary">
                          실행 시간
                        </Typography>
                        <Typography variant="body1">
                          {backtestUtils.formatDuration(
                            backtest.created_at.toString(),
                            (backtest as any).completed_at
                          )}
                        </Typography>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>

              <Grid size={12}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      설정 정보
                    </Typography>
                    <Divider sx={{ mb: 2 }} />
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary">
                        백테스트 기간
                      </Typography>
                      <Typography variant="body1">
                        {new Date(
                          (backtest as any)?.start_date || backtest.created_at
                        ).toLocaleDateString("ko-KR")}{" "}
                        ~{" "}
                        {new Date(
                          (backtest as any)?.end_date || backtest.created_at
                        ).toLocaleDateString("ko-KR")}
                      </Typography>
                    </Box>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary">
                        초기 자본
                      </Typography>
                      <Typography variant="body1">
                        {backtestUtils.formatCurrency(
                          (backtest as any)?.initial_capital || 0
                        )}
                      </Typography>
                    </Box>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary">
                        수수료
                      </Typography>
                      <Typography variant="body1">
                        {(((backtest as any)?.commission || 0) * 100).toFixed(
                          3
                        )}
                        %
                      </Typography>
                    </Box>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary">
                        슬리피지
                      </Typography>
                      <Typography variant="body1">
                        {(((backtest as any)?.slippage || 0) * 100).toFixed(3)}%
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              {/* Action Buttons */}
              <Grid size={12}>
                <Box sx={{ display: "flex", gap: 2, justifyContent: "center" }}>
                  {backtestUtils.isCompleted(backtest.status as any) && (
                    <Button
                      variant="contained"
                      startIcon={<PlayArrow />}
                      onClick={handleExecute}
                    >
                      재실행
                    </Button>
                  )}
                  {backtestUtils.isFailed(backtest.status as any) && (
                    <Button
                      variant="contained"
                      startIcon={<PlayArrow />}
                      onClick={handleExecute}
                    >
                      다시 실행
                    </Button>
                  )}
                  <Button
                    variant="outlined"
                    startIcon={<Edit />}
                    onClick={() => router.push(`/backtests/${backtestId}/edit`)}
                  >
                    설정 수정
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </TabPanel>

          {/* Performance Analysis Tab */}
          <TabPanel value={activeTab} index={1}>
            <Typography variant="h6" gutterBottom>
              성과 분석
            </Typography>
            <Typography variant="body2" color="text.secondary">
              상세한 성과 분석 차트와 지표들이 여기에 표시됩니다.
            </Typography>
            {/* TODO: Add performance charts and detailed metrics */}
          </TabPanel>

          {/* Trades Tab */}
          <TabPanel value={activeTab} index={2}>
            <Typography variant="h6" gutterBottom>
              거래 내역
            </Typography>
            <Typography variant="body2" color="text.secondary">
              백테스트 기간 동안의 모든 거래 내역이 여기에 표시됩니다.
            </Typography>
            {/* TODO: Add trades table */}
          </TabPanel>
        </Paper>
      </Container>
    </PageContainer>
  );
}
