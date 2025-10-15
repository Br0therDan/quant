/**
 * ModelRegistry Component
 *
 * Displays registered models in a grid layout with:
 * - Model cards showing name, version, accuracy, status
 * - Model detail dialog
 * - Deployment action button
 * - Status filtering and sorting
 *
 * @module components/mlops/model-lifecycle/ModelRegistry
 */

import {
	useModelDetail,
	useModels,
	type Model,
	type ModelsQueryParams,
} from "@/hooks/useModelLifecycle";
import ArchiveIcon from "@mui/icons-material/Archive";
import RocketLaunchIcon from "@mui/icons-material/RocketLaunch";
import type { SelectChangeEvent } from "@mui/material";
import {
	Alert,
	Box,
	Button,
	Card,
	CardActions,
	CardContent,
	Chip,
	CircularProgress,
	Dialog,
	DialogActions,
	DialogContent,
	DialogTitle,
	Divider,
	FormControl,
	Grid,
	InputLabel,
	MenuItem,
	Select,
	Typography,
} from "@mui/material";
import { useState } from "react";

// ============================================================================
// Component Props
// ============================================================================

interface ModelRegistryProps {
	/**
	 * Callback when deploy button is clicked
	 */
	onDeployClick?: (modelId: string) => void;

	/**
	 * Callback when archive button is clicked
	 */
	onArchiveClick?: (modelId: string) => void;
}

// ============================================================================
// Helper Functions
// ============================================================================

const getStageColor = (
	stage: Model["stage"],
): "default" | "primary" | "secondary" | "success" | "warning" => {
	const colorMap: Record<
		Model["stage"],
		"default" | "primary" | "secondary" | "success" | "warning"
	> = {
		experimental: "default",
		staging: "secondary",
		production: "success",
		archived: "warning",
	};
	return colorMap[stage] || "default";
};

const getStageLabel = (stage: Model["stage"]): string => {
	const labelMap: Record<Model["stage"], string> = {
		experimental: "실험",
		staging: "스테이징",
		production: "프로덕션",
		archived: "아카이브",
	};
	return labelMap[stage] || stage;
};

// ============================================================================
// Component Implementation
// ============================================================================

