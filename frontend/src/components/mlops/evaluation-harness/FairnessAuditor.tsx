/**
 * FairnessAuditor Component
 *
 * Detects and visualizes model bias and fairness issues with:
 * - Fairness metrics radar chart
 * - Group-wise performance comparison
 * - Bias severity alerts
 * - Remediation recommendations
 *
 * @module components/mlops/evaluation-harness/FairnessAuditor
 */

import {
	useEvaluationHarness,
	useFairnessReport,
	type FairnessAuditRequest,
} from "@/hooks/useEvaluationHarness";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import {
	Alert,
	Box,
	Button,
	Card,
	CardContent,
	Chip,
	CircularProgress,
	Dialog,
	DialogActions,
	DialogContent,
	DialogTitle,
	FormControl,
	InputLabel,
	MenuItem,
	Paper,
	Select,
	Table,
	TableBody,
	TableCell,
	TableContainer,
	TableHead,
	TableRow,
	Typography,
	type SelectChangeEvent,
} from "@mui/material";
import { useState } from "react";
import {
	Legend,
	PolarAngleAxis,
	PolarGrid,
	PolarRadiusAxis,
	Radar,
	RadarChart,
	ResponsiveContainer,
} from "recharts";

// ============================================================================
// Component Props
// ============================================================================

interface FairnessAuditorProps {
	/**
	 * Optional report ID to display
	 */
	reportId?: string | null;

	/**
	 * Available models for fairness audit
	 */
	availableModels?: {
		id: string;
		name: string;
		version: string;
	}[];

	/**
	 * Available protected attributes
	 */
	protectedAttributes?: string[];
}

// ============================================================================
// Component Implementation
// ============================================================================

