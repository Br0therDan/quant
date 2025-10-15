import { useDashboard } from "@/hooks/useDashboard";
import {
	AccountBalance as AccountBalanceIcon,
	Assessment as AssessmentIcon,
	TrendingDown as TrendingDownIcon,
	TrendingUp as TrendingUpIcon,
} from "@mui/icons-material";
import {
	Alert,
	Box,
	Card,
	CardContent,
	Chip,
	CircularProgress,
	Grid,
	Typography,
} from "@mui/material";

interface StatCardProps {
	title: string;
	value: string | number;
	subtitle?: string;
	trend?: "up" | "down" | "neutral";
	trendValue?: string;
	icon?: React.ReactNode;
}

function StatCard({
	title,
	value,
	subtitle,
	trend,
	trendValue,
	icon,
}: StatCardProps) {
	const getTrendColor = () => {
		if (trend === "up") return "success.main";
		if (trend === "down") return "error.main";
		return "text.secondary";
	};

	const getTrendIcon = () => {
		if (trend === "up") return <TrendingUpIcon fontSize="small" />;
		if (trend === "down") return <TrendingDownIcon fontSize="small" />;
		return null;
	};

	return (
		<Card>
			<CardContent>
				<Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
					{icon && (
						<Box
							sx={{
								mr: 2,
								color: "primary.main",
								display: "flex",
								alignItems: "center",
							}}
						>
							{icon}
						</Box>
					)}
					<Typography variant="subtitle2" color="text.secondary">
						{title}
					</Typography>
				</Box>

				<Typography variant="h4" gutterBottom>
					{value}
				</Typography>

				{subtitle && (
					<Typography variant="body2" color="text.secondary">
						{subtitle}
					</Typography>
				)}

				{trend && trendValue && (
					<Box
						sx={{
							display: "flex",
							alignItems: "center",
							mt: 1,
							color: getTrendColor(),
						}}
					>
						{getTrendIcon()}
						<Typography variant="caption" sx={{ ml: 0.5 }}>
							{trendValue}
						</Typography>
					</Box>
				)}
			</CardContent>
		</Card>
	);
}

/**
 * DashboardOverview Component
 *
 * Main dashboard overview displaying:
 * - Portfolio summary (total value, returns, Sharpe ratio)
 * - Performance metrics
 * - Strategy comparison summary
 * - Recent activity indicators
 *
 * Uses useDashboard hook to fetch all dashboard data.
 *
 * @example
 * ```tsx
 * <DashboardOverview />
 * ```
 */
