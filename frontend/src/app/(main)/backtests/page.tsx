"use client";

import PageContainer from "@/components/layout/PageContainer";
import { useBacktest } from "@/hooks/useBacktests";
import {
  Add,
  Assessment,
  Delete,
  Edit,
  FilterList,
  Search,
  ShowChart,
  TrendingDown,
  TrendingUp,
} from "@mui/icons-material";
import {
  Alert,
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  Chip,
  Container,
  Fab,
  FormControl,
  Grid,
  IconButton,
  InputLabel,
  LinearProgress,
  MenuItem,
  Paper,
  Select,
  Stack,
  TextField,
  Tooltip,
  Typography,
} from "@mui/material";
import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";
import { backtestUtils, type BacktestListItem } from "./utils";

type StatusFilter = "ALL" | BacktestListItem["status"];

type SortField = "created_at" | "name" | "status" | "total_return";

const sorters: Record<SortField, (a: BacktestListItem, b: BacktestListItem) => number> = {
  created_at: (a, b) =>
    new Date(b.created_at ?? 0).getTime() - new Date(a.created_at ?? 0).getTime(),
  name: (a, b) => a.name.localeCompare(b.name),
  status: (a, b) => a.status.localeCompare(b.status),
  total_return: (a, b) =>
    (b.performance?.total_return ?? -Infinity) -
    (a.performance?.total_return ?? -Infinity),
};

