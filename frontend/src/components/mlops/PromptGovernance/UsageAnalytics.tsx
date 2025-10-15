/**
 * Prompt Usage Analytics Component
 */

"use client";

import { usePromptUsageLogs } from "@/hooks/usePromptGovernance";
import { CheckCircle, Refresh, TrendingUp, Warning } from "@mui/icons-material";
import { Box, Card, CardContent, Grid, Paper, Typography } from "@mui/material";
import { DataGrid, type GridColDef } from "@mui/x-data-grid";

interface UsageAnalyticsProps {
	promptId: string;
	version: string;
}

export default function UsageAnalytics({
	promptId,
	version,
}: UsageAnalyticsProps) {
	const { usageLogs, isLoading, error } = usePromptUsageLogs(promptId, version);

	const totalUsage = usageLogs?.length || 0;
	const successCount =
		usageLogs?.filter((log) => log.outcome === "success").length || 0;
	const avgToxicity =
		usageLogs && usageLogs.length > 0
			? usageLogs.reduce((sum, log) => sum + (log.toxicity_score || 0), 0) /
				usageLogs.length
			: 0;
	const successRate = totalUsage > 0 ? (successCount / totalUsage) * 100 : 0;

	const columns: GridColDef[] = [
		{
			field: "created_at",
			headerName: "시간",
			flex: 1,
			minWidth: 160,
			valueFormatter: (value) => {
				const date = value as Date | undefined;
				if (!date) return "-";
				return new Date(date).toLocaleString("ko-KR");
			},
		},
		{
			field: "session_id",
			headerName: "세션 ID",
			width: 200,
		},
		{
			field: "outcome",
			headerName: "결과",
			width: 100,
			align: "center",
			headerAlign: "center",
			renderCell: (params) => (
				<Typography
					variant="body2"
					color={params.value === "success" ? "success.main" : "error.main"}
					sx={{ fontWeight: 600 }}
				>
					{params.value === "success" ? "성공" : params.value || "-"}
				</Typography>
			),
		},
		{
			field: "toxicity_score",
			headerName: "유해성 점수",
			width: 140,
			align: "right",
			headerAlign: "right",
			valueFormatter: (value) => {
				const score = value as number | null | undefined;
				return score !== null && score !== undefined ? score.toFixed(2) : "-";
			},
		},
		{
			field: "hallucination_flags",
			headerName: "환각 플래그",
			flex: 1,
			minWidth: 150,
			valueFormatter: (value) => {
				const flags = value as string[] | undefined;
				return flags && flags.length > 0 ? flags.join(", ") : "-";
			},
		},
	];

	if (error) {
		return (
			<Card>
				<CardContent>
					<Typography color="error">
						사용 로그를 불러오는 중 오류가 발생했습니다.
					</Typography>
				</CardContent>
			</Card>
		);
	}

	return (
		<Paper sx={{ p: 3 }}>
			<Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
				사용 통계
			</Typography>

			<Grid container spacing={2} sx={{ mb: 3 }}>
				<Grid size={3}>
					<Card>
						<CardContent>
							<Box
								sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}
							>
								<Refresh color="primary" />
								<Typography variant="body2" color="text.secondary">
									총 사용 횟수
								</Typography>
							</Box>
							<Typography variant="h4" sx={{ fontWeight: 600 }}>
								{totalUsage}
							</Typography>
						</CardContent>
					</Card>
				</Grid>

				<Grid size={3}>
					<Card>
						<CardContent>
							<Box
								sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}
							>
								<CheckCircle color="success" />
								<Typography variant="body2" color="text.secondary">
									성공률
								</Typography>
							</Box>
							<Typography variant="h4" sx={{ fontWeight: 600 }}>
								{successRate.toFixed(1)}%
							</Typography>
						</CardContent>
					</Card>
				</Grid>

				<Grid size={3}>
					<Card>
						<CardContent>
							<Box
								sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}
							>
								<Warning color="warning" />
								<Typography variant="body2" color="text.secondary">
									평균 유해성
								</Typography>
							</Box>
							<Typography variant="h4" sx={{ fontWeight: 600 }}>
								{avgToxicity.toFixed(2)}
							</Typography>
						</CardContent>
					</Card>
				</Grid>

				<Grid size={3}>
					<Card>
						<CardContent>
							<Box
								sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}
							>
								<TrendingUp color="info" />
								<Typography variant="body2" color="text.secondary">
									성공 횟수
								</Typography>
							</Box>
							<Typography variant="h4" sx={{ fontWeight: 600 }}>
								{successCount}
							</Typography>
						</CardContent>
					</Card>
				</Grid>
			</Grid>

			<Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
				사용 로그
			</Typography>

			<DataGrid
				rows={usageLogs}
				columns={columns}
				getRowId={(row) => `${row.prompt_id}-${row.created_at}`}
				loading={isLoading}
				pageSizeOptions={[10, 25, 50]}
				initialState={{
					pagination: { paginationModel: { pageSize: 10 } },
				}}
				sx={{ height: 400 }}
			/>
		</Paper>
	);
}
