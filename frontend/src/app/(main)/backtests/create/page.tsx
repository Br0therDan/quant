
"use client";

import {
	AccountBalance,
	ArrowBack,
	Assessment,
	PlayArrow,
	Save,
	Schedule,
	TrendingUp,
} from "@mui/icons-material";
import {
	Alert,
	Box,
	Button,
	Card,
	CardContent,
	Chip,
	Container,
	Divider,
	FormControl,
	Grid,
	InputAdornment,
	InputLabel,
	MenuItem,
	Paper,
	Select,
	Stack,
	Step,
	StepLabel,
	Stepper,
	TextField,
	Typography,
} from "@mui/material";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFns";
import { DatePicker } from "@mui/x-date-pickers/DatePicker";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { useQuery } from "@tanstack/react-query";
import { ko } from "date-fns/locale";
import { useRouter } from "next/navigation";
import { useState } from "react";
import PageContainer from "@/components/layout/PageContainer";


const steps = [
	"기본 설정",
	"전략 & 워치리스트",
	"백테스트 구성",
	"검토 & 실행",
];

export default function CreateBacktestPage() {
	const router = useRouter();
	const [activeStep, setActiveStep] = useState(0);
	const [errors, setErrors] = useState<string[]>([]);

	// Form state
	const [config, setConfig] = useState<BacktestConfig>({
		name: "",
		description: "",
		watchlist_id: "",
		strategy_id: "",
		start_date: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000)
			.toISOString()
			.split("T")[0], // 1 year ago
		end_date: new Date().toISOString().split("T")[0], // today
		initial_capital: 100000,
		commission: 0.001,
		slippage: 0.0005,
		position_sizing: "equal_weight",
		rebalancing_frequency: "monthly",
	});

	// Fetch data for dropdowns
	const { data: strategiesResponse } = useQuery(
		strategiesGetStrategiesOptions({}),
	);
	const { data: watchlistsResponse } = useQuery(
		watchlistsListWatchlistsOptions({}),
	);

	const strategies = strategiesResponse?.strategies || [];
	const watchlists = Array.isArray(watchlistsResponse)
		? watchlistsResponse
		: (watchlistsResponse as any)?.watchlists || [];

	const { createBacktest, executeBacktest } = useBacktestActions();

	const handleInputChange = (field: keyof BacktestConfig, value: any) => {
		setConfig((prev) => ({
			...prev,
			[field]: value,
		}));
		// Clear errors when user starts typing
		if (errors.length > 0) {
			setErrors([]);
		}
	};

	const validateCurrentStep = (): boolean => {
		const stepErrors: string[] = [];

		switch (activeStep) {
			case 0: // 기본 설정
				if (!config.name.trim()) {
					stepErrors.push("백테스트 이름을 입력해주세요");
				}
				break;
			case 1: // 전략 & 워치리스트
				if (!config.strategy_id) {
					stepErrors.push("전략을 선택해주세요");
				}
				if (!config.watchlist_id) {
					stepErrors.push("워치리스트를 선택해주세요");
				}
				break;
			case 2: // 백테스트 구성
				if (!config.start_date) {
					stepErrors.push("시작 날짜를 선택해주세요");
				}
				if (!config.end_date) {
					stepErrors.push("종료 날짜를 선택해주세요");
				}
				if (
					config.start_date &&
					config.end_date &&
					config.start_date >= config.end_date
				) {
					stepErrors.push("종료 날짜는 시작 날짜보다 뒤여야 합니다");
				}
				if (config.initial_capital <= 0) {
					stepErrors.push("초기 자본은 0보다 커야 합니다");
				}
				break;
			case 3: // 검토 & 실행
				stepErrors.push(...backtestUtils.validateConfig(config));
				break;
		}

		setErrors(stepErrors);
		return stepErrors.length === 0;
	};

	const handleNext = () => {
		if (validateCurrentStep()) {
			setActiveStep((prev) => prev + 1);
		}
	};

	const handleBack = () => {
		setActiveStep((prev) => prev - 1);
		setErrors([]);
	};

	const handleCreateAndRun = async () => {
		if (validateCurrentStep()) {
			try {
				// Create the backtest
				await createBacktest(config);
				// Navigate to backtest monitoring page
				router.push("/backtests");
			} catch (error) {
				console.error("Failed to create backtest:", error);
				setErrors(["백테스트 생성에 실패했습니다"]);
			}
		}
	};

	const handleSaveOnly = async () => {
		if (validateCurrentStep()) {
			try {
				await createBacktest(config);
				router.push("/backtests");
			} catch (error) {
				console.error("Failed to save backtest:", error);
				setErrors(["백테스트 저장에 실패했습니다"]);
			}
		}
	};

	const getSelectedStrategy = () => {
		return strategies.find((s: any) => s.id === config.strategy_id);
	};

	const getSelectedWatchlist = () => {
		if (!Array.isArray(watchlists)) return null;
		return watchlists.find((w: any) => w.id === config.watchlist_id);
	};

	return (
		<PageContainer
			title="새 백테스트 만들기"
			breadcrumbs={[{ title: "백테스트" }, { title: "새 백테스트" }]}
		>
			<Container maxWidth="lg">
				<Box sx={{ mb: 4 }}>
					<Button
						startIcon={<ArrowBack />}
						onClick={() => router.push("/backtests")}
						sx={{ mb: 2 }}
					>
						백테스트 목록으로
					</Button>
				</Box>

				{/* Stepper */}
				<Paper sx={{ p: 3, mb: 3 }}>
					<Stepper activeStep={activeStep} alternativeLabel>
						{steps.map((label) => (
							<Step key={label}>
								<StepLabel>{label}</StepLabel>
							</Step>
						))}
					</Stepper>
				</Paper>

				{/* Error Messages */}
				{errors.length > 0 && (
					<Alert severity="error" sx={{ mb: 3 }}>
						<Box component="ul" sx={{ m: 0, pl: 2.5 }}>
							{errors.map((error, index) => (
								<Box component="li" key={index}>
									{error}
								</Box>
							))}
						</Box>
					</Alert>
				)}

				{/* Step Content */}
				<Paper sx={{ p: 4 }}>
					{/* Step 0: 기본 설정 */}
					{activeStep === 0 && (
						<Box>
							<Typography variant="h6" gutterBottom>
								기본 설정
							</Typography>
							<Typography
								variant="body2"
								color="text.secondary"
								gutterBottom
								sx={{ mb: 3 }}
							>
								백테스트의 기본 정보를 입력해주세요
							</Typography>

							<Grid container spacing={3}>
								<Grid size={12}>
									<TextField
										fullWidth
										label="백테스트 이름"
										placeholder="예: 모멘텀 전략 백테스트 2024"
										value={config.name}
										onChange={(e) => handleInputChange("name", e.target.value)}
										required
									/>
								</Grid>
								<Grid size={12}>
									<TextField
										fullWidth
										label="설명 (선택사항)"
										placeholder="이 백테스트에 대한 설명을 입력하세요"
										value={config.description}
										onChange={(e) =>
											handleInputChange("description", e.target.value)
										}
										multiline
										rows={3}
									/>
								</Grid>
							</Grid>
						</Box>
					)}

					{/* Step 1: 전략 & 워치리스트 */}
					{activeStep === 1 && (
						<Box>
							<Typography variant="h6" gutterBottom>
								전략 & 워치리스트 선택
							</Typography>
							<Typography
								variant="body2"
								color="text.secondary"
								gutterBottom
								sx={{ mb: 3 }}
							>
								백테스트에 사용할 전략과 워치리스트를 선택해주세요
							</Typography>

							<Grid container spacing={3}>
								<Grid size={12}>
									<FormControl fullWidth required>
										<InputLabel>전략</InputLabel>
										<Select
											value={config.strategy_id}
											label="전략"
											onChange={(e) =>
												handleInputChange("strategy_id", e.target.value)
											}
										>
											{strategies.map((strategy: any) => (
												<MenuItem key={strategy.id} value={strategy.id}>
													<Box>
														<Typography variant="body1">
															{strategy.name}
														</Typography>
														<Typography
															variant="caption"
															color="text.secondary"
														>
															{strategy.description}
														</Typography>
													</Box>
												</MenuItem>
											))}
										</Select>
									</FormControl>
									{getSelectedStrategy() && (
										<Card variant="outlined" sx={{ mt: 2 }}>
											<CardContent>
												<Typography variant="subtitle2" gutterBottom>
													선택된 전략
												</Typography>
												<Typography variant="body1" gutterBottom>
													{getSelectedStrategy()?.name}
												</Typography>
												<Typography variant="body2" color="text.secondary">
													{getSelectedStrategy()?.description}
												</Typography>
											</CardContent>
										</Card>
									)}
								</Grid>

								<Grid size={12}>
									<FormControl fullWidth required>
										<InputLabel>워치리스트</InputLabel>
										<Select
											value={config.watchlist_id}
											label="워치리스트"
											onChange={(e) =>
												handleInputChange("watchlist_id", e.target.value)
											}
										>
											{Array.isArray(watchlists) &&
												watchlists.map((watchlist: any) => (
													<MenuItem key={watchlist.id} value={watchlist.id}>
														<Box>
															<Typography variant="body1">
																{watchlist.name}
															</Typography>
															<Typography
																variant="caption"
																color="text.secondary"
															>
																{watchlist.symbols?.length || 0}개 종목
															</Typography>
														</Box>
													</MenuItem>
												))}
										</Select>
									</FormControl>
									{getSelectedWatchlist() && (
										<Card variant="outlined" sx={{ mt: 2 }}>
											<CardContent>
												<Typography variant="subtitle2" gutterBottom>
													선택된 워치리스트
												</Typography>
												<Typography variant="body1" gutterBottom>
													{getSelectedWatchlist()?.name}
												</Typography>
												<Stack
													direction="row"
													spacing={1}
													flexWrap="wrap"
													sx={{ mt: 1 }}
												>
													{getSelectedWatchlist()
														?.symbols?.slice(0, 5)
														?.map((symbol: string) => (
															<Chip key={symbol} label={symbol} size="small" />
														))}
													{(getSelectedWatchlist()?.symbols?.length || 0) >
														5 && (
														<Chip
															label={`+${
																(getSelectedWatchlist()?.symbols?.length || 0) -
																5
															}개 더`}
															size="small"
															variant="outlined"
														/>
													)}
												</Stack>
											</CardContent>
										</Card>
									)}
								</Grid>
							</Grid>
						</Box>
					)}

					{/* Step 2: 백테스트 구성 */}
					{activeStep === 2 && (
						<Box>
							<Typography variant="h6" gutterBottom>
								백테스트 구성
							</Typography>
							<Typography
								variant="body2"
								color="text.secondary"
								gutterBottom
								sx={{ mb: 3 }}
							>
								백테스트 실행을 위한 세부 설정을 입력해주세요
							</Typography>

							<Grid container spacing={3}>
								<Grid size={12}>
									<LocalizationProvider
										dateAdapter={AdapterDateFns}
										adapterLocale={ko}
									>
										<DatePicker
											label="시작 날짜"
											value={new Date(config.start_date)}
											onChange={(date) =>
												handleInputChange(
													"start_date",
													date?.toISOString().split("T")[0] || "",
												)
											}
											slotProps={{ textField: { fullWidth: true } }}
										/>
									</LocalizationProvider>
								</Grid>
								<Grid size={12}>
									<LocalizationProvider
										dateAdapter={AdapterDateFns}
										adapterLocale={ko}
									>
										<DatePicker
											label="종료 날짜"
											value={new Date(config.end_date)}
											onChange={(date) =>
												handleInputChange(
													"end_date",
													date?.toISOString().split("T")[0] || "",
												)
											}
											slotProps={{ textField: { fullWidth: true } }}
										/>
									</LocalizationProvider>
								</Grid>
								<Grid size={12}>
									<TextField
										fullWidth
										label="초기 자본"
										type="number"
										value={config.initial_capital}
										onChange={(e) =>
											handleInputChange(
												"initial_capital",
												Number(e.target.value),
											)
										}
										InputProps={{
											startAdornment: (
												<InputAdornment position="start">$</InputAdornment>
											),
										}}
									/>
								</Grid>
								<Grid size={12}>
									<TextField
										fullWidth
										label="수수료 (%)"
										type="number"
										value={config.commission * 100}
										onChange={(e) =>
											handleInputChange(
												"commission",
												Number(e.target.value) / 100,
											)
										}
										InputProps={{
											startAdornment: (
												<InputAdornment position="start">%</InputAdornment>
											),
										}}
										inputProps={{ step: 0.01, min: 0, max: 10 }}
									/>
								</Grid>
								<Grid size={12}>
									<TextField
										fullWidth
										label="슬리피지 (%)"
										type="number"
										value={config.slippage * 100}
										onChange={(e) =>
											handleInputChange(
												"slippage",
												Number(e.target.value) / 100,
											)
										}
										InputProps={{
											startAdornment: (
												<InputAdornment position="start">%</InputAdornment>
											),
										}}
										inputProps={{ step: 0.01, min: 0, max: 5 }}
									/>
								</Grid>
								<Grid size={12}>
									<FormControl fullWidth>
										<InputLabel>포지션 크기 조정</InputLabel>
										<Select
											value={config.position_sizing}
											label="포지션 크기 조정"
											onChange={(e) =>
												handleInputChange("position_sizing", e.target.value)
											}
										>
											<MenuItem value="equal_weight">동일 가중</MenuItem>
											<MenuItem value="market_cap">시가총액 가중</MenuItem>
											<MenuItem value="volatility_adjusted">
												변동성 조정
											</MenuItem>
										</Select>
									</FormControl>
								</Grid>
								<Grid size={12}>
									<FormControl fullWidth>
										<InputLabel>리밸런싱 빈도</InputLabel>
										<Select
											value={config.rebalancing_frequency}
											label="리밸런싱 빈도"
											onChange={(e) =>
												handleInputChange(
													"rebalancing_frequency",
													e.target.value,
												)
											}
										>
											<MenuItem value="daily">매일</MenuItem>
											<MenuItem value="weekly">매주</MenuItem>
											<MenuItem value="monthly">매월</MenuItem>
											<MenuItem value="quarterly">분기별</MenuItem>
										</Select>
									</FormControl>
								</Grid>
							</Grid>
						</Box>
					)}

					{/* Step 3: 검토 & 실행 */}
					{activeStep === 3 && (
						<Box>
							<Typography variant="h6" gutterBottom>
								백테스트 검토
							</Typography>
							<Typography
								variant="body2"
								color="text.secondary"
								gutterBottom
								sx={{ mb: 3 }}
							>
								설정을 확인하고 백테스트를 실행하세요
							</Typography>

							<Grid container spacing={3}>
								<Grid size={12}>
									<Card variant="outlined">
										<CardContent>
											<Typography
												variant="subtitle1"
												gutterBottom
												sx={{ display: "flex", alignItems: "center" }}
											>
												<TrendingUp sx={{ mr: 1 }} />
												기본 정보
											</Typography>
											<Divider sx={{ mb: 2 }} />
											<Box sx={{ mb: 1 }}>
												<Typography variant="body2" color="text.secondary">
													이름
												</Typography>
												<Typography variant="body1">{config.name}</Typography>
											</Box>
											{config.description && (
												<Box sx={{ mb: 1 }}>
													<Typography variant="body2" color="text.secondary">
														설명
													</Typography>
													<Typography variant="body1">
														{config.description}
													</Typography>
												</Box>
											)}
										</CardContent>
									</Card>
								</Grid>

								<Grid size={12}>
									<Card variant="outlined">
										<CardContent>
											<Typography
												variant="subtitle1"
												gutterBottom
												sx={{ display: "flex", alignItems: "center" }}
											>
												<Assessment sx={{ mr: 1 }} />
												전략 & 워치리스트
											</Typography>
											<Divider sx={{ mb: 2 }} />
											<Box sx={{ mb: 1 }}>
												<Typography variant="body2" color="text.secondary">
													전략
												</Typography>
												<Typography variant="body1">
													{getSelectedStrategy()?.name}
												</Typography>
											</Box>
											<Box sx={{ mb: 1 }}>
												<Typography variant="body2" color="text.secondary">
													워치리스트
												</Typography>
												<Typography variant="body1">
													{getSelectedWatchlist()?.name}
												</Typography>
											</Box>
										</CardContent>
									</Card>
								</Grid>

								<Grid size={12}>
									<Card variant="outlined">
										<CardContent>
											<Typography
												variant="subtitle1"
												gutterBottom
												sx={{ display: "flex", alignItems: "center" }}
											>
												<Schedule sx={{ mr: 1 }} />
												기간 설정
											</Typography>
											<Divider sx={{ mb: 2 }} />
											<Box sx={{ mb: 1 }}>
												<Typography variant="body2" color="text.secondary">
													시작 날짜
												</Typography>
												<Typography variant="body1">
													{new Date(config.start_date).toLocaleDateString(
														"ko-KR",
													)}
												</Typography>
											</Box>
											<Box sx={{ mb: 1 }}>
												<Typography variant="body2" color="text.secondary">
													종료 날짜
												</Typography>
												<Typography variant="body1">
													{new Date(config.end_date).toLocaleDateString(
														"ko-KR",
													)}
												</Typography>
											</Box>
											<Box sx={{ mb: 1 }}>
												<Typography variant="body2" color="text.secondary">
													백테스트 기간
												</Typography>
												<Typography variant="body1">
													{Math.ceil(
														(new Date(config.end_date).getTime() -
															new Date(config.start_date).getTime()) /
															(1000 * 60 * 60 * 24),
													)}
													일
												</Typography>
											</Box>
										</CardContent>
									</Card>
								</Grid>

								<Grid size={12}>
									<Card variant="outlined">
										<CardContent>
											<Typography
												variant="subtitle1"
												gutterBottom
												sx={{ display: "flex", alignItems: "center" }}
											>
												<AccountBalance sx={{ mr: 1 }} />
												거래 설정
											</Typography>
											<Divider sx={{ mb: 2 }} />
											<Box sx={{ mb: 1 }}>
												<Typography variant="body2" color="text.secondary">
													초기 자본
												</Typography>
												<Typography variant="body1">
													{backtestUtils.formatCurrency(config.initial_capital)}
												</Typography>
											</Box>
											<Box sx={{ mb: 1 }}>
												<Typography variant="body2" color="text.secondary">
													수수료
												</Typography>
												<Typography variant="body1">
													{(config.commission * 100).toFixed(3)}%
												</Typography>
											</Box>
											<Box sx={{ mb: 1 }}>
												<Typography variant="body2" color="text.secondary">
													슬리피지
												</Typography>
												<Typography variant="body1">
													{(config.slippage * 100).toFixed(3)}%
												</Typography>
											</Box>
											<Box sx={{ mb: 1 }}>
												<Typography variant="body2" color="text.secondary">
													리밸런싱
												</Typography>
												<Typography variant="body1">
													{config.rebalancing_frequency === "daily"
														? "매일"
														: config.rebalancing_frequency === "weekly"
															? "매주"
															: config.rebalancing_frequency === "monthly"
																? "매월"
																: "분기별"}
												</Typography>
											</Box>
										</CardContent>
									</Card>
								</Grid>
							</Grid>
						</Box>
					)}
				</Paper>

				{/* Navigation Buttons */}
				<Box sx={{ display: "flex", justifyContent: "space-between", mt: 3 }}>
					<Button disabled={activeStep === 0} onClick={handleBack}>
						이전
					</Button>

					<Box sx={{ display: "flex", gap: 2 }}>
						{activeStep === steps.length - 1 ? (
							<>
								<Button
									variant="outlined"
									startIcon={<Save />}
									onClick={handleSaveOnly}
								>
									저장만 하기
								</Button>
								<Button
									variant="contained"
									startIcon={<PlayArrow />}
									onClick={handleCreateAndRun}
								>
									생성 후 실행
								</Button>
							</>
						) : (
							<Button variant="contained" onClick={handleNext}>
								다음
							</Button>
						)}
					</Box>
				</Box>
			</Container>
		</PageContainer>
	);
}