export default function BacktestsPage() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("ALL");
  const [sortBy, setSortBy] = useState<SortField>("created_at");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

  const {
    backtestList,
    deleteBacktest,
    isLoading: { backtestList: listLoading },
    isError: { backtestList: listError },
    isMutating,
  } = useBacktest();

  const backtests = useMemo(() => {
    const items = backtestList?.backtests ?? [];
    if (!items.length) {
      return [];
    }

    const filtered = items.filter((item) => {
      if (statusFilter !== "ALL" && item.status !== statusFilter) {
        return false;
      }
      if (searchQuery.trim().length > 0) {
        const query = searchQuery.toLowerCase();
        const description = item.description?.toLowerCase() ?? "";
        const symbols = item.config?.symbols?.join(", ").toLowerCase() ?? "";
        return (
          item.name.toLowerCase().includes(query) ||
          description.includes(query) ||
          symbols.includes(query)
        );
      }
      return true;
    });

    const sorter = sorters[sortBy];
    const sorted = [...filtered].sort((a, b) => sorter(a, b));
    if (sortOrder === "asc") {
      sorted.reverse();
    }
    return sorted;
  }, [backtestList?.backtests, searchQuery, statusFilter, sortBy, sortOrder]);

  const handleCreateNew = () => {
    router.push("/backtests/create");
  };

  const handleViewBacktest = (id: string) => {
    router.push(`/backtests/${id}`);
  };

  const handleDeleteBacktest = (id: string) => {
    if (confirm("정말로 이 백테스트를 삭제하시겠습니까?")) {
      deleteBacktest(id);
    }
  };

  if (listError) {
    return (
      <PageContainer title="백테스트" breadcrumbs={[{ title: "백테스트" }]}>
        <Alert severity="error">
          백테스트 목록을 불러오는 중 오류가 발생했습니다.
        </Alert>
      </PageContainer>
    );
  }

  return (
    <PageContainer
      title="백테스트"
      breadcrumbs={[{ title: "백테스트" }]}
    >
      <Container maxWidth="lg">
        <Box sx={{ mb: 4 }}>
          <Typography variant="body1" color="text.secondary">
            실행된 백테스트를 확인하고 새로운 전략을 테스트해보세요.
          </Typography>
        </Box>

        <Paper sx={{ p: 3, mb: 3 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid size={12} >
              <TextField
                fullWidth
                placeholder="백테스트 이름, 설명 또는 심볼 검색"
                value={searchQuery}
                onChange={(event) => setSearchQuery(event.target.value)}
                InputProps={{
                  startAdornment: (
                    <Search sx={{ mr: 1, color: "text.secondary" }} />
                  ),
                }}
              />
            </Grid>
            <Grid size={6} >
              <FormControl fullWidth>
                <InputLabel id="status-filter-label">상태</InputLabel>
                <Select
                  labelId="status-filter-label"
                  value={statusFilter}
                  label="상태"
                  onChange={(event) =>
                    setStatusFilter(event.target.value as StatusFilter)
                  }
                >
                  <MenuItem value="ALL">전체</MenuItem>
                  <MenuItem value="pending">대기 중</MenuItem>
                  <MenuItem value="running">실행 중</MenuItem>
                  <MenuItem value="completed">완료</MenuItem>
                  <MenuItem value="failed">실패</MenuItem>
                  <MenuItem value="cancelled">취소됨</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid size={6} >
              <FormControl fullWidth>
                <InputLabel id="sort-field-label">정렬</InputLabel>
                <Select
                  labelId="sort-field-label"
                  value={sortBy}
                  label="정렬"
                  onChange={(event) =>
                    setSortBy(event.target.value as SortField)
                  }
                >
                  <MenuItem value="created_at">생성일</MenuItem>
                  <MenuItem value="name">이름</MenuItem>
                  <MenuItem value="status">상태</MenuItem>
                  <MenuItem value="total_return">총 수익률</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid size={6} >
              <FormControl fullWidth>
                <InputLabel id="sort-order-label">순서</InputLabel>
                <Select
                  labelId="sort-order-label"
                  value={sortOrder}
                  label="순서"
                  onChange={(event) =>
                    setSortOrder(event.target.value as "asc" | "desc")
                  }
                >
                  <MenuItem value="desc">내림차순</MenuItem>
                  <MenuItem value="asc">오름차순</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid size={6} >
              <Button
                variant="outlined"
                startIcon={<FilterList />}
                fullWidth
                onClick={() => {
                  setSearchQuery("");
                  setStatusFilter("ALL");
                  setSortBy("created_at");
                  setSortOrder("desc");
                }}
              >
                초기화
              </Button>
            </Grid>
          </Grid>
        </Paper>

        {listLoading && (
          <Box sx={{ mb: 3 }}>
            <LinearProgress />
          </Box>
        )}

        <Grid container spacing={3}>
          {backtests.map((backtest) => {
            const performance = backtest.performance;
            const totalReturn = performance?.total_return;
            const sharpeRatio = performance?.sharpe_ratio;
            const maxDrawdown = performance?.max_drawdown;
            const winRate = performance?.win_rate;

            return (
              <Grid size={12} key={backtest.id}>
                <Card
                  sx={{
                    height: "100%",
                    display: "flex",
                    flexDirection: "column",
                    transition: "box-shadow 0.2s ease, transform 0.2s ease",
                    cursor: "pointer",
                    "&:hover": {
                      boxShadow: 6,
                      transform: "translateY(-4px)",
                    },
                  }}
                  onClick={() => handleViewBacktest(backtest.id)}
                >
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Box
                      sx={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "flex-start",
                        mb: 2,
                        gap: 1,
                      }}
                    >
                      <Box sx={{ flex: 1, minWidth: 0 }}>
                        <Typography
                          variant="h6"
                          component="h3"
                          gutterBottom
                          noWrap
                        >
                          {backtest.name}
                        </Typography>
                        <Typography
                          variant="body2"
                          color="text.secondary"
                          gutterBottom
                        >
                          {backtestUtils.extractSymbols(backtest)}
                        </Typography>
                      </Box>
                      <Chip
                        label={backtestUtils.formatStatus(backtest.status)}
                        size="small"
                        sx={{
                          backgroundColor: backtestUtils.getStatusColor(
                            backtest.status,
                          ),
                          color: "white",
                        }}
                      />
                    </Box>

                    {backtestUtils.isRunning(backtest.status) && (
                      <Box sx={{ mb: 2 }}>
                        <LinearProgress />
                        <Typography
                          variant="caption"
                          color="text.secondary"
                          sx={{ mt: 1 }}
                        >
                          백테스트가 실행 중입니다…
                        </Typography>
                      </Box>
                    )}

                    <Grid container spacing={2}>
                      <Grid size={6}>
                        <Stack spacing={0.5} alignItems="flex-start">
                          <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
                            {totalReturn !== undefined && totalReturn !== null ? (
                              totalReturn >= 0 ? (
                                <TrendingUp color="success" fontSize="small" />
                              ) : (
                                <TrendingDown color="error" fontSize="small" />
                              )
                            ) : (
                              <ShowChart fontSize="small" />
                            )}
                            <Typography
                              variant="body1"
                              sx={{
                                color: totalReturn && totalReturn < 0 ? "error.main" : "success.main",
                              }}
                            >
                              {backtestUtils.formatPercentage(totalReturn)}
                            </Typography>
                          </Box>
                          <Typography variant="caption" color="text.secondary">
                            총 수익률
                          </Typography>
                        </Stack>
                      </Grid>
                      <Grid size={6}>
                        <Stack spacing={0.5} alignItems="flex-start">
                          <Assessment fontSize="small" />
                          <Typography variant="body1">
                            {backtestUtils.formatNumber(sharpeRatio)}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            샤프 비율
                          </Typography>
                        </Stack>
                      </Grid>
                      <Grid size={6} >
                        <Stack spacing={0.5} alignItems="flex-start">
                          <TrendingDown color="error" fontSize="small" />
                          <Typography variant="body1" color="error">
                            {backtestUtils.formatPercentage(
                              maxDrawdown ? Math.abs(maxDrawdown) : maxDrawdown,
                            )}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            최대 낙폭
                          </Typography>
                        </Stack>
                      </Grid>
                      <Grid size={6} >
                        <Stack spacing={0.5} alignItems="flex-start">
                          <ShowChart fontSize="small" color="primary" />
                          <Typography variant="body1" color="primary">
                            {backtestUtils.formatPercentage(winRate)}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            승률
                          </Typography>
                        </Stack>
                      </Grid>
                    </Grid>

                    <Box sx={{ mt: 2 }}>
                      <Typography variant="caption" color="text.secondary">
                        생성일: {backtestUtils.formatDate(backtest.created_at)}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" display="block">
                        최근 업데이트: {backtestUtils.formatDate(backtest.updated_at ?? backtest.created_at)}
                      </Typography>
                    </Box>
                  </CardContent>

                  <CardActions sx={{ justifyContent: "space-between" }}>
                    <Button size="small" onClick={() => handleViewBacktest(backtest.id)}>
                      자세히 보기
                    </Button>
                    <Stack direction="row" spacing={1}>
                      <Tooltip title="수정">
                        <span>
                          <IconButton
                            size="small"
                            onClick={(event) => {
                              event.stopPropagation();
                              router.push(`/backtests/${backtest.id}/edit`);
                            }}
                          >
                            <Edit fontSize="small" />
                          </IconButton>
                        </span>
                      </Tooltip>
                      <Tooltip title="삭제">
                        <span>
                          <IconButton
                            size="small"
                            color="error"
                            disabled={isMutating.deleteBacktest}
                            onClick={(event) => {
                              event.stopPropagation();
                              handleDeleteBacktest(backtest.id);
                            }}
                          >
                            <Delete fontSize="small" />
                          </IconButton>
                        </span>
                      </Tooltip>
                    </Stack>
                  </CardActions>
                </Card>
              </Grid>
            );
          })}
        </Grid>

        {!listLoading && backtests.length === 0 && (
          <Paper sx={{ p: 6, textAlign: "center", mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              백테스트가 없습니다
            </Typography>
            <Typography variant="body2" color="text.secondary">
              새로운 백테스트를 생성하여 전략의 성과를 확인해보세요.
            </Typography>
            <Button
              variant="contained"
              startIcon={<Add />}
              sx={{ mt: 2 }}
              onClick={handleCreateNew}
            >
              새 백테스트 만들기
            </Button>
          </Paper>
        )}

        <Fab
          color="primary"
          sx={{ position: "fixed", bottom: 24, right: 24 }}
          onClick={handleCreateNew}
          aria-label="create backtest"
        >
          <Add />
        </Fab>
      </Container>
    </PageContainer>
  );
}
