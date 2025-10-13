"use client";

import PageContainer from "@/components/layout/PageContainer";
import { useBacktest } from "@/hooks/useBacktests";
import { ArrowBack, CheckCircle, PlaylistAdd, Save } from "@mui/icons-material";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Container,
  FormControl,
  Grid,
  InputAdornment,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Stack,
  Step,
  StepLabel,
  Stepper,
  TextField,
  Typography,
} from "@mui/material";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFns";
import { DatePicker } from "@mui/x-date-pickers/DatePicker";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { ko } from "date-fns/locale";
import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";
import { backtestUtils } from "../utils";

type StepKey = 0 | 1 | 2 | 3;

type FormState = {
  name: string;
  description: string;
  startDate: Date;
  endDate: Date;
  symbols: string;
  initialCash: number;
  maxPositionSize: number;
  commissionRate: number;
  slippageRate: number;
  rebalanceFrequency: "daily" | "weekly" | "monthly";
  tags: string;
};

const steps: { title: string; description: string }[] = [
  { title: "기본 정보", description: "백테스트의 이름과 설명을 입력하세요." },
  {
    title: "자산 및 기간",
    description: "대상 심볼과 백테스트 기간을 설정합니다.",
  },
  {
    title: "거래 설정",
    description: "자본 규모와 거래 관련 매개변수를 입력합니다.",
  },
  {
    title: "검토",
    description: "입력한 내용을 확인하고 백테스트를 생성합니다.",
  },
];

const defaultState: FormState = {
  name: "",
  description: "",
  startDate: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000),
  endDate: new Date(),
  symbols: "AAPL, MSFT, NVDA",
  initialCash: 1000000,
  maxPositionSize: 0.2,
  commissionRate: 0.001,
  slippageRate: 0.0005,
  rebalanceFrequency: "monthly",
  tags: "기본,모멘텀",
};

