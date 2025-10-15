import type { RecentTradesResponse } from "@/client/types.gen";
import {
	TrendingUp as BuyIcon,
	Clear as ClearIcon,
	FilterList as FilterIcon,
	TrendingDown as SellIcon,
} from "@mui/icons-material";
import {
	Box,
	Card,
	CardContent,
	Chip,
	IconButton,
	MenuItem,
	Table,
	TableBody,
	TableCell,
	TableContainer,
	TableHead,
	TablePagination,
	TableRow,
	TextField,
	Typography,
	useTheme,
} from "@mui/material";
import { useState } from "react";

interface RecentTradesTableProps {
	trades: RecentTradesResponse;
	maxRows?: number;
}

type TradeType = "all" | "BUY" | "SELL";
type SortField = "date" | "symbol" | "type" | "quantity" | "price" | "profit";
type SortOrder = "asc" | "desc";

interface Trade {
	date: string;
	symbol: string;
	type: string;
	quantity: number;
	price: number;
	profit: number;
}

/**
 * RecentTradesTable Component
 *
 * Displays recent trades with:
 * - Filterable columns (symbol, type)
 * - Sortable columns (all)
 * - Pagination
 * - Color-coded profit/loss
 *
 * @example
 * ```tsx
 * <RecentTradesTable
 *   trades={recentTrades}
 *   maxRows={10}
 * />
 * ```
 */
