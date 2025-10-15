/**
 * BenchmarkSuite Component
 *
 * Displays and manages benchmark test suites with:
 * - Benchmark list table with status and last run info
 * - Run button with progress tracking
 * - Create benchmark dialog
 * - Test case configuration
 *
 * @module components/mlops/evaluation-harness/BenchmarkSuite
 */

import {
	useBenchmarkDetail,
	useBenchmarkRun,
	useEvaluationHarness,
	type BenchmarkCreate,
} from "@/hooks/useEvaluationHarness";
import AddIcon from "@mui/icons-material/Add";
import DeleteIcon from "@mui/icons-material/Delete";
import InfoIcon from "@mui/icons-material/Info";
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
	IconButton,
	LinearProgress,
	Paper,
	Table,
	TableBody,
	TableCell,
	TableContainer,
	TableHead,
	TableRow,
	TextField,
	Tooltip,
	Typography,
} from "@mui/material";
import { useState } from "react";

// ============================================================================
// Component Props
// ============================================================================

interface BenchmarkSuiteProps {
	/**
	 * Optional model ID to run benchmarks against
	 */
	modelId?: string;

	/**
	 * Callback when benchmark is selected
	 */
	onBenchmarkSelect?: (benchmarkId: string) => void;
}

// ============================================================================
// Component Implementation
// ============================================================================

