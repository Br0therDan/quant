/**
 * EvaluationResults Component
 *
 * Displays comprehensive evaluation results with:
 * - Metric cards (Accuracy, Precision, Recall, F1, AUC)
 * - Confusion Matrix heatmap
 * - ROC Curve chart
 * - Precision-Recall Curve chart
 *
 * @module components/mlops/evaluation-harness/EvaluationResults
 */

import { useEvaluationJob } from "@/hooks/useEvaluationHarness";
import {
	Alert,
	Box,
	Card,
	CardContent,
	CircularProgress,
	Tab,
	Tabs,
	Typography,
} from "@mui/material";
import Grid from "@mui/material/Grid";
import { useState } from "react";
import {
	CartesianGrid,
	Cell,
	Legend,
	Line,
	LineChart,
	ResponsiveContainer,
	Scatter,
	ScatterChart,
	Tooltip,
	XAxis,
	YAxis,
} from "recharts";

// ============================================================================
// Component Props
// ============================================================================

interface EvaluationResultsProps {
	/**
	 * Evaluation job ID to display results for
	 */
	jobId: string | null;
}

// ============================================================================
// Helper Functions
// ============================================================================

const getConfusionMatrixHeatmapData = (
	confusionMatrix: number[][],
	classLabels: string[],
) => {
	const data: {
		x: number;
		y: number;
		value: number;
		predicted: string;
		actual: string;
	}[] = [];

	for (let i = 0; i < confusionMatrix.length; i++) {
		for (let j = 0; j < confusionMatrix[i].length; j++) {
			data.push({
				x: j,
				y: i,
				value: confusionMatrix[i][j],
				predicted: classLabels[j] || `Class ${j}`,
				actual: classLabels[i] || `Class ${i}`,
			});
		}
	}

	return data;
};

const getColorForValue = (value: number, max: number): string => {
	const intensity = value / max;
	const red = Math.floor(255 * intensity);
	const green = Math.floor(255 * (1 - intensity));
	return `rgb(${red}, ${green}, 100)`;
};

// ============================================================================
// Component Implementation
// ============================================================================

