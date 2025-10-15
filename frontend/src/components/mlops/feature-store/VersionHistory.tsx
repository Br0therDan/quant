/**
 * VersionHistory Component
 *
 * Displays version history for a feature using a Timeline component.
 * Features:
 * - Timeline visualization of version changes
 * - Version comparison (diff view)
 * - Rollback functionality
 * - Change description display
 *
 * @module components/mlops/feature-store/VersionHistory
 */

import { useFeatureVersions } from "@/hooks/useFeatureStore";
import CodeIcon from "@mui/icons-material/Code";
import CompareArrowsIcon from "@mui/icons-material/CompareArrows";
import RestoreIcon from "@mui/icons-material/Restore";
import Timeline from "@mui/lab/Timeline";
import TimelineConnector from "@mui/lab/TimelineConnector";
import TimelineContent from "@mui/lab/TimelineContent";
import TimelineDot from "@mui/lab/TimelineDot";
import TimelineItem from "@mui/lab/TimelineItem";
import TimelineOppositeContent from "@mui/lab/TimelineOppositeContent";
import TimelineSeparator from "@mui/lab/TimelineSeparator";
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
	Typography,
} from "@mui/material";
import { useState } from "react";

// ============================================================================
// Component Props
// ============================================================================

interface VersionHistoryProps {
	/**
	 * Feature ID to display version history for
	 */
	featureId: string | null;

	/**
	 * Callback when a version is restored
	 */
	onRestore?: (versionId: string) => void;
}

// ============================================================================
// Component Implementation
// ============================================================================