export const ModelRegistry: React.FC<ModelRegistryProps> = ({
	onDeployClick,
	onArchiveClick,
}) => {
	// ============================================================================
	// State
	// ============================================================================

	const [queryParams, setQueryParams] = useState<ModelsQueryParams>({
		page: 1,
		limit: 12,
		sort_by: "created_at",
		sort_order: "desc",
	});

	const [selectedModel, setSelectedModel] = useState<{
		model_name: string;
		version: string;
	} | null>(null);
	const [detailDialogOpen, setDetailDialogOpen] = useState(false);

	// ============================================================================
	// Hooks
	// ============================================================================

	const { modelsList, modelsTotal, isLoading, error } = useModels(queryParams);
	const {
		modelDetail,
		isLoading: isLoadingDetail,
		error: detailError,
	} = useModelDetail(
		selectedModel?.model_name || null,
		selectedModel?.version || null,
	);

	// ============================================================================
	// Event Handlers
	// ============================================================================

	const handleStageFilterChange = (event: SelectChangeEvent<string>) => {
		const value = event.target.value as Model["stage"] | "";
		setQueryParams((prev) => ({
			...prev,
			stage: value || undefined,
			page: 1,
		}));
	};

	const handleSortChange = (event: SelectChangeEvent<string>) => {
		const [sortBy, sortOrder] = event.target.value.split(":");
		setQueryParams((prev) => ({
			...prev,
			sort_by: sortBy as ModelsQueryParams["sort_by"],
			sort_order: sortOrder as ModelsQueryParams["sort_order"],
		}));
	};

	const handleModelClick = (model_name: string, version: string) => {
		setSelectedModel({ model_name, version });
		setDetailDialogOpen(true);
	};

	const handleCloseDialog = () => {
		setDetailDialogOpen(false);
		setSelectedModel(null);
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

	if (error) {
		return (
			<Card>
				<CardContent>
					<Alert severity="error">모델 목록 로딩 실패: {error.message}</Alert>
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
					<Typography variant="h5" component="h2" gutterBottom>
						모델 레지스트리
					</Typography>

					{/* Filters */}
					<Box sx={{ display: "flex", gap: 2, mb: 3 }}>
						{/* Stage Filter */}
						<FormControl size="small" sx={{ minWidth: 150 }}>
							<InputLabel>단계</InputLabel>
							<Select
								value={queryParams.stage || ""}
								label="단계"
								onChange={handleStageFilterChange}
							>
								<MenuItem value="">전체</MenuItem>
								<MenuItem value="experimental">실험</MenuItem>
								<MenuItem value="staging">스테이징</MenuItem>
								<MenuItem value="production">프로덕션</MenuItem>
								<MenuItem value="archived">아카이브</MenuItem>
							</Select>
						</FormControl>

						{/* Sort */}
						<FormControl size="small" sx={{ minWidth: 180 }}>
							<InputLabel>정렬</InputLabel>
							<Select
								value={`${queryParams.sort_by}:${queryParams.sort_order}`}
								label="정렬"
								onChange={handleSortChange}
							>
								<MenuItem value="name:asc">이름 (오름차순)</MenuItem>
								<MenuItem value="name:desc">이름 (내림차순)</MenuItem>
								<MenuItem value="created_at:desc">최신순</MenuItem>
								<MenuItem value="created_at:asc">오래된순</MenuItem>
								<MenuItem value="accuracy:desc">정확도 (높은 순)</MenuItem>
								<MenuItem value="accuracy:asc">정확도 (낮은 순)</MenuItem>
							</Select>
						</FormControl>
					</Box>

					{/* Model Grid */}
					{modelsList.length === 0 ? (
						<Alert severity="info">등록된 모델이 없습니다.</Alert>
					) : (
						<Grid container spacing={2}>
							{modelsList.map((model) => (
								<Grid
									size={{ xs: 12, sm: 6, md: 4 }}
									key={`${model.model_name}-${model.version}`}
								>
									<Card
										variant="outlined"
										sx={{
											cursor: "pointer",
											transition: "all 0.2s",
											"&:hover": {
												borderColor: "primary.main",
												boxShadow: 2,
											},
										}}
										onClick={() =>
											handleModelClick(model.model_name, model.version)
										}
									>
										<CardContent>
											<Box
												sx={{
													display: "flex",
													justifyContent: "space-between",
													alignItems: "flex-start",
													mb: 1,
												}}
											>
												<Typography variant="h6" component="h3">
													{model.model_name}
												</Typography>
												<Chip
													label={getStageLabel(model.stage)}
													color={getStageColor(model.stage)}
													size="small"
												/>
											</Box>

											<Typography
												variant="body2"
												color="text.secondary"
												gutterBottom
											>
												버전 {model.version}
											</Typography>

											<Box sx={{ my: 2 }}>
												<Box
													sx={{
														display: "flex",
														justifyContent: "space-between",
														mb: 1,
													}}
												>
													<Typography variant="body2">메트릭</Typography>
													<Typography variant="body2" fontWeight="bold">
														{model.metrics.length}개
													</Typography>
												</Box>
												<Box
													sx={{
														display: "flex",
														justifyContent: "space-between",
														mb: 1,
													}}
												>
													<Typography variant="body2">승인자</Typography>
													<Typography variant="body2" fontWeight="bold">
														{model.approved_by || "미승인"}
													</Typography>
												</Box>
											</Box>

											<Typography variant="caption" color="text.secondary">
												{new Date(model.created_at).toLocaleDateString("ko-KR")}
											</Typography>
										</CardContent>

										<CardActions
											sx={{ justifyContent: "flex-end", px: 2, pb: 2 }}
										>
											{model.stage !== "archived" && (
												<>
													<Button
														size="small"
														startIcon={<ArchiveIcon />}
														onClick={(e) => {
															e.stopPropagation();
															onArchiveClick?.(
																`${model.model_name}/${model.version}`,
															);
														}}
													>
														아카이브
													</Button>
													<Button
														size="small"
														variant="contained"
														startIcon={<RocketLaunchIcon />}
														onClick={(e) => {
															e.stopPropagation();
															onDeployClick?.(
																`${model.model_name}/${model.version}`,
															);
														}}
													>
														배포
													</Button>
												</>
											)}
										</CardActions>
									</Card>
								</Grid>
							))}
						</Grid>
					)}

					{/* Summary */}
					<Box sx={{ mt: 2 }}>
						<Typography variant="body2" color="text.secondary">
							총 {modelsTotal.toLocaleString()}개의 모델
						</Typography>
					</Box>
				</CardContent>
			</Card>

			{/* Model Detail Dialog */}
			<Dialog
				open={detailDialogOpen}
				onClose={handleCloseDialog}
				maxWidth="md"
				fullWidth
			>
				<DialogTitle>모델 상세 정보</DialogTitle>
				<DialogContent>
					{isLoadingDetail ? (
						<Box sx={{ display: "flex", justifyContent: "center", py: 4 }}>
							<CircularProgress />
						</Box>
					) : detailError ? (
						<Alert severity="error">
							모델 상세 정보 로딩 실패: {detailError.message}
						</Alert>
					) : modelDetail ? (
						<Box>
							{/* Header */}
							<Box sx={{ mb: 3 }}>
								<Box
									sx={{
										display: "flex",
										justifyContent: "space-between",
										alignItems: "flex-start",
										mb: 1,
									}}
								>
									<Typography variant="h6">{modelDetail.model_name}</Typography>
									<Chip
										label={getStageLabel(modelDetail.stage)}
										color={getStageColor(modelDetail.stage)}
									/>
								</Box>
								<Typography variant="body2" color="text.secondary">
									버전 {modelDetail.version}
								</Typography>
							</Box>

							<Divider sx={{ my: 2 }} />

							{/* Metrics */}
							<Box sx={{ mb: 3 }}>
								<Typography variant="subtitle2" gutterBottom>
									메트릭 ({modelDetail.metrics.length}개)
								</Typography>
								<Grid container spacing={2}>
									{modelDetail.metrics.map((metric, index) => (
										<Grid size={{ xs: 12, md: 6 }} key={index}>
											<Card variant="outlined">
												<CardContent>
													<Typography variant="body2" color="text.secondary">
														{metric.metric_name}
													</Typography>
													<Typography variant="h6">
														{metric.value.toFixed(4)}
													</Typography>
													{metric.dataset && (
														<Typography
															variant="caption"
															color="text.secondary"
														>
															Dataset: {metric.dataset}
														</Typography>
													)}
												</CardContent>
											</Card>
										</Grid>
									))}
								</Grid>
							</Box>

							{/* Model Info */}
							<Box sx={{ mb: 3 }}>
								<Typography variant="subtitle2" gutterBottom>
									모델 정보
								</Typography>
								<Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
									<Box
										sx={{ display: "flex", justifyContent: "space-between" }}
									>
										<Typography variant="body2" color="text.secondary">
											Run ID
										</Typography>
										<Typography variant="body2">
											{modelDetail.run_id}
										</Typography>
									</Box>
									<Box
										sx={{ display: "flex", justifyContent: "space-between" }}
									>
										<Typography variant="body2" color="text.secondary">
											승인자
										</Typography>
										<Typography variant="body2">
											{modelDetail.approved_by || "미승인"}
										</Typography>
									</Box>
									<Box
										sx={{ display: "flex", justifyContent: "space-between" }}
									>
										<Typography variant="body2" color="text.secondary">
											승인일
										</Typography>
										<Typography variant="body2">
											{modelDetail.approved_at
												? new Date(modelDetail.approved_at).toLocaleDateString(
														"ko-KR",
													)
												: "미승인"}
										</Typography>
									</Box>
									<Box
										sx={{ display: "flex", justifyContent: "space-between" }}
									>
										<Typography variant="body2" color="text.secondary">
											생성일
										</Typography>
										<Typography variant="body2">
											{new Date(modelDetail.created_at).toLocaleDateString(
												"ko-KR",
											)}
										</Typography>
									</Box>
								</Box>
							</Box>

							{/* Approval Checklist */}
							{modelDetail.approval_checklist.length > 0 && (
								<Box>
									<Typography variant="subtitle2" gutterBottom>
										승인 체크리스트
									</Typography>
									<Box
										sx={{ display: "flex", flexDirection: "column", gap: 0.5 }}
									>
										{modelDetail.approval_checklist.map((item, index) => (
											<Chip
												key={index}
												label={item.name}
												size="small"
												variant="outlined"
												color={
													item.status === "passed"
														? "success"
														: item.status === "failed"
															? "error"
															: "default"
												}
											/>
										))}
									</Box>
								</Box>
							)}
						</Box>
					) : null}
				</DialogContent>
				<DialogActions>
					<Button onClick={handleCloseDialog}>닫기</Button>
					{modelDetail && modelDetail.stage !== "archived" && (
						<>
							<Button
								startIcon={<ArchiveIcon />}
								onClick={() => {
									onArchiveClick?.(
										`${modelDetail.model_name}/${modelDetail.version}`,
									);
									handleCloseDialog();
								}}
							>
								아카이브
							</Button>
							<Button
								variant="contained"
								startIcon={<RocketLaunchIcon />}
								onClick={() => {
									onDeployClick?.(
										`${modelDetail.model_name}/${modelDetail.version}`,
									);
									handleCloseDialog();
								}}
							>
								배포
							</Button>
						</>
					)}
				</DialogActions>
			</Dialog>
		</>
	);
};
