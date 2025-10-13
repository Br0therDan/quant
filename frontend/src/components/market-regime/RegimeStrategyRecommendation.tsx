/**
 * RegimeStrategyRecommendation Component
 *
 * 시장 국면에 따른 전략 추천 컴포넌트
 *
 * **주요 기능**:
 * - 국면별 최적 전략 추천 (Bullish, Bearish, Volatile, Sideways)
 * - 추천 인디케이터 목록
 * - 리스크 레벨 표시
 * - 실행 가능한 액션 (백테스트, 전략 생성)
 * - 참고 자료 링크
 *
 * **추천 로직**:
 * - Bullish: Momentum, Trend-following 전략
 * - Bearish: Short, Defensive 전략
 * - Volatile: Mean-reversion, Options 전략
 * - Sideways: Range-trading, Theta decay 전략
 *
 * **사용 예시**:
 * ```tsx
 * <RegimeStrategyRecommendation
 *   symbol="AAPL"
 *   lookbackDays={60}
 *   onCreateStrategy={(strategyConfig) => { ... }}
 * />
 * ```
 *
 * @module components/market-regime/RegimeStrategyRecommendation
 */

import type { MarketRegimeType } from "@/client";
import { useRegimeDetection } from "@/hooks/useRegimeDetection";
import AddIcon from "@mui/icons-material/Add";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import ShowChartIcon from "@mui/icons-material/ShowChart";
import TrendingDownIcon from "@mui/icons-material/TrendingDown";
import TrendingFlatIcon from "@mui/icons-material/TrendingFlat";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import WarningIcon from "@mui/icons-material/Warning";
import {
	Alert,
	Box,
	Button,
	Card,
	CardActions,
	CardContent,
	CardHeader,
	Chip,
	Divider,
	List,
	ListItem,
	ListItemIcon,
	ListItemText,
	Skeleton,
	Typography,
} from "@mui/material";

// ============================================================================
// Props Interface
// ============================================================================

export interface RegimeStrategyRecommendationProps {
	/** 심볼 (예: "AAPL") */
	symbol: string;
	/** Lookback 기간 (일수, 기본값: 60) */
	lookbackDays?: number;
	/** 전략 생성 콜백 */
	onCreateStrategy?: (strategyConfig: StrategyConfig) => void;
	/** 백테스트 시작 콜백 */
	onStartBacktest?: (strategyConfig: StrategyConfig) => void;
}

// ============================================================================
// Type: 전략 설정
// ============================================================================

export interface StrategyConfig {
	name: string;
	regime: MarketRegimeType;
	indicators: string[];
	risk_level: "Low" | "Medium" | "High";
}

// ============================================================================
// Type: 국면별 추천 데이터
// ============================================================================

interface RegimeRecommendation {
	title: string;
	description: string;
	strategies: string[];
	indicators: string[];
	risk_level: "Low" | "Medium" | "High";
	icon: React.ReactElement;
	tips: string[];
}

// ============================================================================
// Data: 국면별 추천 매핑
// ============================================================================

