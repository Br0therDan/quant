import { PlayArrow } from "@mui/icons-material";
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
 * StressTest 컴포넌트
 * 스트레스 테스트 시뮬레이션
 */
export const StressTest = () => {
	const [scenario, setScenario] = useState("market-crash");

	const handleRunTest = () => {
		console.log("Running stress test:", scenario);
	};

	return (
		<Card>
			<CardContent>
				<Typography variant="h6" gutterBottom>
					Stress Test Simulator
				</Typography>

				<Box sx={{ display: "flex", flexDirection: "column", gap: 3, mt: 2 }}>
					<FormControl fullWidth>
						<InputLabel>Stress Scenario</InputLabel>
						<Select
							value={scenario}
							onChange={(e) => setScenario(e.target.value)}
							label="Stress Scenario"
						>
							<MenuItem value="market-crash">Market Crash (-30%)</MenuItem>
							<MenuItem value="volatility-spike">
								Volatility Spike (VIX +50%)
							</MenuItem>
							<MenuItem value="liquidity-crisis">Liquidity Crisis</MenuItem>
							<MenuItem value="interest-rate">Interest Rate Shock</MenuItem>
						</Select>
					</FormControl>

					<Button
						variant="contained"
						startIcon={<PlayArrow />}
						onClick={handleRunTest}
						fullWidth
					>
						Run Stress Test
					</Button>

					<Box sx={{ mt: 2, p: 2, bgcolor: "grey.100", borderRadius: 1 }}>
						<Typography variant="body2" gutterBottom>
							시뮬레이션 결과:
						</Typography>
						<Typography variant="caption" color="text.secondary">
							스트레스 테스트 결과가 여기에 표시됩니다.
						</Typography>
					</Box>
				</Box>
			</CardContent>
		</Card>
	);
};
