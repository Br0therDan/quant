"use client";

import {
  BarChart as BarIcon,
  CandlestickChart as CandlestickIcon,
  ShowChart as LineIcon,
  Refresh as RefreshIcon,
} from "@mui/icons-material";
import {
  Box,
  Button,
  ButtonGroup,
  Chip,
  IconButton,
  Tooltip,
  useTheme,
} from "@mui/material";
import { DatePicker } from "@mui/x-date-pickers";
import dayjs, { type Dayjs } from "dayjs";

interface ChartControlsProps {
  startDate: Dayjs | null;
  endDate: Dayjs | null;
  onStartDateChange: (date: Dayjs | null) => void;
  onEndDateChange: (date: Dayjs | null) => void;
  interval: string;
  onIntervalChange: (interval: string) => void;
  onRefresh: () => void;
  isLoading?: boolean;
  chartType?: string;
  onChartTypeChange?: (type: string) => void;
}

const TIME_PERIODS = [
  { label: "1D", value: "1d" },
  { label: "5D", value: "5d" },
  { label: "1M", value: "1m" },
  { label: "3M", value: "3m" },
  { label: "6M", value: "6m" },
  { label: "1Y", value: "1y" },
  { label: "5Y", value: "5y" },
];

const CHART_TYPES = [
  { icon: CandlestickIcon, label: "캔들스틱", value: "candlestick" },
  { icon: LineIcon, label: "라인", value: "line" },
  { icon: BarIcon, label: "바", value: "bar" },
];

export default function ChartControls({
  startDate,
  endDate,
  onStartDateChange,
  onEndDateChange,
  interval,
  onIntervalChange,
  onRefresh,
  isLoading = false,
  chartType = "candlestick",
  onChartTypeChange,
}: ChartControlsProps) {
  const theme = useTheme();

  const handlePeriodChange = (period: string) => {
    const end = dayjs();
    let start: Dayjs;

    switch (period) {
      case "1d":
        start = end.subtract(1, "day");
        break;
      case "5d":
        start = end.subtract(5, "day");
        break;
      case "1m":
        start = end.subtract(1, "month");
        break;
      case "3m":
        start = end.subtract(3, "month");
        break;
      case "6m":
        start = end.subtract(6, "month");
        break;
      case "1y":
        start = end.subtract(1, "year");
        break;
      case "5y":
        start = end.subtract(5, "year");
        break;
      default:
        start = end.subtract(1, "month");
    }

    onStartDateChange(start);
    onEndDateChange(end);
    onIntervalChange(period);
  };

  const currentPeriod =
    TIME_PERIODS.find((p) => p.value === interval)?.value || "1m";

  return (
    <Box
      sx={{
        p: 2,
        borderTop: 1,
        borderColor: "divider",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        flexWrap: "wrap",
        gap: 2,
      }}
    >
      {/* 왼쪽: 기간 선택 */}
      <Box display="flex" alignItems="center" gap={2}>
        <ButtonGroup size="small" variant="outlined">
          {TIME_PERIODS.map((period) => (
            <Button
              key={period.value}
              variant={
                currentPeriod === period.value ? "contained" : "outlined"
              }
              onClick={() => handlePeriodChange(period.value)}
              sx={{ minWidth: 40 }}
            >
              {period.label}
            </Button>
          ))}
        </ButtonGroup>

        {/* 커스텀 날짜 선택 */}
        <Box display="flex" alignItems="center" gap={1}>
          <DatePicker
            label="시작일"
            value={startDate}
            onChange={(value) => onStartDateChange(value ? dayjs(value) : null)}
            slotProps={{
              textField: {
                size: "small",
                sx: { width: 140 },
              },
            }}
          />
          <DatePicker
            label="종료일"
            value={endDate}
            onChange={(value) => onEndDateChange(value ? dayjs(value) : null)}
            slotProps={{
              textField: {
                size: "small",
                sx: { width: 140 },
              },
            }}
          />
        </Box>
      </Box>

      {/* 오른쪽: 차트 타입 및 새로고침 */}
      <Box display="flex" alignItems="center" gap={2}>
        {/* 차트 타입 선택 */}
        {onChartTypeChange && (
          <ButtonGroup size="small" variant="outlined">
            {CHART_TYPES.map((type) => {
              const IconComponent = type.icon;
              return (
                <Tooltip key={type.value} title={type.label}>
                  <Button
                    variant={
                      chartType === type.value ? "contained" : "outlined"
                    }
                    onClick={() => onChartTypeChange(type.value)}
                    sx={{ minWidth: 40 }}
                  >
                    <IconComponent sx={{ fontSize: 18 }} />
                  </Button>
                </Tooltip>
              );
            })}
          </ButtonGroup>
        )}

        {/* 새로고침 버튼 */}
        <Tooltip title="새로고침">
          <IconButton
            onClick={onRefresh}
            disabled={isLoading}
            size="small"
            sx={{
              border: 1,
              borderColor: "divider",
              "&:hover": {
                borderColor: theme.palette.primary.main,
              },
            }}
          >
            <RefreshIcon sx={{ fontSize: 18 }} />
          </IconButton>
        </Tooltip>

        {/* 로딩 상태 표시 */}
        {isLoading && (
          <Chip
            label="로딩 중..."
            size="small"
            color="primary"
            variant="outlined"
          />
        )}
      </Box>
    </Box>
  );
}
