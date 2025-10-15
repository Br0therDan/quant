/**
 * FeatureDetail Component
 *
 * Displays detailed information for a specific feature including:
 * - Metadata (name, type, description, tags, creator)
 * - Statistics (mean, median, std, min, max, missing ratio)
 * - Distribution chart (histogram)
 * - Edit and delete actions
 *
 * @module components/mlops/feature-store/FeatureDetail
 */

import type { FeatureType, FeatureUpdate } from "@/client";
import { useFeatureDetail, useFeatureStore } from "@/hooks/useFeatureStore";
import CancelIcon from "@mui/icons-material/Cancel";
import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit";
import SaveIcon from "@mui/icons-material/Save";
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
	Grid,
	TextField,
	Typography,
} from "@mui/material";
import { useState } from "react";
import {
	Bar,
	BarChart,
	CartesianGrid,
	ResponsiveContainer,
	Tooltip,
	XAxis,
	YAxis,
} from "recharts";

// ============================================================================
// Component Props
// ============================================================================

interface FeatureDetailProps {
	/**
	 * Feature ID to display
	 */
	featureId: string | null;

	/**
	 * Callback when feature is deleted
	 */
	onDeleted?: () => void;

	/**
	 * Callback when feature is updated
	 */
	onUpdated?: () => void;
}

// ============================================================================
// Type Color Mapping
// ============================================================================

const getTypeColor = (type: FeatureType) => {
	const colorMap: Record<
		FeatureType,
		"primary" | "success" | "warning" | "error" | "info"
	> = {
		technical_indicator: "primary",
		fundamental: "success",
		sentiment: "warning",
		macro_economic: "info",
		derived: "error",
		raw: "info",
	};
	return colorMap[type] || "default";
};

// ============================================================================
// Component Implementation
// ============================================================================

