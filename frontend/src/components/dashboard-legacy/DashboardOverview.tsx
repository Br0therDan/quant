/**
 * Dashboard Overview - KPI Cards
 *
 * Epic 1: Story 1.1 - 전체 백테스트 수, 성공률, 평균 수익률 등 KPI 표시
 */
"use client";

import type { BacktestResponse } from "@/client";
import { useBacktest } from "@/hooks/useBacktests";
import {
	BarChart,
	CheckCircle,
	TrendingDown,
	TrendingUp,
} from "@mui/icons-material";
import { Box, Card, CardContent, Grid, Typography } from "@mui/material";

export default function DashboardOverview() {
	const { backtestList, isLoading } = useBacktest();

	// BacktestListResponse에서 backtests 배열 추출
	const backtests = backtestList?.backtests || [];

	// KPI 계산
	const totalBacktests = backtests.length;
	const successfulBacktests = backtests.filter(
		(bt: BacktestResponse) => bt.status === "completed",
	).length;
	const successRate =
		totalBacktests > 0
			? ((successfulBacktests / totalBacktests) * 100).toFixed(1)
			: "0";

	// 평균 수익률 계산 (완료된 백테스트만)
	const completedBacktests = backtests.filter(
		(bt: BacktestResponse) =>
			bt.status === "completed" && bt.performance?.total_return,
	);
	const avgReturn =
		completedBacktests.length > 0
			? completedBacktests.reduce(
					(sum: number, bt: BacktestResponse) =>
						sum + (bt.performance?.total_return || 0),
					0,
				) / completedBacktests.length
			: 0;

	const kpiCards = [
		{
			title: "총 백테스트",
			value: totalBacktests,
			icon: <BarChart fontSize="large" />,
			color: "#1976d2",
		},
		{
			title: "성공률",
			value: `${successRate}%`,
			icon: <CheckCircle fontSize="large" />,
			color: "#2e7d32",
		},
		{
			title: "평균 수익률",
			value: `${avgReturn.toFixed(2)}%`,
			icon:
				avgReturn >= 0 ? (
					<TrendingUp fontSize="large" />
				) : (
					<TrendingDown fontSize="large" />
				),
			color: avgReturn >= 0 ? "#2e7d32" : "#d32f2f",
		},
	];

	if (isLoading.backtestList) {
		return <Typography>로딩 중...</Typography>;
	}

	return (
		<Box>
			<Typography variant="h5" gutterBottom>
				대시보드 개요
			</Typography>
			<Grid container spacing={3}>
				{kpiCards.map((kpi, index) => (
					<Grid key={index} size={{ xs: 12, sm: 6, md: 4 }}>
						<Card>
							<CardContent>
								<Box
									display="flex"
									alignItems="center"
									justifyContent="space-between"
								>
									<Box>
										<Typography
											variant="body2"
											color="text.secondary"
											gutterBottom
										>
											{kpi.title}
										</Typography>
										<Typography variant="h4">{kpi.value}</Typography>
									</Box>
									<Box sx={{ color: kpi.color }}>{kpi.icon}</Box>
								</Box>
							</CardContent>
						</Card>
					</Grid>
				))}
			</Grid>
		</Box>
	);
}
