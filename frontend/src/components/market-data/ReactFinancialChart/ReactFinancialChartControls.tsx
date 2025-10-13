"use client";

import {
	Add as AddIcon,
	CalendarMonth as CalendarIcon,
	CandlestickChart as CandlestickIcon,
	ShowChart as LineIcon,
	Timeline as TimelineIcon,
} from "@mui/icons-material";
import {
	Accordion,
	AccordionDetails,
	AccordionSummary,
	Box,
	Button,
	ButtonGroup,
	Checkbox,
	Chip,
	FormControl,
	FormControlLabel,
	FormGroup,
	FormLabel,
	IconButton,
	InputLabel,
	MenuItem,
	Select,
	Stack,
	Switch,
	TextField,
	Tooltip,
	Typography,
} from "@mui/material";
import { DatePicker } from "@mui/x-date-pickers";
import dayjs, { type Dayjs } from "dayjs";
import React from "react";
import type { ChartType, IndicatorConfig } from "./ReactFinancialChart";

interface ReactFinancialChartControlsProps {
	startDate: Dayjs | null;
	endDate: Dayjs | null;
	onStartDateChange: (date: Dayjs | null) => void;
	onEndDateChange: (date: Dayjs | null) => void;
	interval: string;
	onIntervalChange: (interval: string) => void;
	chartType: ChartType["type"];
	onChartTypeChange: (type: ChartType["type"]) => void;
	indicators: IndicatorConfig;
	onIndicatorsChange: (indicators: IndicatorConfig) => void;
	adjusted?: boolean;
	onAdjustedChange?: (adjusted: boolean) => void;
	isLoading?: boolean;
}

// 레인지(기간) 옵션
const RANGES = [
	{ label: "1D", value: "1d", days: 1 },
	{ label: "5D", value: "5d", days: 5 },
	{ label: "1M", value: "1m", days: 30 },
	{ label: "3M", value: "3m", days: 90 },
	{ label: "6M", value: "6m", days: 180 },
	{ label: "YTD", value: "ytd", days: null }, // Year to date
	{ label: "1Y", value: "1y", days: 365 },
	{ label: "5Y", value: "5y", days: 1825 },
	{ label: "전체", value: "all", days: null },
];

// 인터벌(봉 종류) 옵션
const INTERVALS = {
	intraday: [
		{ label: "1분", value: "1min" },
		{ label: "5분", value: "5min" },
		{ label: "15분", value: "15min" },
		{ label: "30분", value: "30min" },
		{ label: "60분", value: "60min" },
	],
	daily: [
		{ label: "일봉", value: "daily" },
		{ label: "주봉", value: "weekly" },
		{ label: "월봉", value: "monthly" },
	],
};

// 기본 이동평균 기간
const DEFAULT_MA_PERIODS = [20, 50, 200];

// 차트 타입 옵션
const CHART_TYPES: Array<{
	icon: any;
	label: string;
	value: ChartType["type"];
}> = [
	{ icon: CandlestickIcon, label: "캔들스틱", value: "candlestick" },
	{ icon: TimelineIcon, label: "OHLC", value: "ohlc" },
	{ icon: LineIcon, label: "라인", value: "line" },
	{ icon: LineIcon, label: "영역", value: "area" },
	{ icon: TimelineIcon, label: "스캐터", value: "scatter" },
	{ icon: CandlestickIcon, label: "하이켄아시", value: "heikinAshi" },
	{ icon: CandlestickIcon, label: "렌코", value: "renko" },
	{ icon: CandlestickIcon, label: "카기", value: "kagi" },
	{ icon: CandlestickIcon, label: "P&F", value: "pointAndFigure" },
];

