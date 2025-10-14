/**
 * ForecastComparison Component
 *
 * 여러 예측 기간(Horizon)의 예상 수익률 비교
 *
 * Features:
 * - 다양한 예측 기간 (7/14/30/60/90일)
 * - BarChart 비교 시각화
 * - 수익률 색상 구분 (긍정/부정)
 * - 변동성 표시
 *
 * @author GitHub Copilot
 * @created 2025-01-16
 */

"use client";

import { usePortfolioForecast } from "@/hooks/usePortfolioForecast";
import { TrendingUp as TrendingUpIcon } from "@mui/icons-material";
import {
	Alert,
	Box,
	Card,
	CardContent,
	CardHeader,
	Chip,
	Skeleton,
	Stack,
	Typography,
} from "@mui/material";
import {
	Bar,
	BarChart,
	CartesianGrid,
	Cell,
	Legend,
	ResponsiveContainer,
	Tooltip,
	XAxis,
	YAxis,
} from "recharts";

// ============================================================================
// Types
// ============================================================================

export interface ForecastComparisonProps {
	/** 비교할 예측 기간 배열 (일) */
	horizons?: number[];
	/** 차트 높이 (px) */
	chartHeight?: number;
}

/**
 * 비교 데이터 포인트
 */
interface ComparisonDataPoint {
	horizon: number;
	horizonLabel: string;
	expectedReturn: number;
	volatility: number;
}

// ============================================================================
// Hook: Multiple Horizons
// ============================================================================

/**
 * 여러 예측 기간의 데이터를 병렬 조회
 */
