/**
 * RegimeComparison Component
 *
 * 여러 심볼의 시장 국면을 비교하는 테이블 컴포넌트
 *
 * **주요 기능**:
 * - 여러 심볼 동시 조회 (예: AAPL, TSLA, MSFT)
 * - 국면 비교 테이블 (심볼, 국면, 신뢰도, 메트릭)
 * - 국면별 색상 구분
 * - 정렬 기능 (심볼, 신뢰도, 수익률 등)
 * - 반응형 테이블
 *
 * **사용 예시**:
 * ```tsx
 * <RegimeComparison
 *   symbols={["AAPL", "TSLA", "MSFT", "GOOGL"]}
 *   lookbackDays={60}
 * />
 * ```
 *
 * @module components/market-regime/RegimeComparison
 */

import { useRegimeDetection } from "@/hooks/useRegimeDetection";
import {
	Box,
	Card,
	CardContent,
	CardHeader,
	Chip,
	Paper,
	Skeleton,
	Table,
	TableBody,
	TableCell,
	TableContainer,
	TableHead,
	TableRow,
	TableSortLabel,
	Typography,
} from "@mui/material";
import { useState } from "react";

// ============================================================================
// Props Interface
// ============================================================================

export interface RegimeComparisonProps {
	/** 비교할 심볼 목록 (예: ["AAPL", "TSLA", "MSFT"]) */
	symbols: string[];
	/** Lookback 기간 (일수, 기본값: 60) */
	lookbackDays?: number;
}

// ============================================================================
// Type: 정렬 필드
// ============================================================================

type SortField =
	| "symbol"
	| "regime"
	| "confidence"
	| "trailing_return_pct"
	| "volatility_pct";

// ============================================================================
// Sub-Component: RegimeRow (각 심볼의 행)
// ============================================================================

interface RegimeRowProps {
	symbol: string;
	lookbackDays: number;
}

const RegimeRow: React.FC<RegimeRowProps> = ({ symbol, lookbackDays }) => {
	const { currentRegime, isLoading, error, getRegimeColor, getRegimeLabel } =
		useRegimeDetection({ symbol, lookbackDays });

	// 로딩 상태
	if (isLoading) {
		return (
			<TableRow>
				<TableCell>
					<Skeleton width={80} />
				</TableCell>
				<TableCell>
					<Skeleton width={100} />
				</TableCell>
				<TableCell>
					<Skeleton width={60} />
				</TableCell>
				<TableCell>
					<Skeleton width={60} />
				</TableCell>
				<TableCell>
					<Skeleton width={60} />
				</TableCell>
				<TableCell>
					<Skeleton width={60} />
				</TableCell>
				<TableCell>
					<Skeleton width={60} />
				</TableCell>
			</TableRow>
		);
	}

	// 에러 상태
	if (error) {
		return (
			<TableRow>
				<TableCell>{symbol}</TableCell>
				<TableCell colSpan={6}>
					<Typography variant="caption" color="error">
						데이터 로드 실패
					</Typography>
				</TableCell>
			</TableRow>
		);
	}

	// 데이터 없음
	if (!currentRegime) {
		return (
			<TableRow>
				<TableCell>{symbol}</TableCell>
				<TableCell colSpan={6}>
					<Typography variant="caption" color="text.secondary">
						데이터 없음
					</Typography>
				</TableCell>
			</TableRow>
		);
	}

	// 성공 상태
	const regimeColor = getRegimeColor(currentRegime.regime);
	const regimeLabel = getRegimeLabel(currentRegime.regime);

	return (
		<TableRow hover>
			<TableCell>
				<Typography variant="body2" fontWeight="bold">
					{currentRegime.symbol}
				</Typography>
			</TableCell>
			<TableCell>
				<Chip
					label={regimeLabel}
					size="small"
					sx={{
						bgcolor: regimeColor,
						color: "#fff",
						fontWeight: "bold",
					}}
				/>
			</TableCell>
			<TableCell align="right">
				{(currentRegime.confidence * 100).toFixed(1)}%
			</TableCell>
			<TableCell align="right">
				{currentRegime.metrics.trailing_return_pct.toFixed(2)}%
			</TableCell>
			<TableCell align="right">
				{currentRegime.metrics.volatility_pct.toFixed(2)}%
			</TableCell>
			<TableCell align="right">
				{currentRegime.metrics.drawdown_pct.toFixed(2)}%
			</TableCell>
			<TableCell align="right">
				{currentRegime.metrics.momentum_z.toFixed(2)}
			</TableCell>
		</TableRow>
	);
};