const REGIME_RECOMMENDATIONS: Record<MarketRegimeType, RegimeRecommendation> = {
	bullish: {
		title: "상승장 전략",
		description:
			"시장이 상승 추세에 있을 때는 Momentum 및 Trend-following 전략이 효과적입니다.",
		strategies: [
			"Moving Average Crossover (장기 MA 상단)",
			"RSI Momentum (30 이하 매수)",
			"Breakout (High 돌파)",
			"Buy and Hold (장기 보유)",
		],
		indicators: ["SMA(50)", "EMA(20)", "RSI(14)", "MACD", "Bollinger Bands"],
		risk_level: "Medium",
		icon: <TrendingUpIcon />,
		tips: [
			"✅ 추세 추종 전략 우선",
			"✅ Stop-loss 5-10% 설정",
			"⚠️ 과매수 구간 주의 (RSI > 70)",
		],
	},
	bearish: {
		title: "하락장 전략",
		description:
			"시장이 하락 추세에 있을 때는 Short 포지션 또는 방어적 전략이 적합합니다.",
		strategies: [
			"Short Selling (고점 공매도)",
			"Put Options (풋옵션)",
			"Inverse ETF (인버스)",
			"Cash Preservation (현금 보유)",
		],
		indicators: ["SMA(200)", "RSI(14)", "ATR", "Support Levels"],
		risk_level: "High",
		icon: <TrendingDownIcon />,
		tips: [
			"⚠️ Short 포지션 리스크 관리",
			"✅ 방어적 자산 배분",
			"⚠️ Dead Cat Bounce 주의",
		],
	},
	volatile: {
		title: "변동장 전략",
		description: "변동성이 높을 때는 Mean-reversion 및 옵션 전략이 유리합니다.",
		strategies: [
			"Mean Reversion (평균 회귀)",
			"Bollinger Band Squeeze",
			"Straddle/Strangle Options",
			"Volatility Arbitrage",
		],
		indicators: [
			"Bollinger Bands",
			"ATR",
			"VIX",
			"Standard Deviation",
			"Keltner Channels",
		],
		risk_level: "High",
		icon: <ShowChartIcon />,
		tips: [
			"✅ 짧은 보유 기간 (Intraday)",
			"⚠️ 손절 타이밍 엄격히",
			"✅ 옵션 전략 고려 (IV 높음)",
		],
	},
	sideways: {
		title: "횡보장 전략",
		description:
			"시장이 횡보할 때는 Range-trading 및 Theta decay 전략이 효과적입니다.",
		strategies: [
			"Range Trading (Support/Resistance)",
			"Iron Condor (옵션)",
			"Covered Call (커버드 콜)",
			"Arbitrage (차익거래)",
		],
		indicators: [
			"Support/Resistance",
			"Pivot Points",
			"RSI(14)",
			"Stochastic Oscillator",
		],
		risk_level: "Low",
		icon: <TrendingFlatIcon />,
		tips: [
			"✅ 구간 매매 (Support 매수, Resistance 매도)",
			"✅ Theta decay 활용 (옵션 매도)",
			"⚠️ Breakout 신호 모니터링",
		],
	},
};

// ============================================================================
// Component
// ============================================================================

/**
 * RegimeStrategyRecommendation 컴포넌트
 *
 * **렌더링 구조**:
 * - CardHeader: 제목 + 국면 Chip
 * - CardContent:
 *   - Alert (설명)
 *   - 추천 전략 List
 *   - 추천 인디케이터 Chip
 *   - 팁 List
 *   - 리스크 레벨
 * - CardActions: 전략 생성, 백테스트 버튼
 *
 * @param props - RegimeStrategyRecommendationProps
 */
export const RegimeStrategyRecommendation: React.FC<
	RegimeStrategyRecommendationProps
