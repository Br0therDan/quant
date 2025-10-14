import type { StrategyComparisonResponse } from "@/client/types.gen";
import {
  Box,
  Card,
  CardContent,
  Chip,
  Typography,
  useTheme,
} from "@mui/material";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface StrategyComparisonChartProps {
  comparison: StrategyComparisonResponse;
  height?: number;
  metric?: "return" | "sharpe" | "winRate";
}

interface ChartDataPoint {
  strategy: string;
  return: number;
  sharpe: number;
  winRate: number;
  symbol: string;
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
          {data.strategy}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {data.symbol}
        </Typography>
        <Box sx={{ mt: 1 }}>
          <Typography variant="body2" color="success.main">
            수익률: {data.return.toFixed(2)}%
          </Typography>
          <Typography variant="body2" color="primary">
            Sharpe: {data.sharpe.toFixed(2)}
          </Typography>
          <Typography variant="body2">
            승률: {data.winRate.toFixed(1)}%
          </Typography>
        </Box>
      </Card>
    );
  }

  return null;
}

/**
 * StrategyComparisonChart Component
 *
 * Visualizes strategy performance comparison with:
 * - Return comparison (Bar Chart)
 * - Sharpe Ratio comparison
 * - Win Rate comparison
 * - Sortable metrics
 *
 * Uses Recharts for visualization.
 *
 * @example
 * ```tsx
 * <StrategyComparisonChart
 *   comparison={strategyComparison}
 *   height={400}
 *   metric="return"
 * />
 * ```
 */