// ============================================================================
// Main Component
// ============================================================================

/**
 * RegimeComparison 컴포넌트
 *
 * **렌더링 구조**:
 * - CardHeader: 제목, 서브헤더
 * - TableContainer: 반응형 테이블
 * - TableHead: 정렬 가능한 헤더
 * - TableBody: 각 심볼별 RegimeRow
 *
 * @param props - RegimeComparisonProps
 */
export const RegimeComparison: React.FC<RegimeComparisonProps> = ({
	symbols,
	lookbackDays = 60,
}) => {
	// 정렬 상태
	const [sortField, setSortField] = useState<SortField>("symbol");
	const [sortDirection, setSortDirection] = useState<"asc" | "desc">("asc");

	// ========================================
	// 정렬 핸들러
	// ========================================
	const handleSort = (field: SortField) => {
		if (sortField === field) {
			// 같은 필드 클릭 시 방향 토글
			setSortDirection(sortDirection === "asc" ? "desc" : "asc");
		} else {
			// 다른 필드 클릭 시 해당 필드로 오름차순
			setSortField(field);
			setSortDirection("asc");
		}
	};

	// ========================================
	// Empty State
	// ========================================
	if (symbols.length === 0) {
		return (
			<Card>
				<CardHeader title="국면 비교" />
				<CardContent>
					<Typography color="text.secondary">
						비교할 심볼을 선택해주세요.
					</Typography>
				</CardContent>
			</Card>
		);
	}

	// ========================================
	// 테이블 렌더링
	// ========================================
	return (
		<Card>
			<CardHeader
				title="국면 비교"
				subheader={`${symbols.length}개 심볼 (Lookback: ${lookbackDays}일)`}
			/>
			<CardContent>
				<TableContainer component={Paper} variant="outlined">
					<Table size="small">
						<TableHead>
							<TableRow>
								<TableCell>
									<TableSortLabel
										active={sortField === "symbol"}
										direction={sortField === "symbol" ? sortDirection : "asc"}
										onClick={() => handleSort("symbol")}
									>
										심볼
									</TableSortLabel>
								</TableCell>
								<TableCell>
									<TableSortLabel
										active={sortField === "regime"}
										direction={sortField === "regime" ? sortDirection : "asc"}
										onClick={() => handleSort("regime")}
									>
										국면
									</TableSortLabel>
								</TableCell>
								<TableCell align="right">
									<TableSortLabel
										active={sortField === "confidence"}
										direction={
											sortField === "confidence" ? sortDirection : "asc"
										}
										onClick={() => handleSort("confidence")}
									>
										신뢰도
									</TableSortLabel>
								</TableCell>
								<TableCell align="right">
									<TableSortLabel
										active={sortField === "trailing_return_pct"}
										direction={
											sortField === "trailing_return_pct"
												? sortDirection
												: "asc"
										}
										onClick={() => handleSort("trailing_return_pct")}
									>
										수익률
									</TableSortLabel>
								</TableCell>
								<TableCell align="right">
									<TableSortLabel
										active={sortField === "volatility_pct"}
										direction={
											sortField === "volatility_pct" ? sortDirection : "asc"
										}
										onClick={() => handleSort("volatility_pct")}
									>
										변동성
									</TableSortLabel>
								</TableCell>
								<TableCell align="right">낙폭</TableCell>
								<TableCell align="right">모멘텀 Z</TableCell>
							</TableRow>
						</TableHead>
						<TableBody>
							{symbols.map((symbol) => (
								<RegimeRow
									key={symbol}
									symbol={symbol}
									lookbackDays={lookbackDays}
								/>
							))}
						</TableBody>
					</Table>
				</TableContainer>

				{/* 하단 주석 */}
				<Box sx={{ mt: 2 }}>
					<Typography variant="caption" color="text.secondary">
						* 수익률/변동성/낙폭은 Lookback 기간 내 수치입니다.
					</Typography>
				</Box>
			</CardContent>
		</Card>
	);
};

// ============================================================================
// Exports
// ============================================================================
export default RegimeComparison;