export const FairnessAuditor: React.FC<FairnessAuditorProps> = ({
	reportId: initialReportId,
	availableModels = [],
	protectedAttributes = ["gender", "age", "race", "ethnicity"],
}) => {
	// ============================================================================
	// State
	// ============================================================================

	const [requestDialogOpen, setRequestDialogOpen] = useState(false);
	const [selectedReportId, setSelectedReportId] = useState<string | null>(
		initialReportId || null,
	);

	const [auditRequest, setAuditRequest] = useState<FairnessAuditRequest>({
		model_id: "",
		protected_attributes: [],
		fairness_threshold: 0.8,
	});

	// ============================================================================
	// Hooks
	// ============================================================================

	const {
		fairnessList,
		isLoadingFairness,
		requestFairnessAudit,
		isRequestingAudit,
	} = useEvaluationHarness();

	const { fairnessReport } = useFairnessReport(selectedReportId);

	// ============================================================================
	// Event Handlers
	// ============================================================================

	const handleRequestClick = () => {
		setAuditRequest({
			model_id: "",
			protected_attributes: [],
			fairness_threshold: 0.8,
		});
		setRequestDialogOpen(true);
	};

	const handleRequestSubmit = async () => {
		try {
			const report = await requestFairnessAudit(auditRequest);
			// FairnessReportResponse doesn't have id field, use model_id + created_at as identifier
			setSelectedReportId(report.model_id);
			setRequestDialogOpen(false);
		} catch (error) {
			console.error("Request fairness audit error:", error);
		}
	};

	const handleReportSelect = (event: SelectChangeEvent<string>) => {
		setSelectedReportId(event.target.value);
	};

	// ============================================================================
	// Helper Functions
	// ============================================================================

	const getRadarChartData = () => {
		if (!fairnessReport?.group_metrics) return [];

		// group_metrics is dict[str, dict[str, float]]
		// Flatten to extract some metrics
		const allMetrics: Array<{ metric: string; value: number }> = [];
		Object.entries(fairnessReport.group_metrics).forEach(([group, metrics]) => {
			Object.entries(metrics as Record<string, number>).forEach(
				([key, val]) => {
					allMetrics.push({
						metric: `${group}_${key}`,
						value: val,
					});
				},
			);
		});

		return allMetrics.slice(0, 6).map((item) => ({
			metric: item.metric,
			value: item.value,
			fullMark: 1.0,
		}));
	};

	// ============================================================================
	// Render Loading State
	// ============================================================================

	if (isLoadingFairness) {
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
	// Render
	// ============================================================================

	return (
		<>
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
								공정성 감사
							</Typography>
							<Typography variant="body2" color="text.secondary">
								모델의 편향성과 공정성을 분석합니다
							</Typography>
						</Box>
						<Box sx={{ display: "flex", gap: 1 }}>
							{fairnessList.length > 0 && (
								<FormControl size="small" sx={{ minWidth: 200 }}>
									<InputLabel>리포트 선택</InputLabel>
									<Select
										value={selectedReportId || ""}
										label="리포트 선택"
										onChange={handleReportSelect}
									>
										{fairnessList.map((report: any) => (
											<MenuItem key={report.id} value={report.id}>
												{report.model_name} - {report.created_at}
											</MenuItem>
										))}
									</Select>
								</FormControl>
							)}
							<Button
								variant="contained"
								startIcon={<PlayArrowIcon />}
								onClick={handleRequestClick}
							>
								감사 요청
							</Button>
						</Box>
					</Box>

					{/* Fairness Report */}
					{selectedReportId && fairnessReport ? (
						<Box>
							{/* Overall Fairness Status */}
							<Box sx={{ mb: 3 }}>
								<Alert severity={fairnessReport.passed ? "success" : "warning"}>
									<Typography variant="body2">
										<strong>
											공정성 평가: {fairnessReport.passed ? "통과" : "실패"}
										</strong>
									</Typography>
									<Typography variant="caption">
										전체 공정성 점수:{" "}
										{(fairnessReport.overall_fairness_score * 100).toFixed(1)}%
									</Typography>
								</Alert>
							</Box>

							{/* Fairness Metrics Radar Chart */}
							<Box sx={{ mb: 3 }}>
								<Typography variant="h6" gutterBottom>
									공정성 메트릭
								</Typography>
								<Box sx={{ height: 400 }}>
									<ResponsiveContainer width="100%" height="100%">
										<RadarChart data={getRadarChartData()}>
											<PolarGrid />
											<PolarAngleAxis dataKey="metric" />
											<PolarRadiusAxis domain={[0, 1]} />
											<Radar
												name="공정성 점수"
												dataKey="value"
												stroke="#8884d8"
												fill="#8884d8"
												fillOpacity={0.6}
											/>
											<Legend />
										</RadarChart>
									</ResponsiveContainer>
								</Box>
								<Typography variant="caption" color="text.secondary">
									* 1.0에 가까울수록 공정함
								</Typography>
							</Box>

							{/* Group Metrics Table */}
							<Box sx={{ mb: 3 }}>
								<Typography variant="h6" gutterBottom>
									그룹별 성능 비교
								</Typography>
								<TableContainer component={Paper} variant="outlined">
									<Table>
										<TableHead>
											<TableRow>
												<TableCell>그룹</TableCell>
												<TableCell align="right">정확도</TableCell>
												<TableCell align="right">정밀도</TableCell>
												<TableCell align="right">재현율</TableCell>
												<TableCell align="right">FPR</TableCell>
												<TableCell align="right">FNR</TableCell>
											</TableRow>
										</TableHead>
										<TableBody>
											{Object.entries(fairnessReport.group_metrics).map(
												([group, metrics]: [string, unknown]) => {
													const groupMetrics = metrics as {
														accuracy: number;
														precision: number;
														recall: number;
														fpr: number;
														fnr: number;
													};
													return (
														<TableRow key={group}>
															<TableCell>
																<strong>{group}</strong>
															</TableCell>
															<TableCell align="right">
																{groupMetrics.accuracy.toFixed(4)}
															</TableCell>
															<TableCell align="right">
																{groupMetrics.precision.toFixed(4)}
															</TableCell>
															<TableCell align="right">
																{groupMetrics.recall.toFixed(4)}
															</TableCell>
															<TableCell align="right">
																{groupMetrics.fpr.toFixed(4)}
															</TableCell>
															<TableCell align="right">
																{groupMetrics.fnr.toFixed(4)}
															</TableCell>
														</TableRow>
													);
												},
											)}
										</TableBody>
									</Table>
								</TableContainer>
							</Box>

							{/* Recommendations */}
							{fairnessReport.recommendations &&
								fairnessReport.recommendations.length > 0 && (
									<Box sx={{ mb: 3 }}>
										<Typography variant="h6" gutterBottom>
											권장 사항
										</Typography>
										<Box
											sx={{ display: "flex", flexDirection: "column", gap: 1 }}
										>
											{fairnessReport.recommendations.map(
												(rec: string, index: number) => (
													<Alert
														key={`rec-${index.toString()}`}
														severity="info"
														variant="outlined"
													>
														{rec}
													</Alert>
												),
											)}
										</Box>
									</Box>
								)}

							{/* Protected Attributes */}
							<Box>
								<Typography variant="subtitle2" gutterBottom>
									감사 정보
								</Typography>
								<Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
									<Box
										sx={{ display: "flex", justifyContent: "space-between" }}
									>
										<Typography variant="body2" color="text.secondary">
											보호 속성
										</Typography>
										<Box sx={{ display: "flex", gap: 0.5 }}>
											{fairnessReport.protected_attributes.map(
												(attr: string) => (
													<Chip key={attr} label={attr} size="small" />
												),
											)}
										</Box>
									</Box>
									<Box
										sx={{ display: "flex", justifyContent: "space-between" }}
									>
										<Typography variant="body2" color="text.secondary">
											전체 공정성 점수
										</Typography>
										<Typography variant="body2">
											{(fairnessReport.overall_fairness_score * 100).toFixed(1)}
											%
										</Typography>
									</Box>
									<Box
										sx={{ display: "flex", justifyContent: "space-between" }}
									>
										<Typography variant="body2" color="text.secondary">
											생성일
										</Typography>
										<Typography variant="body2">
											{new Date(fairnessReport.created_at).toLocaleString(
												"ko-KR",
											)}
										</Typography>
									</Box>
								</Box>
							</Box>
						</Box>
					) : (
						<Alert severity="info">
							공정성 리포트를 선택하거나 새로 요청하세요
						</Alert>
					)}
				</CardContent>
			</Card>

			{/* Request Fairness Audit Dialog */}
			<Dialog
				open={requestDialogOpen}
				onClose={() => setRequestDialogOpen(false)}
				maxWidth="sm"
				fullWidth
			>
				<DialogTitle>공정성 감사 요청</DialogTitle>
				<DialogContent>
					<Box sx={{ display: "flex", flexDirection: "column", gap: 2, mt: 1 }}>
						<FormControl fullWidth required>
							<InputLabel>모델</InputLabel>
							<Select
								value={auditRequest.model_id}
								label="모델"
								onChange={(e) =>
									setAuditRequest({ ...auditRequest, model_id: e.target.value })
								}
							>
								{availableModels.map((model) => (
									<MenuItem key={model.id} value={model.id}>
										{model.name} ({model.version})
									</MenuItem>
								))}
							</Select>
						</FormControl>

						<FormControl fullWidth required>
							<InputLabel>보호 속성</InputLabel>
							<Select
								multiple
								value={auditRequest.protected_attributes}
								label="보호 속성"
								onChange={(e) =>
									setAuditRequest({
										...auditRequest,
										protected_attributes:
											typeof e.target.value === "string"
												? e.target.value.split(",")
												: e.target.value,
									})
								}
								renderValue={(selected: string[]) => (
									<Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5 }}>
										{selected.map((value: string) => (
											<Chip key={value} label={value} size="small" />
										))}
									</Box>
								)}
							>
								{protectedAttributes.map((attr) => (
									<MenuItem key={attr} value={attr}>
										{attr}
									</MenuItem>
								))}
							</Select>
						</FormControl>

						<FormControl fullWidth>
							<InputLabel>공정성 임계값</InputLabel>
							<Select
								value={auditRequest.fairness_threshold}
								label="공정성 임계값"
								onChange={(e) =>
									setAuditRequest({
										...auditRequest,
										fairness_threshold: Number(e.target.value),
									})
								}
							>
								<MenuItem value={0.7}>0.7 (낮음)</MenuItem>
								<MenuItem value={0.8}>0.8 (중간)</MenuItem>
								<MenuItem value={0.9}>0.9 (높음)</MenuItem>
								<MenuItem value={0.95}>0.95 (매우 높음)</MenuItem>
							</Select>
						</FormControl>
					</Box>
				</DialogContent>
				<DialogActions>
					<Button onClick={() => setRequestDialogOpen(false)}>취소</Button>
					<Button
						variant="contained"
						onClick={handleRequestSubmit}
						disabled={
							isRequestingAudit ||
							!auditRequest.model_id ||
							auditRequest.protected_attributes.length === 0
						}
					>
						{isRequestingAudit ? "요청 중..." : "요청"}
					</Button>
				</DialogActions>
			</Dialog>
		</>
	);
};