export default function ReactFinancialChartControls({
	startDate,
	endDate,
	onStartDateChange,
	onEndDateChange,
	interval,
	onIntervalChange,
	chartType,
	onChartTypeChange,
	indicators,
	onIndicatorsChange,
	adjusted = true,
	onAdjustedChange,
	isLoading = false,
}: ReactFinancialChartControlsProps) {
	const [selectedRange, setSelectedRange] = React.useState("1m");
	const [showCustomDate, setShowCustomDate] = React.useState(false);
	const [expanded, setExpanded] = React.useState<string | false>("chart");

	// 레인지 변경 핸들러
	const handleRangeChange = (rangeValue: string) => {
		const range = RANGES.find((r) => r.value === rangeValue);
		if (!range) return;

		const end = dayjs();
		let start: Dayjs;

		if (rangeValue === "ytd") {
			start = dayjs().startOf("year");
		} else if (rangeValue === "all") {
			start = end.subtract(20, "year");
		} else if (range.days) {
			start = end.subtract(range.days, "day");
		} else {
			start = end.subtract(30, "day");
		}

		setSelectedRange(rangeValue);
		setShowCustomDate(false);
		onStartDateChange(start);
		onEndDateChange(end);

		// 레인지에 따라 적절한 인터벌 자동 설정
		if (range.days && range.days <= 5) {
			if (!["1min", "5min", "15min", "30min", "60min"].includes(interval)) {
				onIntervalChange("5min");
			}
		} else {
			if (!["daily", "weekly", "monthly"].includes(interval)) {
				onIntervalChange("daily");
			}
		}
	};

	// 커스텀 날짜 표시 토글
	const handleCustomDateToggle = () => {
		setShowCustomDate(!showCustomDate);
		if (!showCustomDate) {
			setSelectedRange("custom");
		}
	};

	// 현재 인터벌이 분봉인지 확인
	const isIntradayInterval = [
		"1min",
		"5min",
		"15min",
		"30min",
		"60min",
	].includes(interval);

	// 사용 가능한 인터벌 목록
	const availableIntervals = isIntradayInterval
		? INTERVALS.intraday
		: INTERVALS.daily;

	// 아코디언 핸들러
	const handleAccordionChange =
		(panel: string) => (_event: React.SyntheticEvent, isExpanded: boolean) => {
			setExpanded(isExpanded ? panel : false);
		};

	// 이동평균 추가/삭제
	const handleAddMA = (type: "ema" | "sma" | "wma" | "tma", period: number) => {
		const current = indicators[type] || [];
		if (!current.includes(period)) {
			onIndicatorsChange({
				...indicators,
				[type]: [...current, period].sort((a, b) => a - b),
			});
		}
	};

	const handleRemoveMA = (
		type: "ema" | "sma" | "wma" | "tma",
		period: number,
	) => {
		const current = indicators[type] || [];
		onIndicatorsChange({
			...indicators,
			[type]: current.filter((p) => p !== period),
		});
	};

	return (
		<Box
			sx={{
				p: 2,
				borderTop: 1,
				borderColor: "divider",
				display: "flex",
				flexDirection: "column",
				gap: 2,
			}}
		>
			{/* 첫 번째 줄: 레인지 선택 */}
			<Box display="flex" alignItems="center" gap={1} flexWrap="wrap">
				<ButtonGroup size="small" variant="outlined">
					{RANGES.map((range) => (
						<Button
							key={range.value}
							variant={selectedRange === range.value ? "contained" : "outlined"}
							onClick={() => handleRangeChange(range.value)}
							sx={{ minWidth: 40, fontSize: "0.75rem" }}
						>
							{range.label}
						</Button>
					))}
				</ButtonGroup>

				<Tooltip title="커스텀 기간 설정">
					<Button
						size="small"
						variant={showCustomDate ? "contained" : "outlined"}
						onClick={handleCustomDateToggle}
						sx={{ minWidth: 40 }}
					>
						<CalendarIcon sx={{ fontSize: 18 }} />
					</Button>
				</Tooltip>

				{isLoading && (
					<Chip
						label="로딩 중..."
						size="small"
						color="primary"
						variant="outlined"
					/>
				)}
			</Box>

			{/* 커스텀 날짜 선택 */}
			{showCustomDate && (
				<Box display="flex" alignItems="center" gap={1}>
					<DatePicker
						label="시작일"
						value={startDate}
						onChange={(value) => onStartDateChange(value ? dayjs(value) : null)}
						slotProps={{
							textField: {
								size: "small",
								sx: { width: 150 },
							},
						}}
					/>
					<DatePicker
						label="종료일"
						value={endDate}
						onChange={(value) => onEndDateChange(value ? dayjs(value) : null)}
						slotProps={{
							textField: {
								size: "small",
								sx: { width: 150 },
							},
						}}
					/>
				</Box>
			)}

			{/* 두 번째 줄: 인터벌 + Adjusted Toggle */}
			<Box
				display="flex"
				alignItems="center"
				justifyContent="space-between"
				flexWrap="wrap"
				gap={2}
			>
				<ButtonGroup size="small" variant="outlined">
					{availableIntervals.map((intv) => (
						<Button
							key={intv.value}
							variant={interval === intv.value ? "contained" : "outlined"}
							onClick={() => onIntervalChange(intv.value)}
							sx={{ minWidth: 50 }}
						>
							{intv.label}
						</Button>
					))}
				</ButtonGroup>

				{onAdjustedChange && (
					<FormControlLabel
						control={
							<Switch
								checked={adjusted}
								onChange={(e) => onAdjustedChange(e.target.checked)}
								size="small"
							/>
						}
						label="Adjusted"
						sx={{
							m: 0,
							"& .MuiFormControlLabel-label": {
								fontSize: "0.875rem",
								fontWeight: adjusted ? 600 : 400,
							},
						}}
					/>
				)}
			</Box>

			{/* 차트 설정 아코디언 */}
			<Accordion
				expanded={expanded === "chart"}
				onChange={handleAccordionChange("chart")}
			>
				<AccordionSummary expandIcon={<ExpandMoreIcon />}>
					<Typography variant="subtitle2">차트 타입</Typography>
				</AccordionSummary>
				<AccordionDetails>
					<FormControl fullWidth size="small">
						<InputLabel>차트 스타일</InputLabel>
						<Select
							value={chartType}
							label="차트 스타일"
							onChange={(e) =>
								onChartTypeChange(e.target.value as ChartType["type"])
							}
						>
							{CHART_TYPES.map((type) => (
								<MenuItem key={type.value} value={type.value}>
									<Box display="flex" alignItems="center" gap={1}>
										<type.icon sx={{ fontSize: 20 }} />
										{type.label}
									</Box>
								</MenuItem>
							))}
						</Select>
					</FormControl>
				</AccordionDetails>
			</Accordion>

			{/* 이동평균선 아코디언 */}
			<Accordion
				expanded={expanded === "ma"}
				onChange={handleAccordionChange("ma")}
			>
				<AccordionSummary expandIcon={<ExpandMoreIcon />}>
					<Typography variant="subtitle2">이동평균선</Typography>
				</AccordionSummary>
				<AccordionDetails>
					<Stack spacing={2}>
						{/* EMA */}
						<MAControl
							label="EMA (지수이동평균)"
							type="ema"
							periods={indicators.ema || []}
							onAdd={handleAddMA}
							onRemove={handleRemoveMA}
						/>

						{/* SMA */}
						<MAControl
							label="SMA (단순이동평균)"
							type="sma"
							periods={indicators.sma || []}
							onAdd={handleAddMA}
							onRemove={handleRemoveMA}
						/>

						{/* WMA */}
						<MAControl
							label="WMA (가중이동평균)"
							type="wma"
							periods={indicators.wma || []}
							onAdd={handleAddMA}
							onRemove={handleRemoveMA}
						/>

						{/* TMA */}
						<MAControl
							label="TMA (삼각이동평균)"
							type="tma"
							periods={indicators.tma || []}
							onAdd={handleAddMA}
							onRemove={handleRemoveMA}
						/>
					</Stack>
				</AccordionDetails>
			</Accordion>

			{/* 변동성 지표 아코디언 */}
			<Accordion
				expanded={expanded === "volatility"}
				onChange={handleAccordionChange("volatility")}
			>
				<AccordionSummary expandIcon={<ExpandMoreIcon />}>
					<Typography variant="subtitle2">변동성 지표</Typography>
				</AccordionSummary>
				<AccordionDetails>
					<FormGroup>
						<FormControlLabel
							control={
								<Checkbox
									checked={indicators.bollingerBand || false}
									onChange={(e) =>
										onIndicatorsChange({
											...indicators,
											bollingerBand: e.target.checked,
										})
									}
								/>
							}
							label="Bollinger Bands"
						/>
						<FormControlLabel
							control={
								<Checkbox
									checked={indicators.atr || false}
									onChange={(e) =>
										onIndicatorsChange({
											...indicators,
											atr: e.target.checked,
										})
									}
								/>
							}
							label="ATR (Average True Range)"
						/>
					</FormGroup>
				</AccordionDetails>
			</Accordion>

			{/* 추세 지표 아코디언 */}
			<Accordion
				expanded={expanded === "trend"}
				onChange={handleAccordionChange("trend")}
			>
				<AccordionSummary expandIcon={<ExpandMoreIcon />}>
					<Typography variant="subtitle2">추세 지표</Typography>
				</AccordionSummary>
				<AccordionDetails>
					<FormGroup>
						<FormControlLabel
							control={
								<Checkbox
									checked={indicators.sar || false}
									onChange={(e) =>
										onIndicatorsChange({
											...indicators,
											sar: e.target.checked,
										})
									}
								/>
							}
							label="SAR (Parabolic SAR)"
						/>
						<FormControlLabel
							control={
								<Checkbox
									checked={indicators.macd || false}
									onChange={(e) =>
										onIndicatorsChange({
											...indicators,
											macd: e.target.checked,
										})
									}
								/>
							}
							label="MACD"
						/>
					</FormGroup>
				</AccordionDetails>
			</Accordion>

			{/* 모멘텀 지표 아코디언 */}
			<Accordion
				expanded={expanded === "momentum"}
				onChange={handleAccordionChange("momentum")}
			>
				<AccordionSummary expandIcon={<ExpandMoreIcon />}>
					<Typography variant="subtitle2">모멘텀 지표</Typography>
				</AccordionSummary>
				<AccordionDetails>
					<FormGroup>
						<FormControlLabel
							control={
								<Checkbox
									checked={indicators.rsi || false}
									onChange={(e) =>
										onIndicatorsChange({
											...indicators,
											rsi: e.target.checked,
										})
									}
								/>
							}
							label="RSI (Relative Strength Index)"
						/>

						<FormControl fullWidth size="small" sx={{ mt: 1 }}>
							<InputLabel>Stochastic</InputLabel>
							<Select
								value={indicators.stochastic || ""}
								label="Stochastic"
								onChange={(e) =>
									onIndicatorsChange({
										...indicators,
										stochastic: e.target.value
											? (e.target.value as "fast" | "slow" | "full")
											: null,
									})
								}
							>
								<MenuItem value="">없음</MenuItem>
								<MenuItem value="fast">Fast Stochastic</MenuItem>
								<MenuItem value="slow">Slow Stochastic</MenuItem>
								<MenuItem value="full">Full Stochastic</MenuItem>
							</Select>
						</FormControl>

						<FormControlLabel
							control={
								<Checkbox
									checked={indicators.forceIndex || false}
									onChange={(e) =>
										onIndicatorsChange({
											...indicators,
											forceIndex: e.target.checked,
										})
									}
								/>
							}
							label="Force Index"
							sx={{ mt: 1 }}
						/>
					</FormGroup>
				</AccordionDetails>
			</Accordion>

			{/* Elder 지표 아코디언 */}
			<Accordion
				expanded={expanded === "elder"}
				onChange={handleAccordionChange("elder")}
			>
				<AccordionSummary expandIcon={<ExpandMoreIcon />}>
					<Typography variant="subtitle2">Elder 시스템</Typography>
				</AccordionSummary>
				<AccordionDetails>
					<FormGroup>
						<FormControlLabel
							control={
								<Checkbox
									checked={indicators.elderRay || false}
									onChange={(e) =>
										onIndicatorsChange({
											...indicators,
											elderRay: e.target.checked,
										})
									}
								/>
							}
							label="Elder Ray"
						/>
						<FormControlLabel
							control={
								<Checkbox
									checked={indicators.elderImpulse || false}
									onChange={(e) =>
										onIndicatorsChange({
											...indicators,
											elderImpulse: e.target.checked,
										})
									}
								/>
							}
							label="Elder Impulse"
						/>
					</FormGroup>
				</AccordionDetails>
			</Accordion>
		</Box>
	);
}

