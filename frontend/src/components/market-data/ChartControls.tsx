"use client";

import {
  CandlestickChart as CandlestickIcon,
  ShowChart as LineIcon,
} from "@mui/icons-material";
import { Box, Button, ButtonGroup, Chip, Tooltip } from "@mui/material";
import { DatePicker } from "@mui/x-date-pickers";
import dayjs, { type Dayjs } from "dayjs";

interface ChartControlsProps {
  startDate: Dayjs | null;
  endDate: Dayjs | null;
  onStartDateChange: (date: Dayjs | null) => void;
  onEndDateChange: (date: Dayjs | null) => void;
  interval: string;
  onIntervalChange: (interval: string) => void;
  intradayInterval?: string;
  onIntradayIntervalChange?: (interval: string) => void;
  isLoading?: boolean;
  chartType?: string;
  onChartTypeChange?: (type: string) => void;
}

const TIME_PERIODS = [
  { label: "Intraday", value: "intraday" },
  { label: "1D", value: "1d" },
  { label: "1W", value: "1w" },
  { label: "1M", value: "1m" },
];

const INTRADAY_INTERVALS = [
  { label: "1분", value: "1min" },
  { label: "5분", value: "5min" },
  { label: "15분", value: "15min" },
  { label: "30분", value: "30min" },
  { label: "60분", value: "60min" },
];

const CHART_TYPES = [
  { icon: CandlestickIcon, label: "캔들스틱", value: "candlestick" },
  { icon: LineIcon, label: "라인", value: "line" },
];

export default function ChartControls({
  startDate,
  endDate,
  onStartDateChange,
  onEndDateChange,
  interval,
  onIntervalChange,
  intradayInterval = "5min",
  onIntradayIntervalChange,
  isLoading = false,
  chartType = "candlestick",
  onChartTypeChange,
}: ChartControlsProps) {
  const handlePeriodChange = (period: string) => {
    const end = dayjs();
    let start: Dayjs;

    switch (period) {
      case "intraday":
        start = end.subtract(1, "day");
        break;
      case "1d":
        start = end.subtract(1, "day");
        break;
      case "1w":
        start = end.subtract(1, "week");
        break;
      case "1m":
        start = end.subtract(1, "month");
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

  const isIntraday = interval === "intraday";

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
      <Box display="flex" alignItems="center" gap={2} flexWrap="wrap">
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

        {/* 인트라데이 인터벌 선택 */}
        {isIntraday && onIntradayIntervalChange && (
          <ButtonGroup size="small" variant="outlined">
            {INTRADAY_INTERVALS.map((intInterval) => (
              <Button
                key={intInterval.value}
                variant={
                  intradayInterval === intInterval.value
                    ? "contained"
                    : "outlined"
                }
                onClick={() => onIntradayIntervalChange(intInterval.value)}
                sx={{ minWidth: 45 }}
              >
                {intInterval.label}
              </Button>
            ))}
          </ButtonGroup>
        )}

        {/* 커스텀 날짜 선택 - 인트라데이가 아닐 때만 표시 */}
        {!isIntraday && (
          <Box display="flex" alignItems="center" gap={1}>
            <DatePicker
              label="시작일"
              value={startDate}
              onChange={(value) =>
                onStartDateChange(value ? dayjs(value) : null)
              }
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
        )}
      </Box>

      {/* 오른쪽: 차트 타입 */}
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
