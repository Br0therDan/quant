/**
 * FeatureList Component
 *
 * Displays a paginated, filterable, and searchable list of features in the feature store.
 * Uses MUI DataGrid for efficient rendering and built-in features like sorting and pagination.
 *
 * @module components/mlops/feature-store/FeatureList
 */

import {
	useFeatureStore,
	type Feature,
	type FeaturesQueryParams,
} from "@/hooks/useFeatureStore";
import AddIcon from "@mui/icons-material/Add";
import SearchIcon from "@mui/icons-material/Search";
import type { SelectChangeEvent } from "@mui/material";
import {
	Box,
	Button,
	Card,
	CardContent,
	Chip,
	CircularProgress,
	FormControl,
	InputLabel,
	MenuItem,
	Select,
	TextField,
	Typography,
} from "@mui/material";
import type { GridColDef, GridPaginationModel } from "@mui/x-data-grid";
import { DataGrid } from "@mui/x-data-grid";
import { useState } from "react";

// ============================================================================
// Component Props
// ============================================================================

interface FeatureListProps {
	/**
	 * Callback when user clicks on a feature row
	 */
	onFeatureClick?: (featureId: string) => void;

	/**
	 * Callback when user clicks the "Create Feature" button
	 */
	onCreateClick?: () => void;
}

// ============================================================================
// Type Color Mapping
// ============================================================================

const getTypeColor = (type: Feature["type"]) => {
	const colorMap: Record<
		Feature["type"],
		"primary" | "success" | "warning" | "error" | "info"
	> = {
		numerical: "primary",
		categorical: "success",
		binary: "warning",
		text: "info",
		datetime: "error",
	};
	return colorMap[type] || "default";
};

// ============================================================================
// Component Implementation
// ============================================================================