// 이동평균 컨트롤 컴포넌트
interface MAControlProps {
	label: string;
	type: "ema" | "sma" | "wma" | "tma";
	periods: number[];
	onAdd: (type: "ema" | "sma" | "wma" | "tma", period: number) => void;
	onRemove: (type: "ema" | "sma" | "wma" | "tma", period: number) => void;
}

function MAControl({ label, type, periods, onAdd, onRemove }: MAControlProps) {
	const [customPeriod, setCustomPeriod] = React.useState("");

	const handleAddCustom = () => {
		const period = Number.parseInt(customPeriod);
		if (period > 0 && !periods.includes(period)) {
			onAdd(type, period);
			setCustomPeriod("");
		}
	};

	return (
		<Box>
			<FormLabel component="legend" sx={{ mb: 1, fontSize: "0.875rem" }}>
				{label}
			</FormLabel>
			<Box display="flex" flexWrap="wrap" gap={1} mb={1}>
				{DEFAULT_MA_PERIODS.map((period) => (
					<Chip
						key={period}
						label={period}
						size="small"
						color={periods.includes(period) ? "primary" : "default"}
						onClick={() =>
							periods.includes(period)
								? onRemove(type, period)
								: onAdd(type, period)
						}
						variant={periods.includes(period) ? "filled" : "outlined"}
					/>
				))}
			</Box>
			{periods
				.filter((p) => !DEFAULT_MA_PERIODS.includes(p))
				.map((period) => (
					<Chip
						key={period}
						label={period}
						size="small"
						color="primary"
						onDelete={() => onRemove(type, period)}
						sx={{ mr: 0.5, mb: 0.5 }}
					/>
				))}
			<Box display="flex" gap={1} mt={1}>
				<TextField
					size="small"
					type="number"
					placeholder="기간"
					value={customPeriod}
					onChange={(e) => setCustomPeriod(e.target.value)}
					sx={{ width: 100 }}
				/>
				<IconButton size="small" color="primary" onClick={handleAddCustom}>
					<AddIcon />
				</IconButton>
			</Box>
		</Box>
	);
}

// ExpandMore 아이콘
function ExpandMoreIcon() {
	return (
		<svg width="24" height="24" viewBox="0 0 24 24">
			<path d="M16.59 8.59L12 13.17 7.41 8.59 6 10l6 6 6-6z" />
		</svg>
	);
}
