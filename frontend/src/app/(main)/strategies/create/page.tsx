"use client";

import type { StrategyType } from "@/client/types.gen";
import PageContainer from "@/components/layout/PageContainer";
import StrategyParameters from "@/components/strategies/StrategyParameters";
import { useStrategy, useStrategyDetail } from "@/hooks/useStrategy";
import { ArrowBack, Save } from "@mui/icons-material";
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
import { useRouter, useSearchParams } from "next/navigation";
import type React from "react";
import { useEffect, useState } from "react";

const steps = ["기본 정보", "파라미터 설정", "백테스트 실행"];

export default function CreateStrategyPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const queryClient = useQueryClient();

  // URL에서 복제 파라미터 추출
  const cloneId = searchParams.get("clone");
  const isClone = !!cloneId;

  const [activeStep, setActiveStep] = useState(0);
  const [strategyData, setStrategyData] = useState({
    name: "",
    description: "",
    strategy_type: "sma_crossover" as StrategyType,
    parameters: {},
    tags: [] as string[],
  });

  // 복제할 전략 데이터 조회
  const { strategy: sourceStrategy, isLoading: isLoadingSource } =
    useStrategyDetail(cloneId || "");

  // 전략 관리 액션들
  const { createStrategy: createStrategyFn, isMutating } = useStrategy();

  const handleCreateStrategy = async (data: any) => {
    try {
      await createStrategyFn(data);
      queryClient.invalidateQueries({ queryKey: ["strategy", "list"] });
      router.push("/strategies/my-strategies");
    } catch (error) {
      console.error("전략 생성 실패:", error);
    }
  };

  // 소스 전략 데이터로 초기화 (복제 모드)
  useEffect(() => {
    if (sourceStrategy && isClone) {
      const { config_type: _, ...configParams } = sourceStrategy.config as any;
      setStrategyData({
        name: `${sourceStrategy.name} (복사본)`,
        description: sourceStrategy.description || "",
        strategy_type: sourceStrategy.strategy_type,
        parameters: configParams || {},
        tags: sourceStrategy.tags || [],
      });
    }
  }, [sourceStrategy, isClone]);
  const handleNext = () => {
    setActiveStep((prevStep) => prevStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const handleSave = () => {
    handleCreateStrategy(strategyData);
  };

  const getPageTitle = () => {
    if (isClone) return "전략 복사";
    return "새 전략 만들기";
  };

  const getBreadcrumbs = () => [
    { title: "Strategy Center" },
    { title: "Strategies" },
    { title: "Create" },
  ];

  if (isLoadingSource) {
    return (
      <PageContainer title={getPageTitle()} breadcrumbs={getBreadcrumbs()}>
        <Box sx={{ display: "flex", justifyContent: "center", py: 4 }}>
          <CircularProgress />
        </Box>
      </PageContainer>
    );
  }

  return (
    <PageContainer
      title={getPageTitle()}
      breadcrumbs={getBreadcrumbs()}
      actions={[
        <Button
          key="back"
          startIcon={<ArrowBack />}
          onClick={() => router.back()}
        >
          뒤로가기
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
                  <FormControl fullWidth required>
                    <InputLabel>전략 타입</InputLabel>
                    <Select
                      value={strategyData.strategy_type}
                      label="전략 타입"
                      onChange={(e: any) =>
                        setStrategyData((prev) => ({
                          ...prev,
                          strategy_type: e.target.value as StrategyType,
                        }))
                      }
                    >
                      <MenuItem value="sma_crossover">SMA 크로스오버</MenuItem>
                      <MenuItem value="rsi_mean_reversion">
                        RSI 평균회귀
                      </MenuItem>
                      <MenuItem value="momentum">모멘텀</MenuItem>
                      <MenuItem value="buy_and_hold">매수후보유</MenuItem>
                    </Select>
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
                전략 저장
              </Typography>

              <Alert severity="info" sx={{ mb: 3 }}>
                전략을 저장하면 내 전략 목록에서 확인할 수 있습니다.
              </Alert>

              <Box
                sx={{ display: "flex", justifyContent: "space-between", mt: 3 }}
              >
                <Button onClick={handleBack}>이전</Button>
                <Button
                  startIcon={<Save />}
                  variant="contained"
                  onClick={handleSave}
                  disabled={isMutating.createStrategy}
                >
                  {isMutating.createStrategy ? "저장 중..." : "저장"}
                </Button>
              </Box>
            </CardContent>
          </Card>
        )}
      </Paper>
    </PageContainer>
  );
}