function useMultipleForecasts(horizons: number[]) {
	// Hook 호출은 반드시 컴포넌트 최상위에서 (조건문 밖에서) 이루어져야 함
	const forecast7 = usePortfolioForecast({
		horizonDays: horizons[0] || 7,
		enabled: horizons.length > 0,
	});
	const forecast14 = usePortfolioForecast({
		horizonDays: horizons[1] || 14,
		enabled: horizons.length > 1,
	});
	const forecast30 = usePortfolioForecast({
		horizonDays: horizons[2] || 30,
		enabled: horizons.length > 2,
	});
	const forecast60 = usePortfolioForecast({
		horizonDays: horizons[3] || 60,
		enabled: horizons.length > 3,
	});
	const forecast90 = usePortfolioForecast({
		horizonDays: horizons[4] || 90,
		enabled: horizons.length > 4,
	});

	const results = [forecast7, forecast14, forecast30, forecast60, forecast90];

	return {
		data: horizons.map((horizon, i) => ({
			horizon,
			forecastData: results[i]?.forecastData,
		})),
		isLoading: results.some((r) => r.isLoading),
		isError: results.some((r) => r.isError),
		errors: results.map((r) => r.error).filter(Boolean),
	};
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * 수익률 색상 결정
 */
function getReturnColor(returnPct: number): string {
	if (returnPct > 0) return "#4caf50"; // Green
	if (returnPct < 0) return "#f44336"; // Red
	return "#9e9e9e"; // Gray
}

// ============================================================================
// Custom Tooltip
// ============================================================================

interface CustomTooltipProps {
	active?: boolean;
	payload?: Array<{
		payload: ComparisonDataPoint;
	}>;
}

function CustomTooltip({ active, payload }: CustomTooltipProps) {
	if (!active || !payload || payload.length === 0) {
		return null;
	}

	const data = payload[0].payload;

	return (
		<Card sx={{ minWidth: 200 }}>
			<CardContent>
				<Typography variant="body2" fontWeight="bold" gutterBottom>
					{data.horizonLabel}
				</Typography>
				<Stack spacing={0.5}>
					<Box sx={{ display: "flex", justifyContent: "space-between" }}>
						<Typography variant="caption">예상 수익률:</Typography>
						<Typography
							variant="caption"
							fontWeight="bold"
							color={data.expectedReturn >= 0 ? "success.main" : "error.main"}
						>
							{data.expectedReturn >= 0 ? "+" : ""}
							{data.expectedReturn.toFixed(2)}%
						</Typography>
					</Box>
					<Box sx={{ display: "flex", justifyContent: "space-between" }}>
						<Typography variant="caption">예상 변동성:</Typography>
						<Typography variant="caption" fontWeight="bold">
							{data.volatility.toFixed(2)}%
						</Typography>
					</Box>
				</Stack>
			</CardContent>
		</Card>
	);
}

// ============================================================================
// Main Component
// ============================================================================

/**
 * ForecastComparison Component
 *
 * @example
 * ```tsx
 * <ForecastComparison horizons={[7, 14, 30, 60, 90]} chartHeight={300} />
 * ```
 */
export default function ForecastComparison({
	horizons = [7, 14, 30, 60, 90],
	chartHeight = 300,
}: ForecastComparisonProps) {
	const { data, isLoading, isError, errors } = useMultipleForecasts(horizons);

	// ============================================================================
	// Render: Loading State
	// ============================================================================

	if (isLoading) {
		return (
			<Card>
				<CardHeader
					title="예측 기간별 비교"
					subheader="여러 예측 기간의 예상 수익률 비교"
				/>
				<CardContent>
					<Skeleton variant="rectangular" height={chartHeight} />
				</CardContent>
			</Card>
		);
	}

	// ============================================================================
	// Render: Error State
	// ============================================================================

	if (isError) {
		return (
			<Card>
				<CardHeader title="예측 기간별 비교" />
				<CardContent>
					<Alert severity="error">
						{errors[0]?.message || "예측 데이터를 불러오는데 실패했습니다."}
					</Alert>
				</CardContent>
			</Card>
		);
	}

	// ============================================================================
	// Data Preparation
	// ============================================================================

	const comparisonData: ComparisonDataPoint[] = data
		.filter((d) => d.forecastData)
		.map((d) => ({
			horizon: d.horizon,
			horizonLabel: `${d.horizon}일`,
			expectedReturn: d.forecastData?.expected_return_pct ?? 0,
			volatility: d.forecastData?.expected_volatility_pct ?? 0,
		}));

	if (comparisonData.length === 0) {
		return (
			<Card>
				<CardHeader title="예측 기간별 비교" />
				<CardContent>
					<Alert severity="info">비교할 예측 데이터가 없습니다.</Alert>
				</CardContent>
			</Card>
		);
	}

	// 최고/최저 수익률
	const maxReturn = Math.max(...comparisonData.map((d) => d.expectedReturn));
	const minReturn = Math.min(...comparisonData.map((d) => d.expectedReturn));
	const maxReturnHorizon = comparisonData.find(
		(d) => d.expectedReturn === maxReturn,
	)?.horizonLabel;
	const minReturnHorizon = comparisonData.find(
		(d) => d.expectedReturn === minReturn,
	)?.horizonLabel;

	// ============================================================================
	// Render: Comparison Chart
	// ============================================================================

	return (
		<Card>
			<CardHeader
				title="예측 기간별 비교"
				subheader="여러 예측 기간의 예상 수익률 비교"
				action={
					<Stack direction="row" spacing={1}>
						<Chip
							icon={<TrendingUpIcon />}
							label={`최고: ${maxReturnHorizon} (+${maxReturn.toFixed(2)}%)`}
							color="success"
							size="small"
							variant="outlined"
						/>
					</Stack>
				}
			/>
			<CardContent>
				<ResponsiveContainer width="100%" height={chartHeight}>
					<BarChart
						data={comparisonData}
						margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
					>
						<CartesianGrid strokeDasharray="3 3" />
						<XAxis dataKey="horizonLabel" tick={{ fontSize: 12 }} />
						<YAxis
							label={{
								value: "예상 수익률 (%)",
								angle: -90,
								position: "insideLeft",
							}}
							tick={{ fontSize: 12 }}
						/>
						<Tooltip content={<CustomTooltip />} />
						<Legend />

						{/* Bar: 예상 수익률 */}
						<Bar dataKey="expectedReturn" name="예상 수익률 (%)">
							{comparisonData.map((entry, index) => (
								<Cell
									key={`cell-${index}`}
									fill={getReturnColor(entry.expectedReturn)}
								/>
							))}
						</Bar>
					</BarChart>
				</ResponsiveContainer>

				{/* Summary */}
				<Box sx={{ mt: 2, p: 2, bgcolor: "grey.50", borderRadius: 1 }}>
					<Typography variant="body2" color="text.secondary" gutterBottom>
						📊 비교 요약:
					</Typography>
					<Stack direction="row" spacing={2} sx={{ ml: 2 }}>
						<Typography variant="caption">
							• 최고 수익률: <strong>{maxReturnHorizon}</strong> (
							{maxReturn >= 0 ? "+" : ""}
							{maxReturn.toFixed(2)}%)
						</Typography>
						<Typography variant="caption">
							• 최저 수익률: <strong>{minReturnHorizon}</strong> (
							{minReturn >= 0 ? "+" : ""}
							{minReturn.toFixed(2)}%)
						</Typography>
					</Stack>
				</Box>
			</CardContent>
		</Card>
	);
}
