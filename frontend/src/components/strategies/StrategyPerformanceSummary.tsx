"use client";

import {
	AttachMoney,
	Info,
	ShowChart,
	Timeline,
	TrendingDown,
	TrendingUp,
} from "@mui/icons-material";
import {
	Box,
	Card,
	CardContent,
	Chip,
	Divider,
	Grid,
	IconButton,
	LinearProgress,
	Stack,
	Tooltip,
	Typography,
} from "@mui/material";

interface PerformanceMetrics {
	total_return?: number;
	annual_return?: number;
	sharpe_ratio?: number;
	max_drawdown?: number;
	volatility?: number;
	win_rate?: number;
	total_trades?: number;
	profit_factor?: number;
}

interface StrategyPerformanceSummaryProps {
	strategyName: string;
	strategyType: string;
	performance?: PerformanceMetrics;
	isLoading?: boolean;
	period?: string;
	benchmarkReturn?: number;
}

export default function StrategyPerformanceSummary({
	strategyName,
	strategyType,
	performance,
	isLoading = false,
	period = "1Y",
	benchmarkReturn,
}: StrategyPerformanceSummaryProps) {
	const formatPercentage = (value?: number) => {
		if (value === undefined || value === null) return "N/A";
		return `${value > 0 ? "+" : ""}${value.toFixed(2)}%`;
	};

	const formatNumber = (value?: number) => {
		if (value === undefined || value === null) return "N/A";
		return value.toFixed(2);
	};

	const getPerformanceColor = (value?: number) => {
		if (value === undefined || value === null) return "text.secondary";
		return value >= 0 ? "success.main" : "error.main";
	};

	const getPerformanceIcon = (value?: number) => {
		if (value === undefined || value === null) return <ShowChart />;
		return value >= 0 ? <TrendingUp /> : <TrendingDown />;
	};

	const getRiskLevel = (sharpeRatio?: number) => {
		if (!sharpeRatio) return { level: "Unknown", color: "default" as const };
		if (sharpeRatio >= 2)
			return { level: "Excellent", color: "success" as const };
		if (sharpeRatio >= 1) return { level: "Good", color: "primary" as const };
		if (sharpeRatio >= 0.5) return { level: "Fair", color: "warning" as const };
		return { level: "Poor", color: "error" as const };
	};

	const riskLevel = getRiskLevel(performance?.sharpe_ratio);

	if (isLoading) {
		return (
			<Card>
				<CardContent>
					<Box sx={{ mb: 2 }}>
						<LinearProgress />
					</Box>
					<Typography variant="h6" sx={{ mb: 1 }}>
						성과 분석 중...
					</Typography>
					<Typography variant="body2" color="text.secondary">
						전략 성과를 계산하고 있습니다.
					</Typography>
				</CardContent>
			</Card>
		);
	}

	return (
		<Card>
			<CardContent>
				<Box
					sx={{
						display: "flex",
						justifyContent: "space-between",
						alignItems: "center",
						mb: 2,
					}}
				>
					<Box>
						<Typography variant="h6" sx={{ mb: 0.5 }}>
							{strategyName}
						</Typography>
						<Stack direction="row" spacing={1} alignItems="center">
							<Chip
								size="small"
								label={strategyType.replace(/_/g, " ").toUpperCase()}
								color="primary"
								variant="outlined"
							/>
							<Chip
								size="small"
								label={period}
								color="default"
								variant="outlined"
							/>
							<Chip
								size="small"
								label={riskLevel.level}
								color={riskLevel.color}
								variant="filled"
							/>
						</Stack>
					</Box>
					<Tooltip title="성과 분석 정보">
						<IconButton size="small">
							<Info />
						</IconButton>
					</Tooltip>
				</Box>

				<Grid container spacing={2}>
					{/* 수익률 */}
					<Grid size={{ xs: 12, sm: 6, md: 3 }}>
						<Box sx={{ textAlign: "center", p: 1 }}>
							<Box
								sx={{
									display: "flex",
									alignItems: "center",
									justifyContent: "center",
									mb: 1,
								}}
							>
								{getPerformanceIcon(performance?.total_return)}
								<Typography
									variant="body2"
									sx={{ ml: 1 }}
									color="text.secondary"
								>
									총 수익률
								</Typography>
							</Box>
							<Typography
								variant="h6"
								sx={{ color: getPerformanceColor(performance?.total_return) }}
							>
								{formatPercentage(performance?.total_return)}
							</Typography>
							{benchmarkReturn && (
								<Typography variant="caption" color="text.secondary">
									vs 벤치마크: {formatPercentage(benchmarkReturn)}
								</Typography>
							)}
						</Box>
					</Grid>

					{/* 연간 수익률 */}
					<Grid size={{ xs: 12, sm: 6, md: 3 }}>
						<Box sx={{ textAlign: "center", p: 1 }}>
							<Box
								sx={{
									display: "flex",
									alignItems: "center",
									justifyContent: "center",
									mb: 1,
								}}
							>
								<AttachMoney />
								<Typography
									variant="body2"
									sx={{ ml: 1 }}
									color="text.secondary"
								>
									연간 수익률
								</Typography>
							</Box>
							<Typography
								variant="h6"
								sx={{ color: getPerformanceColor(performance?.annual_return) }}
							>
								{formatPercentage(performance?.annual_return)}
							</Typography>
						</Box>
					</Grid>

					{/* 샤프 비율 */}
					<Grid size={{ xs: 12, sm: 6, md: 3 }}>
						<Box sx={{ textAlign: "center", p: 1 }}>
							<Box
								sx={{
									display: "flex",
									alignItems: "center",
									justifyContent: "center",
									mb: 1,
								}}
							>
								<Timeline />
								<Typography
									variant="body2"
									sx={{ ml: 1 }}
									color="text.secondary"
								>
									샤프 비율
								</Typography>
							</Box>
							<Typography
								variant="h6"
								sx={{ color: riskLevel.color + ".main" }}
							>
								{formatNumber(performance?.sharpe_ratio)}
							</Typography>
						</Box>
					</Grid>

					{/* 최대 낙폭 */}
					<Grid size={{ xs: 12, sm: 6, md: 3 }}>
						<Box sx={{ textAlign: "center", p: 1 }}>
							<Box
								sx={{
									display: "flex",
									alignItems: "center",
									justifyContent: "center",
									mb: 1,
								}}
							>
								<TrendingDown />
								<Typography
									variant="body2"
									sx={{ ml: 1 }}
									color="text.secondary"
								>
									최대 낙폭
								</Typography>
							</Box>
							<Typography variant="h6" color="error.main">
								{formatPercentage(performance?.max_drawdown)}
							</Typography>
						</Box>
					</Grid>
				</Grid>

				<Divider sx={{ my: 2 }} />

				{/* 상세 지표 */}
				<Grid container spacing={2}>
					<Grid size={{ xs: 12, sm: 6, md: 3 }}>
						<Typography variant="body2" color="text.secondary">
							변동성
						</Typography>
						<Typography variant="body1" fontWeight="medium">
							{formatPercentage(performance?.volatility)}
						</Typography>
					</Grid>

					<Grid size={{ xs: 12, sm: 6, md: 3 }}>
						<Typography variant="body2" color="text.secondary">
							승률
						</Typography>
						<Typography variant="body1" fontWeight="medium">
							{formatPercentage(performance?.win_rate)}
						</Typography>
					</Grid>

					<Grid size={{ xs: 12, sm: 6, md: 3 }}>
						<Typography variant="body2" color="text.secondary">
							총 거래수
						</Typography>
						<Typography variant="body1" fontWeight="medium">
							{performance?.total_trades || "N/A"}
						</Typography>
					</Grid>

					<Grid size={{ xs: 12, sm: 6, md: 3 }}>
						<Typography variant="body2" color="text.secondary">
							수익 팩터
						</Typography>
						<Typography variant="body1" fontWeight="medium">
							{formatNumber(performance?.profit_factor)}
						</Typography>
					</Grid>
				</Grid>

				{!performance && (
					<Box sx={{ textAlign: "center", py: 3 }}>
						<Typography variant="body1" color="text.secondary">
							성과 데이터가 없습니다.
						</Typography>
						<Typography variant="body2" color="text.secondary">
							백테스트를 실행하여 성과를 확인해보세요.
						</Typography>
					</Box>
				)}
			</CardContent>
		</Card>
	);
}
