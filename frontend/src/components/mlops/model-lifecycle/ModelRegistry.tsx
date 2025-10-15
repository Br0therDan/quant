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

const getStatusColor = (
	status: Model["status"],
): "default" | "primary" | "secondary" | "success" | "warning" => {
	const colorMap: Record<
		Model["status"],
		"default" | "primary" | "secondary" | "success" | "warning"
	> = {
		draft: "default",
		registered: "primary",
		staging: "secondary",
		production: "success",
		archived: "warning",
	};
	return colorMap[status] || "default";
};

const getStatusLabel = (status: Model["status"]): string => {
	const labelMap: Record<Model["status"], string> = {
		draft: "초안",
		registered: "등록됨",
		staging: "스테이징",
		production: "프로덕션",
		archived: "아카이브",
	};
	return labelMap[status] || status;
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

	const [selectedModelId, setSelectedModelId] = useState<string | null>(null);
	const [detailDialogOpen, setDetailDialogOpen] = useState(false);

	// ============================================================================
	// Hooks
	// ============================================================================

	const { modelsList, modelsTotal, isLoading, error } = useModels(queryParams);
	const {
		modelDetail,
		isLoading: isLoadingDetail,
		error: detailError,
	} = useModelDetail(selectedModelId);

	// ============================================================================
	// Event Handlers
	// ============================================================================

	const handleStatusFilterChange = (event: SelectChangeEvent<string>) => {
		const value = event.target.value as Model["status"] | "";
		setQueryParams((prev) => ({
			...prev,
			status: value || undefined,
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

	const handleModelClick = (modelId: string) => {
		setSelectedModelId(modelId);
		setDetailDialogOpen(true);
	};

	const handleCloseDialog = () => {
		setDetailDialogOpen(false);
		setSelectedModelId(null);
	};

	const handleDeployClick = (modelId: string, event: React.MouseEvent) => {
		event.stopPropagation();
		onDeployClick?.(modelId);
	};

	const handleArchiveClick = (modelId: string, event: React.MouseEvent) => {
		event.stopPropagation();
		onArchiveClick?.(modelId);
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
						{/* Status Filter */}
						<FormControl size="small" sx={{ minWidth: 150 }}>
							<InputLabel>상태</InputLabel>
							<Select
								value={queryParams.status || ""}
								label="상태"
								onChange={handleStatusFilterChange}
							>
								<MenuItem value="">전체</MenuItem>
								<MenuItem value="draft">초안</MenuItem>
								<MenuItem value="registered">등록됨</MenuItem>
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
								<Grid size={{ xs: 12, sm: 6, md: 4 }} key={model.id}>
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
										onClick={() => handleModelClick(model.id)}
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
													{model.name}
												</Typography>
												<Chip
													label={getStatusLabel(model.status)}
													color={getStatusColor(model.status)}
													size="small"
												/>
											</Box>

											<Typography
												variant="body2"
												color="text.secondary"
												gutterBottom
											>
												{model.version}
											</Typography>

											<Box sx={{ my: 2 }}>
												<Box
													sx={{
														display: "flex",
														justifyContent: "space-between",
														mb: 1,
													}}
												>
													<Typography variant="body2">정확도</Typography>
													<Typography variant="body2" fontWeight="bold">
														{(model.accuracy * 100).toFixed(2)}%
													</Typography>
												</Box>
											</Box>

											<Box
												sx={{
													display: "flex",
													gap: 0.5,
													flexWrap: "wrap",
													mb: 1,
												}}
											>
												{model.tags.slice(0, 3).map((tag) => (
													<Chip
														key={tag}
														label={tag}
														size="small"
														variant="outlined"
													/>
												))}
												{model.tags.length > 3 && (
													<Chip
														label={`+${model.tags.length - 3}`}
														size="small"
														variant="outlined"
													/>
												)}
											</Box>

											<Typography variant="caption" color="text.secondary">
												{new Date(model.created_at).toLocaleDateString("ko-KR")}{" "}
												• {model.created_by}
											</Typography>
										</CardContent>

										<CardActions
											sx={{ justifyContent: "flex-end", px: 2, pb: 2 }}
										>
											{model.status !== "archived" && (
												<>
													<Button
														size="small"
														startIcon={<ArchiveIcon />}
														onClick={(e) => handleArchiveClick(model.id, e)}
													>
														아카이브
													</Button>
													<Button
														size="small"
														variant="contained"
														startIcon={<RocketLaunchIcon />}
														onClick={(e) => handleDeployClick(model.id, e)}
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
									<Typography variant="h6">{modelDetail.name}</Typography>
									<Chip
										label={getStatusLabel(modelDetail.status)}
										color={getStatusColor(modelDetail.status)}
									/>
								</Box>
								<Typography variant="body2" color="text.secondary">
									{modelDetail.version}
								</Typography>
							</Box>

							<Divider sx={{ my: 2 }} />

							{/* Description */}
							<Box sx={{ mb: 3 }}>
								<Typography variant="subtitle2" gutterBottom>
									설명
								</Typography>
								<Typography variant="body2">
									{modelDetail.description}
								</Typography>
							</Box>

							{/* Metrics */}
							<Box sx={{ mb: 3 }}>
								<Typography variant="subtitle2" gutterBottom>
									메트릭
								</Typography>
								<Grid container spacing={2}>
									{Object.entries(modelDetail.metrics).map(([key, value]) => (
										<Grid size={{ xs: 6, md: 3 }} key={key}>
											<Card variant="outlined">
												<CardContent>
													<Typography variant="body2" color="text.secondary">
														{key}
													</Typography>
													<Typography variant="h6">
														{typeof value === "number"
															? (value * 100).toFixed(2) + "%"
															: value}
													</Typography>
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
											프레임워크
										</Typography>
										<Typography variant="body2">
											{modelDetail.framework}
										</Typography>
									</Box>
									<Box
										sx={{ display: "flex", justifyContent: "space-between" }}
									>
										<Typography variant="body2" color="text.secondary">
											크기
										</Typography>
										<Typography variant="body2">
											{modelDetail.size_mb.toFixed(2)} MB
										</Typography>
									</Box>
									<Box
										sx={{ display: "flex", justifyContent: "space-between" }}
									>
										<Typography variant="body2" color="text.secondary">
											배포 횟수
										</Typography>
										<Typography variant="body2">
											{modelDetail.deployment_count}회
										</Typography>
									</Box>
								</Box>
							</Box>

							{/* Tags */}
							<Box>
								<Typography variant="subtitle2" gutterBottom>
									태그
								</Typography>
								<Box sx={{ display: "flex", gap: 0.5, flexWrap: "wrap" }}>
									{modelDetail.tags.map((tag) => (
										<Chip
											key={tag}
											label={tag}
											size="small"
											variant="outlined"
										/>
									))}
								</Box>
							</Box>
						</Box>
					) : null}
				</DialogContent>
				<DialogActions>
					<Button onClick={handleCloseDialog}>닫기</Button>
					{modelDetail && modelDetail.status !== "archived" && (
						<>
							<Button
								startIcon={<ArchiveIcon />}
								onClick={() => {
									onArchiveClick?.(modelDetail.id);
									handleCloseDialog();
								}}
							>
								아카이브
							</Button>
							<Button
								variant="contained"
								startIcon={<RocketLaunchIcon />}
								onClick={() => {
									onDeployClick?.(modelDetail.id);
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
