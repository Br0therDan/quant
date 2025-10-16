import { AutoAwesome } from "@mui/icons-material";
import {
	Box,
	Button,
	Card,
	CardContent,
	FormControl,
	InputLabel,
	MenuItem,
	Select,
	Typography,
} from "@mui/material";
import { useState } from "react";

/**
 * ReportGenerator 컴포넌트
 * AI 리포트 자동 생성
 */
export const ReportGenerator = () => {
	const [reportType, setReportType] = useState("backtest");
	const [strategyId, setStrategyId] = useState("");

	const handleGenerate = () => {
		console.log("Generating report:", { reportType, strategyId });
	};

	return (
		<Card>
			<CardContent>
				<Typography variant="h6" gutterBottom>
					Generate AI Report
				</Typography>

				<Box sx={{ display: "flex", flexDirection: "column", gap: 3, mt: 2 }}>
					<FormControl fullWidth>
						<InputLabel>Report Type</InputLabel>
						<Select
							value={reportType}
							onChange={(e) => setReportType(e.target.value)}
							label="Report Type"
						>
							<MenuItem value="backtest">Backtest Analysis</MenuItem>
							<MenuItem value="strategy">Strategy Performance</MenuItem>
							<MenuItem value="risk">Risk Assessment</MenuItem>
							<MenuItem value="market">Market Overview</MenuItem>
						</Select>
					</FormControl>

					<FormControl fullWidth>
						<InputLabel>Strategy</InputLabel>
						<Select
							value={strategyId}
							onChange={(e) => setStrategyId(e.target.value)}
							label="Strategy"
						>
							<MenuItem value="1">Momentum Strategy</MenuItem>
							<MenuItem value="2">Mean Reversion</MenuItem>
							<MenuItem value="3">RSI Oscillator</MenuItem>
						</Select>
					</FormControl>

					<Button
						variant="contained"
						startIcon={<AutoAwesome />}
						onClick={handleGenerate}
						fullWidth
					>
						Generate Report
					</Button>

					<Box sx={{ mt: 2, p: 2, bgcolor: "grey.100", borderRadius: 1 }}>
						<Typography variant="caption" color="text.secondary">
							생성된 리포트가 여기에 표시됩니다.
						</Typography>
					</Box>
				</Box>
			</CardContent>
		</Card>
	);
};
