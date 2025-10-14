import type { OptimizationProgress } from "@/client/types.gen";
import { Box, Card, CardContent, Typography, useTheme } from "@mui/material";
import { useMemo } from "react";
import {
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface TrialHistoryChartProps {
  progress: OptimizationProgress;
  showBestLine?: boolean;
  showTrendLine?: boolean;
  height?: number;
}

interface ChartDataPoint {
  trial_number: number;
  value: number;
  isBest: boolean;
  params: Record<string, number | string>;
}

// Custom tooltip component (outside main component)
function CustomTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: any;
}) {
  if (active && payload && payload.length > 0) {
    const data = payload[0].payload as ChartDataPoint;

    return (
      <Card sx={{ p: 1, bgcolor: "background.paper", boxShadow: 3 }}>
        <Typography variant="caption" fontWeight="bold">
          Trial #{data.trial_number}
        </Typography>
        <Typography variant="body2" color="primary">
          Value: {data.value.toFixed(4)}
        </Typography>
        {data.isBest && (
          <Typography variant="caption" color="success.main">
            ★ Best Trial
          </Typography>
        )}
        <Box sx={{ mt: 1 }}>
          <Typography variant="caption" color="text.secondary">
            Parameters:
          </Typography>
          {Object.entries(data.params).map(([key, value]) => (
            <Typography key={key} variant="caption" display="block">
              {key}: {typeof value === "number" ? value.toFixed(2) : value}
            </Typography>
          ))}
        </Box>
      </Card>
    );
  }

  return null;
}

/**
 * TrialHistoryChart Component
 *
 * Visualizes optimization trial history with:
 * - Scatter plot of all trials
 * - Best value reference line
 * - Trend line (optional)
 * - Best trial highlighting
 * - Interactive tooltips
 *
 * Uses Recharts for visualization.
 *
 * @example
 * ```tsx
 * <TrialHistoryChart
 *   progress={optimizationProgress}
 *   showBestLine
 *   showTrendLine
 *   height={400}
 * />
 * ```
 */
export function TrialHistoryChart({
  progress,
  showBestLine = true,
  showTrendLine = false,
  height = 400,
}: TrialHistoryChartProps) {
  const theme = useTheme();

  // Process trial data for chart
  const chartData = useMemo(() => {
    if (!progress?.recent_trials || progress.recent_trials.length === 0) {
      return [];
    }

    const trials = progress.recent_trials;
    const bestValue = progress.best_value;

    return trials.map((trial) => ({
      trial_number: trial.trial_number,
      value: typeof trial.value === "number" ? trial.value : 0,
      isBest:
        typeof trial.value === "number" &&
        typeof bestValue === "number" &&
        Math.abs(trial.value - bestValue) < 1e-6,
      params: trial.params,
    })) as ChartDataPoint[];
  }, [progress]);

  // Calculate cumulative best values for trend line
  const cumulativeBestData = useMemo(() => {
    if (chartData.length === 0) return [];

    const data: Array<{ trial_number: number; cumulativeBest: number }> = [];
    let currentBest = chartData[0].value;

    for (const point of chartData) {
      // Update current best based on optimization direction
      // Assuming maximize by default (can be enhanced with direction prop)
      if (point.value > currentBest) {
        currentBest = point.value;
      }

      data.push({
        trial_number: point.trial_number,
        cumulativeBest: currentBest,
      });
    }

    return data;
  }, [chartData]);

  if (chartData.length === 0) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            트라이얼 히스토리
          </Typography>
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              height: height,
            }}
          >
            <Typography variant="body2" color="text.secondary">
              트라이얼 데이터가 없습니다
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          트라이얼 히스토리
        </Typography>

        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          총 {chartData.length}개 트라이얼 | 최적 값:{" "}
          {typeof progress.best_value === "number"
            ? progress.best_value.toFixed(4)
            : progress.best_value}
        </Typography>

        <ResponsiveContainer width="100%" height={height}>
          <ScatterChart
            margin={{
              top: 20,
              right: 30,
              left: 20,
              bottom: 20,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              type="number"
              dataKey="trial_number"
              name="Trial"
              label={{
                value: "Trial Number",
                position: "insideBottom",
                offset: -10,
              }}
            />
            <YAxis
              type="number"
              dataKey="value"
              name="Value"
              label={{
                value: "Objective Value",
                angle: -90,
                position: "insideLeft",
              }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />

            {/* Best value reference line */}
            {showBestLine && typeof progress.best_value === "number" && (
              <ReferenceLine
                y={progress.best_value}
                stroke={theme.palette.success.main}
                strokeDasharray="3 3"
                label={{
                  value: "Best",
                  fill: theme.palette.success.main,
                  fontSize: 12,
                }}
              />
            )}

            {/* Scatter plot of all trials */}
            <Scatter
              name="Trials"
              data={chartData}
              fill={theme.palette.primary.main}
            >
              {chartData.map((entry) => (
                <Cell
                  key={`cell-${entry.trial_number}`}
                  fill={
                    entry.isBest
                      ? theme.palette.success.main
                      : theme.palette.primary.main
                  }
                  r={entry.isBest ? 8 : 5}
                />
              ))}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>

        {/* Trend line chart */}
        {showTrendLine && cumulativeBestData.length > 0 && (
          <Box sx={{ mt: 4 }}>
            <Typography variant="subtitle2" gutterBottom>
              누적 최적 값 추이
            </Typography>

            <ResponsiveContainer width="100%" height={200}>
              <LineChart
                data={cumulativeBestData}
                margin={{
                  top: 10,
                  right: 30,
                  left: 20,
                  bottom: 10,
                }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="trial_number"
                  label={{
                    value: "Trial Number",
                    position: "insideBottom",
                    offset: -5,
                  }}
                />
                <YAxis
                  label={{
                    value: "Cumulative Best Value",
                    angle: -90,
                    position: "insideLeft",
                  }}
                />
                <Tooltip
                  formatter={(value: number) => value.toFixed(4)}
                  labelFormatter={(label) => `Trial #${label}`}
                />
                <Legend />
                <Line
                  type="stepAfter"
                  dataKey="cumulativeBest"
                  name="Cumulative Best"
                  stroke={theme.palette.success.main}
                  strokeWidth={2}
                  dot={{ r: 3 }}
                  activeDot={{ r: 5 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
