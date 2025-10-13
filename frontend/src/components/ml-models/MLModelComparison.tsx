/**
 * MLModelComparison Component
 *
 * Phase 1 Day 5: ML Model Comparison View
 * - Multiple model selection UI (Checkbox)
 * - Comparison table (metrics columns)
 * - Visualization chart (Recharts BarChart)
 */

"use client";

import { useMLModel, useModelComparison } from "@/hooks/useMLModel";
import CompareArrowsIcon from "@mui/icons-material/CompareArrows";
import {
	Alert,
	Box,
	Button,
	Card,
	CardContent,
	Checkbox,
	Chip,
	CircularProgress,
	FormControlLabel,
	Paper,
	Stack,
	Table,
	TableBody,
	TableCell,
	TableContainer,
	TableHead,
	TableRow,
	Typography,
} from "@mui/material";
import Grid from "@mui/material/Grid";
import { useMemo, useState } from "react";
import {
	Bar,
	BarChart,
	CartesianGrid,
	Legend,
	ResponsiveContainer,
	Tooltip,
	XAxis,
	YAxis,
} from "recharts";

type MetricType = "accuracy" | "precision" | "recall" | "f1_score";

const METRICS: { key: MetricType; label: string; color: string }[] = [
	{ key: "accuracy", label: "Accuracy", color: "#1976d2" },
	{ key: "precision", label: "Precision", color: "#f57c00" },
	{ key: "recall", label: "Recall", color: "#388e3c" },
	{ key: "f1_score", label: "F1 Score", color: "#d32f2f" },
];

