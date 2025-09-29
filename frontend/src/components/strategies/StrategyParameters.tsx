"use client";

import {
  ExpandMore,
  Help,
  Preview,
  RestartAlt,
  Save,
} from "@mui/icons-material";
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  FormControl,
  FormControlLabel,
  IconButton,
  MenuItem,
  Select,
  Slider,
  Stack,
  Switch,
  TextField,
  Tooltip,
  Typography,
} from "@mui/material";
import { useEffect, useState } from "react";

interface ParameterSchema {
  type: "number" | "boolean" | "string" | "select";
  description?: string;
  min?: number;
  max?: number;
  step?: number;
  default?: any;
  options?: string[];
  required?: boolean;
  range?: [number, number];
}

interface StrategyParametersProps {
  strategyType: string;
  parameters: Record<string, any>;
  parameterSchema?: Record<string, ParameterSchema>;
  onChange: (parameters: Record<string, any>) => void;
  onSave?: () => void;
  onPreview?: () => void;
  onReset?: () => void;
  isTemplate?: boolean;
  readOnly?: boolean;
}

// 기본 파라미터 스키마 (백엔드에서 오지 않을 경우 대비)
const DEFAULT_SCHEMAS: Record<string, Record<string, ParameterSchema>> = {
  sma_crossover: {
    short_window: {
      type: "number",
      description: "단기 이동평균 기간",
      min: 5,
      max: 50,
      step: 1,
      default: 20,
      required: true,
    },
    long_window: {
      type: "number",
      description: "장기 이동평균 기간",
      min: 20,
      max: 200,
      step: 1,
      default: 50,
      required: true,
    },
  },
  rsi_mean_reversion: {
    rsi_period: {
      type: "number",
      description: "RSI 계산 기간",
      min: 5,
      max: 30,
      step: 1,
      default: 14,
      required: true,
    },
    oversold_threshold: {
      type: "number",
      description: "과매도 임계값",
      min: 10,
      max: 40,
      step: 1,
      default: 30,
      required: true,
    },
    overbought_threshold: {
      type: "number",
      description: "과매수 임계값",
      min: 60,
      max: 90,
      step: 1,
      default: 70,
      required: true,
    },
  },
  momentum: {
    lookback_period: {
      type: "number",
      description: "모멘텀 계산 기간",
      min: 5,
      max: 50,
      step: 1,
      default: 12,
      required: true,
    },
    threshold: {
      type: "number",
      description: "모멘텀 임계값 (%)",
      min: 1,
      max: 20,
      step: 0.5,
      default: 5,
      required: true,
    },
  },
  buy_and_hold: {
    initial_investment: {
      type: "number",
      description: "초기 투자금액",
      min: 1000,
      max: 1000000,
      step: 1000,
      default: 10000,
      required: true,
    },
  },
};