export const FeatureList: React.FC<FeatureListProps> = ({
	onFeatureClick,
	onCreateClick,
}) => {
	// ============================================================================
	// State
	// ============================================================================

	const [queryParams, setQueryParams] = useState<FeaturesQueryParams>({
		page: 1,
		limit: 10,
		sort_by: "created_at",
		sort_order: "desc",
	});

	const [paginationModel, setPaginationModel] = useState<GridPaginationModel>({
		page: 0,
		pageSize: 10,
	});

	// ============================================================================
	// Hooks
	// ============================================================================

	const { featuresList, featuresTotal, isLoadingFeatures, isFetchingFeatures } =
		useFeatureStore(queryParams);

	// ============================================================================
	// Event Handlers
	// ============================================================================

	const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
		const search = event.target.value;
		setQueryParams((prev) => ({
			...prev,
			search: search || undefined,
			page: 1,
		}));
		setPaginationModel((prev) => ({ ...prev, page: 0 }));
	};

	const handleTypeFilterChange = (
		event: SelectChangeEvent<Feature["type"] | "">,
	) => {
		const value = event.target.value as Feature["type"] | "";
		setQueryParams((prev) => ({
			...prev,
			type: value || undefined,
			page: 1,
		}));
		setPaginationModel((prev) => ({ ...prev, page: 0 }));
	};

	const handleSortChange = (event: SelectChangeEvent<string>) => {
		const [sortBy, sortOrder] = event.target.value.split(":");
		setQueryParams((prev) => ({
			...prev,
			sort_by: sortBy as FeaturesQueryParams["sort_by"],
			sort_order: sortOrder as FeaturesQueryParams["sort_order"],
		}));
	};

	const handlePaginationChange = (model: GridPaginationModel) => {
		setPaginationModel(model);
		setQueryParams((prev) => ({
			...prev,
			page: model.page + 1,
			limit: model.pageSize,
		}));
	};

	const handleRowClick = (featureId: string) => {
		onFeatureClick?.(featureId);
	};

	// ============================================================================
	// DataGrid Columns
	// ============================================================================

	const columns: GridColDef<Feature>[] = [
		{
			field: "name",
			headerName: "이름",
			flex: 1.5,
			minWidth: 200,
		},
		{
			field: "type",
			headerName: "타입",
			width: 130,
			renderCell: (params) => (
				<Chip
					label={params.value}
					color={getTypeColor(params.value as Feature["type"])}
					size="small"
				/>
			),
		},
		{
			field: "tags",
			headerName: "태그",
			flex: 1,
			minWidth: 180,
			renderCell: (params) => (
				<Box sx={{ display: "flex", gap: 0.5, flexWrap: "wrap" }}>
					{params.value.slice(0, 3).map((tag: string) => (
						<Chip key={tag} label={tag} size="small" variant="outlined" />
					))}
					{params.value.length > 3 && (
						<Chip
							label={`+${params.value.length - 3}`}
							size="small"
							variant="outlined"
						/>
					)}
				</Box>
			),
		},
		{
			field: "usage_count",
			headerName: "사용 횟수",
			width: 110,
			align: "right",
			headerAlign: "right",
		},
		{
			field: "version",
			headerName: "버전",
			width: 80,
			align: "center",
			headerAlign: "center",
		},
		{
			field: "created_at",
			headerName: "생성일",
			width: 180,
			valueFormatter: (value: string) => {
				return new Date(value).toLocaleString("ko-KR", {
					year: "numeric",
					month: "short",
					day: "numeric",
					hour: "2-digit",
					minute: "2-digit",
				});
			},
		},
	];

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
						피처 목록
					</Typography>
					<Button
						variant="contained"
						startIcon={<AddIcon />}
						onClick={onCreateClick}
					>
						피처 생성
					</Button>
				</Box>

				{/* Filters */}
				<Box sx={{ display: "flex", gap: 2, mb: 3, flexWrap: "wrap" }}>
					{/* Search */}
					<TextField
						placeholder="피처 이름 검색..."
						size="small"
						sx={{ flexGrow: 1, minWidth: 200 }}
						onChange={handleSearchChange}
						slotProps={{
							input: {
								startAdornment: (
									<SearchIcon sx={{ color: "text.secondary", mr: 1 }} />
								),
							},
						}}
					/>

					{/* Type Filter */}
					<FormControl size="small" sx={{ minWidth: 150 }}>
						<InputLabel>타입</InputLabel>
						<Select
							value={queryParams.type || ""}
							label="타입"
							onChange={handleTypeFilterChange}
						>
							<MenuItem value="">전체</MenuItem>
							<MenuItem value="numerical">Numerical</MenuItem>
							<MenuItem value="categorical">Categorical</MenuItem>
							<MenuItem value="binary">Binary</MenuItem>
							<MenuItem value="text">Text</MenuItem>
							<MenuItem value="datetime">Datetime</MenuItem>
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
							<MenuItem value="usage_count:desc">사용 빈도순</MenuItem>
							<MenuItem value="usage_count:asc">사용 빈도 (낮은순)</MenuItem>
						</Select>
					</FormControl>
				</Box>

				{/* DataGrid */}
				<Box sx={{ height: 600, width: "100%" }}>
					<DataGrid
						rows={featuresList}
						columns={columns}
						paginationModel={paginationModel}
						onPaginationModelChange={handlePaginationChange}
						pageSizeOptions={[5, 10, 25, 50]}
						rowCount={featuresTotal}
						paginationMode="server"
						loading={isLoadingFeatures || isFetchingFeatures}
						onRowClick={(params) => handleRowClick(params.row.id)}
						disableRowSelectionOnClick
						sx={{
							"& .MuiDataGrid-row": {
								cursor: "pointer",
							},
						}}
						slots={{
							loadingOverlay: () => (
								<Box
									sx={{
										display: "flex",
										justifyContent: "center",
										alignItems: "center",
										height: "100%",
									}}
								>
									<CircularProgress />
								</Box>
							),
							noRowsOverlay: () => (
								<Box
									sx={{
										display: "flex",
										justifyContent: "center",
										alignItems: "center",
										height: "100%",
										flexDirection: "column",
										gap: 2,
									}}
								>
									<Typography variant="h6" color="text.secondary">
										피처가 없습니다
									</Typography>
									<Button
										variant="contained"
										startIcon={<AddIcon />}
										onClick={onCreateClick}
									>
										첫 피처 생성하기
									</Button>
								</Box>
							),
						}}
					/>
				</Box>

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
						총 {featuresTotal.toLocaleString()}개의 피처
					</Typography>
					{isFetchingFeatures && !isLoadingFeatures && (
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