export function StrategyComparisonChart({
  comparison,
  height = 400,
  metric = "return",
}: StrategyComparisonChartProps) {
  const theme = useTheme();

  // Process comparison data for chart
  const chartData: ChartDataPoint[] =
    comparison?.data?.strategies?.map((strategy) => ({
      strategy: strategy.name || "Unknown",
      return: strategy.total_return || 0,
      sharpe: strategy.sharpe_ratio || 0,
      winRate: strategy.win_rate || 0,
      symbol: strategy.type || "",
    })) || []; // Sort by selected metric
  const sortedData = [...chartData].sort((a, b) => {
    if (metric === "return") return b.return - a.return;
    if (metric === "sharpe") return b.sharpe - a.sharpe;
    if (metric === "winRate") return b.winRate - a.winRate;
    return 0;
  });

  // Get metric config
  const getMetricConfig = () => {
    switch (metric) {
      case "return":
        return {
          dataKey: "return",
          name: "수익률 (%)",
          color: theme.palette.success.main,
          formatter: (value: number) => `${value.toFixed(2)}%`,
        };
      case "sharpe":
        return {
          dataKey: "sharpe",
          name: "Sharpe Ratio",
          color: theme.palette.primary.main,
          formatter: (value: number) => value.toFixed(2),
        };
      case "winRate":
        return {
          dataKey: "winRate",
          name: "승률 (%)",
          color: theme.palette.info.main,
          formatter: (value: number) => `${value.toFixed(1)}%`,
        };
      default:
        return {
          dataKey: "return",
          name: "수익률 (%)",
          color: theme.palette.success.main,
          formatter: (value: number) => `${value.toFixed(2)}%`,
        };
    }
  };

  const metricConfig = getMetricConfig();

  // Get bar color based on value
  const getBarColor = (value: number, index: number) => {
    if (metric === "return") {
      return value >= 0 ? theme.palette.success.main : theme.palette.error.main;
    }
    // Color gradient for other metrics
    const colors = [
      theme.palette.primary.dark,
      theme.palette.primary.main,
      theme.palette.primary.light,
    ];
    return colors[index % colors.length];
  };

  if (sortedData.length === 0) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            전략 비교
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
              비교할 전략 데이터가 없습니다
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  // Calculate statistics
  const avgReturn =
    sortedData.reduce((sum, d) => sum + d.return, 0) / sortedData.length;
  const avgSharpe =
    sortedData.reduce((sum, d) => sum + d.sharpe, 0) / sortedData.length;
  const avgWinRate =
    sortedData.reduce((sum, d) => sum + d.winRate, 0) / sortedData.length;

  const topStrategy = sortedData[0];

  return (
    <Card>
      <CardContent>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            전략 성과 비교
          </Typography>

          <Box
            sx={{
              display: "flex",
              gap: 2,
              flexWrap: "wrap",
              mt: 2,
            }}
          >
            <Chip
              label={`총 ${sortedData.length}개 전략`}
              color="primary"
              size="small"
            />
            <Chip
              label={`평균 수익률: ${avgReturn.toFixed(2)}%`}
              size="small"
              variant="outlined"
            />
            <Chip
              label={`평균 Sharpe: ${avgSharpe.toFixed(2)}`}
              size="small"
              variant="outlined"
            />
            <Chip
              label={`평균 승률: ${avgWinRate.toFixed(1)}%`}
              size="small"
              variant="outlined"
            />
          </Box>

          {topStrategy && (
            <Box
              sx={{
                mt: 2,
                p: 2,
                bgcolor: "action.hover",
                borderRadius: 1,
              }}
            >
              <Typography variant="caption" color="text.secondary">
                🏆 최고 성과 전략
              </Typography>
              <Typography variant="body1" fontWeight="bold">
                {topStrategy.strategy} ({topStrategy.symbol})
              </Typography>
              <Typography variant="body2">
                {metricConfig.formatter(
                  topStrategy[
                    metricConfig.dataKey as keyof ChartDataPoint
                  ] as number
                )}
              </Typography>
            </Box>
          )}
        </Box>

        {/* Bar Chart */}
        <ResponsiveContainer width="100%" height={height}>
          <BarChart
            data={sortedData}
            margin={{
              top: 20,
              right: 30,
              left: 20,
              bottom: 80,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="strategy"
              angle={-45}
              textAnchor="end"
              height={100}
              tick={{ fontSize: 12 }}
            />
            <YAxis
              label={{
                value: metricConfig.name,
                angle: -90,
                position: "insideLeft",
              }}
              tickFormatter={metricConfig.formatter}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />

            <Bar
              dataKey={metricConfig.dataKey}
              name={metricConfig.name}
              radius={[8, 8, 0, 0]}
            >
              {sortedData.map((entry, index) => (
                <Cell
                  key={`cell-${entry.strategy}`}
                  fill={getBarColor(
                    entry[
                      metricConfig.dataKey as keyof ChartDataPoint
                    ] as number,
                    index
                  )}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>

        {/* Summary Statistics */}
        <Box sx={{ mt: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            성과 요약
          </Typography>

          <Box sx={{ display: "flex", gap: 3, flexWrap: "wrap" }}>
            <Box>
              <Typography variant="caption" color="text.secondary">
                최고 수익률
              </Typography>
              <Typography variant="body2" color="success.main">
                {Math.max(...sortedData.map((d) => d.return)).toFixed(2)}%
              </Typography>
            </Box>

            <Box>
              <Typography variant="caption" color="text.secondary">
                최고 Sharpe
              </Typography>
              <Typography variant="body2" color="primary">
                {Math.max(...sortedData.map((d) => d.sharpe)).toFixed(2)}
              </Typography>
            </Box>

            <Box>
              <Typography variant="caption" color="text.secondary">
                최고 승률
              </Typography>
              <Typography variant="body2">
                {Math.max(...sortedData.map((d) => d.winRate)).toFixed(1)}%
              </Typography>
            </Box>

            <Box>
              <Typography variant="caption" color="text.secondary">
                수익 전략
              </Typography>
              <Typography variant="body2">
                {sortedData.filter((d) => d.return > 0).length}개 /{" "}
                {sortedData.length}개
              </Typography>
            </Box>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}
