/**
 * DeploymentPipeline Component
 *
 * Displays deployment pipeline with:
 * - Stepper showing deployment stages (준비 → 검증 → 배포 → 모니터링)
 * - Deployment logs in accordion
 * - Rollback functionality
 * - Real-time status updates
 *
 * @module components/mlops/model-lifecycle/DeploymentPipeline
 */

import {
	useDeploymentDetail,
	type Deployment,
} from "@/hooks/useModelLifecycle";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import ErrorIcon from "@mui/icons-material/Error";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import UndoIcon from "@mui/icons-material/Undo";
import {
	Accordion,
	AccordionDetails,
	AccordionSummary,
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
	LinearProgress,
	Step,
	StepLabel,
	Stepper,
	Typography,
} from "@mui/material";
import { useState } from "react";

// ============================================================================
// Component Props
// ============================================================================

interface DeploymentPipelineProps {
	/**
	 * Deployment ID to display
	 */
	deploymentId: string | null;

	/**
	 * Callback when rollback is requested
	 */
	onRollback?: (deploymentId: string) => void;
}

// ============================================================================
// Helper Functions
// ============================================================================

const getDeploymentSteps = (
	status: Deployment["status"],
): {
	label: string;
	completed: boolean;
	error: boolean;
}[] => {
	const stepOrder = ["pending", "validating", "deploying", "active"];
	const currentIndex = stepOrder.indexOf(status);

	return [
		{
			label: "준비",
			completed: currentIndex > 0 || status === "active",
			error: status === "failed" && currentIndex === 0,
		},
		{
			label: "검증",
			completed: currentIndex > 1 || status === "active",
			error: status === "failed" && currentIndex === 1,
		},
		{
			label: "배포",
			completed: currentIndex > 2 || status === "active",
			error: status === "failed" && currentIndex === 2,
		},
		{
			label: "모니터링",
			completed: status === "active",
			error: false,
		},
	];
};

const getActiveStep = (status: Deployment["status"]): number => {
	const stepMap: Record<string, number> = {
		pending: 0,
		validating: 1,
		deploying: 2,
		active: 3,
		failed: -1,
		rollback: -1,
	};
	return stepMap[status] ?? 0;
};

const getStatusColor = (
	status: Deployment["status"],
): "default" | "primary" | "secondary" | "success" | "error" | "warning" => {
	const colorMap: Record<
		Deployment["status"],
		"default" | "primary" | "secondary" | "success" | "error" | "warning"
	> = {
		pending: "default",
		validating: "primary",
		deploying: "secondary",
		active: "success",
		failed: "error",
		rollback: "warning",
	};
	return colorMap[status] || "default";
};

const getStatusLabel = (status: Deployment["status"]): string => {
	const labelMap: Record<Deployment["status"], string> = {
		pending: "대기 중",
		validating: "검증 중",
		deploying: "배포 중",
		active: "활성",
		failed: "실패",
		rollback: "롤백 중",
	};
	return labelMap[status] || status;
};

// ============================================================================
// Component Implementation
// ============================================================================

