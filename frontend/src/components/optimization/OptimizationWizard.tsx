import type { OptimizationRequest } from "@/client/types.gen";
import { useOptimization } from "@/hooks/useOptimization";
import { useStrategy } from "@/hooks/useStrategy";
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
  Step,
  StepLabel,
  Stepper,
  TextField,
  Typography,
} from "@mui/material";
import { useState } from "react";
import { Controller, useForm } from "react-hook-form";

interface OptimizationWizardProps {
  open: boolean;
  onClose: () => void;
}

interface WizardFormData {
  strategy_name: string;
  symbol: string;
  search_space: {
    [key: string]: [number, number];
  };
  n_trials: number;
  timeout_seconds?: number;
  direction: "maximize" | "minimize";
}

const steps = [
  "전략 선택",
  "파라미터 범위 설정",
  "최적화 옵션",
  "확인 및 시작",
];

/**
 * OptimizationWizard Component
 *
 * 4-step wizard for creating optimization studies:
 * 1. Strategy Selection - Choose strategy template
 * 2. Parameter Range - Define search space for each parameter
 * 3. Optimization Options - Set n_trials, timeout, direction
 * 4. Confirmation - Review and start optimization
 *
 * @example
 * ```tsx
 * const [open, setOpen] = useState(false);
 *
 * <OptimizationWizard
 *   open={open}
 *   onClose={() => setOpen(false)}
 * />
 * ```
 */