export default function StrategyParameters({
  strategyType,
  parameters,
  parameterSchema,
  onChange,
  onSave,
  onPreview,
  onReset,
  isTemplate = false,
  readOnly = false,
}: StrategyParametersProps) {
  const [localParameters, setLocalParameters] = useState(parameters);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const schema = parameterSchema || DEFAULT_SCHEMAS[strategyType] || {};

  useEffect(() => {
    setLocalParameters(parameters);
  }, [parameters]);

  const validateParameter = (key: string, value: any): string | null => {
    const paramSchema = schema[key];
    if (!paramSchema) return null;

    if (
      paramSchema.required &&
      (value === undefined || value === null || value === "")
    ) {
      return "필수 항목입니다.";
    }

    if (paramSchema.type === "number") {
      const numValue = Number(value);
      if (isNaN(numValue)) return "숫자를 입력해주세요.";
      if (paramSchema.min !== undefined && numValue < paramSchema.min) {
        return `최소값은 ${paramSchema.min}입니다.`;
      }
      if (paramSchema.max !== undefined && numValue > paramSchema.max) {
        return `최대값은 ${paramSchema.max}입니다.`;
      }
    }

    return null;
  };

  const handleParameterChange = (key: string, value: any) => {
    if (readOnly) return;

    const newParameters = { ...localParameters, [key]: value };
    setLocalParameters(newParameters);

    // 유효성 검사
    const error = validateParameter(key, value);
    setErrors((prev) => ({
      ...prev,
      [key]: error || "",
    }));

    onChange(newParameters);
  };

  const handleReset = () => {
    if (readOnly) return;

    const defaultParams: Record<string, any> = {};
    Object.entries(schema).forEach(([key, paramSchema]) => {
      defaultParams[key] = paramSchema.default;
    });

    setLocalParameters(defaultParams);
    setErrors({});
    onChange(defaultParams);
    onReset?.();
  };

  const renderParameterInput = (key: string, paramSchema: ParameterSchema) => {
    const value = localParameters[key] ?? paramSchema.default;
    const hasError = errors[key];

    switch (paramSchema.type) {
      case "number":
        const isSlider =
          paramSchema.min !== undefined && paramSchema.max !== undefined;

        return (
          <Stack spacing={2} key={key}>
            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
              <Typography variant="subtitle2" sx={{ minWidth: 100 }}>
                {key
                  .replace(/_/g, " ")
                  .replace(/\b\w/g, (l) => l.toUpperCase())}
              </Typography>
              {paramSchema.description && (
                <Tooltip title={paramSchema.description}>
                  <IconButton size="small">
                    <Help fontSize="small" />
                  </IconButton>
                </Tooltip>
              )}
              {paramSchema.required && (
                <Chip
                  size="small"
                  label="필수"
                  color="error"
                  variant="outlined"
                />
              )}
            </Box>

            {isSlider ? (
              <Box sx={{ px: 2 }}>
                <Slider
                  value={Number(value) || paramSchema.default || 0}
                  min={paramSchema.min}
                  max={paramSchema.max}
                  step={paramSchema.step || 1}
                  onChange={(_, newValue) =>
                    handleParameterChange(key, newValue)
                  }
                  valueLabelDisplay="auto"
                  disabled={readOnly}
                />
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    mt: 1,
                  }}
                >
                  <Typography variant="caption" color="text.secondary">
                    {paramSchema.min}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {paramSchema.max}
                  </Typography>
                </Box>
              </Box>
            ) : (
              <TextField
                type="number"
                value={value || ""}
                onChange={(e) =>
                  handleParameterChange(key, Number(e.target.value))
                }
                error={!!hasError}
                helperText={hasError || paramSchema.description}
                inputProps={{
                  min: paramSchema.min,
                  max: paramSchema.max,
                  step: paramSchema.step || 1,
                }}
                disabled={readOnly}
                size="small"
              />
            )}
          </Stack>
        );

      case "boolean":
        return (
          <Stack spacing={1} key={key}>
            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
              <Typography variant="subtitle2">
                {key
                  .replace(/_/g, " ")
                  .replace(/\b\w/g, (l) => l.toUpperCase())}
              </Typography>
              {paramSchema.description && (
                <Tooltip title={paramSchema.description}>
                  <IconButton size="small">
                    <Help fontSize="small" />
                  </IconButton>
                </Tooltip>
              )}
            </Box>
            <FormControlLabel
              control={
                <Switch
                  checked={Boolean(value)}
                  onChange={(e) => handleParameterChange(key, e.target.checked)}
                  disabled={readOnly}
                />
              }
              label={paramSchema.description || "활성화"}
            />
          </Stack>
        );

      case "select":
        return (
          <Stack spacing={1} key={key}>
            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
              <Typography variant="subtitle2">
                {key
                  .replace(/_/g, " ")
                  .replace(/\b\w/g, (l) => l.toUpperCase())}
              </Typography>
              {paramSchema.description && (
                <Tooltip title={paramSchema.description}>
                  <IconButton size="small">
                    <Help fontSize="small" />
                  </IconButton>
                </Tooltip>
              )}
            </Box>
            <FormControl size="small" error={!!hasError}>
              <Select
                value={value || paramSchema.default || ""}
                onChange={(e) => handleParameterChange(key, e.target.value)}
                disabled={readOnly}
              >
                {paramSchema.options?.map((option) => (
                  <MenuItem key={option} value={option}>
                    {option}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Stack>
        );

      default:
        return (
          <Stack spacing={1} key={key}>
            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
              <Typography variant="subtitle2">
                {key
                  .replace(/_/g, " ")
                  .replace(/\b\w/g, (l) => l.toUpperCase())}
              </Typography>
              {paramSchema.description && (
                <Tooltip title={paramSchema.description}>
                  <IconButton size="small">
                    <Help fontSize="small" />
                  </IconButton>
                </Tooltip>
              )}
            </Box>
            <TextField
              value={value || ""}
              onChange={(e) => handleParameterChange(key, e.target.value)}
              error={!!hasError}
              helperText={hasError || paramSchema.description}
              disabled={readOnly}
              size="small"
            />
          </Stack>
        );
    }
  };

  const hasErrors = Object.values(errors).some((error) => error);

  return (
    <Card>
      <CardContent>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            mb: 2,
          }}
        >
          <Typography variant="h6">
            전략 파라미터 {isTemplate && "(템플릿)"}
          </Typography>
          {!readOnly && (
            <Stack direction="row" spacing={1}>
              <Button
                size="small"
                startIcon={<RestartAlt />}
                onClick={handleReset}
                variant="outlined"
              >
                초기화
              </Button>
              {onPreview && (
                <Button
                  size="small"
                  startIcon={<Preview />}
                  onClick={onPreview}
                  variant="outlined"
                >
                  미리보기
                </Button>
              )}
              {onSave && (
                <Button
                  size="small"
                  startIcon={<Save />}
                  onClick={onSave}
                  variant="contained"
                  disabled={hasErrors}
                >
                  저장
                </Button>
              )}
            </Stack>
          )}
        </Box>

        {hasErrors && (
          <Alert severity="error" sx={{ mb: 2 }}>
            파라미터 설정에 오류가 있습니다. 확인 후 다시 시도해주세요.
          </Alert>
        )}

        <Accordion defaultExpanded>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Typography variant="subtitle1">
              {strategyType
                .replace(/_/g, " ")
                .replace(/\b\w/g, (l) => l.toUpperCase())}{" "}
              설정
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Stack spacing={3}>
              {Object.entries(schema).map(([key, paramSchema]) =>
                renderParameterInput(key, paramSchema)
              )}
              {Object.keys(schema).length === 0 && (
                <Alert severity="info">
                  이 전략에는 설정 가능한 파라미터가 없습니다.
                </Alert>
              )}
            </Stack>
          </AccordionDetails>
        </Accordion>
      </CardContent>
    </Card>
  );
}
