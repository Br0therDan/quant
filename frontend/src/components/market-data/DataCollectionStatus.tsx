/**
 * Data Collection Status - 데이터 수집 진행 상태
 *
 * Epic 2: Story 2.2 - 실시간 수집 진행률 및 히스토리
 */
"use client";

import {
	CheckCircle,
	CloudDownload,
	Error as ErrorIcon,
	Schedule,
} from "@mui/icons-material";
import {
	Box,
	Card,
	CardContent,
	Chip,
	Divider,
	LinearProgress,
	List,
	ListItem,
	Typography,
} from "@mui/material";

interface CollectionTask {
	symbol: string;
	status: "pending" | "in_progress" | "completed" | "failed";
	progress?: number;
	started_at?: string;
	completed_at?: string;
	error_message?: string;
}

interface DataCollectionStatusProps {
	tasks: CollectionTask[];
	overallProgress?: number;
	isCollecting?: boolean;
}

function TaskItem({ task }: { task: CollectionTask }) {
	const getStatusIcon = (status: string) => {
		switch (status) {
			case "completed":
				return <CheckCircle fontSize="small" color="success" />;
			case "failed":
				return <ErrorIcon fontSize="small" color="error" />;
			case "in_progress":
				return <CloudDownload fontSize="small" color="primary" />;
			case "pending":
				return <Schedule fontSize="small" color="action" />;
			default:
				return null;
		}
	};

	const getStatusLabel = (status: string) => {
		switch (status) {
			case "completed":
				return "완료";
			case "failed":
				return "실패";
			case "in_progress":
				return "진행 중";
			case "pending":
				return "대기";
			default:
				return status;
		}
	};

	const getStatusColor = (status: string) => {
		switch (status) {
			case "completed":
				return "success";
			case "failed":
				return "error";
			case "in_progress":
				return "primary";
			case "pending":
				return "default";
			default:
				return "default";
		}
	};

	const formatTime = (dateString?: string) => {
		if (!dateString) return null;
		try {
			return new Date(dateString).toLocaleTimeString("ko-KR", {
				hour: "2-digit",
				minute: "2-digit",
				second: "2-digit",
			});
		} catch {
			return dateString;
		}
	};

	return (
		<ListItem sx={{ px: 0 }}>
			<Box display="flex" alignItems="center" gap={1.5} width="100%">
				{getStatusIcon(task.status)}
				<Box flexGrow={1}>
					<Box
						display="flex"
						alignItems="center"
						justifyContent="space-between"
						mb={0.5}
					>
						<Typography variant="body2" fontWeight="medium">
							{task.symbol}
						</Typography>
						<Chip
							label={getStatusLabel(task.status)}
							size="small"
							color={getStatusColor(task.status) as any}
						/>
					</Box>
					{task.status === "in_progress" && task.progress !== undefined && (
						<Box>
							<LinearProgress
								variant="determinate"
								value={task.progress}
								sx={{ height: 4, borderRadius: 2 }}
							/>
							<Typography variant="caption" color="text.secondary">
								{task.progress.toFixed(0)}%
							</Typography>
						</Box>
					)}
					{task.error_message && (
						<Typography variant="caption" color="error.main">
							{task.error_message}
						</Typography>
					)}
					{(task.started_at || task.completed_at) && (
						<Typography variant="caption" color="text.secondary">
							{task.started_at && `시작: ${formatTime(task.started_at)}`}
							{task.completed_at && ` | 완료: ${formatTime(task.completed_at)}`}
						</Typography>
					)}
				</Box>
			</Box>
		</ListItem>
	);
}

export default function DataCollectionStatus({
	tasks,
	overallProgress,
	isCollecting = false,
}: DataCollectionStatusProps) {
	const totalTasks = tasks.length;
	const completedTasks = tasks.filter((t) => t.status === "completed").length;
	const failedTasks = tasks.filter((t) => t.status === "failed").length;
	const inProgressTasks = tasks.filter(
		(t) => t.status === "in_progress",
	).length;
	const pendingTasks = tasks.filter((t) => t.status === "pending").length;

	return (
		<Card>
			<CardContent>
				<Typography variant="h6" gutterBottom>
					데이터 수집 상태
				</Typography>

				{/* 전체 진행률 */}
				{isCollecting && overallProgress !== undefined && (
					<Box mb={2}>
						<Box
							display="flex"
							alignItems="center"
							justifyContent="space-between"
							mb={1}
						>
							<Typography variant="body2">전체 진행률</Typography>
							<Typography variant="body2" fontWeight="medium">
								{overallProgress.toFixed(0)}%
							</Typography>
						</Box>
						<LinearProgress
							variant="determinate"
							value={overallProgress}
							sx={{ height: 8, borderRadius: 4 }}
						/>
					</Box>
				)}

				{/* 상태 요약 */}
				<Box display="flex" gap={1} mb={2} flexWrap="wrap">
					<Chip label={`전체: ${totalTasks}`} size="small" variant="outlined" />
					{completedTasks > 0 && (
						<Chip
							label={`완료: ${completedTasks}`}
							size="small"
							color="success"
							variant="outlined"
						/>
					)}
					{inProgressTasks > 0 && (
						<Chip
							label={`진행 중: ${inProgressTasks}`}
							size="small"
							color="primary"
							variant="outlined"
						/>
					)}
					{pendingTasks > 0 && (
						<Chip
							label={`대기: ${pendingTasks}`}
							size="small"
							color="default"
							variant="outlined"
						/>
					)}
					{failedTasks > 0 && (
						<Chip
							label={`실패: ${failedTasks}`}
							size="small"
							color="error"
							variant="outlined"
						/>
					)}
				</Box>

				<Divider sx={{ my: 2 }} />

				{/* 작업 목록 */}
				{tasks.length > 0 ? (
					<Box sx={{ maxHeight: 400, overflow: "auto" }}>
						<List dense disablePadding>
							{tasks.map((task, index) => (
								<TaskItem key={`${task.symbol}-${index}`} task={task} />
							))}
						</List>
					</Box>
				) : (
					<Typography variant="body2" color="text.secondary" textAlign="center">
						수집 작업이 없습니다.
					</Typography>
				)}
			</CardContent>
		</Card>
	);
}
