"use client";

import {
  Delete,
  Edit,
  FileCopy,
  MoreVert,
  PlayArrow,
  Settings,
  Timeline,
} from "@mui/icons-material";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Divider,
  Grid,
  IconButton,
  Menu,
  MenuItem,
  Typography,
} from "@mui/material";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import React, { useState } from "react";

import PageContainer from "@/components/layout/PageContainer";
import StrategyParameters from "@/components/strategies/StrategyParameters";
import StrategyPerformanceSummary from "@/components/strategies/StrategyPerformanceSummary";

import {
  strategiesDeleteStrategyMutation,
  strategiesExecuteStrategyMutation,
  strategyUtils,
  useStrategyQuery,
} from "@/services/strategiesQuery";

export default function StrategyDetailPage() {
  const router = useRouter();
  const params = useParams();
  const queryClient = useQueryClient();
  const strategyId = params.id as string;

  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  // 전략 데이터 조회
  const {
    data: strategy,
    isLoading,
    error,
  } = useQuery(
    useStrategyQuery({
      path: { strategy_id: strategyId },
    })
  );

  // 전략 삭제 뮤테이션
  const deleteStrategy = useMutation({
    ...strategiesDeleteStrategyMutation(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["strategiesGetStrategies"] });
      router.push("/strategies/my-strategies");
    },
  });

  // 전략 실행 뮤테이션
  const executeStrategy = useMutation({
    ...strategiesExecuteStrategyMutation(),
    onSuccess: (data: any) => {
      router.push(`/backtests/${data.backtest_id}`);
    },
  });

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleEdit = () => {
    router.push(`/strategies/create?edit=${strategyId}`);
    handleMenuClose();
  };

  const handleClone = () => {
    router.push(`/strategies/create?clone=${strategyId}`);
    handleMenuClose();
  };

  const handleDelete = () => {
    if (confirm("정말로 이 전략을 삭제하시겠습니까?")) {
      deleteStrategy.mutate({
        path: { strategy_id: strategyId },
      });
    }
    handleMenuClose();
  };

  const handleExecute = () => {
    executeStrategy.mutate({
      path: { strategy_id: strategyId },
      body: {
        symbol: "AAPL",
        market_data: {
          start_date: new Date(
            Date.now() - 365 * 24 * 60 * 60 * 1000
          ).toISOString(),
          end_date: new Date().toISOString(),
        },
      },
    });
  };

  const handleViewPerformance = () => {
    router.push(`/strategies/${strategyId}/performance`);
  };

  if (isLoading) {
    return (
      <PageContainer
        title="전략 상세"
        breadcrumbs={[
          { title: "Strategy Center" },
          { title: "Strategies" },
          { title: "Details" },
        ]}
      >
        <Box sx={{ display: "flex", justifyContent: "center", py: 4 }}>
          <CircularProgress />
        </Box>
      </PageContainer>
    );
  }

  if (error || !strategy) {
    return (
      <PageContainer
        title="전략 상세"
        breadcrumbs={[
          { title: "Strategy Center" },
          { title: "Strategies" },
          { title: "Details" },
        ]}
      >
        <Alert severity="error">
          전략을 불러오는 중 오류가 발생했습니다: {(error as any)?.message}
        </Alert>
      </PageContainer>
    );
  }

  return (
    <PageContainer
      title={strategy.name}
      breadcrumbs={[
        { title: "Strategy Center" },
        { title: "Strategies" },
        { title: strategy.name },
      ]}
      actions={[
        <Button
          key="execute"
          variant="contained"
          startIcon={<PlayArrow />}
          onClick={handleExecute}
          disabled={executeStrategy.isPending}
        >
          {executeStrategy.isPending ? "실행 중..." : "백테스트 실행"}
        </Button>,
        <IconButton key="menu" onClick={handleMenuClick}>
          <MoreVert />
        </IconButton>,
      ]}
    >
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleEdit}>
          <Edit sx={{ mr: 1 }} />
          편집
        </MenuItem>
        <MenuItem onClick={handleClone}>
          <FileCopy sx={{ mr: 1 }} />
          복사
        </MenuItem>
        <MenuItem onClick={handleViewPerformance}>
          <Timeline sx={{ mr: 1 }} />
          성과 분석
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleDelete} sx={{ color: "error.main" }}>
          <Delete sx={{ mr: 1 }} />
          삭제
        </MenuItem>
      </Menu>

      <Grid container spacing={3}>
        {/* 기본 정보 */}
        <Grid size={{ xs: 12, md: 8 }}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <Typography variant="h6" sx={{ flexGrow: 1 }}>
                  기본 정보
                </Typography>
                <Chip
                  label={strategyUtils.formatStrategyType(
                    strategy.strategy_type
                  )}
                  color={strategyUtils.getStrategyTypeColor(
                    strategy.strategy_type
                  )}
                  size="small"
                />
              </Box>

              <Typography variant="body1" sx={{ mb: 2 }}>
                {strategy.description || "설명이 없습니다."}
              </Typography>

              <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
                {strategy.tags?.map((tag: string) => (
                  <Chip key={tag} label={tag} size="small" variant="outlined" />
                ))}
              </Box>

              <Divider sx={{ my: 2 }} />

              <Grid container spacing={2}>
                <Grid size={{ xs: 6, sm: 3 }}>
                  <Typography variant="body2" color="text.secondary">
                    생성일
                  </Typography>
                  <Typography variant="body1">
                    {new Date(strategy.created_at).toLocaleDateString()}
                  </Typography>
                </Grid>
                <Grid size={{ xs: 6, sm: 3 }}>
                  <Typography variant="body2" color="text.secondary">
                    수정일
                  </Typography>
                  <Typography variant="body1">
                    {new Date(strategy.updated_at).toLocaleDateString()}
                  </Typography>
                </Grid>
                <Grid size={{ xs: 6, sm: 3 }}>
                  <Typography variant="body2" color="text.secondary">
                    상태
                  </Typography>
                  <Chip
                    label={strategy.is_active ? "활성" : "비활성"}
                    color={strategy.is_active ? "success" : "default"}
                    size="small"
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* 파라미터 설정 */}
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <Settings sx={{ mr: 1 }} />
                <Typography variant="h6">파라미터 설정</Typography>
              </Box>

              <StrategyParameters
                strategyType={strategy.strategy_type}
                parameters={strategy.parameters || {}}
                onChange={() => {}} // readOnly 모드에서는 빈 함수
                readOnly={true}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* 성과 요약 */}
        <Grid size={{ xs: 12, md: 4 }}>
          <StrategyPerformanceSummary
            strategyName={strategy.name}
            strategyType={strategy.strategy_type}
            performance={{
              // 실제 성과 데이터가 있다면 여기에 표시
              total_return: 12.5,
              annual_return: 8.3,
              sharpe_ratio: 1.2,
              max_drawdown: -15.2,
              volatility: 18.5,
              win_rate: 65.0,
              total_trades: 45,
              profit_factor: 1.8,
            }}
            period="1Y"
          />

          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                빠른 작업
              </Typography>

              <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
                <Button
                  startIcon={<Timeline />}
                  onClick={handleViewPerformance}
                  fullWidth
                  variant="outlined"
                >
                  상세 성과 분석
                </Button>
                <Button
                  startIcon={<Edit />}
                  onClick={handleEdit}
                  fullWidth
                  variant="outlined"
                >
                  전략 편집
                </Button>
                <Button
                  startIcon={<FileCopy />}
                  onClick={handleClone}
                  fullWidth
                  variant="outlined"
                >
                  전략 복사
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </PageContainer>
  );
}
