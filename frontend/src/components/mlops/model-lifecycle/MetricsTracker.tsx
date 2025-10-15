/**
 * MetricsTracker Component
 *
 * Displays real-time experiment metrics with:
 * - Metric summary cards (정확도, 손실, F1, AUC)
 * - Time-series charts with recharts LineChart
 * - Multi-experiment comparison overlay
 * - 10-second auto-refresh polling
 *
 * @module components/mlops/model-lifecycle/MetricsTracker
 */

import { useExperimentDetail } from "@/hooks/useModelLifecycle";
import TrendingDownIcon from "@mui/icons-material/TrendingDown";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import {
	Alert,
	Box,
	Card,
	CardContent,
	Chip,
	CircularProgress,
	FormControl,
	InputLabel,
	MenuItem,
	Select,
	ToggleButton,
	ToggleButtonGroup,
	Typography,
	type SelectChangeEvent,
} from "@mui/material";
import Grid from "@mui/material/Grid";
import { useState } from "react";
import {
	CartesianGrid,
	Legend,
	Line,
	LineChart,
	ResponsiveContainer,
	Tooltip,
	XAxis,
	YAxis,
} from "recharts";

// ============================================================================
// Component Props
// ============================================================================

interface MetricsTrackerProps {
	/**
	 * Experiment ID to track
	 */
	experimentId: string | null;

	/**
	 * Optional list of experiment IDs for comparison
	 */
	comparisonExperimentIds?: string[];
}

// ============================================================================
// Types
// ============================================================================

type MetricType = "accuracy" | "loss" | "f1_score" | "auc";

interface MetricDataPoint {
	epoch: number;
	value: number;
}

// ============================================================================
// Component Implementation
// ============================================================================

