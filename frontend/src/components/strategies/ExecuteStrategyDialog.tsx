"use client";

import WatchListSymbolSelector from "@/components/strategies/WatchListSymbolSelector";
import {
	Box,
	Button,
	Dialog,
	DialogActions,
	DialogContent,
	DialogTitle,
	FormControl,
	FormHelperText,
	InputLabel,
	MenuItem,
	Select,
	Stack,
	TextField,
	Typography,
} from "@mui/material";
import { useState } from "react";

interface ExecuteStrategyDialogProps {
	open: boolean;
	onClose: () => void;
	strategy: any;
	onExecute: (params: {
		symbol: string;
		startDate: string;
		endDate: string;
	}) => void;
	isExecuting?: boolean;
}

export default function ExecuteStrategyDialog({
	open,
	onClose,
	strategy,
	onExecute,
	isExecuting = false,
}: ExecuteStrategyDialogProps) {
	// 기본값: 최근 1년
	const defaultEndDate = new Date().toISOString().split("T")[0];
	const defaultStartDate = new Date(Date.now() - 365 * 24 * 60 * 60 * 1000)
		.toISOString()
		.split("T")[0];

	const [symbol, setSymbol] = useState("");
	const [startDate, setStartDate] = useState(defaultStartDate);
	const [endDate, setEndDate] = useState(defaultEndDate);
	const [periodPreset, setPeriodPreset] = useState("1y");

	const handlePeriodChange = (preset: string) => {
		setPeriodPreset(preset);
		const end = new Date();
		const endDateStr = end.toISOString().split("T")[0];
		setEndDate(endDateStr);

		let start: Date;
		switch (preset) {
			case "1m":
				start = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
				break;
			case "3m":
				start = new Date(Date.now() - 90 * 24 * 60 * 60 * 1000);
				break;
			case "6m":
				start = new Date(Date.now() - 180 * 24 * 60 * 60 * 1000);
				break;
			case "1y":
				start = new Date(Date.now() - 365 * 24 * 60 * 60 * 1000);
				break;
			case "3y":
				start = new Date(Date.now() - 3 * 365 * 24 * 60 * 60 * 1000);
				break;
			case "5y":
				start = new Date(Date.now() - 5 * 365 * 24 * 60 * 60 * 1000);
				break;
			case "custom":
				return;
			default:
				start = new Date(Date.now() - 365 * 24 * 60 * 60 * 1000);
		}
		setStartDate(start.toISOString().split("T")[0]);
	};

	const handleExecute = () => {
		if (!symbol) {
			return;
		}

		onExecute({
			symbol,
			startDate: new Date(startDate).toISOString(),
			endDate: new Date(endDate).toISOString(),
		});
	};

	const handleClose = () => {
		if (!isExecuting) {
			onClose();
			// Reset form
			setSymbol("");
			setStartDate(defaultStartDate);
			setEndDate(defaultEndDate);
			setPeriodPreset("1y");
		}
	};

	return (
		<Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
			<DialogTitle>전략 실행</DialogTitle>
			<DialogContent>
				<Stack spacing={3} sx={{ mt: 1 }}>
					<Box>
						<Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
							전략: <strong>{strategy?.name}</strong>
						</Typography>
						<Typography variant="caption" color="text.secondary">
							워치리스트에서 심볼을 선택하고 백테스트 기간을 설정하세요.
						</Typography>
					</Box>

					<WatchListSymbolSelector
						value={symbol}
						onChange={setSymbol}
						label="심볼 선택"
						placeholder="워치리스트에서 심볼 선택"
						required
						error={!symbol}
						helperText={
							!symbol ? "실행할 심볼을 선택해주세요" : `선택된 심볼: ${symbol}`
						}
					/>

					<FormControl fullWidth>
						<InputLabel>기간 프리셋</InputLabel>
						<Select
							value={periodPreset}
							onChange={(e) => handlePeriodChange(e.target.value)}
							label="기간 프리셋"
						>
							<MenuItem value="1m">최근 1개월</MenuItem>
							<MenuItem value="3m">최근 3개월</MenuItem>
							<MenuItem value="6m">최근 6개월</MenuItem>
							<MenuItem value="1y">최근 1년</MenuItem>
							<MenuItem value="3y">최근 3년</MenuItem>
							<MenuItem value="5y">최근 5년</MenuItem>
							<MenuItem value="custom">사용자 지정</MenuItem>
						</Select>
					</FormControl>

					<TextField
						label="시작일"
						type="date"
						value={startDate}
						onChange={(e) => {
							setStartDate(e.target.value);
							setPeriodPreset("custom");
						}}
						InputLabelProps={{ shrink: true }}
						fullWidth
					/>

					<TextField
						label="종료일"
						type="date"
						value={endDate}
						onChange={(e) => {
							setEndDate(e.target.value);
							setPeriodPreset("custom");
						}}
						InputLabelProps={{ shrink: true }}
						fullWidth
					/>

					{startDate && endDate && (
						<FormHelperText>
							백테스트 기간:{" "}
							{Math.ceil(
								(new Date(endDate).getTime() - new Date(startDate).getTime()) /
									(1000 * 60 * 60 * 24),
							)}
							일
						</FormHelperText>
					)}
				</Stack>
			</DialogContent>
			<DialogActions>
				<Button onClick={handleClose} disabled={isExecuting}>
					취소
				</Button>
				<Button
					onClick={handleExecute}
					variant="contained"
					disabled={!symbol || isExecuting}
				>
					{isExecuting ? "실행 중..." : "전략 실행"}
				</Button>
			</DialogActions>
		</Dialog>
	);
}
