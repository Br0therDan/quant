/**
 * ABTestingPanel Component
 *
 * Manages A/B testing for model comparison with:
 * - Stepper for test stages (Setup → Run → Analyze → Decide)
 * - Traffic split configuration
 * - Statistical significance testing
 * - Model comparison results
 *
 * @module components/mlops/evaluation-harness/ABTestingPanel
 */

import {
	useABTestDetail,
	useEvaluationHarness,
	type ABTestCreate,
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
	LinearProgress,
	MenuItem,
	Select,
	TextField,
	Typography,
	type SelectChangeEvent,
} from "@mui/material";
import Grid from "@mui/material/Grid";
import { useState } from "react";

// ============================================================================
// Component Props
// ============================================================================

interface ABTestingPanelProps {
	/**
	 * Optional A/B test ID to display
	 */
	testId?: string | null;

	/**
	 * Available models for A/B testing
	 */
	availableModels?: {
		id: string;
		name: string;
		version: string;
	}[];
}

// ============================================================================
// Component Implementation
// ============================================================================

export const ABTestingPanel: React.FC<ABTestingPanelProps> = ({
	testId: initialTestId,
	availableModels = [],
}) => {
	// ============================================================================
	// State
	// ============================================================================

	const [createDialogOpen, setCreateDialogOpen] = useState(false);
	const [selectedTestId, setSelectedTestId] = useState<string | null>(
		initialTestId || null,
	);

	const [newTest, setNewTest] = useState<ABTestCreate>({
		name: "",
		description: "",
		model_a_id: "",
		model_b_id: "",
		traffic_split_a: 50,
		sample_size: 1000,
		confidence_level: 0.95,
	});

	// ============================================================================
	// Hooks
	// ============================================================================

	const { abTestsList, isLoadingABTests, createABTest, isCreatingABTest } =
		useEvaluationHarness();

	const { abTestDetail } = useABTestDetail(selectedTestId); // ============================================================================
	// Event Handlers
	// ============================================================================

	const handleCreateClick = () => {
		setNewTest({
			name: "",
			description: "",
			model_a_id: "",
			model_b_id: "",
			traffic_split_a: 50,
			sample_size: 1000,
			confidence_level: 0.95,
		});
		setCreateDialogOpen(true);
	};

	const handleCreateSubmit = async () => {
		try {
			const test = await createABTest(newTest);
			setSelectedTestId(test.name); // Use name as ID (no id field)
			setCreateDialogOpen(false);
		} catch (error) {
			console.error("Create A/B test error:", error);
		}
	};

	const handleTestSelect = (event: SelectChangeEvent<string>) => {
		setSelectedTestId(event.target.value);
	};

	// ============================================================================
	// Helper Functions
	// ============================================================================

	const getStatusColor = (
		status: string,
	): "default" | "primary" | "secondary" | "success" => {
		const statusLower = status.toLowerCase();
		const colorMap: Record<
			string,
			"default" | "primary" | "secondary" | "success"
		> = {
			pending: "default",
			running: "primary",
			analyzing: "secondary",
			completed: "success",
		};
		return colorMap[statusLower] || "default";
	};

	// ============================================================================
	// Render Loading State
	// ============================================================================

	if (isLoadingABTests) {
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
								A/B 테스팅
							</Typography>
							<Typography variant="body2" color="text.secondary">
								두 모델의 성능을 통계적으로 비교합니다
							</Typography>
						</Box>
						<Box sx={{ display: "flex", gap: 1 }}>
							{abTestsList.length > 0 && (
								<FormControl size="small" sx={{ minWidth: 200 }}>
									<InputLabel>테스트 선택</InputLabel>
									<Select
										value={selectedTestId || ""}
										label="테스트 선택"
										onChange={handleTestSelect}
									>
										{abTestsList.map((test) => (
											<MenuItem key={test.name} value={test.name}>
												{test.name}
											</MenuItem>
										))}
									</Select>
								</FormControl>
							)}
							<Button
								variant="contained"
								startIcon={<PlayArrowIcon />}
								onClick={handleCreateClick}
							>
								새 테스트 생성
							</Button>
						</Box>
					</Box>

					{/* A/B Test Detail */}
					{selectedTestId && abTestDetail ? (
						<Box>
							{/* Test Info */}
							<Box sx={{ mb: 3 }}>
								<Box
									sx={{
										display: "flex",
										justifyContent: "space-between",
										alignItems: "center",
										mb: 2,
									}}
								>
									<Typography variant="h6">{abTestDetail.name}</Typography>
									<Chip
										label={abTestDetail.status.toUpperCase()}
										color={getStatusColor(abTestDetail.status)}
									/>
								</Box>
								<Typography variant="body2" color="text.secondary">
									{abTestDetail.description}
								</Typography>
							</Box>

							{/* Test Status Info */}
							<Box sx={{ mb: 3 }}>
								<Alert
									severity={abTestDetail.completed_at ? "success" : "info"}
								>
									<Typography variant="body2">
										상태: {abTestDetail.status} | 샘플 크기:{" "}
										{abTestDetail.sample_size.toLocaleString()} | 신뢰 수준:{" "}
										{(abTestDetail.confidence_level * 100).toFixed(0)}%
									</Typography>
									{abTestDetail.completed_at && (
										<Typography
											variant="caption"
											display="block"
											sx={{ mt: 1 }}
										>
											완료:{" "}
											{new Date(abTestDetail.completed_at).toLocaleString(
												"ko-KR",
											)}
										</Typography>
									)}
								</Alert>
							</Box>

							{/* Progress (if running) */}
							{abTestDetail.status === "running" &&
								!abTestDetail.completed_at && (
									<Box sx={{ mb: 3 }}>
										<Typography variant="body2" gutterBottom>
											테스트 진행 중...
										</Typography>
										<LinearProgress />
									</Box>
								)}

							{/* Model Comparison */}
							<Box sx={{ flexGrow: 1, mb: 3 }}>
								<Grid container spacing={2}>
									<Grid size={{ xs: 12, md: 6 }}>
										<Card variant="outlined">
											<CardContent>
												<Typography variant="subtitle2" gutterBottom>
													Model A
												</Typography>
												<Typography variant="h6">
													{abTestDetail.model_a_id}
												</Typography>
												<Typography variant="caption" color="text.secondary">
													트래픽: {abTestDetail.traffic_split_a.toFixed(1)}%
												</Typography>
											</CardContent>
										</Card>
									</Grid>
									<Grid size={{ xs: 12, md: 6 }}>
										<Card variant="outlined">
											<CardContent>
												<Typography variant="subtitle2" gutterBottom>
													Model B
												</Typography>
												<Typography variant="h6">
													{abTestDetail.model_b_id}
												</Typography>
												<Typography variant="caption" color="text.secondary">
													트래픽:{" "}
													{(100 - abTestDetail.traffic_split_a).toFixed(1)}%
												</Typography>
											</CardContent>
										</Card>
									</Grid>
								</Grid>
							</Box>

							{/* Results (if available) */}
							{abTestDetail.results && (
								<Box sx={{ mb: 3 }}>
									<Typography variant="h6" gutterBottom>
										테스트 결과
									</Typography>
									<Alert severity="info">
										<Typography
											variant="body2"
											component="pre"
											sx={{ whiteSpace: "pre-wrap", wordBreak: "break-word" }}
										>
											{JSON.stringify(abTestDetail.results, null, 2)}
										</Typography>
									</Alert>
									<Typography
										variant="caption"
										color="text.secondary"
										sx={{ mt: 1, display: "block" }}
									>
										* 백엔드에서 상세 메트릭 구조가 정의되면 테이블 형식으로
										표시됩니다
									</Typography>
								</Box>
							)}

							{/* Test Configuration */}
							<Box>
								<Typography variant="subtitle2" gutterBottom>
									테스트 설정
								</Typography>
								<Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
									<Box
										sx={{ display: "flex", justifyContent: "space-between" }}
									>
										<Typography variant="body2" color="text.secondary">
											샘플 크기
										</Typography>
										<Typography variant="body2">
											{abTestDetail.sample_size.toLocaleString()}
										</Typography>
									</Box>
									<Box
										sx={{ display: "flex", justifyContent: "space-between" }}
									>
										<Typography variant="body2" color="text.secondary">
											신뢰 수준
										</Typography>
										<Typography variant="body2">
											{(abTestDetail.confidence_level * 100).toFixed(0)}%
										</Typography>
									</Box>
									<Box
										sx={{ display: "flex", justifyContent: "space-between" }}
									>
										<Typography variant="body2" color="text.secondary">
											생성일
										</Typography>
										<Typography variant="body2">
											{new Date(abTestDetail.created_at).toLocaleString(
												"ko-KR",
											)}
										</Typography>
									</Box>
								</Box>
							</Box>
						</Box>
					) : (
						<Alert severity="info">
							A/B 테스트를 선택하거나 새로 생성하세요
						</Alert>
					)}
				</CardContent>
			</Card>

			{/* Create A/B Test Dialog */}
			<Dialog
				open={createDialogOpen}
				onClose={() => setCreateDialogOpen(false)}
				maxWidth="md"
				fullWidth
			>
				<DialogTitle>새 A/B 테스트 생성</DialogTitle>
				<DialogContent>
					<Box sx={{ display: "flex", flexDirection: "column", gap: 2, mt: 1 }}>
						<TextField
							label="테스트 이름"
							value={newTest.name}
							onChange={(e) => setNewTest({ ...newTest, name: e.target.value })}
							fullWidth
							required
						/>
						<TextField
							label="설명"
							value={newTest.description}
							onChange={(e) =>
								setNewTest({ ...newTest, description: e.target.value })
							}
							fullWidth
							multiline
							rows={2}
						/>
						<FormControl fullWidth required>
							<InputLabel>Model A</InputLabel>
							<Select
								value={newTest.model_a_id}
								label="Model A"
								onChange={(e) =>
									setNewTest({ ...newTest, model_a_id: e.target.value })
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
							<InputLabel>Model B</InputLabel>
							<Select
								value={newTest.model_b_id}
								label="Model B"
								onChange={(e) =>
									setNewTest({ ...newTest, model_b_id: e.target.value })
								}
							>
								{availableModels.map((model) => (
									<MenuItem
										key={model.id}
										value={model.id}
										disabled={model.id === newTest.model_a_id}
									>
										{model.name} ({model.version})
									</MenuItem>
								))}
							</Select>
						</FormControl>
						<TextField
							label="트래픽 분할 (Model A %)"
							type="number"
							value={newTest.traffic_split_a}
							onChange={(e) =>
								setNewTest({
									...newTest,
									traffic_split_a: Number(e.target.value),
								})
							}
							inputProps={{ min: 0, max: 100, step: 5 }}
							fullWidth
							helperText={`Model B: ${100 - (newTest.traffic_split_a || 50)}%`}
						/>{" "}
						<TextField
							label="샘플 크기"
							type="number"
							value={newTest.sample_size}
							onChange={(e) =>
								setNewTest({ ...newTest, sample_size: Number(e.target.value) })
							}
							inputProps={{ min: 100, step: 100 }}
							fullWidth
						/>
						<FormControl fullWidth>
							<InputLabel>신뢰 수준</InputLabel>
							<Select
								value={newTest.confidence_level}
								label="신뢰 수준"
								onChange={(e) =>
									setNewTest({
										...newTest,
										confidence_level: Number(e.target.value),
									})
								}
							>
								<MenuItem value={0.9}>90%</MenuItem>
								<MenuItem value={0.95}>95%</MenuItem>
								<MenuItem value={0.99}>99%</MenuItem>
							</Select>
						</FormControl>
					</Box>
				</DialogContent>
				<DialogActions>
					<Button onClick={() => setCreateDialogOpen(false)}>취소</Button>
					<Button
						variant="contained"
						onClick={handleCreateSubmit}
						disabled={
							isCreatingABTest ||
							!newTest.name ||
							!newTest.model_a_id ||
							!newTest.model_b_id ||
							newTest.model_a_id === newTest.model_b_id
						}
					>
						{isCreatingABTest ? "생성 중..." : "생성"}
					</Button>
				</DialogActions>
			</Dialog>
		</>
	);
};