export function DashboardOverview() {
	const {
		dashboardSummary,
		portfolioPerformance,
		strategyComparison,
		isLoading,
		error,
	} = useDashboard();

	if (isLoading.dashboardSummary || isLoading.portfolioPerformance) {
		return (
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
		);
	}

	if (error.dashboardSummary || error.portfolioPerformance) {
		return (
			<Alert severity="error">
				대시보드 데이터를 불러오는 중 오류가 발생했습니다:{" "}
				{error.dashboardSummary?.message || error.portfolioPerformance?.message}
			</Alert>
		);
	}

	// Extract portfolio metrics
	const portfolioValue =
		dashboardSummary?.data?.portfolio?.total_value?.toFixed(2) || "0.00";
	const totalReturn =
		portfolioPerformance?.data?.summary?.total_return?.toFixed(2) || "0.00";
	const sharpeRatio =
		portfolioPerformance?.data?.summary?.sharpe_ratio?.toFixed(2) || "0.00";
	const maxDrawdown =
		portfolioPerformance?.data?.summary?.max_drawdown?.toFixed(2) || "0.00";

	// Extract summary metrics
	const activeStrategies =
		dashboardSummary?.data?.strategies?.active_count || 0;
	const totalBacktests =
		dashboardSummary?.data?.recent_activity?.backtests_count_week || 0;
	const recentTradesCount =
		dashboardSummary?.data?.recent_activity?.trades_count_today || 0;

	// Determine trends
	const returnTrend = Number.parseFloat(totalReturn) >= 0 ? "up" : "down";
	const sharpeTrend = Number.parseFloat(sharpeRatio) >= 1.0 ? "up" : "neutral";

	// Strategy comparison summary
	const topStrategy = strategyComparison?.data?.strategies?.[0];
	const strategyCount = strategyComparison?.data?.strategies?.length || 0;

	return (
		<Box>
			<Typography variant="h4" gutterBottom>
				대시보드 개요
			</Typography>

			<Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
				포트폴리오 성과 및 전략 현황을 한눈에 확인하세요
			</Typography>

			{/* Portfolio Metrics */}
			<Box sx={{ mb: 4 }}>
				<Typography variant="h6" gutterBottom>
					포트폴리오 요약
				</Typography>
				<Grid container spacing={3}>
					<Grid size={{ xs: 12, sm: 6, md: 3 }}>
						<StatCard
							title="포트폴리오 가치"
							value={`$${portfolioValue}`}
							subtitle="현재 총 자산"
							icon={<AccountBalanceIcon />}
						/>
					</Grid>

					<Grid size={{ xs: 12, sm: 6, md: 3 }}>
						<StatCard
							title="총 수익률"
							value={`${totalReturn}%`}
							subtitle="누적 수익률"
							trend={returnTrend}
							trendValue={`${totalReturn}% 변동`}
							icon={<TrendingUpIcon />}
						/>
					</Grid>

					<Grid size={{ xs: 12, sm: 6, md: 3 }}>
						<StatCard
							title="Sharpe Ratio"
							value={sharpeRatio}
							subtitle="위험 대비 수익"
							trend={sharpeTrend}
							icon={<AssessmentIcon />}
						/>
					</Grid>

					<Grid size={{ xs: 12, sm: 6, md: 3 }}>
						<StatCard
							title="최대 손실"
							value={`${maxDrawdown}%`}
							subtitle="Max Drawdown"
							trend="down"
							icon={<TrendingDownIcon />}
						/>
					</Grid>
				</Grid>
			</Box>

			{/* Strategy & Activity Summary */}
			<Box sx={{ mb: 4 }}>
				<Typography variant="h6" gutterBottom>
					전략 및 활동
				</Typography>
				<Grid container spacing={3}>
					<Grid size={{ xs: 12, sm: 6, md: 4 }}>
						<Card>
							<CardContent>
								<Typography variant="subtitle2" color="text.secondary">
									활성 전략
								</Typography>
								<Typography variant="h4" sx={{ my: 2 }}>
									{activeStrategies}
								</Typography>
								<Chip
									label={`${strategyCount}개 전략 비교 가능`}
									size="small"
									color="primary"
									variant="outlined"
								/>
							</CardContent>
						</Card>
					</Grid>

					<Grid size={{ xs: 12, sm: 6, md: 4 }}>
						<Card>
							<CardContent>
								<Typography variant="subtitle2" color="text.secondary">
									백테스트
								</Typography>
								<Typography variant="h4" sx={{ my: 2 }}>
									{totalBacktests}
								</Typography>
								<Typography variant="caption" color="text.secondary">
									총 실행 횟수
								</Typography>
							</CardContent>
						</Card>
					</Grid>

					<Grid size={{ xs: 12, sm: 6, md: 4 }}>
						<Card>
							<CardContent>
								<Typography variant="subtitle2" color="text.secondary">
									최근 거래
								</Typography>
								<Typography variant="h4" sx={{ my: 2 }}>
									{recentTradesCount}
								</Typography>
								<Typography variant="caption" color="text.secondary">
									지난 30일
								</Typography>
							</CardContent>
						</Card>
					</Grid>
				</Grid>
			</Box>

			{/* Top Strategy Highlight */}
			{topStrategy && (
				<Box sx={{ mb: 4 }}>
					<Typography variant="h6" gutterBottom>
						최고 성과 전략
					</Typography>
					<Card>
						<CardContent>
							<Grid container spacing={2}>
								<Grid size={{ xs: 12, md: 6 }}>
									<Typography variant="h5" gutterBottom>
										{topStrategy.name}
									</Typography>
									<Typography variant="body2" color="text.secondary">
										{topStrategy.type}
									</Typography>
								</Grid>

								<Grid size={{ xs: 6, md: 3 }}>
									<Typography variant="caption" color="text.secondary">
										총 수익률
									</Typography>
									<Typography variant="h6" color="success.main">
										{typeof topStrategy.total_return === "number"
											? `${topStrategy.total_return.toFixed(2)}%`
											: "N/A"}
									</Typography>
								</Grid>

								<Grid size={{ xs: 6, md: 3 }}>
									<Typography variant="caption" color="text.secondary">
										Sharpe Ratio
									</Typography>
									<Typography variant="h6">
										{typeof topStrategy.sharpe_ratio === "number"
											? topStrategy.sharpe_ratio.toFixed(2)
											: "N/A"}
									</Typography>
								</Grid>
							</Grid>
						</CardContent>
					</Card>
				</Box>
			)}

			{/* Quick Actions Info */}
			<Card variant="outlined" sx={{ bgcolor: "action.hover" }}>
				<CardContent>
					<Typography variant="body2" color="text.secondary">
						💡 <strong>빠른 시작:</strong> 새 백테스트를 실행하거나 최적화
						스터디를 시작하여 전략 성과를 개선하세요.
					</Typography>
				</CardContent>
			</Card>
		</Box>
	);
}
