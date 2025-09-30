/** biome-ignore-all lint/suspicious/noArrayIndexKey: <explanation> */
/** biome-ignore-all lint/suspicious/noExplicitAny: <explanation> */
"use client";

import {
	ArrowBack,
	Assessment,
	CheckCircle,
	Error as ErrorIcon,
	Monitor,
	Refresh,
	Schedule,
	Settings,
	Stop,
	Timeline,
	TrendingUp,
} from "@mui/icons-material";
import {
	Alert,
	Box,
	Button,
	Card,
	CardContent,
	Chip,
	Container,
	FormControlLabel,
	Grid,
	IconButton,
	LinearProgress,
	Paper,
	Stack,
	Switch,
	Table,
	TableBody,
	TableCell,
	TableContainer,
	TableHead,
	TableRow,
	Tooltip,
	Typography,
} from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import PageContainer from "@/components/layout/PageContainer";
import {
	backtestsGetBacktestOptions,
	backtestUtils,
	useBacktestActions,
} from "@/services/backtestsQuery";

interface LogEntry {
	timestamp: string;
	level: "info" | "warning" | "error";
	message: string;
	details?: string;
}

interface PerformanceMetrics {
	timestamp: string;
	portfolio_value: number;
	total_return: number;
	daily_return: number;
	drawdown: number;
	trades_count: number;
}

// Mock data for demonstration
const mockLogs: LogEntry[] = [
	{
		timestamp: new Date().toISOString(),
		level: "info",
		message: "백테스트 시작됨",
		details: "전략: SMA Crossover, 기간: 2023-01-01 ~ 2024-01-01",
	},
	{
		timestamp: new Date(Date.now() - 60000).toISOString(),
		level: "info",
		message: "매수 신호 발생",
		details: "AAPL 100주 매수",
	},
	{
		timestamp: new Date(Date.now() - 120000).toISOString(),
		level: "warning",
		message: "포트폴리오 위험도 증가",
		details: "집중도가 임계치를 초과했습니다",
	},
	{
		timestamp: new Date(Date.now() - 180000).toISOString(),
		level: "error",
		message: "데이터 수집 오류",
		details: "일부 종목의 가격 데이터를 가져올 수 없습니다",
	},
];

const mockMetrics: PerformanceMetrics[] = [
	{
		timestamp: new Date().toISOString(),
		portfolio_value: 1050000,
		total_return: 0.05,
		daily_return: 0.002,
		drawdown: -0.02,
		trades_count: 15,
	},
	{
		timestamp: new Date(Date.now() - 3600000).toISOString(),
		portfolio_value: 1048000,
		total_return: 0.048,
		daily_return: 0.001,
		drawdown: -0.015,
		trades_count: 14,
	},
];