export const BenchmarkSuite: React.FC<BenchmarkSuiteProps> = ({
	modelId,
	onBenchmarkSelect,
}) => {
	// ============================================================================
	// State
	// ============================================================================

	const [createDialogOpen, setCreateDialogOpen] = useState(false);
	const [selectedBenchmarkId, setSelectedBenchmarkId] = useState<string | null>(
		null,
	);
	const [runDialogOpen, setRunDialogOpen] = useState(false);
	const [activeRunId, setActiveRunId] = useState<string | null>(null);

	// Form state for creating benchmarks
	const [newBenchmark, setNewBenchmark] = useState<BenchmarkCreate>({
		name: "",
		description: "",
		test_cases: [],
	});

	const [newTestCase, setNewTestCase] = useState({
		name: "",
		description: "",
		expected_metrics: {} as Record<string, number>,
	});

	// ============================================================================
	// Hooks
	// ============================================================================

	const {
		benchmarksList,
		isLoadingBenchmarks,
		createBenchmark,
		isCreatingBenchmark,
		runBenchmark,
		isRunningBenchmark,
	} = useEvaluationHarness();

	const { benchmarkDetail } = useBenchmarkDetail(selectedBenchmarkId);

	const { benchmarkRun } = useBenchmarkRun(activeRunId);

	// ============================================================================
	// Event Handlers
	// ============================================================================

	const handleCreateClick = () => {
		setNewBenchmark({
			name: "",
			description: "",
			test_cases: [],
		});
		setCreateDialogOpen(true);
	};

	const handleCreateSubmit = async () => {
		try {
			await createBenchmark(newBenchmark);
			setCreateDialogOpen(false);
		} catch (error) {
			// Error handled by mutation
			console.error("Create benchmark error:", error);
		}
	};

	const handleAddTestCase = () => {
		if (newTestCase.name) {
			setNewBenchmark({
				...newBenchmark,
				test_cases: [...newBenchmark.test_cases, { ...newTestCase }],
			});
			setNewTestCase({
				name: "",
				description: "",
				expected_metrics: {},
			});
		}
	};

	const handleRemoveTestCase = (index: number) => {
		setNewBenchmark({
			...newBenchmark,
			test_cases: newBenchmark.test_cases.filter((_, i) => i !== index),
		});
	};

	const handleRunClick = (benchmarkId: string) => {
		setSelectedBenchmarkId(benchmarkId);
		setRunDialogOpen(true);
	};

	const handleRunSubmit = async () => {
		if (!selectedBenchmarkId || !modelId) return;

		try {
			const run = await runBenchmark({
				benchmark_id: selectedBenchmarkId,
				model_id: modelId,
			});
			setActiveRunId(run.id);
			setRunDialogOpen(false);
		} catch (error) {
			console.error("Run benchmark error:", error);
		}
	};

	const handleBenchmarkClick = (benchmarkId: string) => {
		setSelectedBenchmarkId(benchmarkId);
		onBenchmarkSelect?.(benchmarkId);
	};

	// ============================================================================
	// Helper Functions
	// ============================================================================

	const getStatusColor = (
		status: "draft" | "active" | "archived",
	): "default" | "success" | "warning" => {
		const colorMap = {
			draft: "default" as const,
			active: "success" as const,
			archived: "warning" as const,
		};
		return colorMap[status] || "default";
	};

	const getStatusLabel = (status: "draft" | "active" | "archived"): string => {
		const labelMap = {
			draft: "초안",
			active: "활성",
			archived: "아카이브",
		};
		return labelMap[status] || status;
	};

	const getLastRunStatusColor = (
		status?: "success" | "failed" | "partial",
	): "success" | "error" | "warning" | "default" => {
		if (!status) return "default";
		const colorMap = {
			success: "success" as const,
			failed: "error" as const,
			partial: "warning" as const,
		};
		return colorMap[status] || "default";
	};

	// ============================================================================
	// Render Loading State
	// ============================================================================

	if (isLoadingBenchmarks) {
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
								벤치마크 Suite
							</Typography>
							<Typography variant="body2" color="text.secondary">
								모델 성능을 표준 테스트로 평가합니다
							</Typography>
						</Box>
						<Button
							variant="contained"
							startIcon={<AddIcon />}
							onClick={handleCreateClick}
						>
							벤치마크 생성
						</Button>
					</Box>

					{/* Active Benchmark Run Progress */}
					{benchmarkRun && benchmarkRun.status !== "completed" && (
						<Alert
							severity="info"
							sx={{ mb: 2 }}
							icon={<CircularProgress size={20} />}
						>
							<Typography variant="body2" gutterBottom>
								벤치마크 실행 중: {benchmarkRun.progress}% 완료
							</Typography>
							<LinearProgress
								variant="determinate"
								value={benchmarkRun.progress}
							/>
						</Alert>
					)}

					{/* Benchmarks Table */}
					{benchmarksList.length > 0 ? (
						<TableContainer component={Paper} variant="outlined">
							<Table>
								<TableHead>
									<TableRow>
										<TableCell>이름</TableCell>
										<TableCell>테스트 수</TableCell>
										<TableCell>상태</TableCell>
										<TableCell>마지막 실행</TableCell>
										<TableCell>실행 결과</TableCell>
										<TableCell align="right">액션</TableCell>
									</TableRow>
								</TableHead>
								<TableBody>
									{benchmarksList.map((benchmark) => (
										<TableRow
											key={benchmark.id}
											hover
											onClick={() => handleBenchmarkClick(benchmark.id)}
											sx={{ cursor: "pointer" }}
										>
											<TableCell>
												<Typography variant="body2" fontWeight="medium">
													{benchmark.name}
												</Typography>
												<Typography variant="caption" color="text.secondary">
													{benchmark.description}
												</Typography>
											</TableCell>
											<TableCell>
												<Chip
													label={benchmark.test_count}
													size="small"
													variant="outlined"
												/>
											</TableCell>
											<TableCell>
												<Chip
													label={getStatusLabel(benchmark.status)}
													color={getStatusColor(benchmark.status)}
													size="small"
												/>
											</TableCell>
											<TableCell>
												{benchmark.last_run_at ? (
													<Typography variant="caption">
														{new Date(benchmark.last_run_at).toLocaleString(
															"ko-KR",
														)}
													</Typography>
												) : (
													<Typography variant="caption" color="text.secondary">
														실행 기록 없음
													</Typography>
												)}
											</TableCell>
											<TableCell>
												{benchmark.last_run_status ? (
													<Chip
														label={benchmark.last_run_status.toUpperCase()}
														color={getLastRunStatusColor(
															benchmark.last_run_status,
														)}
														size="small"
													/>
												) : (
													<Typography variant="caption" color="text.secondary">
														-
													</Typography>
												)}
											</TableCell>
											<TableCell align="right">
												<Tooltip title="벤치마크 실행">
													<IconButton
														size="small"
														color="primary"
														onClick={(e) => {
															e.stopPropagation();
															handleRunClick(benchmark.id);
														}}
														disabled={!modelId}
													>
														<PlayArrowIcon />
													</IconButton>
												</Tooltip>
												<Tooltip title="상세 정보">
													<IconButton
														size="small"
														onClick={(e) => {
															e.stopPropagation();
															handleBenchmarkClick(benchmark.id);
														}}
													>
														<InfoIcon />
													</IconButton>
												</Tooltip>
											</TableCell>
										</TableRow>
									))}
								</TableBody>
							</Table>
						</TableContainer>
					) : (
						<Alert severity="info">
							등록된 벤치마크가 없습니다. 새 벤치마크를 생성해보세요.
						</Alert>
					)}

					{/* Selected Benchmark Detail */}
					{selectedBenchmarkId && benchmarkDetail && (
						<Box sx={{ mt: 3 }}>
							<Typography variant="h6" gutterBottom>
								벤치마크 상세
							</Typography>
							<Box sx={{ display: "flex", gap: 2, flexWrap: "wrap" }}>
								<Card variant="outlined" sx={{ flex: 1, minWidth: 200 }}>
									<CardContent>
										<Typography variant="body2" color="text.secondary">
											테스트된 모델 수
										</Typography>
										<Typography variant="h5">
											{benchmarkDetail.models_tested}
										</Typography>
									</CardContent>
								</Card>
								<Card variant="outlined" sx={{ flex: 1, minWidth: 200 }}>
									<CardContent>
										<Typography variant="body2" color="text.secondary">
											평균 점수
										</Typography>
										<Typography variant="h5">
											{(benchmarkDetail.average_score * 100).toFixed(1)}%
										</Typography>
									</CardContent>
								</Card>
							</Box>
						</Box>
					)}
				</CardContent>
			</Card>

			{/* Create Benchmark Dialog */}
			<Dialog
				open={createDialogOpen}
				onClose={() => setCreateDialogOpen(false)}
				maxWidth="md"
				fullWidth
			>
				<DialogTitle>새 벤치마크 생성</DialogTitle>
				<DialogContent>
					<Box sx={{ display: "flex", flexDirection: "column", gap: 2, mt: 1 }}>
						<TextField
							label="벤치마크 이름"
							value={newBenchmark.name}
							onChange={(e) =>
								setNewBenchmark({ ...newBenchmark, name: e.target.value })
							}
							fullWidth
							required
						/>
						<TextField
							label="설명"
							value={newBenchmark.description}
							onChange={(e) =>
								setNewBenchmark({
									...newBenchmark,
									description: e.target.value,
								})
							}
							fullWidth
							multiline
							rows={2}
						/>

						<Typography variant="subtitle2" sx={{ mt: 2 }}>
							테스트 케이스 ({newBenchmark.test_cases.length})
						</Typography>

						{newBenchmark.test_cases.map((testCase, index) => (
							<Box
								key={index}
								sx={{
									display: "flex",
									alignItems: "center",
									gap: 1,
									p: 1,
									bgcolor: "grey.100",
									borderRadius: 1,
								}}
							>
								<Box sx={{ flex: 1 }}>
									<Typography variant="body2">{testCase.name}</Typography>
									<Typography variant="caption" color="text.secondary">
										{testCase.description}
									</Typography>
								</Box>
								<IconButton
									size="small"
									onClick={() => handleRemoveTestCase(index)}
								>
									<DeleteIcon fontSize="small" />
								</IconButton>
							</Box>
						))}

						<Box
							sx={{
								display: "flex",
								gap: 1,
								alignItems: "flex-start",
								mt: 1,
							}}
						>
							<TextField
								label="테스트 이름"
								value={newTestCase.name}
								onChange={(e) =>
									setNewTestCase({ ...newTestCase, name: e.target.value })
								}
								size="small"
								sx={{ flex: 1 }}
							/>
							<TextField
								label="설명"
								value={newTestCase.description}
								onChange={(e) =>
									setNewTestCase({
										...newTestCase,
										description: e.target.value,
									})
								}
								size="small"
								sx={{ flex: 1 }}
							/>
							<Button
								variant="outlined"
								onClick={handleAddTestCase}
								disabled={!newTestCase.name}
							>
								추가
							</Button>
						</Box>
					</Box>
				</DialogContent>
				<DialogActions>
					<Button onClick={() => setCreateDialogOpen(false)}>취소</Button>
					<Button
						variant="contained"
						onClick={handleCreateSubmit}
						disabled={
							isCreatingBenchmark ||
							!newBenchmark.name ||
							newBenchmark.test_cases.length === 0
						}
					>
						{isCreatingBenchmark ? "생성 중..." : "생성"}
					</Button>
				</DialogActions>
			</Dialog>

			{/* Run Benchmark Dialog */}
			<Dialog
				open={runDialogOpen}
				onClose={() => setRunDialogOpen(false)}
				maxWidth="sm"
				fullWidth
			>
				<DialogTitle>벤치마크 실행</DialogTitle>
				<DialogContent>
					<Typography>
						선택한 모델에 대해 벤치마크를 실행하시겠습니까?
					</Typography>
					{!modelId && (
						<Alert severity="warning" sx={{ mt: 2 }}>
							모델을 먼저 선택해주세요
						</Alert>
					)}
				</DialogContent>
				<DialogActions>
					<Button onClick={() => setRunDialogOpen(false)}>취소</Button>
					<Button
						variant="contained"
						onClick={handleRunSubmit}
						disabled={isRunningBenchmark || !modelId}
						startIcon={<PlayArrowIcon />}
					>
						{isRunningBenchmark ? "시작 중..." : "실행"}
					</Button>
				</DialogActions>
			</Dialog>
		</>
	);
};