export function RecentTradesTable({
	trades,
	maxRows = 10,
}: RecentTradesTableProps) {
	const theme = useTheme();

	// State
	const [page, setPage] = useState(0);
	const [rowsPerPage, setRowsPerPage] = useState(maxRows);
	const [symbolFilter, setSymbolFilter] = useState("");
	const [typeFilter, setTypeFilter] = useState<TradeType>("all");
	const [sortField, setSortField] = useState<SortField>("date");
	const [sortOrder, setSortOrder] = useState<SortOrder>("desc");

	// Process trades data
	const processedTrades: Trade[] =
		trades?.data?.trades?.map((trade) => ({
			date: new Date(trade.timestamp).toISOString(),
			symbol: trade.symbol || "",
			type: trade.side?.toUpperCase() || "UNKNOWN",
			quantity: trade.quantity || 0,
			price: trade.price || 0,
			profit: trade.pnl || 0,
		})) || []; // Filter trades
	const filteredTrades = processedTrades.filter((trade) => {
		// Symbol filter
		if (
			symbolFilter &&
			!trade.symbol.toLowerCase().includes(symbolFilter.toLowerCase())
		) {
			return false;
		}

		// Type filter
		if (typeFilter !== "all" && trade.type !== typeFilter) {
			return false;
		}

		return true;
	});

	// Sort trades
	const sortedTrades = [...filteredTrades].sort((a, b) => {
		let aValue: any = a[sortField];
		let bValue: any = b[sortField];

		// Convert date strings to timestamps
		if (sortField === "date") {
			aValue = new Date(aValue).getTime();
			bValue = new Date(bValue).getTime();
		}

		if (sortOrder === "asc") {
			return aValue > bValue ? 1 : -1;
		}
		return aValue < bValue ? 1 : -1;
	});

	// Paginate trades
	const paginatedTrades = sortedTrades.slice(
		page * rowsPerPage,
		page * rowsPerPage + rowsPerPage,
	);

	// Handlers
	const handleChangePage = (_event: unknown, newPage: number) => {
		setPage(newPage);
	};

	const handleChangeRowsPerPage = (
		event: React.ChangeEvent<HTMLInputElement>,
	) => {
		setRowsPerPage(Number.parseInt(event.target.value, 10));
		setPage(0);
	};

	const handleSort = (field: SortField) => {
		if (sortField === field) {
			setSortOrder(sortOrder === "asc" ? "desc" : "asc");
		} else {
			setSortField(field);
			setSortOrder("desc");
		}
	};

	const handleClearFilters = () => {
		setSymbolFilter("");
		setTypeFilter("all");
		setPage(0);
	};

	// Format functions
	const formatDate = (dateStr: string) => {
		const date = new Date(dateStr);
		return date.toLocaleDateString("ko-KR", {
			year: "numeric",
			month: "2-digit",
			day: "2-digit",
			hour: "2-digit",
			minute: "2-digit",
		});
	};

	const formatCurrency = (value: number) => {
		return new Intl.NumberFormat("ko-KR", {
			style: "currency",
			currency: "USD",
		}).format(value);
	};

	// Get trade type icon
	const getTradeIcon = (type: string) => {
		if (type === "BUY") {
			return <BuyIcon fontSize="small" color="success" />;
		}
		if (type === "SELL") {
			return <SellIcon fontSize="small" color="error" />;
		}
		return null;
	};

	// Get profit color
	const getProfitColor = (profit: number) => {
		if (profit > 0) return theme.palette.success.main;
		if (profit < 0) return theme.palette.error.main;
		return theme.palette.text.secondary;
	};

	if (processedTrades.length === 0) {
		return (
			<Card>
				<CardContent>
					<Typography variant="h6" gutterBottom>
						최근 거래
					</Typography>
					<Box
						sx={{
							display: "flex",
							alignItems: "center",
							justifyContent: "center",
							height: 200,
						}}
					>
						<Typography variant="body2" color="text.secondary">
							거래 내역이 없습니다
						</Typography>
					</Box>
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
					<Typography variant="h6">최근 거래</Typography>

					<Box sx={{ display: "flex", gap: 1, alignItems: "center" }}>
						<FilterIcon fontSize="small" />
						<TextField
							size="small"
							placeholder="심볼 검색"
							value={symbolFilter}
							onChange={(e) => {
								setSymbolFilter(e.target.value);
								setPage(0);
							}}
							sx={{ width: 120 }}
						/>

						<TextField
							size="small"
							select
							value={typeFilter}
							onChange={(e) => {
								setTypeFilter(e.target.value as TradeType);
								setPage(0);
							}}
							sx={{ width: 100 }}
						>
							<MenuItem value="all">전체</MenuItem>
							<MenuItem value="BUY">매수</MenuItem>
							<MenuItem value="SELL">매도</MenuItem>
						</TextField>

						{(symbolFilter || typeFilter !== "all") && (
							<IconButton size="small" onClick={handleClearFilters}>
								<ClearIcon fontSize="small" />
							</IconButton>
						)}
					</Box>
				</Box>

				<TableContainer>
					<Table size="small">
						<TableHead>
							<TableRow>
								<TableCell
									onClick={() => handleSort("date")}
									sx={{ cursor: "pointer", fontWeight: "bold" }}
								>
									날짜{" "}
									{sortField === "date" && (sortOrder === "asc" ? "↑" : "↓")}
								</TableCell>
								<TableCell
									onClick={() => handleSort("symbol")}
									sx={{ cursor: "pointer", fontWeight: "bold" }}
								>
									심볼{" "}
									{sortField === "symbol" && (sortOrder === "asc" ? "↑" : "↓")}
								</TableCell>
								<TableCell
									onClick={() => handleSort("type")}
									sx={{ cursor: "pointer", fontWeight: "bold" }}
								>
									유형{" "}
									{sortField === "type" && (sortOrder === "asc" ? "↑" : "↓")}
								</TableCell>
								<TableCell
									align="right"
									onClick={() => handleSort("quantity")}
									sx={{ cursor: "pointer", fontWeight: "bold" }}
								>
									수량{" "}
									{sortField === "quantity" &&
										(sortOrder === "asc" ? "↑" : "↓")}
								</TableCell>
								<TableCell
									align="right"
									onClick={() => handleSort("price")}
									sx={{ cursor: "pointer", fontWeight: "bold" }}
								>
									가격{" "}
									{sortField === "price" && (sortOrder === "asc" ? "↑" : "↓")}
								</TableCell>
								<TableCell
									align="right"
									onClick={() => handleSort("profit")}
									sx={{ cursor: "pointer", fontWeight: "bold" }}
								>
									손익{" "}
									{sortField === "profit" && (sortOrder === "asc" ? "↑" : "↓")}
								</TableCell>
							</TableRow>
						</TableHead>

						<TableBody>
							{paginatedTrades.map((trade, index) => (
								<TableRow key={`${trade.date}-${trade.symbol}-${index}`} hover>
									<TableCell>
										<Typography variant="body2" noWrap>
											{formatDate(trade.date)}
										</Typography>
									</TableCell>

									<TableCell>
										<Chip
											label={trade.symbol}
											size="small"
											variant="outlined"
										/>
									</TableCell>

									<TableCell>
										<Box
											sx={{ display: "flex", alignItems: "center", gap: 0.5 }}
										>
											{getTradeIcon(trade.type)}
											<Typography
												variant="body2"
												color={
													trade.type === "BUY" ? "success.main" : "error.main"
												}
											>
												{trade.type}
											</Typography>
										</Box>
									</TableCell>

									<TableCell align="right">
										<Typography variant="body2">
											{trade.quantity.toLocaleString()}
										</Typography>
									</TableCell>

									<TableCell align="right">
										<Typography variant="body2">
											{formatCurrency(trade.price)}
										</Typography>
									</TableCell>

									<TableCell align="right">
										<Typography
											variant="body2"
											fontWeight="bold"
											sx={{ color: getProfitColor(trade.profit) }}
										>
											{formatCurrency(trade.profit)}
										</Typography>
									</TableCell>
								</TableRow>
							))}
						</TableBody>
					</Table>
				</TableContainer>

				<TablePagination
					rowsPerPageOptions={[5, 10, 25, 50]}
					component="div"
					count={sortedTrades.length}
					rowsPerPage={rowsPerPage}
					page={page}
					onPageChange={handleChangePage}
					onRowsPerPageChange={handleChangeRowsPerPage}
					labelRowsPerPage="페이지당 행 수:"
					labelDisplayedRows={({ from, to, count }) =>
						`${from}-${to} / ${count !== -1 ? count : `${to} 이상`}`
					}
				/>
			</CardContent>
		</Card>
	);
}