export const FeatureDetail: React.FC<FeatureDetailProps> = ({
	featureId,
	onDeleted,
	onUpdated,
}) => {
	// ============================================================================
	// State
	// ============================================================================

	const [isEditing, setIsEditing] = useState(false);
	const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
	const [editFormData, setEditFormData] = useState<FeatureUpdate>({
		description: "",
		tags: [],
	});

	// ============================================================================
	// Hooks
	// ============================================================================

	const { featureDetail, isLoading, error, refetch } =
		useFeatureDetail(featureId);
	const { updateFeature, isUpdatingFeature, deleteFeature, isDeletingFeature } =
		useFeatureStore();

	// ============================================================================
	// Effects - Initialize edit form when feature loads
	// ============================================================================

	useState(() => {
		if (featureDetail && !isEditing) {
			setEditFormData({
				description: featureDetail.description,
				tags: featureDetail.tags,
			});
		}
	});

	// ============================================================================
	// Event Handlers
	// ============================================================================

	const handleEditClick = () => {
		if (featureDetail) {
			setEditFormData({
				description: featureDetail.description,
				tags: featureDetail.tags,
			});
			setIsEditing(true);
		}
	};
	const handleCancelEdit = () => {
		setIsEditing(false);
	};

	const handleSaveEdit = async () => {
		if (!featureId) return;

		try {
			await updateFeature(featureId, editFormData);
			setIsEditing(false);
			refetch();
			onUpdated?.();
		} catch (_error) {
			// Error handling is done in the hook
		}
	};

	const handleDeleteClick = () => {
		setDeleteDialogOpen(true);
	};

	const handleDeleteConfirm = async () => {
		if (!featureId) return;

		try {
			await deleteFeature(featureId);
			setDeleteDialogOpen(false);
			onDeleted?.();
		} catch (_error) {
			// Error handling is done in the hook
		}
	};

	const handleFormChange =
		(field: keyof FeatureUpdate) =>
		(
			event:
				| React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
				| SelectChangeEvent<string>,
		) => {
			setEditFormData((prev: FeatureUpdate) => ({
				...prev,
				[field]: event.target.value,
			}));
		}; // ============================================================================
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

	if (error || !featureDetail) {
		return (
			<Card>
				<CardContent>
					<Alert severity="error">
						{error
							? `피처 로딩 실패: ${error.message}`
							: "피처를 찾을 수 없습니다"}
					</Alert>
				</CardContent>
			</Card>
		);
	}

	// ============================================================================
	// Prepare Distribution Chart Data
	// ============================================================================

	const distributionData = featureDetail.statistics?.distribution || [];
	const chartData = distributionData.slice(0, 20).map((item) => ({
		value: String(item.value),
		count: item.count,
	}));

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
							alignItems: "flex-start",
							mb: 3,
						}}
					>
						<Box>
							<Typography variant="h5" component="h2" gutterBottom>
								{featureDetail.feature_name}
							</Typography>
							<Box
								sx={{ display: "flex", gap: 1, alignItems: "center", mt: 1 }}
							>
								<Chip
									label={featureDetail.feature_type}
									color={getTypeColor(featureDetail.feature_type)}
									size="small"
								/>
								<Typography variant="body2" color="text.secondary">
									버전 {featureDetail.current_version}
								</Typography>
								<Typography variant="body2" color="text.secondary">
									•
								</Typography>
								<Typography variant="body2" color="text.secondary">
									사용 {featureDetail.usage_count}회
								</Typography>
							</Box>
						</Box>
					</Box>

					{/* Description */}
					{isEditing ? (
						<TextField
							fullWidth
							multiline
							rows={3}
							label="설명"
							value={editFormData.description}
							onChange={handleFormChange("description")}
							sx={{ mb: 3 }}
						/>
					) : (
						<Typography variant="body1" paragraph>
							{featureDetail.description}
						</Typography>
					)}

					{/* Tags */}
					<Box sx={{ mb: 3 }}>
						<Typography variant="subtitle2" gutterBottom>
							태그
						</Typography>
						{isEditing ? (
							<TextField
								fullWidth
								size="small"
								label="태그 (쉼표로 구분)"
								value={editFormData.tags?.join(", ") || ""}
								onChange={(e) =>
									setEditFormData((prev: FeatureUpdate) => ({
										...prev,
										tags: e.target.value
											.split(",")
											.map((t) => t.trim())
											.filter(Boolean),
									}))
								}
							/>
						) : (
							<Box sx={{ display: "flex", gap: 0.5, flexWrap: "wrap" }}>
								{featureDetail.tags.map((tag) => (
									<Chip key={tag} label={tag} size="small" variant="outlined" />
								))}
							</Box>
						)}
					</Box>

					{/* Statistics */}
					{featureDetail.statistics && (
						<Box sx={{ mb: 3 }}>
							<Typography variant="subtitle2" gutterBottom>
								통계
							</Typography>
							<Grid container spacing={2}>
								<Grid size={{ xs: 6, md: 3 }}>
									<Card variant="outlined">
										<CardContent>
											<Typography variant="body2" color="text.secondary">
												평균
											</Typography>
											<Typography variant="h6">
												{featureDetail.statistics.mean?.toFixed(2)}
											</Typography>
										</CardContent>
									</Card>
								</Grid>
								<Grid size={{ xs: 6, md: 3 }}>
									<Card variant="outlined">
										<CardContent>
											<Typography variant="body2" color="text.secondary">
												중앙값
											</Typography>
											<Typography variant="h6">
												{featureDetail.statistics.median?.toFixed(2)}
											</Typography>
										</CardContent>
									</Card>
								</Grid>
								<Grid size={{ xs: 6, md: 3 }}>
									<Card variant="outlined">
										<CardContent>
											<Typography variant="body2" color="text.secondary">
												표준편차
											</Typography>
											<Typography variant="h6">
												{featureDetail.statistics.std?.toFixed(2)}
											</Typography>
										</CardContent>
									</Card>
								</Grid>
								<Grid size={{ xs: 6, md: 3 }}>
									<Card variant="outlined">
										<CardContent>
											<Typography variant="body2" color="text.secondary">
												결측치
											</Typography>
											<Typography variant="h6">
												{(
													(featureDetail.statistics.missing_ratio || 0) * 100
												).toFixed(1)}
												%
											</Typography>
										</CardContent>
									</Card>
								</Grid>
							</Grid>
						</Box>
					)}

					{/* Distribution Chart */}
					{chartData.length > 0 && (
						<Box sx={{ mb: 3 }}>
							<Typography variant="subtitle2" gutterBottom>
								분포
							</Typography>
							<ResponsiveContainer width="100%" height={300}>
								<BarChart data={chartData}>
									<CartesianGrid strokeDasharray="3 3" />
									<XAxis
										dataKey="value"
										angle={-45}
										textAnchor="end"
										height={80}
									/>
									<YAxis />
									<Tooltip />
									<Bar dataKey="count" fill="#1976d2" />
								</BarChart>
							</ResponsiveContainer>
						</Box>
					)}

					{/* Transformation Code (Read-only) */}
					<Box sx={{ mb: 2 }}>
						<Typography variant="subtitle2" gutterBottom>
							변환 코드
						</Typography>
						<Box
							sx={{
								p: 2,
								bgcolor: "grey.100",
								borderRadius: 1,
								fontFamily: "monospace",
								fontSize: "0.875rem",
								overflowX: "auto",
							}}
						>
							<pre style={{ margin: 0 }}>
								{featureDetail.transformation?.code}
							</pre>
						</Box>
					</Box>

					{/* Metadata */}
					<Box>
						<Typography variant="caption" color="text.secondary">
							생성자: {featureDetail.owner} | 생성일:{" "}
							{new Date(featureDetail.created_at).toLocaleString("ko-KR")} |
							최종 수정:{" "}
							{new Date(featureDetail.updated_at).toLocaleString("ko-KR")}
						</Typography>
					</Box>
				</CardContent>

				{/* Actions */}
				<CardActions sx={{ justifyContent: "flex-end", px: 2, pb: 2 }}>
					{isEditing ? (
						<>
							<Button
								startIcon={<CancelIcon />}
								onClick={handleCancelEdit}
								disabled={isUpdatingFeature}
							>
								취소
							</Button>
							<Button
								variant="contained"
								startIcon={<SaveIcon />}
								onClick={handleSaveEdit}
								disabled={isUpdatingFeature}
							>
								{isUpdatingFeature ? <CircularProgress size={20} /> : "저장"}
							</Button>
						</>
					) : (
						<>
							<Button
								startIcon={<DeleteIcon />}
								color="error"
								onClick={handleDeleteClick}
							>
								삭제
							</Button>
							<Button
								variant="contained"
								startIcon={<EditIcon />}
								onClick={handleEditClick}
							>
								편집
							</Button>
						</>
					)}
				</CardActions>
			</Card>

			{/* Delete Confirmation Dialog */}
			<Dialog
				open={deleteDialogOpen}
				onClose={() => setDeleteDialogOpen(false)}
			>
				<DialogTitle>피처 삭제</DialogTitle>
				<DialogContent>
					<Typography>
						정말로 <strong>{featureDetail.feature_name}</strong> 피처를
						삭제하시겠습니까?
					</Typography>
					<Typography variant="body2" color="error" sx={{ mt: 2 }}>
						이 작업은 되돌릴 수 없습니다.
					</Typography>
				</DialogContent>
				<DialogActions>
					<Button
						onClick={() => setDeleteDialogOpen(false)}
						disabled={isDeletingFeature}
					>
						취소
					</Button>
					<Button
						color="error"
						variant="contained"
						onClick={handleDeleteConfirm}
						disabled={isDeletingFeature}
					>
						{isDeletingFeature ? <CircularProgress size={20} /> : "삭제"}
					</Button>
				</DialogActions>
			</Dialog>
		</>
	);
};
