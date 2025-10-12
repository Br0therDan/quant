"use client";

import AddIcon from "@mui/icons-material/Add";
import CloseIcon from "@mui/icons-material/Close";
import {
  Box,
  Button,
  ButtonGroup,
  Chip,
  Dialog,
  DialogContent,
  DialogTitle,
  FormControl,
  IconButton,
  MenuItem,
  Select,
  Stack,
  TextField,
  Typography,
  useTheme,
} from "@mui/material";
import React from "react";
import type { ChartType, IndicatorConfig } from "./ReactFinancialChart";

interface ChartHeaderProps {
  symbol: string;
  interval: string;
  onIntervalChange: (interval: string) => void;
  chartType: ChartType["type"];
  onChartTypeChange: (type: ChartType["type"]) => void;
  indicators: IndicatorConfig;
  onIndicatorsChange: (indicators: IndicatorConfig) => void;
}

// 인터벌 옵션
const INTERVAL_OPTIONS = [
  // 분봉
  { label: "1분", value: "1min", group: "분봉" },
  { label: "5분", value: "5min", group: "분봉" },
  { label: "15분", value: "15min", group: "분봉" },
  { label: "30분", value: "30min", group: "분봉" },
  { label: "1시간", value: "60min", group: "분봉" },
  // 일/주/월봉
  { label: "일봉", value: "daily", group: "기간" },
  { label: "주봉", value: "weekly", group: "기간" },
  { label: "월봉", value: "monthly", group: "기간" },
];

// 차트 타입 옵션
const CHART_TYPE_OPTIONS: Array<{
  label: string;
  value: ChartType["type"];
}> = [
  { label: "캔들", value: "candlestick" },
  { label: "바", value: "ohlc" },
  { label: "라인", value: "line" },
  { label: "영역", value: "area" },
  { label: "하이켄아시", value: "heikinAshi" },
  { label: "렌코", value: "renko" },
  { label: "카기", value: "kagi" },
  { label: "P&F", value: "pointAndFigure" },
];

// 기본 MA 기간
const DEFAULT_MA_PERIODS = [5, 10, 20, 50, 100, 200];

