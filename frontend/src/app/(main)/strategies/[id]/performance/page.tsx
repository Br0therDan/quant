"use client";

import {
	ArrowBack,
	Assessment,
	ShowChart,
	TableChart,
	TrendingDown,
	TrendingUp,
} from "@mui/icons-material";
import {
	Alert,
	Box,
	Button,
	Card,
	CardContent,
	Chip,
	CircularProgress,
	FormControl,
	Grid,
	InputLabel,
	MenuItem,
	Paper,
	Select,
	Tab,
	Table,
	TableBody,
	TableCell,
	TableContainer,
	TableHead,
	TableRow,
	Tabs,
	Typography,
} from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import type React from "react";
import { useState } from "react";

import PageContainer from "@/components/layout/PageContainer";
import StrategyPerformanceSummary from "@/components/strategies/StrategyPerformanceSummary";

import { useStrategyQuery } from "@/services/strategiesQuery";

interface TabPanelProps {
	children?: React.ReactNode;
	index: number;
	value: number;
}

function CustomTabPanel(props: TabPanelProps) {
	const { children, value, index, ...other } = props;

	return (
		<div
			role="tabpanel"
			hidden={value !== index}
			id={`simple-tabpanel-${index}`}
			aria-labelledby={`simple-tab-${index}`}
			{...other}
		>
			{value === index && <Box sx={{ py: 3 }}>{children}</Box>}
		</div>
	);
}