export const MLModelComparison = () => {
	const { modelList, isLoading: isListLoading } = useMLModel();
	const [selectedVersions, setSelectedVersions] = useState<string[]>([]);

	// Fetch comparison data (only when versions selected)
	const { isLoading: isComparisonLoading, error: comparisonError } =
		useModelComparison(
			"accuracy",
			selectedVersions.length > 0 ? selectedVersions : undefined,
			selectedVersions.length > 0,
		);

	// Handle version selection
	const handleVersionToggle = (version: string) => {
		setSelectedVersions((prev) =>
			prev.includes(version)
				? prev.filter((v) => v !== version)
				: [...prev, version],
		);
	};

	const handleSelectAll = () => {
		if (selectedVersions.length === modelList?.models?.length) {
			setSelectedVersions([]);
		} else {
			setSelectedVersions(
				modelList?.models?.map((m) => m.version).filter(Boolean) as string[],
			);
		}
	};

	// Prepare chart data from selected models
	const chartData = useMemo(() => {
		if (!modelList?.models) return [];

		return modelList.models
			.filter((m) => selectedVersions.includes(m.version))
			.map((model) => ({
				version: model.version,
				accuracy: (model.metrics?.accuracy || 0) * 100,
				precision: (model.metrics?.precision || 0) * 100,
				recall: (model.metrics?.recall || 0) * 100,
				f1_score: (model.metrics?.f1_score || 0) * 100,
			}));
	}, [modelList, selectedVersions]);

	// Loading state
	if (isListLoading) {
		return (
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
		);
	}

	// Empty state
	if (!modelList?.models || modelList.models.length === 0) {
		return (
			<Alert severity="info">
				비교할 모델이 없습니다. 먼저 모델을 학습하세요.
			</Alert>
		);
	}

	return (
		<Box sx={{ flexGrow: 1 }}>
			{/* Header */}
			<Box sx={{ mb: 3 }}>
				<Typography variant="h5" component="h2" gutterBottom>
					모델 성능 비교
				</Typography>
				<Typography variant="body2" color="text.secondary">
					여러 모델의 성능 지표를 비교하여 최적의 모델을 선택하세요
				</Typography>
			</Box>

			<Grid container spacing={3}>
				{/* Model Selection Panel */}
				<Grid size={{ xs: 12, md: 4 }}>
					<Card>
						<CardContent>
							<Box
								sx={{
									display: "flex",
									justifyContent: "space-between",
									alignItems: "center",
									mb: 2,
								}}
							>
								<Typography variant="h6">모델 선택</Typography>
								<Button size="small" onClick={handleSelectAll}>
									{selectedVersions.length === modelList?.models?.length
										? "전체 해제"
										: "전체 선택"}
								</Button>
							</Box>

							<Stack spacing={1}>
								{modelList.models.map((model) => (
									<FormControlLabel
										key={model.version}
										control={
											<Checkbox
												checked={selectedVersions.includes(model.version)}
												onChange={() => handleVersionToggle(model.version)}
											/>
										}
										label={
											<Box
												sx={{
													display: "flex",
													alignItems: "center",
													gap: 1,
												}}
											>
												<Chip label={model.version} size="small" />
												<Typography variant="body2" color="text.secondary">
													{((model.metrics?.accuracy || 0) * 100).toFixed(2)}%
												</Typography>
											</Box>
										}
									/>
								))}
							</Stack>

							<Box sx={{ mt: 2 }}>
								<Typography variant="caption" color="text.secondary">
									선택된 모델: {selectedVersions.length}개
								</Typography>
							</Box>
						</CardContent>
					</Card>
				</Grid>

				{/* Comparison Results */}
				<Grid size={{ xs: 12, md: 8 }}>
					{selectedVersions.length === 0 ? (
						<Card>
							<CardContent>
								<Box sx={{ textAlign: "center", py: 8 }}>
									<CompareArrowsIcon
										sx={{ fontSize: 64, color: "text.secondary", mb: 2 }}
									/>
									<Typography variant="h6" color="text.secondary" gutterBottom>
										모델을 선택하세요
									</Typography>
									<Typography variant="body2" color="text.secondary">
										좌측에서 비교할 모델을 선택하면 성능 비교 차트가 표시됩니다
									</Typography>
								</Box>
							</CardContent>
						</Card>
					) : (
						<Stack spacing={3}>
							{/* Comparison Chart */}
							<Card>
								<CardContent>
									<Typography variant="h6" gutterBottom>
										성능 지표 비교
									</Typography>

									{isComparisonLoading ? (
										<Box
											sx={{
												display: "flex",
												justifyContent: "center",
												py: 4,
											}}
										>
											<CircularProgress />
										</Box>
									) : comparisonError ? (
										<Alert severity="error">{comparisonError.message}</Alert>
									) : (
										<ResponsiveContainer width="100%" height={400}>
											<BarChart data={chartData}>
												<CartesianGrid strokeDasharray="3 3" />
												<XAxis dataKey="version" />
												<YAxis domain={[0, 100]} />
												<Tooltip
													formatter={(value: number) => `${value.toFixed(2)}%`}
												/>
												<Legend />
												{METRICS.map((metric) => (
													<Bar
														key={metric.key}
														dataKey={metric.key}
														fill={metric.color}
														name={metric.label}
													/>
												))}
											</BarChart>
										</ResponsiveContainer>
									)}
								</CardContent>
							</Card>

							{/* Comparison Table */}
							<Card>
								<CardContent>
									<Typography variant="h6" gutterBottom>
										상세 비교표
									</Typography>

									<TableContainer component={Paper} variant="outlined">
										<Table size="small">
											<TableHead>
												<TableRow>
													<TableCell>
														<strong>모델 버전</strong>
													</TableCell>
													<TableCell align="right">
														<strong>Accuracy</strong>
													</TableCell>
													<TableCell align="right">
														<strong>Precision</strong>
													</TableCell>
													<TableCell align="right">
														<strong>Recall</strong>
													</TableCell>
													<TableCell align="right">
														<strong>F1 Score</strong>
													</TableCell>
													<TableCell align="right">
														<strong>특징 수</strong>
													</TableCell>
												</TableRow>
											</TableHead>
											<TableBody>
												{modelList.models
													.filter((m) => selectedVersions.includes(m.version))
													.map((model) => (
														<TableRow key={model.version}>
															<TableCell>
																<Chip label={model.version} size="small" />
															</TableCell>
															<TableCell align="right">
																{((model.metrics?.accuracy || 0) * 100).toFixed(
																	2,
																)}
																%
															</TableCell>
															<TableCell align="right">
																{(
																	(model.metrics?.precision || 0) * 100
																).toFixed(2)}
																%
															</TableCell>
															<TableCell align="right">
																{((model.metrics?.recall || 0) * 100).toFixed(
																	2,
																)}
																%
															</TableCell>
															<TableCell align="right">
																{((model.metrics?.f1_score || 0) * 100).toFixed(
																	2,
																)}
																%
															</TableCell>
															<TableCell align="right">
																{model.feature_count}개
															</TableCell>
														</TableRow>
													))}
											</TableBody>
										</Table>
									</TableContainer>

									{/* Best Model Indicator */}
									<Box sx={{ mt: 2 }}>
										<Alert severity="success">
											<Typography variant="body2">
												<strong>최고 성능 모델:</strong>{" "}
												{chartData.reduce(
													(best, current) =>
														current.accuracy > best.accuracy ? current : best,
													chartData[0],
												)?.version || "N/A"}{" "}
												(Accuracy 기준)
											</Typography>
										</Alert>
									</Box>
								</CardContent>
							</Card>
						</Stack>
					)}
				</Grid>
			</Grid>
		</Box>
	);
};