> = ({ symbol, lookbackDays = 60, onCreateStrategy, onStartBacktest }) => {
	const { currentRegime, isLoading, error, getRegimeColor, getRegimeLabel } =
		useRegimeDetection({ symbol, lookbackDays });

	// ========================================
	// 로딩 상태
	// ========================================
	if (isLoading) {
		return (
			<Card>
				<CardHeader title="전략 추천" />
				<CardContent>
					<Skeleton variant="text" width="80%" height={40} />
					<Skeleton variant="rectangular" height={200} sx={{ mt: 2 }} />
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
				<CardHeader title="전략 추천" />
				<CardContent>
					<Typography color="error">
						국면 데이터를 불러올 수 없습니다: {error.message}
					</Typography>
				</CardContent>
			</Card>
		);
	}

	// ========================================
	// 데이터 없음
	// ========================================
	if (!currentRegime) {
		return (
			<Card>
				<CardHeader title="전략 추천" />
				<CardContent>
					<Typography color="text.secondary">
						국면 데이터가 없습니다.
					</Typography>
				</CardContent>
			</Card>
		);
	}

	// ========================================
	// 추천 데이터 가져오기
	// ========================================
	const recommendation = REGIME_RECOMMENDATIONS[currentRegime.regime];
	const regimeColor = getRegimeColor(currentRegime.regime);
	const regimeLabel = getRegimeLabel(currentRegime.regime);

	// 리스크 레벨 색상
	const riskColors: Record<string, string> = {
		Low: "success",
		Medium: "warning",
		High: "error",
	};

	// 전략 생성 핸들러
	const handleCreateStrategy = () => {
		if (onCreateStrategy) {
			const strategyConfig: StrategyConfig = {
				name: `${symbol} ${regimeLabel} 전략`,
				regime: currentRegime.regime,
				indicators: recommendation.indicators,
				risk_level: recommendation.risk_level,
			};
			onCreateStrategy(strategyConfig);
		}
	};

	// 백테스트 시작 핸들러
	const handleStartBacktest = () => {
		if (onStartBacktest) {
			const strategyConfig: StrategyConfig = {
				name: `${symbol} ${regimeLabel} 백테스트`,
				regime: currentRegime.regime,
				indicators: recommendation.indicators,
				risk_level: recommendation.risk_level,
			};
			onStartBacktest(strategyConfig);
		}
	};

	// ========================================
	// 렌더링
	// ========================================
	return (
		<Card>
			<CardHeader
				title="전략 추천"
				subheader={`${symbol} - ${regimeLabel}`}
				avatar={recommendation.icon}
				action={
					<Chip
						label={regimeLabel}
						size="small"
						sx={{
							bgcolor: regimeColor,
							color: "#fff",
							fontWeight: "bold",
						}}
					/>
				}
			/>
			<CardContent>
				{/* 설명 Alert */}
				<Alert severity="info" sx={{ mb: 2 }}>
					{recommendation.description}
				</Alert>

				{/* 추천 전략 목록 */}
				<Typography variant="subtitle2" gutterBottom>
					추천 전략
				</Typography>
				<List dense>
					{recommendation.strategies.map((strategy, index) => (
						<ListItem key={index}>
							<ListItemIcon>
								<CheckCircleIcon color="primary" fontSize="small" />
							</ListItemIcon>
							<ListItemText primary={strategy} />
						</ListItem>
					))}
				</List>

				<Divider sx={{ my: 2 }} />

				{/* 추천 인디케이터 */}
				<Typography variant="subtitle2" gutterBottom>
					추천 인디케이터
				</Typography>
				<Box sx={{ display: "flex", flexWrap: "wrap", gap: 1, mb: 2 }}>
					{recommendation.indicators.map((indicator) => (
						<Chip key={indicator} label={indicator} size="small" />
					))}
				</Box>

				<Divider sx={{ my: 2 }} />

				{/* 팁 */}
				<Typography variant="subtitle2" gutterBottom>
					주의사항 & 팁
				</Typography>
				<List dense>
					{recommendation.tips.map((tip, index) => (
						<ListItem key={index}>
							<ListItemIcon>
								<WarningIcon color="warning" fontSize="small" />
							</ListItemIcon>
							<ListItemText
								primary={tip}
								primaryTypographyProps={{ variant: "body2" }}
							/>
						</ListItem>
					))}
				</List>

				<Divider sx={{ my: 2 }} />

				{/* 리스크 레벨 */}
				<Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
					<Typography variant="subtitle2">리스크 레벨:</Typography>
					<Chip
						label={recommendation.risk_level}
						color={riskColors[recommendation.risk_level] as any}
						size="small"
					/>
				</Box>
			</CardContent>

			{/* 액션 버튼 */}
			<CardActions>
				<Button
					size="small"
					startIcon={<AddIcon />}
					onClick={handleCreateStrategy}
					disabled={!onCreateStrategy}
				>
					전략 생성
				</Button>
				<Button
					size="small"
					startIcon={<PlayArrowIcon />}
					onClick={handleStartBacktest}
					disabled={!onStartBacktest}
					variant="contained"
				>
					백테스트 시작
				</Button>
			</CardActions>
		</Card>
	);
};

// ============================================================================
// Exports
// ============================================================================
export default RegimeStrategyRecommendation;
