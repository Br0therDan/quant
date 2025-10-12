"use client";

import {
  CalendarMonth as CalendarIcon,
  CandlestickChart as CandlestickIcon,
  ShowChart as LineIcon,
} from "@mui/icons-material";
import {
  Box,
  Button,
  ButtonGroup,
  Chip,
  FormControlLabel,
  Switch,
  Tooltip,
} from "@mui/material";
import { DatePicker } from "@mui/x-date-pickers";
import dayjs, { type Dayjs } from "dayjs";
import React from "react";

interface LightWeightChartControlsProps {
  startDate: Dayjs | null;
  endDate: Dayjs | null;
  onStartDateChange: (date: Dayjs | null) => void;
  onEndDateChange: (date: Dayjs | null) => void;
  interval: string;
  onIntervalChange: (interval: string) => void;
  isLoading?: boolean;
  chartType?: string;
  onChartTypeChange?: (type: string) => void;
  adjusted?: boolean;
  onAdjustedChange?: (adjusted: boolean) => void;
}

// 레인지(기간) 옵션
const RANGES = [
  { label: "1D", value: "1d", days: 1 },
  { label: "5D", value: "5d", days: 5 },
  { label: "1M", value: "1m", days: 30 },
  { label: "3M", value: "3m", days: 90 },
  { label: "6M", value: "6m", days: 180 },
  { label: "YTD", value: "ytd", days: null }, // Year to date
  { label: "1Y", value: "1y", days: 365 },
  { label: "5Y", value: "5y", days: 1825 },
  { label: "전체", value: "all", days: null },
];

// 인터벌(봉 종류) 옵션
const INTERVALS = {
  intraday: [
    { label: "1분", value: "1min" },
    { label: "5분", value: "5min" },
    { label: "15분", value: "15min" },
    { label: "30분", value: "30min" },
    { label: "60분", value: "60min" },
  ],
  daily: [
    { label: "일봉", value: "daily" },
    { label: "주봉", value: "weekly" },
    { label: "월봉", value: "monthly" },
  ],
};

const CHART_TYPES = [
  { icon: CandlestickIcon, label: "캔들스틱", value: "candlestick" },
  { icon: LineIcon, label: "라인", value: "line" },
];

export default function LightWeightChartControls({
  startDate,
  endDate,
  onStartDateChange,
  onEndDateChange,
  interval,
  onIntervalChange,
  isLoading = false,
  chartType = "candlestick",
  onChartTypeChange,
  adjusted = true,
  onAdjustedChange,
}: LightWeightChartControlsProps) {
  const [selectedRange, setSelectedRange] = React.useState("1m");
  const [showCustomDate, setShowCustomDate] = React.useState(false);

  // 레인지 변경 핸들러
  const handleRangeChange = (rangeValue: string) => {
    const range = RANGES.find((r) => r.value === rangeValue);
    if (!range) return;

    const end = dayjs();
    let start: Dayjs;

    if (rangeValue === "ytd") {
      // Year to date
      start = dayjs().startOf("year");
    } else if (rangeValue === "all") {
      // 전체: 20년 전부터
      start = end.subtract(20, "year");
    } else if (range.days) {
      start = end.subtract(range.days, "day");
    } else {
      start = end.subtract(30, "day");
    }

    setSelectedRange(rangeValue);
    setShowCustomDate(false);
    onStartDateChange(start);
    onEndDateChange(end);

    // 레인지에 따라 적절한 인터벌 자동 설정
    if (range.days && range.days <= 5) {
      // 5일 이하: 분봉 (현재 분봉이 아니면 기본 5분으로)
      if (!["1min", "5min", "15min", "30min", "60min"].includes(interval)) {
        onIntervalChange("5min");
      }
    } else {
      // 그 외: 일봉/주봉/월봉 (현재 일반 봉이 아니면 기본 일봉으로)
      if (!["daily", "weekly", "monthly"].includes(interval)) {
        onIntervalChange("daily");
      }
    }
  };

  // 커스텀 날짜 표시 토글
  const handleCustomDateToggle = () => {
    setShowCustomDate(!showCustomDate);
    if (!showCustomDate) {
      setSelectedRange("custom");
    }
  };

  // 현재 인터벌이 분봉인지 확인
  const isIntradayInterval = [
    "1min",
    "5min",
    "15min",
    "30min",
    "60min",
  ].includes(interval);

  // 사용 가능한 인터벌 목록
  const availableIntervals = isIntradayInterval
    ? INTERVALS.intraday
    : INTERVALS.daily;

  return (
    <Box
      sx={{
        p: 2,
        borderTop: 1,
        borderColor: "divider",
        display: "flex",
        flexDirection: "column",
        gap: 2,
      }}
    >
      {/* 첫 번째 줄: 레인지 선택 */}
      <Box display="flex" alignItems="center" gap={1} flexWrap="wrap">
        <ButtonGroup size="small" variant="outlined">
          {RANGES.map((range) => (
            <Button
              key={range.value}
              variant={selectedRange === range.value ? "contained" : "outlined"}
              onClick={() => handleRangeChange(range.value)}
              sx={{ minWidth: 40, fontSize: "0.75rem" }}
            >
              {range.label}
            </Button>
          ))}
        </ButtonGroup>

        {/* 커스텀 날짜 아이콘 버튼 */}
        <Tooltip title="커스텀 기간 설정">
          <Button
            size="small"
            variant={showCustomDate ? "contained" : "outlined"}
            onClick={handleCustomDateToggle}
            sx={{ minWidth: 40 }}
          >
            <CalendarIcon sx={{ fontSize: 18 }} />
          </Button>
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

      {/* 커스텀 날짜 선택 (토글) */}
      {showCustomDate && (
        <Box display="flex" alignItems="center" gap={1}>
          <DatePicker
            label="시작일"
            value={startDate}
            onChange={(value) => onStartDateChange(value ? dayjs(value) : null)}
            slotProps={{
              textField: {
                size: "small",
                sx: { width: 150 },
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
                sx: { width: 150 },
              },
            }}
          />
        </Box>
      )}

      {/* 두 번째 줄: 인터벌 + 차트 타입 + Adjusted Toggle */}
      <Box
        display="flex"
        alignItems="center"
        justifyContent="space-between"
        flexWrap="wrap"
        gap={2}
      >
        {/* 왼쪽: 인터벌 선택 */}
        <ButtonGroup size="small" variant="outlined">
          {availableIntervals.map((intv) => (
            <Button
              key={intv.value}
              variant={interval === intv.value ? "contained" : "outlined"}
              onClick={() => onIntervalChange(intv.value)}
              sx={{ minWidth: 50 }}
            >
              {intv.label}
            </Button>
          ))}
        </ButtonGroup>

        {/* 오른쪽: Adjusted Toggle + 차트 타입 선택 */}
        <Box display="flex" alignItems="center" gap={2}>
          {/* Adjusted Price Toggle */}
          {onAdjustedChange && (
            <FormControlLabel
              control={
                <Switch
                  checked={adjusted}
                  onChange={(e) => onAdjustedChange(e.target.checked)}
                  size="small"
                />
              }
              label="Adjusted"
              sx={{
                m: 0,
                "& .MuiFormControlLabel-label": {
                  fontSize: "0.875rem",
                  fontWeight: adjusted ? 600 : 400,
                },
              }}
            />
          )}

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
        </Box>
      </Box>
    </Box>
  );
}
