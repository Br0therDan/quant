/**
 * ExperimentList Component
 *
 * Displays a list of ML experiments with:
 * - Filtering by status and date range
 * - Sorting by name, date, duration
 * - Experiment comparison (multi-select)
 * - Status badges and metrics display
 *
 * @module components/mlops/model-lifecycle/ExperimentList
 */

import {
	useModelLifecycle,
	type Experiment,
	type ExperimentsQueryParams,
} from "@/hooks/useModelLifecycle";
import CompareArrowsIcon from "@mui/icons-material/CompareArrows";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import type { SelectChangeEvent } from "@mui/material";
import {
	Alert,
	Box,
	Button,
	Card,
	CardContent,
	Checkbox,
	Chip,
	CircularProgress,
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
	TextField,
	Typography,
} from "@mui/material";
import { useState } from "react";

// ============================================================================
// Component Props
// ============================================================================

interface ExperimentListProps {
	/**
	 * Callback when experiment row is clicked
	 */
	onExperimentClick?: (experimentId: string) => void;

	/**
	 * Callback when compare button is clicked
	 */
	onCompareClick?: (experimentIds: string[]) => void;

	/**
	 * Callback when create experiment button is clicked
	 */
	onCreateClick?: () => void;
}

// ============================================================================
// Helper Functions
// ============================================================================

const getStatusColor = (
	status: Experiment["status"],
): "success" | "warning" | "error" | "info" | "default" => {
	const colorMap: Record<
		Experiment["status"],
		"success" | "warning" | "error" | "info"
	> = {
		active: "info",
		archived: "warning",
	};
	return colorMap[status] || "default";
};

const getStatusLabel = (status: Experiment["status"]): string => {
	const labelMap: Record<Experiment["status"], string> = {
		active: "활성",
		archived: "보관됨",
	};
	return labelMap[status] || status;
};

const formatDuration = (seconds?: number | null): string => {
	if (!seconds) return "-";
	const hours = Math.floor(seconds / 3600);
	const minutes = Math.floor((seconds % 3600) / 60);
	if (hours > 0) return `${hours}시간 ${minutes}분`;
	return `${minutes}분`;
}; // ============================================================================
// Component Implementation
// ============================================================================