export function OptimizationWizard({ open, onClose }: OptimizationWizardProps) {
  const [activeStep, setActiveStep] = useState(0);
  const { createOptimization, isOptimizing } = useOptimization();
  const { strategyList } = useStrategy();

  const {
    control,
    handleSubmit,
    watch,
    setValue,
    reset,
    formState: { errors },
  } = useForm<WizardFormData>({
    defaultValues: {
      strategy_name: "",
      symbol: "AAPL",
      search_space: {},
      n_trials: 100,
      timeout_seconds: 3600,
      direction: "maximize",
    },
  });

  const selectedStrategy = watch("strategy_name");
  const searchSpace = watch("search_space");
  const nTrials = watch("n_trials");
  const direction = watch("direction");

  // Handle next step
  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  // Handle back step
  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  // Handle reset wizard
  const handleReset = () => {
    setActiveStep(0);
    reset();
  };

  // Handle close
  const handleClose = () => {
    handleReset();
    onClose();
  };

  // Handle form submission
  const onSubmit = (data: WizardFormData) => {
    const request: OptimizationRequest = {
      strategy_name: data.strategy_name,
      symbol: data.symbol,
      search_space: data.search_space,
      n_trials: data.n_trials,
      timeout_seconds: data.timeout_seconds,
      direction: data.direction,
    };

    createOptimization(request, {
      onSuccess: () => {
        handleClose();
      },
    });
  };

  // Add parameter to search space
  const addParameter = (paramName: string, min: number, max: number) => {
    setValue(`search_space.${paramName}`, [min, max]);
  };

  // Remove parameter from search space
  const removeParameter = (paramName: string) => {
    const newSearchSpace = { ...searchSpace };
    delete newSearchSpace[paramName];
    setValue("search_space", newSearchSpace);
  };

  // Render step content
  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              전략 템플릿 선택
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              최적화할 전략을 선택하세요
            </Typography>

            <Controller
              name="strategy_name"
              control={control}
              rules={{ required: "전략을 선택해주세요" }}
              render={({ field }) => (
                <TextField
                  {...field}
                  select
                  fullWidth
                  label="전략"
                  error={!!errors.strategy_name}
                  helperText={errors.strategy_name?.message}
                  SelectProps={{
                    native: true,
                  }}
                >
                  <option value="">전략 선택</option>
                  {strategyList?.map((strategy) => (
                    <option key={strategy.id} value={strategy.name}>
                      {strategy.name}
                    </option>
                  ))}
                </TextField>
              )}
            />

            <Box sx={{ mt: 3 }}>
              <Controller
                name="symbol"
                control={control}
                rules={{ required: "심볼을 입력해주세요" }}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="심볼"
                    placeholder="AAPL"
                    error={!!errors.symbol}
                    helperText={errors.symbol?.message}
                  />
                )}
              />
            </Box>
          </Box>
        );

      case 1:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              파라미터 범위 설정
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              각 파라미터의 검색 범위를 설정하세요
            </Typography>

            {/* Parameter Input Form */}
            <Card variant="outlined" sx={{ mb: 3 }}>
              <CardContent>
                <Grid container spacing={2} alignItems="center">
                  <Grid size={4}>
                    <TextField
                      id="param-name"
                      fullWidth
                      label="파라미터 이름"
                      placeholder="rsi_period"
                      size="small"
                    />
                  </Grid>
                  <Grid size={3}>
                    <TextField
                      id="param-min"
                      fullWidth
                      label="최소값"
                      type="number"
                      placeholder="10"
                      size="small"
                    />
                  </Grid>
                  <Grid size={3}>
                    <TextField
                      id="param-max"
                      fullWidth
                      label="최대값"
                      type="number"
                      placeholder="30"
                      size="small"
                    />
                  </Grid>
                  <Grid size={2}>
                    <Button
                      fullWidth
                      variant="contained"
                      size="small"
                      onClick={() => {
                        const name = (
                          document.getElementById(
                            "param-name"
                          ) as HTMLInputElement
                        )?.value;
                        const min = Number(
                          (
                            document.getElementById(
                              "param-min"
                            ) as HTMLInputElement
                          )?.value
                        );
                        const max = Number(
                          (
                            document.getElementById(
                              "param-max"
                            ) as HTMLInputElement
                          )?.value
                        );

                        if (name && !Number.isNaN(min) && !Number.isNaN(max)) {
                          addParameter(name, min, max);
                          // Clear inputs
                          (
                            document.getElementById(
                              "param-name"
                            ) as HTMLInputElement
                          ).value = "";
                          (
                            document.getElementById(
                              "param-min"
                            ) as HTMLInputElement
                          ).value = "";
                          (
                            document.getElementById(
                              "param-max"
                            ) as HTMLInputElement
                          ).value = "";
                        }
                      }}
                    >
                      추가
                    </Button>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>

            {/* Parameter List */}
            {Object.keys(searchSpace).length === 0 ? (
              <Typography variant="body2" color="text.secondary" align="center">
                파라미터를 추가해주세요
              </Typography>
            ) : (
              <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
                {Object.entries(searchSpace).map(([name, range]) => (
                  <Chip
                    key={name}
                    label={`${name}: [${range[0]}, ${range[1]}]`}
                    onDelete={() => removeParameter(name)}
                    color="primary"
                    variant="outlined"
                  />
                ))}
              </Box>
            )}
          </Box>
        );

      case 2:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              최적화 옵션
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              최적화 실행 옵션을 설정하세요
            </Typography>

            <Grid container spacing={3}>
              <Grid size={12}>
                <Controller
                  name="n_trials"
                  control={control}
                  rules={{
                    required: "트라이얼 수를 입력해주세요",
                    min: { value: 10, message: "최소 10회 이상" },
                    max: { value: 1000, message: "최대 1000회" },
                  }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="트라이얼 수"
                      type="number"
                      error={!!errors.n_trials}
                      helperText={
                        errors.n_trials?.message || "최적화 반복 횟수 (10-1000)"
                      }
                    />
                  )}
                />
              </Grid>

              <Grid size={12}>
                <Controller
                  name="timeout_seconds"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="타임아웃 (초)"
                      type="number"
                      helperText="최대 실행 시간 (초 단위, 선택사항)"
                    />
                  )}
                />
              </Grid>

              <Grid size={12}>
                <Controller
                  name="direction"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      select
                      fullWidth
                      label="최적화 방향"
                      SelectProps={{
                        native: true,
                      }}
                      helperText="Sharpe Ratio는 최대화, Drawdown은 최소화"
                    >
                      <option value="maximize">최대화 (Maximize)</option>
                      <option value="minimize">최소화 (Minimize)</option>
                    </TextField>
                  )}
                />
              </Grid>
            </Grid>
          </Box>
        );

      case 3:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              최적화 설정 확인
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              설정을 확인하고 최적화를 시작하세요
            </Typography>

            <Card variant="outlined">
              <CardContent>
                <Grid container spacing={2}>
                  <Grid size={6}>
                    <Typography variant="caption" color="text.secondary">
                      전략
                    </Typography>
                    <Typography variant="body1">{selectedStrategy}</Typography>
                  </Grid>

                  <Grid size={6}>
                    <Typography variant="caption" color="text.secondary">
                      심볼
                    </Typography>
                    <Typography variant="body1">{watch("symbol")}</Typography>
                  </Grid>

                  <Grid size={12}>
                    <Typography
                      variant="caption"
                      color="text.secondary"
                      gutterBottom
                    >
                      검색 공간
                    </Typography>
                    <Box
                      sx={{ display: "flex", flexWrap: "wrap", gap: 1, mt: 1 }}
                    >
                      {Object.entries(searchSpace).map(([name, range]) => (
                        <Chip
                          key={name}
                          label={`${name}: [${range[0]}, ${range[1]}]`}
                          size="small"
                          color="primary"
                        />
                      ))}
                    </Box>
                  </Grid>

                  <Grid size={4}>
                    <Typography variant="caption" color="text.secondary">
                      트라이얼 수
                    </Typography>
                    <Typography variant="body1">{nTrials}회</Typography>
                  </Grid>

                  <Grid size={4}>
                    <Typography variant="caption" color="text.secondary">
                      타임아웃
                    </Typography>
                    <Typography variant="body1">
                      {watch("timeout_seconds") || "없음"}초
                    </Typography>
                  </Grid>

                  <Grid size={4}>
                    <Typography variant="caption" color="text.secondary">
                      최적화 방향
                    </Typography>
                    <Typography variant="body1">
                      {direction === "maximize" ? "최대화" : "최소화"}
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Box>
        );

      default:
        return null;
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>최적화 스터디 생성</DialogTitle>

      <DialogContent>
        <Box sx={{ mt: 2 }}>
          <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>

          <Box sx={{ minHeight: 300 }}>{renderStepContent(activeStep)}</Box>
        </Box>
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose} disabled={isOptimizing}>
          취소
        </Button>

        {activeStep > 0 && (
          <Button onClick={handleBack} disabled={isOptimizing}>
            이전
          </Button>
        )}

        {activeStep < steps.length - 1 ? (
          <Button
            variant="contained"
            onClick={handleNext}
            disabled={
              (activeStep === 0 && !selectedStrategy) ||
              (activeStep === 1 && Object.keys(searchSpace).length === 0)
            }
          >
            다음
          </Button>
        ) : (
          <Button
            variant="contained"
            onClick={handleSubmit(onSubmit)}
            disabled={isOptimizing}
          >
            {isOptimizing ? "시작 중..." : "최적화 시작"}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
}
