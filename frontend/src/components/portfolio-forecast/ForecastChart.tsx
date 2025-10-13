/**
 * ForecastChart Component
 *
 * 확률적 포트폴리오 가치 예측을 시각화하는 차트
 *
 * Features:
 * - Area Chart (5th, 50th, 95th percentile bands)
 * - Gradient fill (신뢰 구간)
 * - Responsive layout
 * - Custom tooltip (시나리오별 정보)
 *
 * @author GitHub Copilot
 * @created 2025-01-16
 */

"use client";

import type { ForecastPercentileBand } from "@/client";
import { usePortfolioForecast } from "@/hooks/usePortfolioForecast";
import {
  TrendingDown as TrendingDownIcon,
  TrendingFlat as TrendingFlatIcon,
  TrendingUp as TrendingUpIcon,
} from "@mui/icons-material";
import {
  Alert,
  Box,
  Card,
  CardContent,
  CardHeader,
  Chip,
  Skeleton,
  Stack,
  Typography,
} from "@mui/material";
import {
  Area,
  AreaChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

// ============================================================================
// Types
// ============================================================================

export interface ForecastChartProps {
  /** 예측 기간 (일, 7-120일) */
  horizonDays?: number;
  /** 차트 높이 (px) */
  chartHeight?: number;
  /** 자동 조회 활성화 */
  enabled?: boolean;
}

/**
 * 차트 데이터 포인트
 */
interface ChartDataPoint {
  day: number;
  dayLabel: string;
  percentile5: number;
  percentile50: number;
  percentile95: number;
  currentValue: number;
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * 차트 데이터 생성 (선형 보간)
 *
 * @param horizonDays - 예측 기간
 * @param currentValue - 현재 포트폴리오 가치
 * @param bands - 백분위 밴드
 * @returns 차트 데이터 배열
 */
function generateChartData(
  horizonDays: number,
  currentValue: number,
  bands: ForecastPercentileBand[]
): ChartDataPoint[] {
  const dataPoints: ChartDataPoint[] = [];

  // 현재 시점 (Day 0)
  dataPoints.push({
    day: 0,
    dayLabel: "Today",
    percentile5: currentValue,
    percentile50: currentValue,
    percentile95: currentValue,
    currentValue,
  });

  // 예측 시점 (Day N)
  const band5 = bands.find((b) => b.percentile === 5);
  const band50 = bands.find((b) => b.percentile === 50);
  const band95 = bands.find((b) => b.percentile === 95);

  // 중간 포인트 생성 (선형 보간)
  const steps = Math.min(10, horizonDays); // 최대 10개 포인트
  for (let i = 1; i <= steps; i++) {
    const day = Math.round((horizonDays / steps) * i);
    const ratio = i / steps;

    dataPoints.push({
      day,
      dayLabel: `+${day}d`,
      percentile5:
        currentValue +
        (band5 ? (band5.projected_value - currentValue) * ratio : 0),
      percentile50:
        currentValue +
        (band50 ? (band50.projected_value - currentValue) * ratio : 0),
      percentile95:
        currentValue +
        (band95 ? (band95.projected_value - currentValue) * ratio : 0),
      currentValue,
    });
  }

  return dataPoints;
}

/**
 * 통화 포맷팅 (백만/천 단위)
 */
function formatCurrency(value: number): string {
  if (value >= 1_000_000) {
    return `$${(value / 1_000_000).toFixed(2)}M`;
  }
  if (value >= 1_000) {
    return `$${(value / 1_000).toFixed(1)}K`;
  }
  return `$${value.toFixed(0)}`;
}

// ============================================================================
// Custom Tooltip
// ============================================================================

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{
    payload: ChartDataPoint;
  }>;
}

function CustomTooltip({ active, payload }: CustomTooltipProps) {
  if (!active || !payload || payload.length === 0) {
    return null;
  }

  const data = payload[0].payload;

  return (
    <Card sx={{ minWidth: 200 }}>
      <CardContent>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          {data.dayLabel}
        </Typography>
        <Stack spacing={0.5}>
          <Box sx={{ display: "flex", justifyContent: "space-between" }}>
            <Typography variant="caption" color="success.main">
              강세 (95th):
            </Typography>
            <Typography variant="caption" fontWeight="bold">
              {formatCurrency(data.percentile95)}
            </Typography>
          </Box>
          <Box sx={{ display: "flex", justifyContent: "space-between" }}>
            <Typography variant="caption" color="info.main">
              기본 (50th):
            </Typography>
            <Typography variant="caption" fontWeight="bold">
              {formatCurrency(data.percentile50)}
            </Typography>
          </Box>
          <Box sx={{ display: "flex", justifyContent: "space-between" }}>
            <Typography variant="caption" color="error.main">
              약세 (5th):
            </Typography>
            <Typography variant="caption" fontWeight="bold">
              {formatCurrency(data.percentile5)}
            </Typography>
          </Box>
        </Stack>
      </CardContent>
    </Card>
  );
}

// ============================================================================
// Main Component
// ============================================================================

/**
 * ForecastChart Component
 *
 * @example
 * ```tsx
 * <ForecastChart horizonDays={30} chartHeight={400} />
 * ```
 */
export default function ForecastChart({
  horizonDays = 30,
  chartHeight = 400,
  enabled = true,
}: ForecastChartProps) {
  const { forecastData, isLoading, isError, error } = usePortfolioForecast({
    horizonDays,
    enabled,
  });

  // ============================================================================
  // Render: Loading State
  // ============================================================================

  if (isLoading) {
    return (
      <Card>
        <CardHeader title="포트폴리오 예측 차트" />
        <CardContent>
          <Skeleton variant="rectangular" height={chartHeight} />
        </CardContent>
      </Card>
    );
  }

  // ============================================================================
  // Render: Error State
  // ============================================================================

  if (isError) {
    return (
      <Card>
        <CardHeader title="포트폴리오 예측 차트" />
        <CardContent>
          <Alert severity="error">
            {error?.message ||
              "포트폴리오 예측 데이터를 불러오는데 실패했습니다."}
          </Alert>
        </CardContent>
      </Card>
    );
  }

  // ============================================================================
  // Render: No Data State
  // ============================================================================

  if (!forecastData) {
    return (
      <Card>
        <CardHeader title="포트폴리오 예측 차트" />
        <CardContent>
          <Alert severity="info">포트폴리오 예측 데이터가 없습니다.</Alert>
        </CardContent>
      </Card>
    );
  }

  // ============================================================================
  // Data Preparation
  // ============================================================================

  const {
    last_portfolio_value,
    expected_return_pct,
    expected_volatility_pct,
    percentile_bands,
    horizon_days,
  } = forecastData;

  const chartData = generateChartData(
    horizon_days,
    last_portfolio_value,
    percentile_bands
  );

  // 추세 아이콘
  const TrendIcon =
    expected_return_pct > 1
      ? TrendingUpIcon
      : expected_return_pct < -1
      ? TrendingDownIcon
      : TrendingFlatIcon;

  const trendColor =
    expected_return_pct > 1
      ? "success"
      : expected_return_pct < -1
      ? "error"
      : "default";

  // ============================================================================
  // Render: Chart
  // ============================================================================

  return (
    <Card>
      <CardHeader
        title="포트폴리오 예측 차트"
        subheader={`${horizon_days}일 예측 (확률적 시나리오)`}
        action={
          <Stack direction="row" spacing={1}>
            <Chip
              icon={<TrendIcon />}
              label={`${
                expected_return_pct >= 0 ? "+" : ""
              }${expected_return_pct.toFixed(2)}%`}
              color={trendColor}
              size="small"
            />
            <Chip
              label={`변동성: ${expected_volatility_pct.toFixed(2)}%`}
              variant="outlined"
              size="small"
            />
          </Stack>
        }
      />
      <CardContent>
        <ResponsiveContainer width="100%" height={chartHeight}>
          <AreaChart
            data={chartData}
            margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
          >
            {/* Gradient Definitions */}
            <defs>
              <linearGradient id="colorBullish" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#4caf50" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#4caf50" stopOpacity={0.1} />
              </linearGradient>
              <linearGradient id="colorBase" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#2196f3" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#2196f3" stopOpacity={0.1} />
              </linearGradient>
              <linearGradient id="colorBearish" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#f44336" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#f44336" stopOpacity={0.1} />
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="dayLabel" tick={{ fontSize: 12 }} />
            <YAxis tickFormatter={formatCurrency} tick={{ fontSize: 12 }} />
            <Tooltip content={<CustomTooltip />} />
            <Legend />

            {/* Area: 95th Percentile (Bullish) */}
            <Area
              type="monotone"
              dataKey="percentile95"
              stroke="#4caf50"
              strokeWidth={2}
              fill="url(#colorBullish)"
              name="강세 시나리오 (95th)"
            />

            {/* Area: 50th Percentile (Base) */}
            <Area
              type="monotone"
              dataKey="percentile50"
              stroke="#2196f3"
              strokeWidth={3}
              fill="url(#colorBase)"
              name="기본 시나리오 (50th)"
            />

            {/* Area: 5th Percentile (Bearish) */}
            <Area
              type="monotone"
              dataKey="percentile5"
              stroke="#f44336"
              strokeWidth={2}
              fill="url(#colorBearish)"
              name="약세 시나리오 (5th)"
            />

            {/* Reference Line: Current Value */}
            <Area
              type="monotone"
              dataKey="currentValue"
              stroke="#9e9e9e"
              strokeWidth={1}
              strokeDasharray="5 5"
              fill="none"
              name="현재 가치"
            />
          </AreaChart>
        </ResponsiveContainer>

        {/* Chart Description */}
        <Box sx={{ mt: 2 }}>
          <Typography variant="caption" color="text.secondary">
            * 차트는 확률적 예측 모델을 기반으로 한 시뮬레이션이며, 실제 결과와
            다를 수 있습니다.
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
}
