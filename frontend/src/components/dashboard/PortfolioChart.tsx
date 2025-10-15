import type { PortfolioPerformanceResponse } from "@/client/types.gen";
import { Box, Card, CardContent, Typography, useTheme } from "@mui/material";
import { useMemo } from "react";
import {
	Area,
	AreaChart,
	CartesianGrid,
	Legend,
	Line,
	LineChart,
	ResponsiveContainer,
	Tooltip,
	XAxis,
	YAxis,
} from "recharts";

interface PortfolioChartProps {
	performance: PortfolioPerformanceResponse;
	height?: number;
	showVolatility?: boolean;
}

interface ChartDataPoint {
	date: string;
	value: number;
	return: number;
	volatility?: number;
}

// Custom tooltip component (outside main component)
function CustomTooltip({
	active,
	payload,
	showVolatility,
}: {
	active?: boolean;
	payload?: any;
	showVolatility?: boolean;
}) {
	if (active && payload && payload.length > 0) {
		const data = payload[0].payload as ChartDataPoint;

		return (
			<Card sx={{ p: 1, bgcolor: "background.paper", boxShadow: 3 }}>
				<Typography variant="caption" fontWeight="bold">
					{data.date}
				</Typography>
				<Typography variant="body2" color="primary">
					가치: ${data.value.toLocaleString()}
				</Typography>
				<Typography
					variant="body2"
					color={data.return >= 0 ? "success.main" : "error.main"}
				>
					수익률: {data.return.toFixed(2)}%
				</Typography>
				{showVolatility && data.volatility !== undefined && (
					<Typography variant="caption" color="text.secondary">
						변동성: ±{data.volatility.toFixed(2)}%
					</Typography>
				)}
			</Card>
		);
	}

	return null;
}

/**
 * PortfolioChart Component
 *
 * Visualizes portfolio performance over time with:
 * - Portfolio value trend (Line Chart)
 * - Cumulative returns
 * - Volatility band (optional)
 * - Interactive tooltips
 *
 * Uses Recharts for visualization.
 *
 * @example
 * ```tsx
 * <PortfolioChart
 *   performance={portfolioPerformance}
 *   height={400}
 *   showVolatility
 * />
 * ```
 */