export const VersionHistory: React.FC<VersionHistoryProps> = ({
	featureId,
	onRestore,
}) => {
	// ============================================================================
	// State
	// ============================================================================

	const [selectedVersions, setSelectedVersions] = useState<string[]>([]);
	const [compareDialogOpen, setCompareDialogOpen] = useState(false);
	const [rollbackDialogOpen, setRollbackDialogOpen] = useState(false);
	const [selectedRollbackVersion, setSelectedRollbackVersion] = useState<
		string | null
	>(null);

	// ============================================================================
	// Hooks
	// ============================================================================

	const { versions, isLoading, error } = useFeatureVersions(featureId);

	// ============================================================================
	// Event Handlers
	// ============================================================================

	const handleVersionSelect = (versionId: string) => {
		setSelectedVersions((prev) => {
			if (prev.includes(versionId)) {
				return prev.filter((id) => id !== versionId);
			}
			if (prev.length >= 2) {
				return [prev[1], versionId];
			}
			return [...prev, versionId];
		});
	};

	const handleCompareClick = () => {
		if (selectedVersions.length === 2) {
			setCompareDialogOpen(true);
		}
	};

	const handleRollbackClick = (versionId: string) => {
		setSelectedRollbackVersion(versionId);
		setRollbackDialogOpen(true);
	};

	const handleRollbackConfirm = () => {
		if (selectedRollbackVersion) {
			onRestore?.(selectedRollbackVersion);
			setRollbackDialogOpen(false);
			setSelectedRollbackVersion(null);
		}
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
							minHeight: 300,
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
					<Alert severity="error">
						버전 히스토리 로딩 실패: {error.message}
					</Alert>
				</CardContent>
			</Card>
		);
	}

	// ============================================================================
	// Render Empty State
	// ============================================================================

	if (!versions || versions.length === 0) {
		return (
			<Card>
				<CardContent>
					<Box sx={{ textAlign: "center", py: 4 }}>
						<CodeIcon sx={{ fontSize: 64, color: "text.secondary", mb: 2 }} />
						<Typography variant="h6" color="text.secondary">
							버전 히스토리가 없습니다
						</Typography>
						<Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
							피처를 수정하면 버전이 자동으로 생성됩니다
						</Typography>
					</Box>
				</CardContent>
			</Card>
		);
	}

	// ============================================================================
	// Get selected versions for comparison
	// ============================================================================

	const version1 = versions.find((v) => v.id === selectedVersions[0]);
	const version2 = versions.find((v) => v.id === selectedVersions[1]);

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
						<Typography variant="h6" component="h3">
							버전 히스토리
						</Typography>
						<Button
							variant="outlined"
							startIcon={<CompareArrowsIcon />}
							onClick={handleCompareClick}
							disabled={selectedVersions.length !== 2}
						>
							비교 ({selectedVersions.length}/2)
						</Button>
					</Box>

					{/* Timeline */}
					<Timeline position="right">
						{versions.map((version, index) => {
							const isLatest = index === 0;
							const isSelected = selectedVersions.includes(version.id);

							return (
								<TimelineItem key={version.id}>
									<TimelineOppositeContent
										color="text.secondary"
										sx={{ flex: 0.3 }}
									>
										<Typography variant="body2">
											{new Date(version.created_at).toLocaleString("ko-KR", {
												year: "numeric",
												month: "short",
												day: "numeric",
												hour: "2-digit",
												minute: "2-digit",
											})}
										</Typography>
									</TimelineOppositeContent>

									<TimelineSeparator>
										<TimelineDot
											color={
												isLatest ? "primary" : isSelected ? "secondary" : "grey"
											}
											sx={{ cursor: "pointer" }}
											onClick={() => handleVersionSelect(version.id)}
										>
											{isLatest && (
												<Chip
													label="최신"
													size="small"
													sx={{ position: "absolute", top: -8 }}
												/>
											)}
										</TimelineDot>
										{index < versions.length - 1 && <TimelineConnector />}
									</TimelineSeparator>

									<TimelineContent>
										<Box
											sx={{
												p: 2,
												border: 1,
												borderColor: isSelected ? "secondary.main" : "divider",
												borderRadius: 1,
												bgcolor: isSelected
													? "action.selected"
													: "background.paper",
												cursor: "pointer",
												transition: "all 0.2s",
												"&:hover": {
													borderColor: "primary.main",
													bgcolor: "action.hover",
												},
											}}
											onClick={() => handleVersionSelect(version.id)}
										>
											<Box
												sx={{
													display: "flex",
													justifyContent: "space-between",
													alignItems: "flex-start",
													mb: 1,
												}}
											>
												<Typography variant="subtitle2">
													버전 {version.version}
												</Typography>
												{!isLatest && (
													<Button
														size="small"
														startIcon={<RestoreIcon />}
														onClick={(e) => {
															e.stopPropagation();
															handleRollbackClick(version.id);
														}}
													>
														롤백
													</Button>
												)}
											</Box>

											<Typography variant="body2" paragraph>
												{version.description}
											</Typography>

											{version.changes && (
												<Box
													sx={{
														p: 1,
														bgcolor: "grey.100",
														borderRadius: 1,
														fontSize: "0.75rem",
													}}
												>
													<Typography
														variant="caption"
														sx={{
															fontWeight: "bold",
															display: "block",
															mb: 0.5,
														}}
													>
														변경 사항:
													</Typography>
													<Typography
														variant="caption"
														component="pre"
														sx={{ margin: 0, whiteSpace: "pre-wrap" }}
													>
														{version.changes}
													</Typography>
												</Box>
											)}

											<Typography
												variant="caption"
												color="text.secondary"
												sx={{ display: "block", mt: 1 }}
											>
												작성자: {version.created_by}
											</Typography>
										</Box>
									</TimelineContent>
								</TimelineItem>
							);
						})}
					</Timeline>
				</CardContent>
			</Card>

			{/* Compare Dialog */}
			<Dialog
				open={compareDialogOpen}
				onClose={() => setCompareDialogOpen(false)}
				maxWidth="md"
				fullWidth
			>
				<DialogTitle>버전 비교</DialogTitle>
				<DialogContent>
					{version1 && version2 && (
						<Box sx={{ display: "flex", gap: 2 }}>
							{/* Version 1 */}
							<Box sx={{ flex: 1 }}>
								<Typography variant="subtitle2" gutterBottom>
									버전 {version1.version}
								</Typography>
								<Box
									sx={{
										p: 2,
										bgcolor: "grey.100",
										borderRadius: 1,
										fontFamily: "monospace",
										fontSize: "0.875rem",
										minHeight: 200,
										maxHeight: 400,
										overflow: "auto",
									}}
								>
									<pre style={{ margin: 0, whiteSpace: "pre-wrap" }}>
										{version1.transformation_code}
									</pre>
								</Box>
							</Box>

							{/* Version 2 */}
							<Box sx={{ flex: 1 }}>
								<Typography variant="subtitle2" gutterBottom>
									버전 {version2.version}
								</Typography>
								<Box
									sx={{
										p: 2,
										bgcolor: "grey.100",
										borderRadius: 1,
										fontFamily: "monospace",
										fontSize: "0.875rem",
										minHeight: 200,
										maxHeight: 400,
										overflow: "auto",
									}}
								>
									<pre style={{ margin: 0, whiteSpace: "pre-wrap" }}>
										{version2.transformation_code}
									</pre>
								</Box>
							</Box>
						</Box>
					)}
				</DialogContent>
				<DialogActions>
					<Button onClick={() => setCompareDialogOpen(false)}>닫기</Button>
				</DialogActions>
			</Dialog>

			{/* Rollback Confirmation Dialog */}
			<Dialog
				open={rollbackDialogOpen}
				onClose={() => setRollbackDialogOpen(false)}
			>
				<DialogTitle>버전 롤백</DialogTitle>
				<DialogContent>
					<Typography>정말로 이 버전으로 롤백하시겠습니까?</Typography>
					<Typography variant="body2" color="warning.main" sx={{ mt: 2 }}>
						현재 버전의 변경 사항이 손실될 수 있습니다.
					</Typography>
				</DialogContent>
				<DialogActions>
					<Button onClick={() => setRollbackDialogOpen(false)}>취소</Button>
					<Button
						color="warning"
						variant="contained"
						onClick={handleRollbackConfirm}
					>
						롤백
					</Button>
				</DialogActions>
			</Dialog>
		</>
	);
};
