/**
 * RegimeHistoryChart Component
 *
 * 시장 국면의 시계열 변화를 시각화하는 차트 컴포넌트
 *
 * **주요 기능**:
 * - 시간에 따른 국면 변화 표시 (Line Chart)
 * - 신뢰도 영역 표시 (Area Chart)
 * - 국면별 색상 구분
 * - 툴팁 (날짜, 국면, 신뢰도, 메트릭)
 * - 반응형 디자인
 *
 * **데이터 구조** (Mock):
 * ```typescript
 * {
 *   date: Date,
 *   regime: "bullish" | "bearish" | "volatile" | "sideways",
 *   confidence: 0.85,
 *   metrics: { trailing_return_pct, volatility_pct, ... }
 * }
 * ```
 *
 * **사용 예시**:
 * ```tsx
 * <RegimeHistoryChart
 *   symbol="AAPL"
 *   lookbackDays={60}
 *   chartHeight={300}
 * />
 * ```
 *
 * **Note**: 현재 Backend API에 히스토리 엔드포인트가 없으므로,
 * 현재 스냅샷을 기반으로 Mock 데이터를 생성합니다.
 * 향후 `/api/v1/market-data/regime/history` API 추가 시 연동 가능.
 *
 * @module components/market-regime/RegimeHistoryChart
 */

import type { MarketRegimeType } from "@/client";
import { useRegimeDetection } from "@/hooks/useRegimeDetection";
import {
	Box,
	Card,
	CardContent,
	CardHeader,
	Skeleton,
	Typography,
} from "@mui/material";
import { useMemo } from "react";
import {
	Area,
	AreaChart,
	CartesianGrid,
	Legend,
	ResponsiveContainer,
	Tooltip,
	XAxis,
	YAxis,
} from "recharts";

// ============================================================================
// Props Interface
// ============================================================================

export interface RegimeHistoryChartProps {
	/** 심볼 (예: "AAPL") */
	symbol: string;
	/** Lookback 기간 (일수, 기본값: 60) */
	lookbackDays?: number;
	/** 차트 높이 (px, 기본값: 300) */
	chartHeight?: number;
	/** 히스토리 기간 (일수, 기본값: 30) */
	historyDays?: number;
}

// ============================================================================
// Mock Data Generator (임시)
// ============================================================================

/**
 * Mock 히스토리 데이터 생성 함수
 *
 * **로직**:
 * - 현재 국면을 기반으로 과거 30일 데이터 역산
 * - 국면 변화: 5-7일마다 랜덤 전환 (70% 유지, 30% 변경)
 * - 신뢰도: 0.6-0.95 범위 랜덤
 * - 메트릭: 국면별 현실적인 범위
 *
 * **향후**: Backend `/api/v1/market-data/regime/history` API로 대체
 */
interface HistoryDataPoint {
	date: Date;
	regime: MarketRegimeType;
	confidence: number;
	trailing_return_pct: number;
	volatility_pct: number;
	regimeNumeric: number; // 차트용 (bullish=4, bearish=1, volatile=3, sideways=2)
}

const generateMockHistory = (
	currentRegime: MarketRegimeType,
	days: number,
): HistoryDataPoint[] => {
	const history: HistoryDataPoint[] = [];
	const today = new Date();
	let regime = currentRegime;

	// 국면 순서: bearish(1) < sideways(2) < volatile(3) < bullish(4)
	const regimeNumericMap: Record<MarketRegimeType, number> = {
		bearish: 1,
		sideways: 2,
		volatile: 3,
		bullish: 4,
	};

	const regimes: MarketRegimeType[] = [
		"bullish",
		"bearish",
		"volatile",
		"sideways",
	];

	for (let i = days - 1; i >= 0; i--) {
		// 5-7일마다 국면 변경 확률
		const shouldChange = i % 6 === 0 && Math.random() > 0.7;
		if (shouldChange) {
			regime = regimes[Math.floor(Math.random() * regimes.length)];
		}

		// 신뢰도: 0.6-0.95
		const confidence = 0.6 + Math.random() * 0.35;

		// 메트릭 생성 (국면별 특성)
		let trailing_return_pct: number;
		let volatility_pct: number;

		switch (regime) {
			case "bullish":
				trailing_return_pct = 5 + Math.random() * 10; // 5-15%
				volatility_pct = 10 + Math.random() * 10; // 10-20%
				break;
			case "bearish":
				trailing_return_pct = -15 + Math.random() * 10; // -15% ~ -5%
				volatility_pct = 20 + Math.random() * 15; // 20-35%
				break;
			case "volatile":
				trailing_return_pct = -5 + Math.random() * 10; // -5% ~ 5%
				volatility_pct = 30 + Math.random() * 20; // 30-50%
				break;
			case "sideways":
				trailing_return_pct = -2 + Math.random() * 4; // -2% ~ 2%
				volatility_pct = 5 + Math.random() * 10; // 5-15%
				break;
		}

		const date = new Date(today);
		date.setDate(date.getDate() - i);

		history.push({
			date,
			regime,
			confidence,
			trailing_return_pct,
			volatility_pct,
			regimeNumeric: regimeNumericMap[regime],
		});
	}

	return history;
};

// ============================================================================
// Custom Tooltip
// ============================================================================

interface CustomTooltipProps {
	active?: boolean;
	payload?: Array<{
		name: string;
		value: number;
		payload: HistoryDataPoint;
	}>;
}

