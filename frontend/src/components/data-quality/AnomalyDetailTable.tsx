import type { DataQualityAlert, DataQualitySeverity } from "@/client/types.gen";
import {
	Box,
	Card,
	CardContent,
	Chip,
	FormControl,
	InputLabel,
	MenuItem,
	Paper,
	Select,
	Table,
	TableBody,
	TableCell,
	TableContainer,
	TableHead,
	TablePagination,
	TableRow,
	TableSortLabel,
	TextField,
	Typography,
	type SelectChangeEvent,
} from "@mui/material";
import { useMemo, useState } from "react";

interface AnomalyDetailTableProps {
	alerts: DataQualityAlert[];
	title?: string;
}

type SortOrder = "asc" | "desc";
type SortField =
	| "occurred_at"
	| "symbol"
	| "severity"
	| "iso_score"
	| "prophet_score"
	| "price_change_pct"
	| "volume_z_score";

/**
 * AnomalyDetailTable Component
 *
 * 데이터 품질 알림 상세 테이블
 *
 * Features:
 * - Material-UI Table 사용
 * - 컬럼: 날짜, 심볼, 데이터 타입, 심각도, 점수, 메시지
 * - 필터: 심볼 검색, 심각도 필터
 * - 정렬: 모든 컬럼 정렬 가능
 * - 페이지네이션: 페이지당 10/25/50 행
 *
 * @example
 * ```tsx
 * import { AnomalyDetailTable } from "@/components/data-quality/AnomalyDetailTable";
 * import { useDataQuality } from "@/hooks/useDataQuality";
 *
 * function AnomalyPage() {
 *   const { recentAlerts } = useDataQuality();
 *   return <AnomalyDetailTable alerts={recentAlerts} title="이상 탐지 상세" />;
 * }
 * ```
 */