export default function StrategyPerformancePage() {
	const router = useRouter();
	const params = useParams();
	const strategyId = params.id as string;

	const [tabValue, setTabValue] = useState(0);
	const [selectedPeriod, setSelectedPeriod] = useState("1Y");

	// 전략 데이터 조회
	const {
		data: strategy,
		isLoading: strategyLoading,
		error: strategyError,
	} = useQuery(
		useStrategyQuery({
			path: { strategy_id: strategyId },
		}),
	);

	// 백테스트 결과는 모의 데이터 사용 (실제 API 구현 시 교체)
	const backtestsLoading = false;
	const backtestsError = null;

	const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
		setTabValue(newValue);
	};

	const handleBack = () => {
		router.push(`/strategies/${strategyId}`);
	};

	if (strategyLoading || backtestsLoading) {
		return (
			<PageContainer
				title="성과 분석"
				breadcrumbs={[
					{ title: "Strategy Center" },
					{ title: "Strategies" },
					{ title: "Performance" },
				]}
			>
				<Box sx={{ display: "flex", justifyContent: "center", py: 4 }}>
					<CircularProgress />
				</Box>
			</PageContainer>
		);
	}

	if (strategyError || backtestsError || !strategy) {
		return (
			<PageContainer
				title="성과 분석"
				breadcrumbs={[
					{ title: "Strategy Center" },
					{ title: "Strategies" },
					{ title: "Performance" },
				]}
			>
				<Alert severity="error">
					데이터를 불러오는 중 오류가 발생했습니다:{" "}
					{(strategyError || (backtestsError as any))?.message}
				</Alert>
			</PageContainer>
		);
	}

	// 가장 최근 백테스트 결과 (모의 데이터)
	const latestBacktest = {
		id: "1",
		total_return: 12.5,
		annual_return: 8.3,
		sharpe_ratio: 1.2,
		max_drawdown: -15.2,
		volatility: 18.5,
		win_rate: 65.0,
		total_trades: 45,
		profit_factor: 1.8,
		start_date: "2023-01-01",
		end_date: "2024-01-01",
	};

	// 거래 내역 (모의 데이터)
	const trades = [
		{
			id: 1,
			date: "2024-01-15",
			type: "BUY",
			symbol: "AAPL",
			quantity: 100,
			price: 150.25,
			pnl: 0,
			status: "FILLED",
		},
		{
			id: 2,
			date: "2024-01-20",
			type: "SELL",
			symbol: "AAPL",
			quantity: 100,
			price: 155.8,
			pnl: 555.0,
			status: "FILLED",
		},
		{
			id: 3,
			date: "2024-02-01",
			type: "BUY",
			symbol: "MSFT",
			quantity: 50,
			price: 380.45,
			pnl: 0,
			status: "FILLED",
		},
		{
			id: 4,
			date: "2024-02-10",
			type: "SELL",
			symbol: "MSFT",
			quantity: 50,
			price: 375.2,
			pnl: -262.5,
			status: "FILLED",
		},
	];

	// 월별 수익률 (모의 데이터)
	const monthlyReturns = [
		{ month: "2024-01", return: 2.5 },
		{ month: "2024-02", return: -1.2 },
		{ month: "2024-03", return: 4.1 },
		{ month: "2024-04", return: 1.8 },
		{ month: "2024-05", return: -0.5 },
		{ month: "2024-06", return: 3.2 },
	];

	return (
		<PageContainer
			title={`${strategy.name} - 성과 분석`}
			breadcrumbs={[
				{ title: "Strategy Center" },
				{ title: "Strategies" },
				{ title: strategy.name },
				{ title: "Performance" },
			]}
			actions={[
				<Button
					key="back"
					variant="outlined"
					startIcon={<ArrowBack />}
					onClick={handleBack}
				>
					전략으로 돌아가기
				</Button>,
			]}
		>
			<Grid container spacing={3}>
				{/* 성과 요약 */}
				<Grid size={{ xs: 12, lg: 4 }}>
					<StrategyPerformanceSummary
						strategyName={strategy.name}
						strategyType={strategy.strategy_type}
						performance={latestBacktest}
						period={selectedPeriod}
					/>

					<Card sx={{ mt: 3 }}>
						<CardContent>
							<Typography variant="h6" sx={{ mb: 2 }}>
								분석 기간
							</Typography>
							<FormControl fullWidth>
								<InputLabel>기간 선택</InputLabel>
								<Select
									value={selectedPeriod}
									label="기간 선택"
									onChange={(e) => setSelectedPeriod(e.target.value)}
								>
									<MenuItem value="1M">1개월</MenuItem>
									<MenuItem value="3M">3개월</MenuItem>
									<MenuItem value="6M">6개월</MenuItem>
									<MenuItem value="1Y">1년</MenuItem>
									<MenuItem value="3Y">3년</MenuItem>
									<MenuItem value="5Y">5년</MenuItem>
									<MenuItem value="ALL">전체</MenuItem>
								</Select>
							</FormControl>
						</CardContent>
					</Card>
				</Grid>

				{/* 상세 분석 */}
				<Grid size={{ xs: 12, lg: 8 }}>
					<Card>
						<CardContent>
							<Box sx={{ borderBottom: 1, borderColor: "divider" }}>
								<Tabs value={tabValue} onChange={handleTabChange}>
									<Tab
										icon={<ShowChart />}
										label="수익률 차트"
										iconPosition="start"
									/>
									<Tab
										icon={<TableChart />}
										label="거래 내역"
										iconPosition="start"
									/>
									<Tab
										icon={<Assessment />}
										label="월별 수익률"
										iconPosition="start"
									/>
								</Tabs>
							</Box>

							<CustomTabPanel value={tabValue} index={0}>
								<Box
									sx={{
										height: 400,
										display: "flex",
										alignItems: "center",
										justifyContent: "center",
									}}
								>
									<Typography variant="h6" color="text.secondary">
										수익률 차트가 여기에 표시됩니다
									</Typography>
								</Box>
							</CustomTabPanel>

							<CustomTabPanel value={tabValue} index={1}>
								<TableContainer component={Paper} variant="outlined">
									<Table>
										<TableHead>
											<TableRow>
												<TableCell>날짜</TableCell>
												<TableCell>유형</TableCell>
												<TableCell>종목</TableCell>
												<TableCell align="right">수량</TableCell>
												<TableCell align="right">가격</TableCell>
												<TableCell align="right">손익</TableCell>
												<TableCell>상태</TableCell>
											</TableRow>
										</TableHead>
										<TableBody>
											{trades.map((trade) => (
												<TableRow key={trade.id}>
													<TableCell>{trade.date}</TableCell>
													<TableCell>
														<Chip
															label={trade.type}
															color={
																trade.type === "BUY" ? "primary" : "secondary"
															}
															size="small"
															icon={
																trade.type === "BUY" ? (
																	<TrendingUp />
																) : (
																	<TrendingDown />
																)
															}
														/>
													</TableCell>
													<TableCell>{trade.symbol}</TableCell>
													<TableCell align="right">
														{trade.quantity.toLocaleString()}
													</TableCell>
													<TableCell align="right">
														${trade.price.toFixed(2)}
													</TableCell>
													<TableCell
														align="right"
														sx={{
															color:
																trade.pnl > 0
																	? "success.main"
																	: trade.pnl < 0
																		? "error.main"
																		: "text.primary",
														}}
													>
														{trade.pnl !== 0 ? `$${trade.pnl.toFixed(2)}` : "-"}
													</TableCell>
													<TableCell>
														<Chip
															label={trade.status}
															color="success"
															size="small"
														/>
													</TableCell>
												</TableRow>
											))}
										</TableBody>
									</Table>
								</TableContainer>
							</CustomTabPanel>

							<CustomTabPanel value={tabValue} index={2}>
								<TableContainer component={Paper} variant="outlined">
									<Table>
										<TableHead>
											<TableRow>
												<TableCell>월</TableCell>
												<TableCell align="right">수익률 (%)</TableCell>
												<TableCell align="center">상태</TableCell>
											</TableRow>
										</TableHead>
										<TableBody>
											{monthlyReturns.map((item) => (
												<TableRow key={item.month}>
													<TableCell>{item.month}</TableCell>
													<TableCell
														align="right"
														sx={{
															color:
																item.return > 0
																	? "success.main"
																	: item.return < 0
																		? "error.main"
																		: "text.primary",
														}}
													>
														{item.return > 0 ? "+" : ""}
														{item.return.toFixed(1)}%
													</TableCell>
													<TableCell align="center">
														{item.return > 0 ? (
															<TrendingUp color="success" />
														) : item.return < 0 ? (
															<TrendingDown color="error" />
														) : (
															"-"
														)}
													</TableCell>
												</TableRow>
											))}
										</TableBody>
									</Table>
								</TableContainer>
							</CustomTabPanel>
						</CardContent>
					</Card>
				</Grid>
			</Grid>
		</PageContainer>
	);
}