export default function CreateBacktestPage() {
  const router = useRouter();
  const [step, setStep] = useState<StepKey>(0);
  const [formState, setFormState] = useState<FormState>(defaultState);
  const [errors, setErrors] = useState<string[]>([]);

  const {
    createBacktestAsync,
    executeBacktestAsync,
    isMutating: { createBacktest: creating },
  } = useBacktest();

  const symbolList = useMemo(
    () =>
      formState.symbols
        .split(",")
        .map((symbol) => symbol.trim().toUpperCase())
        .filter((symbol) => symbol.length > 0),
    [formState.symbols]
  );

  const tagList = useMemo(
    () =>
      formState.tags
        .split(",")
        .map((tag) => tag.trim())
        .filter((tag) => tag.length > 0),
    [formState.tags]
  );

  const buildPayload = () => ({
    name: formState.name,
    description: formState.description || undefined,
    config: {
      name: formState.name,
      description: formState.description || undefined,
      start_date: formState.startDate,
      end_date: formState.endDate,
      symbols: symbolList,
      initial_cash: formState.initialCash,
      max_position_size: formState.maxPositionSize,
      commission_rate: formState.commissionRate,
      slippage_rate: formState.slippageRate,
      rebalance_frequency: formState.rebalanceFrequency,
      tags: tagList,
    },
  });

  const validateCurrentStep = () => {
    const payload = buildPayload();
    const validationErrors: string[] = [];

    if (step === 0) {
      if (!payload.name.trim()) {
        validationErrors.push("백테스트 이름을 입력해주세요.");
      }
    }

    if (step === 1) {
      if (!payload.config.start_date || !payload.config.end_date) {
        validationErrors.push("시작일과 종료일을 모두 선택해주세요.");
      } else if (
        payload.config.start_date &&
        payload.config.end_date &&
        payload.config.start_date >= payload.config.end_date
      ) {
        validationErrors.push("종료일은 시작일 이후여야 합니다.");
      }
      if (!symbolList.length) {
        validationErrors.push("최소 한 개 이상의 심볼을 입력해주세요.");
      }
    }

    if (step === 2) {
      if (payload.config.initial_cash && payload.config.initial_cash <= 0) {
        validationErrors.push("초기 자본은 0보다 커야 합니다.");
      }
      if (
        payload.config.max_position_size <= 0 ||
        payload.config.max_position_size > 1
      ) {
        validationErrors.push(
          "최대 포지션 크기는 0보다 크고 1 이하이어야 합니다."
        );
      }
    }

    if (step === 3) {
      validationErrors.push(...backtestUtils.validateConfig(payload.config));
    }

    setErrors(validationErrors);
    return validationErrors.length === 0;
  };

  const handleNext = () => {
    if (validateCurrentStep()) {
      setStep((prev) => (prev + 1) as StepKey);
      setErrors([]);
    }
  };

  const handleBack = () => {
    setStep((prev) => (prev - 1) as StepKey);
    setErrors([]);
  };

  const handleSubmit = async () => {
    if (!validateCurrentStep()) {
      return;
    }
    const payload = buildPayload();
    try {
      // Step 1: Create backtest
      const backtest = await createBacktestAsync(payload);

      if (!backtest) {
        throw new Error("백테스트 생성에 실패했습니다");
      }

      // Step 2: Execute backtest with empty signals (will trigger strategy execution)
      await executeBacktestAsync({
        backtestId: backtest.id,
        signals: [],
      });

      // Navigate to backtest detail page
      router.push(`/backtests/${backtest.id}`);
    } catch (error) {
      console.error("Failed to create/execute backtest", error);
      setErrors(["백테스트 생성 또는 실행에 실패했습니다. 다시 시도해주세요."]);
    }
  };
  return (
    <PageContainer
      title="새 백테스트 만들기"
      breadcrumbs={[{ title: "백테스트" }, { title: "새 백테스트" }]}
    >
      <Container maxWidth="lg">
        <Box sx={{ mb: 4 }}>
          <Button
            startIcon={<ArrowBack />}
            onClick={() => router.push("/backtests")}
          >
            백테스트 목록으로
          </Button>
        </Box>

        <Paper sx={{ p: 3, mb: 3 }}>
          <Stepper activeStep={step} alternativeLabel>
            {steps.map((item) => (
              <Step key={item.title}>
                <StepLabel>{item.title}</StepLabel>
              </Step>
            ))}
          </Stepper>
        </Paper>

        {errors.length > 0 && (
          <Alert severity="error" sx={{ mb: 3 }}>
            <Box component="ul" sx={{ m: 0, pl: 3 }}>
              {errors.map((error) => (
                <Box component="li" key={error}>
                  {error}
                </Box>
              ))}
            </Box>
          </Alert>
        )}

        <Paper sx={{ p: 4 }}>
          {step === 0 && (
            <Stack spacing={3}>
              <Box>
                <Typography variant="h6" gutterBottom>
                  기본 정보
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  백테스트를 구분하기 위한 이름과 설명을 입력하세요.
                </Typography>
              </Box>
              <TextField
                label="백테스트 이름"
                value={formState.name}
                onChange={(event) =>
                  setFormState((prev) => ({
                    ...prev,
                    name: event.target.value,
                  }))
                }
                required
                fullWidth
              />
              <TextField
                label="설명"
                value={formState.description}
                onChange={(event) =>
                  setFormState((prev) => ({
                    ...prev,
                    description: event.target.value,
                  }))
                }
                multiline
                minRows={3}
                fullWidth
              />
            </Stack>
          )}

          {step === 1 && (
            <LocalizationProvider
              dateAdapter={AdapterDateFns}
              adapterLocale={ko}
            >
              <Stack spacing={3}>
                <Box>
                  <Typography variant="h6" gutterBottom>
                    자산 및 기간 설정
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    분석할 자산과 기간을 선택하세요.
                  </Typography>
                </Box>
                <DatePicker
                  label="시작일"
                  value={formState.startDate}
                  onChange={(date) =>
                    setFormState((prev) => ({
                      ...prev,
                      startDate:
                        date == null
                          ? prev.startDate
                          : typeof (date as any).toDate === "function"
                          ? (date as any).toDate()
                          : (date as Date),
                    }))
                  }
                  slotProps={{ textField: { fullWidth: true } }}
                />

                <DatePicker
                  label="종료일"
                  value={formState.endDate}
                  onChange={(date) =>
                    setFormState((prev) => ({
                      ...prev,
                      endDate:
                        date == null
                          ? prev.endDate
                          : typeof (date as any).toDate === "function"
                          ? (date as any).toDate()
                          : (date as Date),
                    }))
                  }
                  slotProps={{ textField: { fullWidth: true } }}
                />
                <TextField
                  label="심볼 목록"
                  helperText="쉼표로 구분하여 입력하세요 (예: AAPL, MSFT)"
                  value={formState.symbols}
                  onChange={(event) =>
                    setFormState((prev) => ({
                      ...prev,
                      symbols: event.target.value,
                    }))
                  }
                  multiline
                  minRows={3}
                  fullWidth
                />
              </Stack>
            </LocalizationProvider>
          )}

          {step === 2 && (
            <Stack spacing={3}>
              <Box>
                <Typography variant="h6" gutterBottom>
                  거래 설정
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  자본 규모와 거래 매개변수를 입력하세요.
                </Typography>
              </Box>
              <Grid container spacing={3}>
                <Grid size={12}>
                  <TextField
                    label="초기 자본"
                    type="number"
                    value={formState.initialCash}
                    onChange={(event) =>
                      setFormState((prev) => ({
                        ...prev,
                        initialCash: Number(event.target.value),
                      }))
                    }
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">$</InputAdornment>
                      ),
                    }}
                    fullWidth
                  />
                </Grid>
                <Grid size={12}>
                  <TextField
                    label="최대 포지션 비중 (%)"
                    type="number"
                    value={formState.maxPositionSize * 100}
                    onChange={(event) =>
                      setFormState((prev) => ({
                        ...prev,
                        maxPositionSize: Number(event.target.value) / 100,
                      }))
                    }
                    fullWidth
                  />
                </Grid>
                <Grid size={12}>
                  <TextField
                    label="수수료율 (%)"
                    type="number"
                    value={formState.commissionRate * 100}
                    onChange={(event) =>
                      setFormState((prev) => ({
                        ...prev,
                        commissionRate: Number(event.target.value) / 100,
                      }))
                    }
                    fullWidth
                  />
                </Grid>
                <Grid size={12}>
                  <TextField
                    label="슬리피지 (%)"
                    type="number"
                    value={formState.slippageRate * 100}
                    onChange={(event) =>
                      setFormState((prev) => ({
                        ...prev,
                        slippageRate: Number(event.target.value) / 100,
                      }))
                    }
                    fullWidth
                  />
                </Grid>
                <Grid size={12}>
                  <FormControl fullWidth>
                    <InputLabel>리밸런싱 주기</InputLabel>
                    <Select
                      label="리밸런싱 주기"
                      value={formState.rebalanceFrequency}
                      onChange={(event) =>
                        setFormState((prev) => ({
                          ...prev,
                          rebalanceFrequency: event.target
                            .value as FormState["rebalanceFrequency"],
                        }))
                      }
                    >
                      <MenuItem value="daily">매일</MenuItem>
                      <MenuItem value="weekly">매주</MenuItem>
                      <MenuItem value="monthly">매월</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid size={12}>
                  <TextField
                    label="태그"
                    helperText="쉼표로 구분하여 입력하세요"
                    value={formState.tags}
                    onChange={(event) =>
                      setFormState((prev) => ({
                        ...prev,
                        tags: event.target.value,
                      }))
                    }
                    fullWidth
                  />
                </Grid>
              </Grid>
            </Stack>
          )}

          {step === 3 && (
            <Stack spacing={3}>
              <Box>
                <Typography variant="h6" gutterBottom>
                  설정 검토
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  백테스트 생성 전에 입력한 내용을 다시 한 번 확인하세요.
                </Typography>
              </Box>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle1" gutterBottom>
                    요약 정보
                  </Typography>
                  <Stack spacing={1.5}>
                    <Typography variant="body1">
                      이름: {formState.name}
                    </Typography>
                    <Typography variant="body1">
                      설명: {formState.description || "(없음)"}
                    </Typography>
                    <Typography variant="body1">
                      기간: {formState.startDate.toLocaleDateString()} ~{" "}
                      {formState.endDate.toLocaleDateString()}
                    </Typography>
                    <Typography variant="body1">
                      심볼:{" "}
                      {symbolList.length ? symbolList.join(", ") : "(없음)"}
                    </Typography>
                    <Typography variant="body1">
                      초기 자본:{" "}
                      {backtestUtils.formatCurrency(formState.initialCash)}
                    </Typography>
                    <Typography variant="body1">
                      최대 포지션 비중:{" "}
                      {backtestUtils.formatPercentage(
                        formState.maxPositionSize
                      )}
                    </Typography>
                    <Typography variant="body1">
                      수수료율:{" "}
                      {backtestUtils.formatPercentage(
                        formState.commissionRate,
                        3
                      )}
                    </Typography>
                    <Typography variant="body1">
                      슬리피지:{" "}
                      {backtestUtils.formatPercentage(
                        formState.slippageRate,
                        3
                      )}
                    </Typography>
                    <Typography variant="body1">
                      리밸런싱 주기: {formState.rebalanceFrequency}
                    </Typography>
                    <Typography variant="body1">
                      태그: {tagList.length ? tagList.join(", ") : "(없음)"}
                    </Typography>
                  </Stack>
                </CardContent>
              </Card>
            </Stack>
          )}

          <Stack direction="row" justifyContent="space-between" sx={{ mt: 4 }}>
            <Button
              variant="outlined"
              onClick={handleBack}
              disabled={step === 0 || creating}
            >
              이전
            </Button>
            {step < 3 ? (
              <Button variant="contained" onClick={handleNext}>
                다음 단계
              </Button>
            ) : (
              <Stack direction="row" spacing={2}>
                <Button
                  variant="outlined"
                  startIcon={<Save />}
                  onClick={handleSubmit}
                  disabled={creating}
                >
                  저장 후 종료
                </Button>
                <Button
                  variant="contained"
                  startIcon={<PlaylistAdd />}
                  onClick={handleSubmit}
                  disabled={creating}
                >
                  백테스트 생성
                </Button>
              </Stack>
            )}
          </Stack>
        </Paper>

        <Stack direction="row" spacing={2} sx={{ mt: 4 }}>
          <Button
            variant="text"
            color="secondary"
            startIcon={<CheckCircle />}
            onClick={() => {
              setFormState(defaultState);
              setStep(0);
            }}
          >
            설정 초기화
          </Button>
        </Stack>
      </Container>
    </PageContainer>
  );
}