export default function BacktestMonitoringPage() {
	const params = useParams();
	const router = useRouter();
	const backtestId = params.id as string;
	const [autoRefresh, setAutoRefresh] = useState(true);
	const [refreshInterval, setRefreshInterval] = useState(5000); // 5 seconds

	// Fetch backtest data
	const {
		data: backtestResponse,
		isLoading: backtestLoading,
		error: backtestError,
		refetch: refetchBacktest,
	} = useQuery(
		backtestsGetBacktestOptions({ path: { backtest_id: backtestId } }),
	);

	const {
		data: resultsResponse,
		isLoading: resultsLoading,
		refetch: refetchResults,
	} = useQuery({
		queryKey: ["backtest-results", backtestId],
		queryFn: async () => {
			if (!backtestId) throw new Error("No backtest ID");
			// Return mock data for now since API is not properly configured
			return {};
		},
		enabled: !!backtestId,
	});

	const backtest = backtestResponse;
	const results = resultsResponse;

	const { executeBacktest, deleteBacktest } = useBacktestActions();

	const stopBacktest = async (id: string) => {
		// TODO: Implement stop functionality
		console.log("Stop backtest:", id);
	};

	// Auto-refresh logic
	useEffect(() => {
		if (!autoRefresh || !backtest?.status) return;

		const status = backtest.status as string;
		if (!backtestUtils.isRunning(status as any)) return;

		const interval = setInterval(() => {
			refetchBacktest();
			refetchResults();
		}, refreshInterval);

		return () => clearInterval(interval);
	}, [
		autoRefresh,
		refreshInterval,
		backtest?.status,
		refetchBacktest,
		refetchResults,
	]);

	const handleRefresh = () => {
		refetchBacktest();
		refetchResults();
	};

	const handleStop = async () => {
		try {
			await stopBacktest(backtestId);
			refetchBacktest();
		} catch (error) {
			console.error("Failed to stop backtest:", error);
		}
	};

	const getLogLevelColor = (level: string) => {
		switch (level) {
			case "error":
				return "error";
			case "warning":
				return "warning";
			case "info":
			default:
				return "info";
		}
	};

	const getLogLevelIcon = (level: string) => {
		switch (level) {
			case "error":
				return <ErrorIcon />;
			case "warning":
				return <Schedule />;
			case "info":
			default:
				return <CheckCircle />;
		}
	};

	if (backtestLoading) {
		return (
			<PageContainer
				title="백테스트 모니터링"
				breadcrumbs={[
					{ title: "백테스트" },
					{ title: "상세 보기" },
					{ title: "모니터링" },
				]}
			>
				<Box sx={{ mt: 4 }}>
					<LinearProgress />
				</Box>
			</PageContainer>
		);
	}

	if (backtestError || !backtest) {
		return (
			<PageContainer
				title="백테스트 모니터링"
				breadcrumbs={[
					{ title: "백테스트" },
					{ title: "상세 보기" },
					{ title: "모니터링" },
				]}
			>
				<Alert severity="error">
					백테스트를 찾을 수 없거나 불러오는 중 오류가 발생했습니다.
				</Alert>
			</PageContainer>
		);
	}

	return (
		<PageContainer
			title={`${backtest?.name || "백테스트"} - 모니터링`}
			breadcrumbs={[
				{ title: "백테스트" },
				{ title: backtest?.name || "상세 보기" },
				{ title: "모니터링" },
			]}
		>
			<Container maxWidth="lg">
				{/* Header */}
				<Box sx={{ mb: 4 }}>
					<Box
						sx={{
							display: "flex",
							justifyContent: "space-between",
							alignItems: "center",
							mb: 2,
						}}
					>
						<Button
							startIcon={<ArrowBack />}
							onClick={() => router.push(`/backtests/${backtestId}`)}
						>
							상세 보기로 돌아가기
						</Button>

						<Stack direction="row" spacing={1} alignItems="center">
							<FormControlLabel
								control={
									<Switch
										checked={autoRefresh}
										onChange={(e) => setAutoRefresh(e.target.checked)}
									/>
								}
								label="자동 새로고침"
							/>
							<Tooltip title="수동 새로고침">
								<IconButton onClick={handleRefresh}>
									<Refresh />
								</IconButton>
							</Tooltip>
							{backtest?.status &&
								backtestUtils.isRunning(backtest.status as any) && (
									<Button
										variant="outlined"
										color="error"
										startIcon={<Stop />}
										onClick={handleStop}
									>
										중단
									</Button>
								)}
						</Stack>
					</Box>

					<Alert
						severity={
							backtest?.status &&
							backtestUtils.isRunning(backtest.status as any)
								? "info"
								: "success"
						}
						icon={<Monitor />}
					>
						<Typography variant="subtitle2">
							실시간 모니터링 {autoRefresh ? "활성" : "비활성"}
						</Typography>
						<Typography variant="body2">
							상태:{" "}
							{backtest?.status
								? backtestUtils.formatStatus(backtest.status as any)
								: "알 수 없음"}
							{autoRefresh &&
								backtest?.status &&
								backtestUtils.isRunning(backtest.status as any) &&
								` | 다음 새로고침: ${refreshInterval / 1000}초 후`}
						</Typography>
					</Alert>
				</Box>

				{/* Real-time Status */}
				<Grid container spacing={3} sx={{ mb: 3 }}>
					<Grid size={12}>
						<Card>
							<CardContent sx={{ textAlign: "center" }}>
								<Monitor sx={{ mb: 1, fontSize: 40, color: "primary.main" }} />
								<Typography variant="h4" color="primary">
									{backtest?.status &&
									backtestUtils.isRunning(backtest.status as any)
										? "실행 중"
										: "중단됨"}
								</Typography>
								<Typography variant="body2" color="text.secondary">
									실행 상태
								</Typography>
							</CardContent>
						</Card>
					</Grid>
					<Grid size={12}>
						<Card>
							<CardContent sx={{ textAlign: "center" }}>
								<Timeline sx={{ mb: 1, fontSize: 40 }} />
								<Typography variant="h4">
									{mockMetrics[0]?.trades_count || 0}
								</Typography>
								<Typography variant="body2" color="text.secondary">
									총 거래 수
								</Typography>
							</CardContent>
						</Card>
					</Grid>
					<Grid size={12}>
						<Card>
							<CardContent sx={{ textAlign: "center" }}>
								<TrendingUp
									sx={{ mb: 1, fontSize: 40, color: "success.main" }}
								/>
								<Typography variant="h4" color="success.main">
									{mockMetrics[0]?.portfolio_value
										? backtestUtils.formatCurrency(
												mockMetrics[0].portfolio_value,
											)
										: "-"}
								</Typography>
								<Typography variant="body2" color="text.secondary">
									현재 포트폴리오 가치
								</Typography>
							</CardContent>
						</Card>
					</Grid>
					<Grid size={12}>
						<Card>
							<CardContent sx={{ textAlign: "center" }}>
								<Assessment sx={{ mb: 1, fontSize: 40 }} />
								<Typography
									variant="h4"
									color={
										mockMetrics[0]?.total_return >= 0
											? "success.main"
											: "error.main"
									}
								>
									{mockMetrics[0]?.total_return
										? backtestUtils.formatPercentage(
												mockMetrics[0].total_return,
											)
										: "-"}
								</Typography>
								<Typography variant="body2" color="text.secondary">
									총 수익률
								</Typography>
							</CardContent>
						</Card>
					</Grid>
				</Grid>

				{/* Progress Indicator */}
				{backtest?.status &&
					backtestUtils.isRunning(backtest.status as any) && (
						<Paper sx={{ p: 3, mb: 3 }}>
							<Typography variant="h6" gutterBottom>
								진행 상황
							</Typography>
							<Box sx={{ mt: 2 }}>
								<Typography variant="body2" color="text.secondary" gutterBottom>
									백테스트 진행률 (예상)
								</Typography>
								<LinearProgress
									variant="determinate"
									value={65}
									sx={{ height: 8, borderRadius: 4 }}
								/>
								<Typography
									variant="body2"
									color="text.secondary"
									sx={{ mt: 1 }}
								>
									65% 완료 (예상 남은 시간: 2분 30초)
								</Typography>
							</Box>
						</Paper>
					)}

				{/* Real-time Logs */}
				<Paper sx={{ mb: 3 }}>
					<Box sx={{ p: 2, borderBottom: 1, borderColor: "divider" }}>
						<Typography variant="h6">실시간 로그</Typography>
					</Box>
					<TableContainer sx={{ maxHeight: 400 }}>
						<Table stickyHeader>
							<TableHead>
								<TableRow>
									<TableCell>시간</TableCell>
									<TableCell>레벨</TableCell>
									<TableCell>메시지</TableCell>
									<TableCell>상세</TableCell>
								</TableRow>
							</TableHead>
							<TableBody>
								{mockLogs.map((log, index) => (
									<TableRow key={index}>
										<TableCell>
											{new Date(log.timestamp).toLocaleTimeString("ko-KR")}
										</TableCell>
										<TableCell>
											<Chip
												icon={getLogLevelIcon(log.level)}
												label={log.level.toUpperCase()}
												size="small"
												color={getLogLevelColor(log.level) as any}
												variant="outlined"
											/>
										</TableCell>
										<TableCell>{log.message}</TableCell>
										<TableCell>
											<Typography variant="body2" color="text.secondary">
												{log.details || "-"}
											</Typography>
										</TableCell>
									</TableRow>
								))}
							</TableBody>
						</Table>
					</TableContainer>
				</Paper>

				{/* Performance Metrics History */}
				<Paper sx={{ mb: 3 }}>
					<Box sx={{ p: 2, borderBottom: 1, borderColor: "divider" }}>
						<Typography variant="h6">성과 지표 이력</Typography>
					</Box>
					<TableContainer>
						<Table>
							<TableHead>
								<TableRow>
									<TableCell>시간</TableCell>
									<TableCell align="right">포트폴리오 가치</TableCell>
									<TableCell align="right">총 수익률</TableCell>
									<TableCell align="right">일일 수익률</TableCell>
									<TableCell align="right">낙폭</TableCell>
									<TableCell align="right">거래 수</TableCell>
								</TableRow>
							</TableHead>
							<TableBody>
								{mockMetrics.map((metric, index) => (
									<TableRow key={index}>
										<TableCell>
											{new Date(metric.timestamp).toLocaleTimeString("ko-KR")}
										</TableCell>
										<TableCell align="right">
											{backtestUtils.formatCurrency(metric.portfolio_value)}
										</TableCell>
										<TableCell
											align="right"
											sx={{
												color:
													metric.total_return >= 0
														? "success.main"
														: "error.main",
											}}
										>
											{backtestUtils.formatPercentage(metric.total_return)}
										</TableCell>
										<TableCell
											align="right"
											sx={{
												color:
													metric.daily_return >= 0
														? "success.main"
														: "error.main",
											}}
										>
											{backtestUtils.formatPercentage(metric.daily_return)}
										</TableCell>
										<TableCell align="right" color="error">
											{backtestUtils.formatPercentage(
												Math.abs(metric.drawdown),
											)}
										</TableCell>
										<TableCell align="right">{metric.trades_count}</TableCell>
									</TableRow>
								))}
							</TableBody>
						</Table>
					</TableContainer>
				</Paper>

				{/* Quick Actions */}
				<Box sx={{ display: "flex", justifyContent: "center", gap: 2 }}>
					<Button
						variant="outlined"
						startIcon={<Settings />}
						onClick={() => router.push(`/backtests/${backtestId}/settings`)}
					>
						설정 변경
					</Button>
					<Button
						variant="outlined"
						startIcon={<Assessment />}
						onClick={() => router.push(`/backtests/${backtestId}/report`)}
					>
						상세 리포트
					</Button>
				</Box>
			</Container>
		</PageContainer>
	);
}