export const DeploymentPipeline: React.FC<DeploymentPipelineProps> = ({
	deploymentId,
	onRollback,
}) => {
	// ============================================================================
	// State
	// ============================================================================

	const [rollbackDialogOpen, setRollbackDialogOpen] = useState(false);

	// ============================================================================
	// Hooks
	// ============================================================================

	const { deploymentDetail, isLoading, error } =
		useDeploymentDetail(deploymentId);

	// ============================================================================
	// Event Handlers
	// ============================================================================

	const handleRollbackClick = () => {
		setRollbackDialogOpen(true);
	};

	const handleRollbackConfirm = () => {
		if (deploymentId) {
			onRollback?.(deploymentId);
			setRollbackDialogOpen(false);
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

	if (error || !deploymentDetail) {
		return (
			<Card>
				<CardContent>
					<Alert severity="error">
						{error
							? `배포 정보 로딩 실패: ${error.message}`
							: "배포를 찾을 수 없습니다"}
					</Alert>
				</CardContent>
			</Card>
		);
	}

	// ============================================================================
	// Prepare Data
	// ============================================================================

	const steps = getDeploymentSteps(deploymentDetail.status);
	const activeStep = getActiveStep(deploymentDetail.status);
	const isInProgress =
		deploymentDetail.status === "pending" ||
		deploymentDetail.status === "validating" ||
		deploymentDetail.status === "deploying";

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
							<Typography variant="h5" component="h2">
								배포 파이프라인
							</Typography>
							<Typography variant="body2" color="text.secondary">
								{deploymentDetail.model_name} {deploymentDetail.model_version}
							</Typography>
						</Box>
						<Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
							<Chip
								label={getStatusLabel(deploymentDetail.status)}
								color={getStatusColor(deploymentDetail.status)}
							/>
							{deploymentDetail.status === "active" && (
								<Button
									size="small"
									startIcon={<UndoIcon />}
									onClick={handleRollbackClick}
								>
									롤백
								</Button>
							)}
						</Box>
					</Box>

					{/* Progress Bar */}
					{isInProgress && (
						<Box sx={{ mb: 3 }}>
							<LinearProgress />
						</Box>
					)}

					{/* Stepper */}
					<Box sx={{ mb: 4 }}>
						<Stepper activeStep={activeStep}>
							{steps.map((step) => (
								<Step key={step.label} completed={step.completed}>
									<StepLabel
										error={step.error}
										StepIconComponent={
											step.completed
												? () => (
														<CheckCircleIcon
															color="success"
															sx={{ fontSize: 24 }}
														/>
													)
												: step.error
													? () => (
															<ErrorIcon color="error" sx={{ fontSize: 24 }} />
														)
													: undefined
										}
									>
										{step.label}
									</StepLabel>
								</Step>
							))}
						</Stepper>
					</Box>

					{/* Deployment Info */}
					<Box sx={{ mb: 3 }}>
						<Typography variant="subtitle2" gutterBottom>
							배포 정보
						</Typography>
						<Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
							<Box sx={{ display: "flex", justifyContent: "space-between" }}>
								<Typography variant="body2" color="text.secondary">
									환경
								</Typography>
								<Chip
									label={deploymentDetail.environment.toUpperCase()}
									size="small"
									color={
										deploymentDetail.environment === "production"
											? "error"
											: deploymentDetail.environment === "staging"
												? "warning"
												: "default"
									}
								/>
							</Box>
							<Box sx={{ display: "flex", justifyContent: "space-between" }}>
								<Typography variant="body2" color="text.secondary">
									엔드포인트
								</Typography>
								<Typography
									variant="body2"
									sx={{ fontFamily: "monospace", fontSize: "0.875rem" }}
								>
									{deploymentDetail.endpoint}
								</Typography>
							</Box>
							{deploymentDetail.deployed_at && (
								<Box sx={{ display: "flex", justifyContent: "space-between" }}>
									<Typography variant="body2" color="text.secondary">
										배포 시간
									</Typography>
									<Typography variant="body2">
										{new Date(deploymentDetail.deployed_at).toLocaleString(
											"ko-KR",
										)}
									</Typography>
								</Box>
							)}
							<Box sx={{ display: "flex", justifyContent: "space-between" }}>
								<Typography variant="body2" color="text.secondary">
									배포자
								</Typography>
								<Typography variant="body2">
									{deploymentDetail.created_by}
								</Typography>
							</Box>
						</Box>
					</Box>

					{/* Deployment Logs */}
					<Box>
						<Typography variant="subtitle2" gutterBottom>
							배포 로그
						</Typography>
						{deploymentDetail.logs && deploymentDetail.logs.length > 0 ? (
							<Accordion>
								<AccordionSummary expandIcon={<ExpandMoreIcon />}>
									<Typography variant="body2">
										로그 보기 ({deploymentDetail.logs.length}개 항목)
									</Typography>
								</AccordionSummary>
								<AccordionDetails>
									<Box
										sx={{
											maxHeight: 300,
											overflow: "auto",
											bgcolor: "grey.100",
											p: 2,
											borderRadius: 1,
											fontFamily: "monospace",
											fontSize: "0.875rem",
										}}
									>
										{deploymentDetail.logs.map((log, index) => (
											<Box key={index} sx={{ mb: 0.5 }}>
												<Typography
													variant="caption"
													component="pre"
													sx={{ margin: 0, whiteSpace: "pre-wrap" }}
												>
													[{new Date().toLocaleTimeString("ko-KR")}] {log}
												</Typography>
											</Box>
										))}
									</Box>
								</AccordionDetails>
							</Accordion>
						) : (
							<Alert severity="info">로그가 없습니다</Alert>
						)}
					</Box>

					{/* Health Metrics (for active deployments) */}
					{deploymentDetail.status === "active" && (
						<Box sx={{ mt: 3 }}>
							<Typography variant="subtitle2" gutterBottom>
								헬스 메트릭
							</Typography>
							<Box sx={{ display: "flex", gap: 2, flexWrap: "wrap" }}>
								<Card variant="outlined" sx={{ flex: 1, minWidth: 150 }}>
									<CardContent>
										<Typography variant="body2" color="text.secondary">
											요청 수
										</Typography>
										<Typography variant="h6">
											{deploymentDetail.request_count.toLocaleString()}
										</Typography>
									</CardContent>
								</Card>
								<Card variant="outlined" sx={{ flex: 1, minWidth: 150 }}>
									<CardContent>
										<Typography variant="body2" color="text.secondary">
											에러율
										</Typography>
										<Typography
											variant="h6"
											color={
												deploymentDetail.error_rate > 0.05 ? "error" : "success"
											}
										>
											{(deploymentDetail.error_rate * 100).toFixed(2)}%
										</Typography>
									</CardContent>
								</Card>
								<Card variant="outlined" sx={{ flex: 1, minWidth: 150 }}>
									<CardContent>
										<Typography variant="body2" color="text.secondary">
											평균 지연시간
										</Typography>
										<Typography variant="h6">
											{deploymentDetail.avg_latency_ms}ms
										</Typography>
									</CardContent>
								</Card>
							</Box>
						</Box>
					)}
				</CardContent>
			</Card>

			{/* Rollback Confirmation Dialog */}
			<Dialog
				open={rollbackDialogOpen}
				onClose={() => setRollbackDialogOpen(false)}
			>
				<DialogTitle>배포 롤백</DialogTitle>
				<DialogContent>
					<Typography>정말로 이 배포를 롤백하시겠습니까?</Typography>
					<Typography variant="body2" color="warning.main" sx={{ mt: 2 }}>
						이전 버전으로 롤백되며, 현재 배포는 비활성화됩니다.
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