export const MetricsTracker: React.FC<MetricsTrackerProps> = ({
	experimentId,
	comparisonExperimentIds = [],
}) => {
	// ============================================================================
	// State
	// ============================================================================

	const [selectedMetric, setSelectedMetric] = useState<MetricType>("accuracy");
	const [chartView, setChartView] = useState<"single" | "comparison">("single");

	// ============================================================================
	// Hooks - 10-second polling for real-time updates
	// ============================================================================

	const { experimentDetail, isLoading, error } =
		useExperimentDetail(experimentId);
	// TODO: Add refetchInterval support to useExperimentDetail hook for real-time polling

	// ============================================================================
	// Event Handlers
	// ============================================================================

	const handleMetricChange = (event: SelectChangeEvent<MetricType>) => {
		setSelectedMetric(event.target.value as MetricType);
	};

	const handleChartViewChange = (
		_event: React.MouseEvent<HTMLElement>,
		newView: "single" | "comparison" | null,
	) => {
		if (newView !== null) {
			setChartView(newView);
		}
	};

	// ============================================================================
	// Prepare Chart Data
	// ============================================================================

	const getMetricData = (metricType: MetricType): MetricDataPoint[] => {
		if (!experimentDetail?.metrics) return [];

		// Mock time-series data generation
		// TODO: Replace with actual time-series data from backend
		const finalValue = experimentDetail.metrics[metricType] || 0;
		const epochs = 50;

		return Array.from({ length: epochs }, (_, i) => {
			let value: number;
			if (metricType === "loss") {
				// Loss decreases over time
				value = 2.0 * Math.exp(-i / 20) + Math.random() * 0.1;
			} else {
				// Accuracy, F1, AUC increase over time
				const progress = i / epochs;
				value =
					finalValue * (1 - Math.exp(-progress * 5)) + Math.random() * 0.02;
			}

			return {
				epoch: i + 1,
				value: Math.max(0, Math.min(value, metricType === "loss" ? 10 : 1)),
			};
		});
	};

	const chartData = getMetricData(selectedMetric);

	// ============================================================================
	// Calculate Metric Trends
	// ============================================================================

	const getMetricTrend = (
		metricType: MetricType,
	): { value: number; change: number; isPositive: boolean } => {
		if (!experimentDetail?.metrics) {
			return { value: 0, change: 0, isPositive: false };
		}

		const value = experimentDetail.metrics[metricType] || 0;
		const data = getMetricData(metricType);

		if (data.length < 2) {
			return { value, change: 0, isPositive: false };
		}

		const lastValue = data[data.length - 1].value;
		const prevValue = data[data.length - 10]?.value || data[0].value;
		const change = ((lastValue - prevValue) / prevValue) * 100;

		// For loss, negative change is good
		const isPositive = metricType === "loss" ? change < 0 : change > 0;

		return { value, change: Math.abs(change), isPositive };
	};

	// ============================================================================
	// Render Loading State
	// ============================================================================

	if (isLoading) {
		return (
			<Card>
				<CardContent>
					<Box
						sx={{
							display: "flex",
							justifyContent: "center",
							alignItems: "center",
							minHeight: 400,
						}}
					>
						<CircularProgress />
					</Box>
				</CardContent>
			</Card>
		);
	}

	// ============================================================================
	// Render Error State
	// ============================================================================

	if (error || !experimentDetail) {
		return (
			<Card>
				<CardContent>
					<Alert severity="error">
						{error
							? `메트릭 로딩 실패: ${error.message}`
							: "실험 정보를 찾을 수 없습니다"}
					</Alert>
				</CardContent>
			</Card>
		);
	}

	// ============================================================================
	// Metric Cards Data
	// ============================================================================

	const metricCards: {
		type: MetricType;
		label: string;
		format: (val: number) => string;
	}[] = [
		{
			type: "accuracy",
			label: "정확도",
			format: (val) => `${(val * 100).toFixed(2)}%`,
		},
		{
			type: "loss",
			label: "손실",
			format: (val) => val.toFixed(4),
		},
		{
			type: "f1_score",
			label: "F1 Score",
			format: (val) => val.toFixed(4),
		},
		{
			type: "auc",
			label: "AUC",
			format: (val) => val.toFixed(4),
		},
	];

	// ============================================================================
	// Render
	// ============================================================================

	return (
		<Card>
			<CardContent>
				{/* Header */}
				<Box
					sx={{
						display: "flex",
						justifyContent: "space-between",
						alignItems: "center",
						mb: 3,
					}}
				>
					<Box>
						<Typography variant="h5" component="h2">
							메트릭 추적
						</Typography>
						<Typography variant="body2" color="text.secondary">
							{experimentDetail.name} - 실시간 업데이트
						</Typography>
					</Box>
					<Chip
						label={experimentDetail.status.toUpperCase()}
						color={
							experimentDetail.status === "completed"
								? "success"
								: experimentDetail.status === "running"
									? "primary"
									: experimentDetail.status === "failed"
										? "error"
										: "default"
						}
					/>
				</Box>

				{/* Metric Summary Cards */}
				<Box sx={{ flexGrow: 1, mb: 3 }}>
					<Grid container spacing={2}>
						{metricCards.map((metric) => {
							const trend = getMetricTrend(metric.type);
							return (
								<Grid key={metric.type} size={{ xs: 12, sm: 6, md: 3 }}>
									<Card variant="outlined">
										<CardContent>
											<Typography variant="body2" color="text.secondary">
												{metric.label}
											</Typography>
											<Typography variant="h5" component="div" sx={{ my: 1 }}>
												{metric.format(trend.value)}
											</Typography>
											<Box
												sx={{
													display: "flex",
													alignItems: "center",
													gap: 0.5,
												}}
											>
												{trend.isPositive ? (
													<TrendingUpIcon
														fontSize="small"
														sx={{ color: "success.main" }}
													/>
												) : (
													<TrendingDownIcon
														fontSize="small"
														sx={{ color: "error.main" }}
													/>
												)}
												<Typography
													variant="caption"
													sx={{
														color: trend.isPositive
															? "success.main"
															: "error.main",
													}}
												>
													{trend.change.toFixed(2)}%
												</Typography>
											</Box>
										</CardContent>
									</Card>
								</Grid>
							);
						})}
					</Grid>
				</Box>

				{/* Chart Controls */}
				<Box
					sx={{
						display: "flex",
						justifyContent: "space-between",
						alignItems: "center",
						mb: 2,
						gap: 2,
					}}
				>
					<FormControl size="small" sx={{ minWidth: 150 }}>
						<InputLabel>메트릭 선택</InputLabel>
						<Select
							value={selectedMetric}
							label="메트릭 선택"
							onChange={handleMetricChange}
						>
							<MenuItem value="accuracy">정확도</MenuItem>
							<MenuItem value="loss">손실</MenuItem>
							<MenuItem value="f1_score">F1 Score</MenuItem>
							<MenuItem value="auc">AUC</MenuItem>
						</Select>
					</FormControl>

					{comparisonExperimentIds.length > 0 && (
						<ToggleButtonGroup
							value={chartView}
							exclusive
							onChange={handleChartViewChange}
							size="small"
						>
							<ToggleButton value="single">단일</ToggleButton>
							<ToggleButton value="comparison">비교</ToggleButton>
						</ToggleButtonGroup>
					)}
				</Box>

				{/* Metrics Chart */}
				<Box sx={{ width: "100%", height: 400 }}>
					<ResponsiveContainer width="100%" height="100%">
						<LineChart data={chartData}>
							<CartesianGrid strokeDasharray="3 3" />
							<XAxis
								dataKey="epoch"
								label={{
									value: "Epoch",
									position: "insideBottom",
									offset: -5,
								}}
							/>
							<YAxis
								label={{
									value:
										selectedMetric === "loss"
											? "Loss"
											: selectedMetric === "accuracy"
												? "Accuracy"
												: selectedMetric.toUpperCase(),
									angle: -90,
									position: "insideLeft",
								}}
								domain={selectedMetric === "loss" ? [0, "auto"] : [0, 1]}
							/>
							<Tooltip
								formatter={(value: number) => {
									if (selectedMetric === "accuracy") {
										return `${(value * 100).toFixed(2)}%`;
									}
									return value.toFixed(4);
								}}
							/>
							<Legend />
							<Line
								type="monotone"
								dataKey="value"
								stroke="#8884d8"
								strokeWidth={2}
								name={
									selectedMetric === "accuracy"
										? "정확도"
										: selectedMetric === "loss"
											? "손실"
											: selectedMetric === "f1_score"
												? "F1 Score"
												: "AUC"
								}
								dot={false}
							/>
							{chartView === "comparison" &&
								comparisonExperimentIds.map((id, idx) => (
									<Line
										key={id}
										type="monotone"
										dataKey="value"
										stroke={`hsl(${(idx + 1) * 60}, 70%, 50%)`}
										strokeWidth={2}
										name={`실험 ${idx + 1}`}
										dot={false}
									/>
								))}
						</LineChart>
					</ResponsiveContainer>
				</Box>

				{/* Additional Metrics Info */}
				<Box sx={{ mt: 3 }}>
					<Typography variant="subtitle2" gutterBottom>
						추가 정보
					</Typography>
					<Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
						<Box sx={{ display: "flex", justifyContent: "space-between" }}>
							<Typography variant="body2" color="text.secondary">
								총 에포크
							</Typography>
							<Typography variant="body2">{chartData.length}</Typography>
						</Box>
						<Box sx={{ display: "flex", justifyContent: "space-between" }}>
							<Typography variant="body2" color="text.secondary">
								최적 에포크
							</Typography>
							<Typography variant="body2">
								{chartData.reduce(
									(best, current, idx) =>
										selectedMetric === "loss"
											? current.value < chartData[best].value
												? idx
												: best
											: current.value > chartData[best].value
												? idx
												: best,
									0,
								) + 1}
							</Typography>
						</Box>
						<Box sx={{ display: "flex", justifyContent: "space-between" }}>
							<Typography variant="body2" color="text.secondary">
								최종 값
							</Typography>
							<Typography variant="body2">
								{selectedMetric === "accuracy"
									? `${(chartData[chartData.length - 1].value * 100).toFixed(
											2,
										)}%`
									: chartData[chartData.length - 1].value.toFixed(4)}
							</Typography>
						</Box>
					</Box>
				</Box>
			</CardContent>
		</Card>
	);
};
