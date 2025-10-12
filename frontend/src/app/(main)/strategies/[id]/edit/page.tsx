"use client";

import type { StrategyType } from "@/client/types.gen";
import PageContainer from "@/components/layout/PageContainer";
import StrategyParameters from "@/components/strategies/StrategyParameters";
import { useStrategy, useStrategyDetail } from "@/hooks/useStrategy";
import { ArrowBack, PlayArrow, Save } from "@mui/icons-material";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Step,
  StepLabel,
  Stepper,
  TextField,
  Typography,
} from "@mui/material";
import { useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import type React from "react";
import { useEffect, useState } from "react";

const steps = ["기본 정보", "파라미터 설정", "백테스트 실행"];

export default function EditStrategyPage() {
  const router = useRouter();
  const params = useParams();
  const queryClient = useQueryClient();
  const strategyId = params.id as string;

  const [activeStep, setActiveStep] = useState(0);
  const [strategyData, setStrategyData] = useState({
    name: "",
    description: "",
    strategy_type: "sma_crossover" as StrategyType,
    parameters: {},
    tags: [] as string[],
  });

  // 전략 데이터 조회
  const {
    data: strategy,
    isLoading: isLoadingStrategy,
    error,
  } = useStrategyDetail(strategyId);

  // 전략 관리 액션들
  const {
    updateStrategy: updateStrategyFn,
    executeStrategy: executeStrategyFn,
    isMutating,
  } = useStrategy();

  // 전략 데이터로 초기화
  useEffect(() => {
    if (strategy) {
      setStrategyData({
        name: strategy.name,
        description: strategy.description || "",
        strategy_type: strategy.strategy_type,
        parameters: strategy.parameters || {},
        tags: strategy.tags || [],
      });
    }
  }, [strategy]);

  const handleNext = () => {
    setActiveStep((prevStep) => prevStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const handleSave = async () => {
    try {
      await updateStrategyFn({ id: strategyId, updateData: strategyData });
      queryClient.invalidateQueries({ queryKey: ["strategy", "list"] });
      queryClient.invalidateQueries({
        queryKey: ["strategy", "detail", strategyId],
      });
      router.push(`/strategies/${strategyId}`);
    } catch (error) {
      console.error("전략 업데이트 실패:", error);
    }
  };

  const handleExecute = async () => {
    try {
      await executeStrategyFn({
        id: strategyId,
        data: {
          symbol: "AAPL",
          market_data: {
            start_date: new Date(
              Date.now() - 365 * 24 * 60 * 60 * 1000
            ).toISOString(),
            end_date: new Date().toISOString(),
          },
        },
      });
      router.push(`/backtests`);
    } catch (error) {
      console.error("전략 실행 실패:", error);
    }
  };

  if (error) {
    return (
      <PageContainer
        title="전략 편집"
        breadcrumbs={[
          { title: "Strategy Center" },
          { title: "Strategies" },
          { title: "Edit" },
        ]}
      >
        <Alert severity="error">
          전략을 불러오는 중 오류가 발생했습니다: {(error as any)?.message}
        </Alert>
      </PageContainer>
    );
  }

  if (isLoadingStrategy) {
    return (
      <PageContainer
        title="전략 편집"
        breadcrumbs={[
          { title: "Strategy Center" },
          { title: "Strategies" },
          { title: "Edit" },
        ]}
      >
        <Box sx={{ display: "flex", justifyContent: "center", py: 4 }}>
          <CircularProgress />
        </Box>
      </PageContainer>
    );
  }

  return (
    <PageContainer
      title={`"${strategy?.name}" 편집`}
      breadcrumbs={[
        { title: "Strategy Center" },
        { title: "Strategies" },
        { title: strategy?.name || "전략" },
        { title: "Edit" },
      ]}
      actions={[
        <Button
          key="back"
          startIcon={<ArrowBack />}
          onClick={() => router.push(`/strategies/${strategyId}`)}
        >
          취소
        </Button>,
      ]}
    >
      <Paper sx={{ p: 3, mb: 3 }}>
        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {activeStep === 0 && (
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3 }}>
                기본 정보 설정
              </Typography>

              <Grid container spacing={3}>
                <Grid size={{ xs: 12 }}>
                  <TextField
                    fullWidth
                    label="전략 이름"
                    value={strategyData.name}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                      setStrategyData((prev) => ({
                        ...prev,
                        name: e.target.value,
                      }))
                    }
                    required
                  />
                </Grid>

                <Grid size={{ xs: 12 }}>
                  <TextField
                    fullWidth
                    multiline
                    rows={4}
                    label="설명"
                    value={strategyData.description}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                      setStrategyData((prev) => ({
                        ...prev,
                        description: e.target.value,
                      }))
                    }
                  />
                </Grid>

                <Grid size={{ xs: 12 }}>
                  <FormControl fullWidth required disabled>
                    <InputLabel>전략 타입</InputLabel>
                    <Select
                      value={strategyData.strategy_type}
                      label="전략 타입"
                      disabled
                    >
                      <MenuItem value="sma_crossover">SMA Crossover</MenuItem>
                      <MenuItem value="rsi">RSI</MenuItem>
                      <MenuItem value="bollinger_bands">
                        Bollinger Bands
                      </MenuItem>
                      <MenuItem value="macd">MACD</MenuItem>
                      <MenuItem value="momentum">Momentum</MenuItem>
                    </Select>
                    <Typography
                      variant="caption"
                      color="text.secondary"
                      sx={{ mt: 1 }}
                    >
                      전략 타입은 변경할 수 없습니다.
                    </Typography>
                  </FormControl>
                </Grid>
              </Grid>

              <Box sx={{ display: "flex", justifyContent: "flex-end", mt: 3 }}>
                <Button variant="contained" onClick={handleNext}>
                  다음
                </Button>
              </Box>
            </CardContent>
          </Card>
        )}

        {activeStep === 1 && (
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3 }}>
                파라미터 설정
              </Typography>

              <StrategyParameters
                strategyType={strategyData.strategy_type}
                parameters={strategyData.parameters}
                onChange={(newParams) =>
                  setStrategyData((prev) => ({
                    ...prev,
                    parameters: newParams,
                  }))
                }
              />

              <Box
                sx={{ display: "flex", justifyContent: "space-between", mt: 3 }}
              >
                <Button onClick={handleBack}>이전</Button>
                <Button variant="contained" onClick={handleNext}>
                  다음
                </Button>
              </Box>
            </CardContent>
          </Card>
        )}

        {activeStep === 2 && (
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3 }}>
                저장 및 백테스트
              </Typography>

              <Alert severity="info" sx={{ mb: 3 }}>
                전략을 저장하고 백테스트를 실행하여 성과를 확인할 수 있습니다.
              </Alert>

              <Box
                sx={{ display: "flex", justifyContent: "space-between", mt: 3 }}
              >
                <Button onClick={handleBack}>이전</Button>
                <Box sx={{ display: "flex", gap: 2 }}>
                  <Button
                    startIcon={<Save />}
                    variant="outlined"
                    onClick={handleSave}
                    disabled={isMutating.updateStrategy}
                  >
                    {isMutating.updateStrategy ? "저장 중..." : "저장"}
                  </Button>
                  <Button
                    startIcon={<PlayArrow />}
                    variant="contained"
                    onClick={handleExecute}
                    disabled={isMutating.executeStrategy}
                  >
                    {isMutating.executeStrategy
                      ? "실행 중..."
                      : "백테스트 실행"}
                  </Button>
                </Box>
              </Box>
            </CardContent>
          </Card>
        )}
      </Paper>
    </PageContainer>
  );
}
