"use client";

import {
	Add,
	Assessment,
	Delete,
	Edit,
	Favorite,
	FavoriteBorder,
	FilterList,
	PlayArrow,
	Search,
	ShowChart,
	TrendingDown,
	TrendingUp,
} from "@mui/icons-material";
import {
	Alert,
	Box,
	Button,
	Card,
	CardActions,
	CardContent,
	Chip,
	Container,
	Fab,
	FormControl,
	Grid,
	IconButton,
	InputLabel,
	LinearProgress,
	MenuItem,
	Paper,
	Select,
	Stack,
	TextField,
	Tooltip,
	Typography,
} from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import React, { useState } from "react";
import PageContainer from "@/components/layout/PageContainer";
import {
	type BacktestStatus,
	type BacktestSummary,
	backtestsGetBacktestsOptions,
	backtestUtils,
} from "@/services/backtestsQuery";

export default function BacktestsPage() {
	const router = useRouter();
	const [searchQuery, setSearchQuery] = useState("");
	const [statusFilter, setStatusFilter] = useState<BacktestStatus | "ALL">(
		"ALL",
	);
	const [sortBy, setSortBy] = useState<
		"created_at" | "name" | "total_return" | "status"
	>("created_at");
	const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

	// Use TanStack Query properly
	const {
		data: backtestsResponse,
		isLoading,
		error,
	} = useQuery(backtestsGetBacktestsOptions({}));

	// Extract the actual backtests array from response
	const backtests = backtestsResponse?.backtests || [];

	// Filter and sort backtests
	const filteredBacktests = React.useMemo(() => {
		let filtered = backtests;

		// Apply search filter
		if (searchQuery) {
			filtered = filtered.filter(
				(backtest: any) =>
					backtest.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
					backtest.strategy_name
						?.toLowerCase()
						.includes(searchQuery.toLowerCase()),
			);
		}

		// Apply status filter
		if (statusFilter !== "ALL") {
			filtered = filtered.filter(
				(backtest: any) => backtest.status === statusFilter,
			);
		}

		// Apply sorting if we have a valid array
		if (Array.isArray(filtered)) {
			return backtestUtils.sortBacktests(
				filtered as unknown as BacktestSummary[],
				sortBy,
				sortOrder,
			);
		}
		return [];
	}, [backtests, searchQuery, statusFilter, sortBy, sortOrder]);

	const handleCreateNew = () => {
		router.push("/backtests/create");
	};

	const handleViewBacktest = (id: string) => {
		router.push(`/backtests/${id}`);
	};

	const handleExecuteBacktest = async (id: string) => {
		console.log("Execute backtest:", id);
	};

	const handleDeleteBacktest = async (id: string) => {
		console.log("Delete backtest:", id);
	};

	const handleToggleFavorite = async (id: string) => {
		console.log("Toggle favorite:", id);
	};

	const getReturnIcon = (value?: number) => {
		if (value === undefined || value === null) return <ShowChart />;
		return value >= 0 ? (
			<TrendingUp color="success" />
		) : (
			<TrendingDown color="error" />
		);
	};

	const getReturnColor = (value?: number) => {
		if (value === undefined || value === null) return "text.secondary";
		return value >= 0 ? "success.main" : "error.main";
	};

	if (error) {
		return (
			<PageContainer
				title="백테스트 히스토리"
				breadcrumbs={[{ title: "백테스트" }]}
			>
				<Alert severity="error">
					백테스트 목록을 불러오는 중 오류가 발생했습니다.
				</Alert>
			</PageContainer>
		);
	}

	return (
		<PageContainer
			title="백테스트 히스토리"
			breadcrumbs={[{ title: "백테스트" }]}
		>
			<Container maxWidth="lg">
				{/* Header */}
				<Box sx={{ mb: 4 }}>
					<Typography variant="body1" color="text.secondary">
						실행된 백테스트 결과를 확인하고 관리하세요
					</Typography>
				</Box>

				{/* Filters and Search */}
				<Paper sx={{ p: 3, mb: 3 }}>
					<Grid container spacing={2} alignItems="center">
						<Grid size={4}>
							<TextField
								fullWidth
								placeholder="백테스트 이름이나 전략으로 검색..."
								value={searchQuery}
								onChange={(e) => setSearchQuery(e.target.value)}
								InputProps={{
									startAdornment: (
										<Search sx={{ mr: 1, color: "text.secondary" }} />
									),
								}}
							/>
						</Grid>
						<Grid size={2}>
							<FormControl fullWidth>
								<InputLabel>상태</InputLabel>
								<Select
									value={statusFilter}
									label="상태"
									onChange={(e) =>
										setStatusFilter(e.target.value as BacktestStatus | "ALL")
									}
								>
									<MenuItem value="ALL">전체</MenuItem>
									<MenuItem value="COMPLETED">완료</MenuItem>
									<MenuItem value="FAILED">실패</MenuItem>
									<MenuItem value="QUEUED">대기중</MenuItem>
									<MenuItem value="INITIALIZING">실행중</MenuItem>
								</Select>
							</FormControl>
						</Grid>
						<Grid size={2}>
							<FormControl fullWidth>
								<InputLabel>정렬</InputLabel>
								<Select
									value={sortBy}
									label="정렬"
									onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
								>
									<MenuItem value="created_at">생성일</MenuItem>
									<MenuItem value="name">이름</MenuItem>
									<MenuItem value="total_return">수익률</MenuItem>
									<MenuItem value="status">상태</MenuItem>
								</Select>
							</FormControl>
						</Grid>
						<Grid size={2}>
							<FormControl fullWidth>
								<InputLabel>순서</InputLabel>
								<Select
									value={sortOrder}
									label="순서"
									onChange={(e) =>
										setSortOrder(e.target.value as "asc" | "desc")
									}
								>
									<MenuItem value="desc">내림차순</MenuItem>
									<MenuItem value="asc">오름차순</MenuItem>
								</Select>
							</FormControl>
						</Grid>
						<Grid size={2}>
							<Button
								variant="outlined"
								startIcon={<FilterList />}
								fullWidth
								onClick={() => {
									setSearchQuery("");
									setStatusFilter("ALL");
									setSortBy("created_at");
									setSortOrder("desc");
								}}
							>
								초기화
							</Button>
						</Grid>
					</Grid>
				</Paper>

				{/* Loading */}
				{isLoading && (
					<Box sx={{ mb: 3 }}>
						<LinearProgress />
					</Box>
				)}

				{/* Backtest Cards */}
				<Grid container spacing={3}>
					{filteredBacktests.map((backtest: any) => (
						<Grid size={4} key={backtest.id}>
							<Card
								sx={{
									cursor: "pointer",
									transition: "all 0.2s",
									"&:hover": {
										boxShadow: 4,
										transform: "translateY(-2px)",
									},
								}}
							>
								<CardContent>
									<Box
										sx={{
											display: "flex",
											justifyContent: "space-between",
											alignItems: "flex-start",
											mb: 2,
										}}
									>
										<Box sx={{ flex: 1 }}>
											<Typography variant="h6" component="h3" gutterBottom>
												{backtest.name}
											</Typography>
											<Typography
												variant="body2"
												color="text.secondary"
												gutterBottom
											>
												전략: {backtest.strategy_name} ({backtest.strategy_type}
												)
											</Typography>
										</Box>
										<Stack direction="row" spacing={1} alignItems="center">
											<Chip
												label={backtestUtils.formatStatus(backtest.status)}
												size="small"
												sx={{
													backgroundColor: backtestUtils.getStatusColor(
														backtest.status,
													),
													color: "white",
												}}
											/>
											<IconButton
												size="small"
												onClick={(e) => {
													e.stopPropagation();
													handleToggleFavorite(backtest.id);
												}}
											>
												{backtest.is_favorite ? (
													<Favorite color="error" />
												) : (
													<FavoriteBorder />
												)}
											</IconButton>
										</Stack>
									</Box>

									{/* Progress bar for running backtests */}
									{backtestUtils.isRunning(backtest.status) && (
										<Box sx={{ mb: 2 }}>
											<LinearProgress variant="indeterminate" />
											<Typography
												variant="caption"
												color="text.secondary"
												sx={{ mt: 1 }}
											>
												{backtestUtils.formatStatus(backtest.status)}...
											</Typography>
										</Box>
									)}

									{/* Performance Metrics */}
									{backtestUtils.isCompleted(backtest.status) && (
										<Grid container spacing={2} sx={{ mb: 2 }}>
											<Grid size={3}>
												<Box sx={{ textAlign: "center" }}>
													<Box
														sx={{
															display: "flex",
															alignItems: "center",
															justifyContent: "center",
															mb: 1,
														}}
													>
														{getReturnIcon(backtest.total_return)}
													</Box>
													<Typography
														variant="h6"
														sx={{
															color: getReturnColor(backtest.total_return),
														}}
													>
														{backtest.total_return
															? backtestUtils.formatPercentage(
																	backtest.total_return,
																)
															: "-"}
													</Typography>
													<Typography variant="caption" color="text.secondary">
														총 수익률
													</Typography>
												</Box>
											</Grid>
											<Grid size={3}>
												<Box sx={{ textAlign: "center" }}>
													<Assessment sx={{ mb: 1 }} />
													<Typography variant="h6">
														{backtest.sharpe_ratio
															? backtestUtils.formatNumber(
																	backtest.sharpe_ratio,
																)
															: "-"}
													</Typography>
													<Typography variant="caption" color="text.secondary">
														샤프 비율
													</Typography>
												</Box>
											</Grid>
											<Grid size={3}>
												<Box sx={{ textAlign: "center" }}>
													<TrendingDown sx={{ mb: 1, color: "error.main" }} />
													<Typography variant="h6" color="error">
														{backtest.max_drawdown
															? backtestUtils.formatPercentage(
																	Math.abs(backtest.max_drawdown),
																)
															: "-"}
													</Typography>
													<Typography variant="caption" color="text.secondary">
														최대 낙폭
													</Typography>
												</Box>
											</Grid>
											<Grid size={3}>
												<Box sx={{ textAlign: "center" }}>
													<ShowChart sx={{ mb: 1 }} />
													<Typography variant="h6">
														{backtest.duration
															? backtestUtils.formatDuration(
																	backtest.created_at,
																	backtest.completed_at,
																)
															: "-"}
													</Typography>
													<Typography variant="caption" color="text.secondary">
														실행 시간
													</Typography>
												</Box>
											</Grid>
										</Grid>
									)}

									{/* Tags */}
									{backtest.tags?.length > 0 && (
										<Box sx={{ mb: 2 }}>
											<Stack direction="row" spacing={1} flexWrap="wrap">
												{backtest.tags.map((tag: string) => (
													<Chip
														key={tag}
														label={tag}
														size="small"
														variant="outlined"
													/>
												))}
											</Stack>
										</Box>
									)}

									{/* Meta Information */}
									<Typography variant="caption" color="text.secondary">
										생성일:{" "}
										{new Date(backtest.created_at).toLocaleDateString("ko-KR")}{" "}
										· 수정일:{" "}
										{new Date(backtest.updated_at).toLocaleDateString("ko-KR")}
									</Typography>
								</CardContent>

								<CardActions sx={{ justifyContent: "space-between" }}>
									<Box>
										<Button
											size="small"
											onClick={(e) => {
												e.stopPropagation();
												handleViewBacktest(backtest.id);
											}}
										>
											자세히 보기
										</Button>
										{backtestUtils.isCompleted(backtest.status) && (
											<Button
												size="small"
												startIcon={<PlayArrow />}
												onClick={(e) => {
													e.stopPropagation();
													handleExecuteBacktest(backtest.id);
												}}
											>
												재실행
											</Button>
										)}
									</Box>
									<Box>
										<Tooltip title="수정">
											<IconButton
												size="small"
												onClick={(e) => {
													e.stopPropagation();
													router.push(`/backtests/${backtest.id}/edit`);
												}}
											>
												<Edit />
											</IconButton>
										</Tooltip>
										<Tooltip title="삭제">
											<IconButton
												size="small"
												color="error"
												onClick={(e) => {
													e.stopPropagation();
													handleDeleteBacktest(backtest.id);
												}}
											>
												<Delete />
											</IconButton>
										</Tooltip>
									</Box>
								</CardActions>
							</Card>
						</Grid>
					))}
				</Grid>

				{/* Empty State */}
				{!isLoading && filteredBacktests.length === 0 && (
					<Paper sx={{ p: 6, textAlign: "center" }}>
						<Typography variant="h6" gutterBottom>
							백테스트가 없습니다
						</Typography>
						<Typography variant="body2" color="text.secondary" gutterBottom>
							새로운 백테스트를 생성하여 전략의 성과를 확인해보세요
						</Typography>
						<Button
							variant="contained"
							startIcon={<Add />}
							onClick={handleCreateNew}
							sx={{ mt: 2 }}
						>
							새 백테스트 만들기
						</Button>
					</Paper>
				)}

				{/* Floating Action Button */}
				<Fab
					color="primary"
					sx={{ position: "fixed", bottom: 24, right: 24 }}
					onClick={handleCreateNew}
				>
					<Add />
				</Fab>
			</Container>
		</PageContainer>
	);
}