export default function ChartHeader({
  symbol,
  interval,
  onIntervalChange,
  chartType,
  onChartTypeChange,
  indicators,
  onIndicatorsChange,
}: ChartHeaderProps) {
  const theme = useTheme();
  const [indicatorDialogOpen, setIndicatorDialogOpen] = React.useState(false);

  // 활성화된 지표 개수 계산
  const activeIndicatorCount = React.useMemo(() => {
    let count = 0;
    if (indicators.ema?.length) count += indicators.ema.length;
    if (indicators.sma?.length) count += indicators.sma.length;
    if (indicators.wma?.length) count += indicators.wma.length;
    if (indicators.tma?.length) count += indicators.tma.length;
    if (indicators.bollingerBand) count++;
    if (indicators.atr) count++;
    if (indicators.sar) count++;
    if (indicators.macd) count++;
    if (indicators.rsi) count++;
    if (indicators.stochastic) count++;
    if (indicators.forceIndex) count++;
    if (indicators.elderRay) count++;
    if (indicators.elderImpulse) count++;
    return count;
  }, [indicators]);

  // MA 추가/제거
  const handleAddMA = (type: "ema" | "sma" | "wma" | "tma", period: number) => {
    const current = indicators[type] || [];
    if (!current.includes(period)) {
      onIndicatorsChange({
        ...indicators,
        [type]: [...current, period].sort((a, b) => a - b),
      });
    }
  };

  const handleRemoveMA = (
    type: "ema" | "sma" | "wma" | "tma",
    period: number
  ) => {
    const current = indicators[type] || [];
    onIndicatorsChange({
      ...indicators,
      [type]: current.filter((p) => p !== period),
    });
  };

  // 지표 토글
  const handleToggleIndicator = (key: keyof IndicatorConfig) => {
    if (key === "stochastic") {
      onIndicatorsChange({
        ...indicators,
        stochastic: indicators.stochastic ? null : "fast",
      });
    } else {
      onIndicatorsChange({
        ...indicators,
        [key]: !indicators[key],
      });
    }
  };

  return (
    <>
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          gap: 1,
          px: 2,
          py: 1,
          borderBottom: `1px solid ${theme.palette.divider}`,
        }}
      >
        {/* 심볼 */}
        <Typography variant="h6" fontWeight="bold" sx={{ mr: 2 }}>
          {symbol}
        </Typography>

        {/* 인터벌 드롭다운 */}
        <FormControl size="small" sx={{ minWidth: 100 }}>
          <Select
            value={interval}
            onChange={(e) => onIntervalChange(e.target.value)}
            sx={{
              fontSize: "0.875rem",
              "& .MuiOutlinedInput-notchedOutline": {
                border: "none",
              },
              "&:hover .MuiOutlinedInput-notchedOutline": {
                border: "none",
              },
              "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
                border: "none",
              },
            }}
          >
            {INTERVAL_OPTIONS.map((option) => (
              <MenuItem key={option.value} value={option.value}>
                {option.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {/* 차트 타입 드롭다운 */}
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <Select
            value={chartType}
            onChange={(e) =>
              onChartTypeChange(e.target.value as ChartType["type"])
            }
            sx={{
              fontSize: "0.875rem",
              "& .MuiOutlinedInput-notchedOutline": {
                border: "none",
              },
              "&:hover .MuiOutlinedInput-notchedOutline": {
                border: "none",
              },
              "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
                border: "none",
              },
            }}
          >
            {CHART_TYPE_OPTIONS.map((option) => (
              <MenuItem key={option.value} value={option.value}>
                {option.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {/* 지표 버튼 */}
        <Button
          variant="outlined"
          size="small"
          onClick={() => setIndicatorDialogOpen(true)}
          sx={{
            fontSize: "0.875rem",
            textTransform: "none",
            borderColor: theme.palette.divider,
            color: theme.palette.text.primary,
          }}
        >
          지표 {activeIndicatorCount > 0 && `(${activeIndicatorCount})`}
        </Button>
      </Box>

      {/* 지표 다이얼로그 */}
      <Dialog
        open={indicatorDialogOpen}
        onClose={() => setIndicatorDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box
            display="flex"
            justifyContent="space-between"
            alignItems="center"
          >
            <Typography variant="h6">지표 설정</Typography>
            <IconButton
              onClick={() => setIndicatorDialogOpen(false)}
              size="small"
            >
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent dividers>
          <Stack spacing={3}>
            {/* 이동평균선 */}
            <Box>
              <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                이동평균선
              </Typography>
              <Stack spacing={2}>
                <MAControl
                  label="EMA"
                  type="ema"
                  periods={indicators.ema || []}
                  onAdd={handleAddMA}
                  onRemove={handleRemoveMA}
                />
                <MAControl
                  label="SMA"
                  type="sma"
                  periods={indicators.sma || []}
                  onAdd={handleAddMA}
                  onRemove={handleRemoveMA}
                />
                <MAControl
                  label="WMA"
                  type="wma"
                  periods={indicators.wma || []}
                  onAdd={handleAddMA}
                  onRemove={handleRemoveMA}
                />
                <MAControl
                  label="TMA"
                  type="tma"
                  periods={indicators.tma || []}
                  onAdd={handleAddMA}
                  onRemove={handleRemoveMA}
                />
              </Stack>
            </Box>

            {/* 추세 지표 */}
            <Box>
              <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                추세 지표
              </Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                <Chip
                  label="Bollinger Bands"
                  onClick={() => handleToggleIndicator("bollingerBand")}
                  color={indicators.bollingerBand ? "primary" : "default"}
                  variant={indicators.bollingerBand ? "filled" : "outlined"}
                />
                <Chip
                  label="SAR"
                  onClick={() => handleToggleIndicator("sar")}
                  color={indicators.sar ? "primary" : "default"}
                  variant={indicators.sar ? "filled" : "outlined"}
                />
                <Chip
                  label="MACD"
                  onClick={() => handleToggleIndicator("macd")}
                  color={indicators.macd ? "primary" : "default"}
                  variant={indicators.macd ? "filled" : "outlined"}
                />
              </Stack>
            </Box>

            {/* 모멘텀 지표 */}
            <Box>
              <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                모멘텀 지표
              </Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                <Chip
                  label="RSI"
                  onClick={() => handleToggleIndicator("rsi")}
                  color={indicators.rsi ? "primary" : "default"}
                  variant={indicators.rsi ? "filled" : "outlined"}
                />
                <Chip
                  label="Stochastic"
                  onClick={() => handleToggleIndicator("stochastic")}
                  color={indicators.stochastic ? "primary" : "default"}
                  variant={indicators.stochastic ? "filled" : "outlined"}
                />
                <Chip
                  label="Force Index"
                  onClick={() => handleToggleIndicator("forceIndex")}
                  color={indicators.forceIndex ? "primary" : "default"}
                  variant={indicators.forceIndex ? "filled" : "outlined"}
                />
              </Stack>
            </Box>

            {/* 변동성 지표 */}
            <Box>
              <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                변동성 지표
              </Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                <Chip
                  label="ATR"
                  onClick={() => handleToggleIndicator("atr")}
                  color={indicators.atr ? "primary" : "default"}
                  variant={indicators.atr ? "filled" : "outlined"}
                />
              </Stack>
            </Box>

            {/* Elder 지표 */}
            <Box>
              <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                Elder 지표
              </Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                <Chip
                  label="Elder Ray"
                  onClick={() => handleToggleIndicator("elderRay")}
                  color={indicators.elderRay ? "primary" : "default"}
                  variant={indicators.elderRay ? "filled" : "outlined"}
                />
                <Chip
                  label="Elder Impulse"
                  onClick={() => handleToggleIndicator("elderImpulse")}
                  color={indicators.elderImpulse ? "primary" : "default"}
                  variant={indicators.elderImpulse ? "filled" : "outlined"}
                />
              </Stack>
            </Box>
          </Stack>
        </DialogContent>
      </Dialog>
    </>
  );
}

// MA 컨트롤 서브 컴포넌트
interface MAControlProps {
  label: string;
  type: "ema" | "sma" | "wma" | "tma";
  periods: number[];
  onAdd: (type: "ema" | "sma" | "wma" | "tma", period: number) => void;
  onRemove: (type: "ema" | "sma" | "wma" | "tma", period: number) => void;
}

function MAControl({ label, type, periods, onAdd, onRemove }: MAControlProps) {
  const [customPeriod, setCustomPeriod] = React.useState("");

  const handleAddCustom = () => {
    const period = parseInt(customPeriod, 10);
    if (!Number.isNaN(period) && period > 0) {
      onAdd(type, period);
      setCustomPeriod("");
    }
  };

  return (
    <Box>
      <Typography variant="body2" color="text.secondary" gutterBottom>
        {label}
      </Typography>
      <Stack
        direction="row"
        spacing={1}
        alignItems="center"
        flexWrap="wrap"
        useFlexGap
      >
        {/* 기본 기간 버튼 */}
        <ButtonGroup size="small" variant="outlined">
          {DEFAULT_MA_PERIODS.map((period) => (
            <Button
              key={period}
              onClick={() =>
                periods.includes(period)
                  ? onRemove(type, period)
                  : onAdd(type, period)
              }
              variant={periods.includes(period) ? "contained" : "outlined"}
            >
              {period}
            </Button>
          ))}
        </ButtonGroup>

        {/* 커스텀 입력 */}
        <TextField
          size="small"
          placeholder="커스텀"
          value={customPeriod}
          onChange={(e) => setCustomPeriod(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              handleAddCustom();
            }
          }}
          sx={{ width: 80 }}
          type="number"
          InputProps={{
            endAdornment: (
              <IconButton size="small" onClick={handleAddCustom}>
                <AddIcon fontSize="small" />
              </IconButton>
            ),
          }}
        />

        {/* 활성화된 커스텀 기간 */}
        {periods
          .filter((p) => !DEFAULT_MA_PERIODS.includes(p))
          .map((period) => (
            <Chip
              key={period}
              label={period}
              onDelete={() => onRemove(type, period)}
              size="small"
              color="primary"
            />
          ))}
      </Stack>
    </Box>
  );
}