const CustomTooltip: React.FC<CustomTooltipProps> = ({ active, payload }) => {
	if (!active || !payload || payload.length === 0) return null;

	const data = payload[0].payload;
	const regimeLabels: Record<MarketRegimeType, string> = {
		bullish: "상승장",
		bearish: "하락장",
		volatile: "변동장",
		sideways: "횡보장",
	};

	return (
		<Card sx={{ minWidth: 200 }}>
			<CardContent>
				<Typography variant="subtitle2" gutterBottom>
					{data.date.toLocaleDateString("ko-KR")}
				</Typography>
				<Typography variant="body2" color="text.secondary">
					<strong>국면:</strong> {regimeLabels[data.regime]}
				</Typography>
				<Typography variant="body2" color="text.secondary">
					<strong>신뢰도:</strong> {(data.confidence * 100).toFixed(1)}%
				</Typography>
				<Typography variant="body2" color="text.secondary">
					<strong>수익률:</strong> {data.trailing_return_pct.toFixed(2)}%
				</Typography>
				<Typography variant="body2" color="text.secondary">
					<strong>변동성:</strong> {data.volatility_pct.toFixed(2)}%
				</Typography>
			</CardContent>
		</Card>
	);
};

// ============================================================================
// Component
// ============================================================================

/**
 * RegimeHistoryChart 컴포넌트
 *
 * **렌더링 상태**:
 * - Loading: Skeleton
 * - Success: AreaChart (신뢰도 영역 + 국면 레이블)
 * - Error: 에러 메시지
 *
 * @param props - RegimeHistoryChartProps
 */
export const RegimeHistoryChart: React.FC<RegimeHistoryChartProps> = ({
	symbol,
	lookbackDays = 60,
	chartHeight = 300,
	historyDays = 30,
}) => {
	const { currentRegime, isLoading, error, getRegimeLabel } =
		useRegimeDetection({ symbol, lookbackDays });

	// Mock 데이터 생성 (메모이제이션)
	const historyData = useMemo(() => {
		if (!currentRegime) return [];
		return generateMockHistory(currentRegime.regime, historyDays);
	}, [currentRegime, historyDays]);

	// ========================================
	// 로딩 상태
	// ========================================
	if (isLoading) {
		return (
			<Card>
				<CardHeader title="국면 변화 추이" />
				<CardContent>
					<Skeleton variant="rectangular" height={chartHeight} />
				</CardContent>
			</Card>
		);
	}

	// ========================================
	// 에러 상태
	// ========================================
	if (error) {
		return (
			<Card>
				<CardHeader title="국면 변화 추이" />
				<CardContent>
					<Typography color="error">
						데이터를 불러올 수 없습니다: {error.message}
					</Typography>
				</CardContent>
			</Card>
		);
	}

	// ========================================
	// 데이터 없음
	// ========================================
	if (!currentRegime || historyData.length === 0) {
		return (
			<Card>
				<CardHeader title="국면 변화 추이" />
				<CardContent>
					<Typography color="text.secondary">
						히스토리 데이터가 없습니다.
					</Typography>
				</CardContent>
			</Card>
		);
	}

	// ========================================
	// 차트 렌더링
	// ========================================
	return (
		<Card>
			<CardHeader
				title="국면 변화 추이"
				subheader={`최근 ${historyDays}일 (현재: ${getRegimeLabel(
					currentRegime.regime,
				)})`}
			/>
			<CardContent>
				<ResponsiveContainer width="100%" height={chartHeight}>
					<AreaChart
						data={historyData}
						margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
					>
						<defs>
							<linearGradient id="colorConfidence" x1="0" y1="0" x2="0" y2="1">
								<stop offset="5%" stopColor="#8884d8" stopOpacity={0.8} />
								<stop offset="95%" stopColor="#8884d8" stopOpacity={0} />
							</linearGradient>
						</defs>
						<CartesianGrid strokeDasharray="3 3" />
						<XAxis
							dataKey="date"
							tickFormatter={(date: Date) =>
								date.toLocaleDateString("ko-KR", {
									month: "numeric",
									day: "numeric",
								})
							}
							tick={{ fontSize: 12 }}
						/>
						<YAxis
							yAxisId="left"
							domain={[0, 1]}
							tickFormatter={(value: number) => `${(value * 100).toFixed(0)}%`}
							tick={{ fontSize: 12 }}
						/>
						<YAxis
							yAxisId="right"
							orientation="right"
							domain={[1, 4]}
							ticks={[1, 2, 3, 4]}
							tickFormatter={(value: number) => {
								const labels = ["", "하락", "횡보", "변동", "상승"];
								return labels[value] || "";
							}}
							tick={{ fontSize: 12 }}
						/>
						<Tooltip content={<CustomTooltip />} />
						<Legend />
						<Area
							yAxisId="left"
							type="monotone"
							dataKey="confidence"
							stroke="#8884d8"
							fillOpacity={1}
							fill="url(#colorConfidence)"
							name="신뢰도"
						/>
						<Area
							yAxisId="right"
							type="stepAfter"
							dataKey="regimeNumeric"
							stroke="#82ca9d"
							fill="none"
							strokeWidth={2}
							name="국면"
							dot={{ r: 3 }}
						/>
					</AreaChart>
				</ResponsiveContainer>

				{/* 하단 주석 */}
				<Box sx={{ mt: 2, display: "flex", justifyContent: "center" }}>
					<Typography variant="caption" color="text.secondary">
						Note: 히스토리 데이터는 Mock 데이터입니다. Backend API 연동 예정.
					</Typography>
				</Box>
			</CardContent>
		</Card>
	);
};

// ============================================================================
// Exports
// ============================================================================
export default RegimeHistoryChart;