export const ExperimentList: React.FC<ExperimentListProps> = ({
	onExperimentClick,
	onCompareClick,
	onCreateClick,
}) => {
	// ============================================================================
	// State
	// ============================================================================

	const [queryParams, setQueryParams] = useState<ExperimentsQueryParams>({
		page: 1,
		limit: 10,
		sort_by: "created_at",
		sort_order: "desc",
	});

	const [selectedExperiments, setSelectedExperiments] = useState<string[]>([]);

	// ============================================================================
	// Hooks
	// ============================================================================

	const {
		experimentsList,
		experimentsTotal,
		isLoadingExperiments,
		isFetchingExperiments,
	} = useModelLifecycle(queryParams);

	// ============================================================================
	// Event Handlers
	// ============================================================================

	const handleStatusFilterChange = (event: SelectChangeEvent<string>) => {
		const value = event.target.value as Experiment["status"] | "";
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
			sort_by: sortBy as ExperimentsQueryParams["sort_by"],
			sort_order: sortOrder as ExperimentsQueryParams["sort_order"],
		}));
	};

	const handleDateFromChange = (event: React.ChangeEvent<HTMLInputElement>) => {
		setQueryParams((prev) => ({
			...prev,
			date_from: event.target.value || undefined,
			page: 1,
		}));
	};

	const handleDateToChange = (event: React.ChangeEvent<HTMLInputElement>) => {
		setQueryParams((prev) => ({
			...prev,
			date_to: event.target.value || undefined,
			page: 1,
		}));
	};

	const handleExperimentSelect = (experimentId: string) => {
		setSelectedExperiments((prev) => {
			if (prev.includes(experimentId)) {
				return prev.filter((id) => id !== experimentId);
			}
			return [...prev, experimentId];
		});
	};

	const handleSelectAll = (event: React.ChangeEvent<HTMLInputElement>) => {
		if (event.target.checked) {
			setSelectedExperiments(experimentsList.map((exp) => exp.id));
		} else {
			setSelectedExperiments([]);
		}
	};

	const handleCompareClick = () => {
		if (selectedExperiments.length >= 2) {
			onCompareClick?.(selectedExperiments);
		}
	};

	// ============================================================================
	// Render Loading State
	// ============================================================================

	if (isLoadingExperiments) {
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
					<Typography variant="h5" component="h2">
						실험 목록
					</Typography>
					<Box sx={{ display: "flex", gap: 1 }}>
						<Button
							variant="outlined"
							startIcon={<CompareArrowsIcon />}
							onClick={handleCompareClick}
							disabled={selectedExperiments.length < 2}
						>
							비교 ({selectedExperiments.length})
						</Button>
						<Button
							variant="contained"
							startIcon={<PlayArrowIcon />}
							onClick={onCreateClick}
						>
							실험 생성
						</Button>
					</Box>
				</Box>

				{/* Filters */}
				<Box sx={{ display: "flex", gap: 2, mb: 3, flexWrap: "wrap" }}>
					{/* Status Filter */}
					<FormControl size="small" sx={{ minWidth: 150 }}>
						<InputLabel>상태</InputLabel>
						<Select
							value={queryParams.status || ""}
							label="상태"
							onChange={handleStatusFilterChange}
						>
							<MenuItem value="">전체</MenuItem>
							<MenuItem value="running">실행 중</MenuItem>
							<MenuItem value="completed">완료</MenuItem>
							<MenuItem value="failed">실패</MenuItem>
							<MenuItem value="cancelled">취소됨</MenuItem>
						</Select>
					</FormControl>

					{/* Date Range */}
					<TextField
						type="date"
						label="시작일"
						size="small"
						slotProps={{ inputLabel: { shrink: true } }}
						onChange={handleDateFromChange}
						sx={{ minWidth: 150 }}
					/>
					<TextField
						type="date"
						label="종료일"
						size="small"
						slotProps={{ inputLabel: { shrink: true } }}
						onChange={handleDateToChange}
						sx={{ minWidth: 150 }}
					/>

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
							<MenuItem value="duration:desc">실행 시간 (긴 순)</MenuItem>
							<MenuItem value="duration:asc">실행 시간 (짧은 순)</MenuItem>
						</Select>
					</FormControl>
				</Box>

				{/* Table */}
				{experimentsList.length === 0 ? (
					<Alert severity="info">실험이 없습니다. 첫 실험을 생성하세요.</Alert>
				) : (
					<TableContainer component={Paper} variant="outlined">
						<Table>
							<TableHead>
								<TableRow>
									<TableCell padding="checkbox">
										<Checkbox
											indeterminate={
												selectedExperiments.length > 0 &&
												selectedExperiments.length < experimentsList.length
											}
											checked={
												experimentsList.length > 0 &&
												selectedExperiments.length === experimentsList.length
											}
											onChange={handleSelectAll}
										/>
									</TableCell>
									<TableCell>이름</TableCell>
									<TableCell>상태</TableCell>
									<TableCell align="right">정확도</TableCell>
									<TableCell align="right">F1 점수</TableCell>
									<TableCell align="right">실행 시간</TableCell>
									<TableCell>생성일</TableCell>
									<TableCell>생성시간</TableCell>
								</TableRow>
							</TableHead>
							<TableBody>
								{experimentsList.map((experiment) => (
									<TableRow
										key={experiment.id}
										hover
										sx={{ cursor: "pointer" }}
										onClick={() => onExperimentClick?.(experiment.id)}
									>
										<TableCell padding="checkbox">
											<Checkbox
												checked={selectedExperiments.includes(experiment.id)}
												onChange={() => handleExperimentSelect(experiment.id)}
												onClick={(e) => e.stopPropagation()}
											/>
										</TableCell>
										<TableCell>
											<Typography variant="body2" fontWeight="medium">
												{experiment.name}
											</Typography>
											<Typography variant="caption" color="text.secondary">
												{experiment.description}
											</Typography>
										</TableCell>
										<TableCell>
											<Chip
												label={getStatusLabel(experiment.status)}
												color={getStatusColor(experiment.status)}
												size="small"
											/>
										</TableCell>
										<TableCell align="right">
											{experiment.metrics?.accuracy
												? (experiment.metrics.accuracy * 100).toFixed(2) + "%"
												: "-"}
										</TableCell>
										<TableCell align="right">
											{experiment.metrics?.f1_score
												? (experiment.metrics.f1_score * 100).toFixed(2) + "%"
												: "-"}
										</TableCell>
										<TableCell align="right">
											{formatDuration(experiment.duration_seconds)}
										</TableCell>
										<TableCell>
											{new Date(experiment.created_at).toLocaleDateString(
												"ko-KR",
											)}
										</TableCell>
										<TableCell>
											{new Date(experiment.created_at).toLocaleTimeString(
												"ko-KR",
											)}
										</TableCell>
									</TableRow>
								))}
							</TableBody>
						</Table>
					</TableContainer>
				)}

				{/* Summary */}
				<Box
					sx={{
						mt: 2,
						display: "flex",
						justifyContent: "space-between",
						alignItems: "center",
					}}
				>
					<Typography variant="body2" color="text.secondary">
						총 {experimentsTotal.toLocaleString()}개의 실험
					</Typography>
					{isFetchingExperiments && !isLoadingExperiments && (
						<Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
							<CircularProgress size={16} />
							<Typography variant="body2" color="text.secondary">
								업데이트 중...
							</Typography>
						</Box>
					)}
				</Box>
			</CardContent>
		</Card>
	);
};
