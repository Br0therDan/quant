"use client";

import {
	Autocomplete,
	Box,
	Button,
	Card,
	CardContent,
	FormControl,
	InputLabel,
	MenuItem,
	Select,
	TextField,
	Typography,
} from "@mui/material";
import { DatePicker } from "@mui/x-date-pickers";
import dayjs, { type Dayjs } from "dayjs";

interface MarketDataControlsProps {
	selectedSymbol: string;
	onSymbolChange: (symbol: string) => void;
	availableSymbols: string[];
	startDate: Dayjs | null;
	endDate: Dayjs | null;
	onStartDateChange: (date: Dayjs | null) => void;
	onEndDateChange: (date: Dayjs | null) => void;
	interval: string;
	onIntervalChange: (interval: string) => void;
	onRefresh: () => void;
	isLoading?: boolean;
}

const INTERVALS = [
	{ value: "1d", label: "1일" },
	{ value: "1w", label: "1주" },
	{ value: "1m", label: "1개월" },
];

export default function MarketDataControls({
	selectedSymbol,
	onSymbolChange,
	availableSymbols,
	startDate,
	endDate,
	onStartDateChange,
	onEndDateChange,
	interval,
	onIntervalChange,
	onRefresh,
	isLoading = false,
}: MarketDataControlsProps) {
	return (
		<Card>
			<CardContent>
				<Typography variant="h6" gutterBottom>
					차트 설정
				</Typography>

				<Box display="flex" flexDirection="column" gap={2}>
					{/* 심볼 선택 */}
					<Autocomplete
						value={selectedSymbol}
						onChange={(_, newValue) => {
							if (newValue) {
								onSymbolChange(newValue);
							}
						}}
						options={availableSymbols}
						renderInput={(params) => (
							<TextField
								{...params}
								label="종목 심볼"
								placeholder="심볼을 선택하세요"
							/>
						)}
						disabled={isLoading}
					/>

					{/* 날짜 범위 */}
					<Box display="flex" gap={2}>
						<DatePicker
							label="시작 날짜"
							value={startDate}
							onChange={(value) =>
								onStartDateChange(value ? dayjs(value) : null)
							}
							disabled={isLoading}
							maxDate={dayjs()}
						/>
						<DatePicker
							label="종료 날짜"
							value={endDate}
							onChange={(value) => onEndDateChange(value ? dayjs(value) : null)}
							disabled={isLoading}
							maxDate={dayjs()}
							minDate={startDate || undefined}
						/>
					</Box>

					{/* 간격 선택 */}
					<FormControl>
						<InputLabel>데이터 간격</InputLabel>
						<Select
							value={interval}
							onChange={(e) => onIntervalChange(e.target.value)}
							label="데이터 간격"
							disabled={isLoading}
						>
							{INTERVALS.map((item) => (
								<MenuItem key={item.value} value={item.value}>
									{item.label}
								</MenuItem>
							))}
						</Select>
					</FormControl>

					{/* 새로고침 버튼 */}
					<Button
						variant="contained"
						onClick={onRefresh}
						disabled={isLoading || !selectedSymbol}
						fullWidth
					>
						{isLoading ? "로딩 중..." : "데이터 새로고침"}
					</Button>
				</Box>
			</CardContent>
		</Card>
	);
}
