/**
 * RegimeIndicator Component
 *
 * 현재 시장 국면을 Badge/Chip 형태로 시각화하는 컴포넌트
 *
 * **주요 기능**:
 * - 국면 타입 표시 (상승장, 하락장, 변동장, 횡보장)
 * - 신뢰도 표시 (85% 등)
 * - 국면별 색상 구분 (Green, Red, Orange, Gray)
 * - 새로고침 버튼 (수동 재계산)
 * - Skeleton 로딩 상태
 *
 * **사용 예시**:
 * ```tsx
 * <RegimeIndicator
 *   symbol="AAPL"
 *   lookbackDays={60}
 *   showRefreshButton
 *   variant="outlined"
 * />
 * ```
 *
 * @module components/market-regime/RegimeIndicator
 */

import type { MarketRegimeType } from "@/client";
import { useRegimeDetection } from "@/hooks/useRegimeDetection";
import RefreshIcon from "@mui/icons-material/Refresh";
import ShowChartIcon from "@mui/icons-material/ShowChart";
import TrendingDownIcon from "@mui/icons-material/TrendingDown";
import TrendingFlatIcon from "@mui/icons-material/TrendingFlat";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import {
	Box,
	Chip,
	IconButton,
	Skeleton,
	Tooltip,
	Typography,
} from "@mui/material";
import type React from "react";

// ============================================================================
// Props Interface
// ============================================================================

export interface RegimeIndicatorProps {
	/** 심볼 (예: "AAPL") */
	symbol: string;
	/** Lookback 기간 (일수, 기본값: 60) */
	lookbackDays?: number;
	/** 새로고침 버튼 표시 여부 (기본값: true) */
	showRefreshButton?: boolean;
	/** 신뢰도 표시 여부 (기본값: true) */
	showConfidence?: boolean;
	/** Chip variant (filled | outlined) */
	variant?: "filled" | "outlined";
	/** 크기 (small | medium) */
	size?: "small" | "medium";
}

// ============================================================================
// Helper: 국면별 아이콘
// ============================================================================

const getRegimeIcon = (
	regime?: MarketRegimeType,
): React.ReactElement | undefined => {
	switch (regime) {
		case "bullish":
			return <TrendingUpIcon fontSize="small" />;
		case "bearish":
			return <TrendingDownIcon fontSize="small" />;
		case "volatile":
			return <ShowChartIcon fontSize="small" />;
		case "sideways":
			return <TrendingFlatIcon fontSize="small" />;
		default:
			return undefined;
	}
};

// ============================================================================
// Component
// ============================================================================

/**
 * RegimeIndicator 컴포넌트
 *
 * **렌더링 상태**:
 * - Loading: Skeleton (Chip 모양)
 * - Success: Chip (국면 라벨 + 신뢰도 + 아이콘) + 새로고침 버튼
 * - Error: 에러 Chip (빨간색)
 *
 * @param props - RegimeIndicatorProps
 */
export const RegimeIndicator: React.FC<RegimeIndicatorProps> = ({
	symbol,
	lookbackDays = 60,
	showRefreshButton = true,
	showConfidence = true,
	variant = "filled",
	size = "medium",
}) => {
	const {
		currentRegime,
		isLoading,
		error,
		refresh,
		isRefreshing,
		getRegimeColor,
		getRegimeLabel,
		formatConfidence,
	} = useRegimeDetection({ symbol, lookbackDays });

	// ========================================
	// 로딩 상태
	// ========================================
	if (isLoading) {
		return (
			<Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
				<Skeleton variant="rounded" width={150} height={32} />
				{showRefreshButton && (
					<Skeleton variant="circular" width={40} height={40} />
				)}
			</Box>
		);
	}

	// ========================================
	// 에러 상태
	// ========================================
	if (error) {
		return (
			<Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
				<Chip
					label="국면 감지 실패"
					color="error"
					size={size}
					variant={variant}
				/>
				{showRefreshButton && (
					<Tooltip title="다시 시도">
						<IconButton
							size="small"
							onClick={() => refresh.mutate()}
							disabled={isRefreshing}
						>
							<RefreshIcon />
						</IconButton>
					</Tooltip>
				)}
			</Box>
		);
	}

	// ========================================
	// 데이터 없음
	// ========================================
	if (!currentRegime) {
		return (
			<Chip
				label="국면 데이터 없음"
				color="default"
				size={size}
				variant={variant}
			/>
		);
	}

	// ========================================
	// 성공 상태
	// ========================================
	const regimeLabel = getRegimeLabel(currentRegime.regime);
	const regimeColor = getRegimeColor(currentRegime.regime);
	const confidence = formatConfidence(currentRegime.confidence);

	// Chip 라벨 구성
	const chipLabel = showConfidence
		? `${regimeLabel} (${confidence})`
		: regimeLabel;

	return (
		<Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
			{/* 국면 Chip */}
			<Chip
				label={chipLabel}
				icon={getRegimeIcon(currentRegime.regime)}
				size={size}
				variant={variant}
				sx={{
					bgcolor: variant === "filled" ? regimeColor : "transparent",
					color: variant === "filled" ? "#fff" : regimeColor,
					borderColor: variant === "outlined" ? regimeColor : undefined,
					fontWeight: "bold",
					"& .MuiChip-icon": {
						color: variant === "filled" ? "#fff" : regimeColor,
					},
				}}
			/>

			{/* 새로고침 버튼 */}
			{showRefreshButton && (
				<Tooltip title="국면 재계산">
					<IconButton
						size="small"
						onClick={() => refresh.mutate()}
						disabled={isRefreshing}
						sx={{
							"&:hover": {
								bgcolor: "action.hover",
							},
						}}
					>
						<RefreshIcon
							sx={{
								animation: isRefreshing ? "spin 1s linear infinite" : "none",
								"@keyframes spin": {
									from: { transform: "rotate(0deg)" },
									to: { transform: "rotate(360deg)" },
								},
							}}
						/>
					</IconButton>
				</Tooltip>
			)}

			{/* Lookback 정보 (Tooltip) */}
			<Tooltip
				title={
					<Box>
						<Typography variant="caption" display="block">
							<strong>심볼:</strong> {currentRegime.symbol}
						</Typography>
						<Typography variant="caption" display="block">
							<strong>Lookback:</strong> {currentRegime.lookback_days}일
						</Typography>
						<Typography variant="caption" display="block">
							<strong>기준 시점:</strong>{" "}
							{new Date(currentRegime.as_of).toLocaleString("ko-KR")}
						</Typography>
						{currentRegime.notes && currentRegime.notes.length > 0 && (
							<Typography variant="caption" display="block" sx={{ mt: 1 }}>
								<strong>참고:</strong> {currentRegime.notes.join(", ")}
							</Typography>
						)}
					</Box>
				}
				arrow
			>
				<Typography
					variant="caption"
					sx={{
						color: "text.secondary",
						cursor: "help",
						display: { xs: "none", sm: "block" }, // 모바일에서 숨김
					}}
				>
					{lookbackDays}일
				</Typography>
			</Tooltip>
		</Box>
	);
};

// ============================================================================
// Exports
// ============================================================================
export default RegimeIndicator;