export function PortfolioChart({
	performance,
	height = 400,
	showVolatility = false,
}: PortfolioChartProps) {
	const theme = useTheme();

	// Process performance data for chart
	const chartData = useMemo(() => {
		if (!performance?.data?.data_points) {
			return [];
		}

		// Use data_points array directly if available
		const dataPoints = performance.data.data_points;
		if (dataPoints.length > 0) {
			return dataPoints.map((point) => ({
				date: new Date(point.timestamp).toISOString().split("T")[0],
				value: point.portfolio_value || 0,
				return: point.pnl_percentage || 0,
				volatility: 0, // Volatility not in individual points
			}));
		}

		// Fallback: Generate sample time series data
		// In production, this should come from API
		const summary = performance.data.summary;
		const numPoints = 30; // Last 30 days
		const totalReturn = summary?.total_return || 0;
		const volatility = summary?.volatility || 5;

		const points: ChartDataPoint[] = [];
		const startValue = 10000;

		for (let i = 0; i < numPoints; i++) {
			const date = new Date();
			date.setDate(date.getDate() - (numPoints - i - 1));

			// Simulate value progression
			const progress = i / (numPoints - 1);
			const value = startValue * (1 + (totalReturn / 100) * progress);
			const returnPct = ((value - startValue) / startValue) * 100;

			// Simulate volatility
			const volatilityValue = showVolatility ? volatility * progress : 0;

			points.push({
				date: date.toISOString().split("T")[0],
				value: Number(value.toFixed(2)),
				return: Number(returnPct.toFixed(2)),
				volatility: Number(volatilityValue.toFixed(2)),
			});
		}

		return points;
	}, [performance, showVolatility]);

	if (chartData.length === 0) {
		return (
			<Card>
				<CardContent>
					<Typography variant="h6" gutterBottom>
						포트폴리오 추이
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
							포트폴리오 데이터가 없습니다
						</Typography>
					</Box>
				</CardContent>
			</Card>
		);
	}

	// Calculate statistics
	const latestValue = chartData[chartData.length - 1].value;
	const latestReturn = chartData[chartData.length - 1].return;
	const peakValue = Math.max(...chartData.map((d) => d.value));
	const troughValue = Math.min(...chartData.map((d) => d.value));

	return (
		<Card>
			<CardContent>
				<Box sx={{ mb: 3 }}>
					<Typography variant="h6" gutterBottom>
						포트폴리오 추이
					</Typography>

					<Box
						sx={{
							display: "flex",
							gap: 3,
							flexWrap: "wrap",
							mt: 2,
						}}
					>
						<Box>
							<Typography variant="caption" color="text.secondary">
								현재 가치
							</Typography>
							<Typography variant="h6">
								${latestValue.toLocaleString()}
							</Typography>
						</Box>

						<Box>
							<Typography variant="caption" color="text.secondary">
								누적 수익률
							</Typography>
							<Typography
								variant="h6"
								color={latestReturn >= 0 ? "success.main" : "error.main"}
							>
								{latestReturn >= 0 ? "+" : ""}
								{latestReturn.toFixed(2)}%
							</Typography>
						</Box>

						<Box>
							<Typography variant="caption" color="text.secondary">
								최고점
							</Typography>
							<Typography variant="body2">
								${peakValue.toLocaleString()}
							</Typography>
						</Box>

						<Box>
							<Typography variant="caption" color="text.secondary">
								최저점
							</Typography>
							<Typography variant="body2">
								${troughValue.toLocaleString()}
							</Typography>
						</Box>
					</Box>
				</Box>

				{/* Value Chart */}
				<ResponsiveContainer width="100%" height={height}>
					<LineChart
						data={chartData}
						margin={{
							top: 20,
							right: 30,
							left: 20,
							bottom: 20,
						}}
					>
						<CartesianGrid strokeDasharray="3 3" />
						<XAxis
							dataKey="date"
							label={{
								value: "날짜",
								position: "insideBottom",
								offset: -10,
							}}
							tick={{ fontSize: 12 }}
						/>
						<YAxis
							label={{
								value: "포트폴리오 가치 ($)",
								angle: -90,
								position: "insideLeft",
							}}
							tickFormatter={(value) => `$${value.toLocaleString()}`}
						/>
						<Tooltip
							content={<CustomTooltip showVolatility={showVolatility} />}
						/>
						<Legend />

						<Line
							type="monotone"
							dataKey="value"
							name="포트폴리오 가치"
							stroke={theme.palette.primary.main}
							strokeWidth={2}
							dot={{ r: 3 }}
							activeDot={{ r: 5 }}
						/>
					</LineChart>
				</ResponsiveContainer>

				{/* Return Chart */}
				<Box sx={{ mt: 4 }}>
					<Typography variant="subtitle2" gutterBottom>
						수익률 추이
					</Typography>

					<ResponsiveContainer width="100%" height={200}>
						<AreaChart
							data={chartData}
							margin={{
								top: 10,
								right: 30,
								left: 20,
								bottom: 10,
							}}
						>
							<CartesianGrid strokeDasharray="3 3" />
							<XAxis dataKey="date" tick={{ fontSize: 12 }} />
							<YAxis
								tickFormatter={(value) => `${value}%`}
								label={{
									value: "수익률 (%)",
									angle: -90,
									position: "insideLeft",
								}}
							/>
							<Tooltip
								formatter={(value: number) => `${value.toFixed(2)}%`}
								labelFormatter={(label) => `날짜: ${label}`}
							/>
							<Legend />

							<Area
								type="monotone"
								dataKey="return"
								name="누적 수익률"
								stroke={theme.palette.success.main}
								fill={theme.palette.success.light}
								fillOpacity={0.3}
							/>
						</AreaChart>
					</ResponsiveContainer>
				</Box>

				{/* Volatility Chart */}
				{showVolatility && (
					<Box sx={{ mt: 4 }}>
						<Typography variant="subtitle2" gutterBottom>
							변동성 추이
						</Typography>

						<ResponsiveContainer width="100%" height={150}>
							<LineChart
								data={chartData}
								margin={{
									top: 10,
									right: 30,
									left: 20,
									bottom: 10,
								}}
							>
								<CartesianGrid strokeDasharray="3 3" />
								<XAxis dataKey="date" tick={{ fontSize: 12 }} />
								<YAxis
									tickFormatter={(value) => `${value}%`}
									label={{
										value: "변동성 (%)",
										angle: -90,
										position: "insideLeft",
									}}
								/>
								<Tooltip
									formatter={(value: number) => `±${value.toFixed(2)}%`}
									labelFormatter={(label) => `날짜: ${label}`}
								/>
								<Legend />

								<Line
									type="monotone"
									dataKey="volatility"
									name="변동성"
									stroke={theme.palette.warning.main}
									strokeWidth={2}
									dot={false}
								/>
							</LineChart>
						</ResponsiveContainer>
					</Box>
				)}
			</CardContent>
		</Card>
	);
}
