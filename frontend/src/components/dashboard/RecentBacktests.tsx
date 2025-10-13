/**
 * Recent Backtests - 최근 백테스트 목록
 *
 * Epic 1: Story 1.1 - 최근 5개 백테스트 표시
 */
"use client";

import type { BacktestResponse } from "@/client";
import { useBacktest } from "@/hooks/useBacktests";
import { ArrowForward } from "@mui/icons-material";
import {
	Box,
	Card,
	CardContent,
	Chip,
	IconButton,
	List,
	ListItem,
	ListItemText,
	Typography,
} from "@mui/material";
import { useRouter } from "next/navigation";

export default function RecentBacktests() {
	const router = useRouter();
	const { backtestList, isLoading } = useBacktest();

	const backtests = backtestList?.backtests || [];
	const recentBacktests = backtests
		.sort(
			(a: BacktestResponse, b: BacktestResponse) =>
				new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
		)
		.slice(0, 5);

	const getStatusColor = (status: string) => {
		switch (status) {
			case "completed":
				return "success";
			case "running":
				return "primary";
			case "failed":
				return "error";
			case "pending":
				return "warning";
			default:
				return "default";
		}
	};

	const getStatusLabel = (status: string) => {
		const labels: Record<string, string> = {
			completed: "완료",
			running: "실행 중",
			failed: "실패",
			pending: "대기",
			cancelled: "취소",
		};
		return labels[status] || status;
	};

	if (isLoading.backtestList) {
		return (
			<Card>
				<CardContent>
					<Typography variant="h6" gutterBottom>
						최근 백테스트
					</Typography>
					<Typography color="text.secondary">로딩 중...</Typography>
				</CardContent>
			</Card>
		);
	}

	if (recentBacktests.length === 0) {
		return (
			<Card>
				<CardContent>
					<Typography variant="h6" gutterBottom>
						최근 백테스트
					</Typography>
					<Typography color="text.secondary">백테스트가 없습니다.</Typography>
				</CardContent>
			</Card>
		);
	}

	return (
		<Card>
			<CardContent>
				<Box
					display="flex"
					justifyContent="space-between"
					alignItems="center"
					mb={2}
				>
					<Typography variant="h6">최근 백테스트</Typography>
					<IconButton size="small" onClick={() => router.push("/backtests")}>
						<ArrowForward />
					</IconButton>
				</Box>
				<List>
					{recentBacktests.map((backtest: BacktestResponse) => (
						<ListItem
							key={backtest.id}
							sx={{
								borderRadius: 1,
								mb: 1,
								cursor: "pointer",
								"&:hover": {
									bgcolor: "action.hover",
								},
							}}
							onClick={() => router.push(`/backtests/${backtest.id}`)}
						>
							<ListItemText
								primary={
									<Box display="flex" alignItems="center" gap={1}>
										<Typography variant="subtitle2">{backtest.name}</Typography>
										<Chip
											label={getStatusLabel(backtest.status)}
											size="small"
											color={getStatusColor(backtest.status) as any}
										/>
									</Box>
								}
								secondary={
									<Box>
										<Typography variant="caption" color="text.secondary">
											{new Date(backtest.created_at).toLocaleDateString(
												"ko-KR",
											)}
										</Typography>
										{backtest.performance?.total_return !== undefined && (
											<Typography
												variant="caption"
												color={
													backtest.performance.total_return >= 0
														? "success.main"
														: "error.main"
												}
												sx={{ ml: 2 }}
											>
												수익률: {backtest.performance.total_return.toFixed(2)}%
											</Typography>
										)}
									</Box>
								}
							/>
						</ListItem>
					))}
				</List>
			</CardContent>
		</Card>
	);
}