export const EvaluationResults: React.FC<EvaluationResultsProps> = ({
	jobId,
}) => {
	// ============================================================================
	// State
	// ============================================================================

	const [selectedTab, setSelectedTab] = useState(0);

	// ============================================================================
	// Hooks
	// ============================================================================

	const { evaluationJob, isLoading, error } = useEvaluationJob(jobId);

	// ============================================================================
	// Event Handlers
	// ============================================================================

	const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
		setSelectedTab(newValue);
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

	if (error || !evaluationJob || !evaluationJob.metrics) {
		return (
			<Card>
				<CardContent>
					<Alert severity="error">
						{error
							? `평가 결과 로딩 실패: ${error.message}`
							: "평가 결과를 찾을 수 없습니다"}
					</Alert>
				</CardContent>
			</Card>
		);
	}

	// ============================================================================
	// Prepare Data
	// ============================================================================

	const metrics = evaluationJob.metrics;
	const confusionMatrixData = getConfusionMatrixHeatmapData(
		metrics.confusion_matrix,
		metrics.class_labels,
	);
	const maxValue = Math.max(
		...metrics.confusion_matrix.flat().map((v) => v || 0),
	);

	// ROC Curve data
	const rocCurveData =
		metrics.roc_curve?.fpr.map((fpr, index) => ({
			fpr,
			tpr: metrics.roc_curve?.tpr[index] || 0,
			threshold: metrics.roc_curve?.thresholds[index] || 0,
		})) || [];

	// PR Curve data
	const prCurveData =
		metrics.precision_recall_curve?.recall.map((recall, index) => ({
			recall,
			precision: metrics.precision_recall_curve?.precision[index] || 0,
			threshold: metrics.precision_recall_curve?.thresholds[index] || 0,
		})) || [];

	// ============================================================================
	// Render
	// ============================================================================

	return (
		<Card>
			<CardContent>
				{/* Header */}
				<Box sx={{ mb: 3 }}>
					<Typography variant="h5" component="h2">
						평가 결과
					</Typography>
					<Typography variant="body2" color="text.secondary">
						{evaluationJob.model_name} - Dataset: {evaluationJob.dataset_id}
					</Typography>
				</Box>

				{/* Metric Summary Cards */}
				<Box sx={{ flexGrow: 1, mb: 3 }}>
					<Grid container spacing={2}>
						<Grid size={{ xs: 12, sm: 6, md: 2.4 }}>
							<Card variant="outlined">
								<CardContent>
									<Typography variant="body2" color="text.secondary">
										Accuracy
									</Typography>
									<Typography variant="h5">
										{(metrics.accuracy * 100).toFixed(2)}%
									</Typography>
								</CardContent>
							</Card>
						</Grid>
						<Grid size={{ xs: 12, sm: 6, md: 2.4 }}>
							<Card variant="outlined">
								<CardContent>
									<Typography variant="body2" color="text.secondary">
										Precision
									</Typography>
									<Typography variant="h5">
										{(metrics.precision * 100).toFixed(2)}%
									</Typography>
								</CardContent>
							</Card>
						</Grid>
						<Grid size={{ xs: 12, sm: 6, md: 2.4 }}>
							<Card variant="outlined">
								<CardContent>
									<Typography variant="body2" color="text.secondary">
										Recall
									</Typography>
									<Typography variant="h5">
										{(metrics.recall * 100).toFixed(2)}%
									</Typography>
								</CardContent>
							</Card>
						</Grid>
						<Grid size={{ xs: 12, sm: 6, md: 2.4 }}>
							<Card variant="outlined">
								<CardContent>
									<Typography variant="body2" color="text.secondary">
										F1 Score
									</Typography>
									<Typography variant="h5">
										{metrics.f1_score.toFixed(4)}
									</Typography>
								</CardContent>
							</Card>
						</Grid>
						<Grid size={{ xs: 12, sm: 6, md: 2.4 }}>
							<Card variant="outlined">
								<CardContent>
									<Typography variant="body2" color="text.secondary">
										AUC-ROC
									</Typography>
									<Typography variant="h5">
										{metrics.auc_roc.toFixed(4)}
									</Typography>
								</CardContent>
							</Card>
						</Grid>
					</Grid>
				</Box>

				{/* Tabs for different visualizations */}
				<Box sx={{ borderBottom: 1, borderColor: "divider", mb: 2 }}>
					<Tabs value={selectedTab} onChange={handleTabChange}>
						<Tab label="Confusion Matrix" />
						<Tab label="ROC Curve" />
						<Tab label="Precision-Recall Curve" />
					</Tabs>
				</Box>

				{/* Tab Panels */}
				{selectedTab === 0 && (
					<Box>
						<Typography variant="h6" gutterBottom>
							Confusion Matrix
						</Typography>
						<Box sx={{ width: "100%", height: 400 }}>
							<ResponsiveContainer width="100%" height="100%">
								<ScatterChart
									margin={{ top: 20, right: 20, bottom: 60, left: 60 }}
								>
									<CartesianGrid strokeDasharray="3 3" />
									<XAxis
										type="number"
										dataKey="x"
										name="Predicted"
										domain={[-0.5, metrics.class_labels.length - 0.5]}
										ticks={metrics.class_labels.map((_, i) => i)}
										tickFormatter={(value) =>
											metrics.class_labels[value] || `${value}`
										}
										label={{
											value: "Predicted Class",
											position: "insideBottom",
											offset: -10,
										}}
									/>
									<YAxis
										type="number"
										dataKey="y"
										name="Actual"
										domain={[-0.5, metrics.class_labels.length - 0.5]}
										ticks={metrics.class_labels.map((_, i) => i)}
										tickFormatter={(value) =>
											metrics.class_labels[value] || `${value}`
										}
										reversed
										label={{
											value: "Actual Class",
											angle: -90,
											position: "insideLeft",
										}}
									/>
									<Tooltip
										formatter={(value: number, name: string) => {
											if (name === "value") return [`Count: ${value}`, ""];
											return [value, name];
										}}
										labelFormatter={(label) => {
											const point = confusionMatrixData.find(
												(d) => d.x === label,
											);
											return point
												? `${point.actual} → ${point.predicted}`
												: "";
										}}
									/>
									<Scatter name="Confusion Matrix" data={confusionMatrixData}>
										{confusionMatrixData.map((entry, index) => (
											<Cell
												key={`cell-${index}`}
												fill={getColorForValue(entry.value, maxValue)}
											/>
										))}
									</Scatter>
								</ScatterChart>
							</ResponsiveContainer>
						</Box>
					</Box>
				)}

				{selectedTab === 1 && (
					<Box>
						<Typography variant="h6" gutterBottom>
							ROC Curve (AUC = {metrics.auc_roc.toFixed(4)})
						</Typography>
						<Box sx={{ width: "100%", height: 400 }}>
							<ResponsiveContainer width="100%" height="100%">
								<LineChart data={rocCurveData}>
									<CartesianGrid strokeDasharray="3 3" />
									<XAxis
										dataKey="fpr"
										type="number"
										domain={[0, 1]}
										label={{
											value: "False Positive Rate",
											position: "insideBottom",
											offset: -5,
										}}
									/>
									<YAxis
										dataKey="tpr"
										type="number"
										domain={[0, 1]}
										label={{
											value: "True Positive Rate",
											angle: -90,
											position: "insideLeft",
										}}
									/>
									<Tooltip formatter={(value: number) => value.toFixed(4)} />
									<Legend />
									<Line
										type="monotone"
										dataKey="tpr"
										stroke="#8884d8"
										strokeWidth={2}
										dot={false}
										name="ROC Curve"
									/>
									<Line
										type="monotone"
										data={[
											{ fpr: 0, tpr: 0 },
											{ fpr: 1, tpr: 1 },
										]}
										dataKey="tpr"
										stroke="#ccc"
										strokeWidth={1}
										strokeDasharray="5 5"
										dot={false}
										name="Random Classifier"
									/>
								</LineChart>
							</ResponsiveContainer>
						</Box>
					</Box>
				)}

				{selectedTab === 2 && (
					<Box>
						<Typography variant="h6" gutterBottom>
							Precision-Recall Curve
						</Typography>
						<Box sx={{ width: "100%", height: 400 }}>
							<ResponsiveContainer width="100%" height="100%">
								<LineChart data={prCurveData}>
									<CartesianGrid strokeDasharray="3 3" />
									<XAxis
										dataKey="recall"
										type="number"
										domain={[0, 1]}
										label={{
											value: "Recall",
											position: "insideBottom",
											offset: -5,
										}}
									/>
									<YAxis
										dataKey="precision"
										type="number"
										domain={[0, 1]}
										label={{
											value: "Precision",
											angle: -90,
											position: "insideLeft",
										}}
									/>
									<Tooltip formatter={(value: number) => value.toFixed(4)} />
									<Legend />
									<Line
										type="monotone"
										dataKey="precision"
										stroke="#82ca9d"
										strokeWidth={2}
										dot={false}
										name="PR Curve"
									/>
								</LineChart>
							</ResponsiveContainer>
						</Box>
					</Box>
				)}

				{/* Additional Info */}
				<Box sx={{ mt: 3 }}>
					<Typography variant="subtitle2" gutterBottom>
						평가 정보
					</Typography>
					<Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
						<Box sx={{ display: "flex", justifyContent: "space-between" }}>
							<Typography variant="body2" color="text.secondary">
								평가 완료 시간
							</Typography>
							<Typography variant="body2">
								{evaluationJob.completed_at
									? new Date(evaluationJob.completed_at).toLocaleString("ko-KR")
									: "진행 중"}
							</Typography>
						</Box>
						<Box sx={{ display: "flex", justifyContent: "space-between" }}>
							<Typography variant="body2" color="text.secondary">
								클래스 수
							</Typography>
							<Typography variant="body2">
								{metrics.class_labels.length}
							</Typography>
						</Box>
						<Box sx={{ display: "flex", justifyContent: "space-between" }}>
							<Typography variant="body2" color="text.secondary">
								총 샘플 수
							</Typography>
							<Typography variant="body2">
								{metrics.confusion_matrix.flat().reduce((a, b) => a + b, 0)}
							</Typography>
						</Box>
					</Box>
				</Box>
			</CardContent>
		</Card>
	);
};
