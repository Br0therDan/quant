/**
 * Prompt Template List Component
 *
 * LLM 프롬프트 템플릿 목록 및 필터링
 *
 * 주요 기능:
 * - DataGrid 기반 템플릿 목록 표시
 * - 상태 필터링 (Draft, Under Review, Approved, Rejected)
 * - 태그 필터링
 * - 새 템플릿 생성 버튼
 * - 템플릿 클릭 시 상세 페이지 이동
 *
 * @author AI MLOps Team
 * @since Phase 4 - Day 9
 */

"use client";

import { usePromptGovernance } from "@/hooks/usePromptGovernance";
import { Add } from "@mui/icons-material";
import {
	Box,
	Button,
	Chip,
	FormControl,
	InputLabel,
	MenuItem,
	Paper,
	Select,
	Typography,
} from "@mui/material";
import { DataGrid, type GridColDef } from "@mui/x-data-grid";
import { useRouter } from "next/navigation";
import { useState } from "react";

// Status 색상 매핑
const STATUS_COLORS: Record<
	string,
	"default" | "warning" | "success" | "error"
> = {
	draft: "default",
	under_review: "warning",
	approved: "success",
	rejected: "error",
};

export default function PromptTemplateList() {
	const router = useRouter();
	const [statusFilter, setStatusFilter] = useState<string>("");
	const [tagFilter, setTagFilter] = useState<string>("");

	const { templatesList, isLoadingTemplates } = usePromptGovernance({
		status: statusFilter || undefined,
		tag: tagFilter || undefined,
	});

	// ============================================================================
	// DataGrid Columns
	// ============================================================================

	const columns: GridColDef[] = [
		{
			field: "name",
			headerName: "템플릿 이름",
			flex: 1.5,
			minWidth: 200,
		},
		{
			field: "version",
			headerName: "버전",
			width: 100,
			align: "center",
			headerAlign: "center",
		},
		{
			field: "status",
			headerName: "상태",
			width: 140,
			align: "center",
			headerAlign: "center",
			renderCell: (params) => {
				const status = params.value as string;
				const statusLabels: Record<string, string> = {
					draft: "초안",
					under_review: "검토 중",
					approved: "승인됨",
					rejected: "거부됨",
				};

				return (
					<Chip
						label={statusLabels[status] || status}
						color={STATUS_COLORS[status] || "default"}
						size="small"
					/>
				);
			},
		},
		{
			field: "tags",
			headerName: "태그",
			flex: 1,
			minWidth: 200,
			renderCell: (params) => {
				const tags = params.value as string[];
				if (!tags || tags.length === 0) return "-";
				return (
					<Box sx={{ display: "flex", gap: 0.5, flexWrap: "wrap" }}>
						{tags.slice(0, 3).map((tag) => (
							<Chip key={tag} label={tag} size="small" variant="outlined" />
						))}
						{tags.length > 3 && (
							<Chip label={`+${tags.length - 3}`} size="small" />
						)}
					</Box>
				);
			},
		},
		{
			field: "created_by",
			headerName: "생성자",
			width: 140,
		},
		{
			field: "created_at",
			headerName: "생성일",
			width: 160,
			valueFormatter: (value) => {
				const date = value as string | undefined;
				if (!date) return "-";
				return new Date(date).toLocaleString("ko-KR");
			},
		},
		{
			field: "updated_at",
			headerName: "수정일",
			width: 160,
			valueFormatter: (value) => {
				const date = value as string | undefined;
				if (!date) return "-";
				return new Date(date).toLocaleString("ko-KR");
			},
		},
	];

	// ============================================================================
	// Event Handlers
	// ============================================================================

	const handleRowClick = (params: {
		row: { prompt_id: string; version: string };
	}) => {
		router.push(
			`/mlops/prompt-governance/${params.row.prompt_id}/${params.row.version}`,
		);
	};

	const handleCreateTemplate = () => {
		router.push("/mlops/prompt-governance/new");
	};

	// ============================================================================
	// Render
	// ============================================================================

	return (
		<Paper sx={{ p: 3 }}>
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
					<Typography variant="h5" sx={{ fontWeight: 600 }}>
						프롬프트 템플릿 관리
					</Typography>
					<Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
						LLM 프롬프트 템플릿 생성, 버전 관리, 승인 워크플로우
					</Typography>
				</Box>
				<Button
					variant="contained"
					startIcon={<Add />}
					onClick={handleCreateTemplate}
					sx={{ height: "fit-content" }}
				>
					새 템플릿
				</Button>
			</Box>

			{/* Filters */}
			<Box sx={{ display: "flex", gap: 2, mb: 3 }}>
				<FormControl sx={{ minWidth: 200 }}>
					<InputLabel>상태 필터</InputLabel>
					<Select
						value={statusFilter}
						onChange={(e) => setStatusFilter(e.target.value)}
						label="상태 필터"
					>
						<MenuItem value="">
							<em>전체</em>
						</MenuItem>
						<MenuItem value="draft">초안</MenuItem>
						<MenuItem value="under_review">검토 중</MenuItem>
						<MenuItem value="approved">승인됨</MenuItem>
						<MenuItem value="rejected">거부됨</MenuItem>
					</Select>
				</FormControl>

				<FormControl sx={{ minWidth: 200 }}>
					<InputLabel>태그 필터</InputLabel>
					<Select
						value={tagFilter}
						onChange={(e) => setTagFilter(e.target.value)}
						label="태그 필터"
					>
						<MenuItem value="">
							<em>전체</em>
						</MenuItem>
						<MenuItem value="classification">Classification</MenuItem>
						<MenuItem value="summarization">Summarization</MenuItem>
						<MenuItem value="generation">Generation</MenuItem>
						<MenuItem value="analysis">Analysis</MenuItem>
					</Select>
				</FormControl>
			</Box>

			{/* DataGrid */}
			<DataGrid
				rows={templatesList}
				columns={columns}
				getRowId={(row) => `${row.prompt_id}-${row.version}`}
				loading={isLoadingTemplates}
				onRowClick={handleRowClick}
				pageSizeOptions={[10, 25, 50]}
				initialState={{
					pagination: { paginationModel: { pageSize: 25 } },
				}}
				sx={{
					height: 600,
					"& .MuiDataGrid-row": {
						cursor: "pointer",
					},
					"& .MuiDataGrid-row:hover": {
						backgroundColor: "action.hover",
					},
				}}
			/>
		</Paper>
	);
}