export function AnomalyDetailTable({
	alerts,
	title = "이상 탐지 상세",
}: AnomalyDetailTableProps) {
	// 페이지네이션
	const [page, setPage] = useState(0);
	const [rowsPerPage, setRowsPerPage] = useState(10);

	// 정렬
	const [sortField, setSortField] = useState<SortField>("occurred_at");
	const [sortOrder, setSortOrder] = useState<SortOrder>("desc");

	// 필터
	const [symbolFilter, setSymbolFilter] = useState("");
	const [severityFilter, setSeverityFilter] = useState<
		DataQualitySeverity | "all"
	>("all");

	// 심각도 라벨
	const getSeverityLabel = (severity: DataQualitySeverity) => {
		const labels = {
			critical: "긴급",
			high: "높음",
			medium: "중간",
			low: "낮음",
			normal: "정상",
		};
		return labels[severity] || severity;
	};

	// 심각도 색상
	const getSeverityColor = (
		severity: DataQualitySeverity,
	): "error" | "warning" | "info" | "success" => {
		const colors = {
			critical: "error" as const,
			high: "error" as const,
			medium: "warning" as const,
			low: "info" as const,
			normal: "success" as const,
		};
		return colors[severity] || "info";
	};

	// 필터링 및 정렬
	const filteredAndSortedAlerts = useMemo(() => {
		let filtered = alerts;

		// 심볼 필터
		if (symbolFilter) {
			filtered = filtered.filter((alert) =>
				alert.symbol.toLowerCase().includes(symbolFilter.toLowerCase()),
			);
		}

		// 심각도 필터
		if (severityFilter !== "all") {
			filtered = filtered.filter((alert) => alert.severity === severityFilter);
		}

		// 정렬
		const sorted = [...filtered].sort((a, b) => {
			let aValue: number | string | Date | null | undefined = a[sortField];
			let bValue: number | string | Date | null | undefined = b[sortField];

			// 날짜 타입 처리
			if (sortField === "occurred_at") {
				aValue = new Date(a.occurred_at).getTime();
				bValue = new Date(b.occurred_at).getTime();
			}

			// null 처리 (prophet_score)
			if (sortField === "prophet_score") {
				aValue = a.prophet_score ?? 0;
				bValue = b.prophet_score ?? 0;
			}

			// undefined 처리
			if (aValue === null || aValue === undefined) return 1;
			if (bValue === null || bValue === undefined) return -1;

			if (aValue < bValue) {
				return sortOrder === "asc" ? -1 : 1;
			}
			if (aValue > bValue) {
				return sortOrder === "asc" ? 1 : -1;
			}
			return 0;
		});

		return sorted;
	}, [alerts, symbolFilter, severityFilter, sortField, sortOrder]);

	// 페이지 변경 핸들러
	const handleChangePage = (_event: unknown, newPage: number) => {
		setPage(newPage);
	};

	// 페이지당 행 수 변경 핸들러
	const handleChangeRowsPerPage = (
		event: React.ChangeEvent<HTMLInputElement>,
	) => {
		setRowsPerPage(Number.parseInt(event.target.value, 10));
		setPage(0);
	};

	// 정렬 핸들러
	const handleSort = (field: SortField) => {
		const isAsc = sortField === field && sortOrder === "asc";
		setSortOrder(isAsc ? "desc" : "asc");
		setSortField(field);
	};

	// 심각도 필터 핸들러
	const handleSeverityFilterChange = (event: SelectChangeEvent<string>) => {
		setSeverityFilter(event.target.value as DataQualitySeverity | "all");
		setPage(0);
	};

	// 페이지네이션 적용
	const paginatedAlerts = filteredAndSortedAlerts.slice(
		page * rowsPerPage,
		page * rowsPerPage + rowsPerPage,
	);

	return (
		<Card>
			<CardContent>
				<Typography variant="h6" gutterBottom>
					{title} ({filteredAndSortedAlerts.length}개)
				</Typography>

				{/* 필터 */}
				<Box sx={{ display: "flex", gap: 2, mb: 2 }}>
					<TextField
						label="심볼 검색"
						variant="outlined"
						size="small"
						value={symbolFilter}
						onChange={(e) => {
							setSymbolFilter(e.target.value);
							setPage(0);
						}}
						sx={{ minWidth: 200 }}
					/>

					<FormControl size="small" sx={{ minWidth: 150 }}>
						<InputLabel>심각도 필터</InputLabel>
						<Select
							value={severityFilter}
							label="심각도 필터"
							onChange={handleSeverityFilterChange}
						>
							<MenuItem value="all">전체</MenuItem>
							<MenuItem value="critical">긴급</MenuItem>
							<MenuItem value="high">높음</MenuItem>
							<MenuItem value="medium">중간</MenuItem>
							<MenuItem value="low">낮음</MenuItem>
							<MenuItem value="normal">정상</MenuItem>
						</Select>
					</FormControl>
				</Box>

				{/* 테이블 */}
				<TableContainer component={Paper} sx={{ maxHeight: 600 }}>
					<Table stickyHeader size="small">
						<TableHead>
							<TableRow>
								<TableCell>
									<TableSortLabel
										active={sortField === "occurred_at"}
										direction={sortField === "occurred_at" ? sortOrder : "asc"}
										onClick={() => handleSort("occurred_at")}
									>
										발생 시각
									</TableSortLabel>
								</TableCell>
								<TableCell>
									<TableSortLabel
										active={sortField === "symbol"}
										direction={sortField === "symbol" ? sortOrder : "asc"}
										onClick={() => handleSort("symbol")}
									>
										심볼
									</TableSortLabel>
								</TableCell>
								<TableCell>데이터 타입</TableCell>
								<TableCell>
									<TableSortLabel
										active={sortField === "severity"}
										direction={sortField === "severity" ? sortOrder : "asc"}
										onClick={() => handleSort("severity")}
									>
										심각도
									</TableSortLabel>
								</TableCell>
								<TableCell align="right">
									<TableSortLabel
										active={sortField === "iso_score"}
										direction={sortField === "iso_score" ? sortOrder : "asc"}
										onClick={() => handleSort("iso_score")}
									>
										ISO 점수
									</TableSortLabel>
								</TableCell>
								<TableCell align="right">
									<TableSortLabel
										active={sortField === "prophet_score"}
										direction={
											sortField === "prophet_score" ? sortOrder : "asc"
										}
										onClick={() => handleSort("prophet_score")}
									>
										Prophet 점수
									</TableSortLabel>
								</TableCell>
								<TableCell align="right">
									<TableSortLabel
										active={sortField === "price_change_pct"}
										direction={
											sortField === "price_change_pct" ? sortOrder : "asc"
										}
										onClick={() => handleSort("price_change_pct")}
									>
										가격 변동률
									</TableSortLabel>
								</TableCell>
								<TableCell align="right">
									<TableSortLabel
										active={sortField === "volume_z_score"}
										direction={
											sortField === "volume_z_score" ? sortOrder : "asc"
										}
										onClick={() => handleSort("volume_z_score")}
									>
										거래량 Z
									</TableSortLabel>
								</TableCell>
								<TableCell>메시지</TableCell>
							</TableRow>
						</TableHead>
						<TableBody>
							{paginatedAlerts.length === 0 ? (
								<TableRow>
									<TableCell colSpan={9} align="center">
										<Typography variant="body2" color="text.secondary">
											데이터가 없습니다.
										</Typography>
									</TableCell>
								</TableRow>
							) : (
								paginatedAlerts.map((alert, index) => (
									<TableRow key={`${alert.symbol}-${index}`} hover>
										<TableCell>
											{new Date(alert.occurred_at).toLocaleDateString("ko-KR")}
											<br />
											<Typography variant="caption" color="text.secondary">
												{new Date(alert.occurred_at).toLocaleTimeString(
													"ko-KR",
												)}
											</Typography>
										</TableCell>
										<TableCell>
											<Chip
												label={alert.symbol}
												size="small"
												variant="outlined"
											/>
										</TableCell>
										<TableCell>{alert.data_type}</TableCell>
										<TableCell>
											<Chip
												label={getSeverityLabel(alert.severity)}
												size="small"
												color={getSeverityColor(alert.severity)}
											/>
										</TableCell>
										<TableCell align="right">
											{alert.iso_score.toFixed(4)}
										</TableCell>
										<TableCell align="right">
											{alert.prophet_score?.toFixed(4) || "N/A"}
										</TableCell>
										<TableCell align="right">
											{alert.price_change_pct.toFixed(2)}%
										</TableCell>
										<TableCell align="right">
											{alert.volume_z_score.toFixed(2)}
										</TableCell>
										<TableCell>
											<Typography variant="body2" noWrap>
												{alert.message}
											</Typography>
										</TableCell>
									</TableRow>
								))
							)}
						</TableBody>
					</Table>
				</TableContainer>

				{/* 페이지네이션 */}
				<TablePagination
					component="div"
					count={filteredAndSortedAlerts.length}
					page={page}
					onPageChange={handleChangePage}
					rowsPerPage={rowsPerPage}
					onRowsPerPageChange={handleChangeRowsPerPage}
					rowsPerPageOptions={[10, 25, 50]}
					labelRowsPerPage="페이지당 행 수"
					labelDisplayedRows={({ from, to, count }) =>
						`${from}-${to} / 총 ${count}개`
					}
				/>
			</CardContent>
		</Card>
	);
}
