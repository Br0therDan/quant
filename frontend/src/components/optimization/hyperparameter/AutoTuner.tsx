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
 * AutoTuner 컴포넌트
 * 자동 하이퍼파라미터 튜닝
 */
export const AutoTuner = () => {
	const [algorithm, setAlgorithm] = useState("bayesian");
	const [strategy, setStrategy] = useState("1");

	const handleStartTuning = () => {
		console.log("Starting tuning:", { algorithm, strategy });
	};

	return (
		<Card>
			<CardContent>
				<Typography variant="h6" gutterBottom>
					Auto Tuner
				</Typography>

				<Box sx={{ display: "flex", flexDirection: "column", gap: 3, mt: 2 }}>
					<FormControl fullWidth>
						<InputLabel>Tuning Algorithm</InputLabel>
						<Select
							value={algorithm}
							onChange={(e) => setAlgorithm(e.target.value)}
							label="Tuning Algorithm"
						>
							<MenuItem value="grid">Grid Search</MenuItem>
							<MenuItem value="random">Random Search</MenuItem>
							<MenuItem value="bayesian">Bayesian Optimization</MenuItem>
							<MenuItem value="genetic">Genetic Algorithm</MenuItem>
						</Select>
					</FormControl>

					<FormControl fullWidth>
						<InputLabel>Strategy</InputLabel>
						<Select
							value={strategy}
							onChange={(e) => setStrategy(e.target.value)}
							label="Strategy"
						>
							<MenuItem value="1">Momentum Strategy</MenuItem>
							<MenuItem value="2">Mean Reversion</MenuItem>
							<MenuItem value="3">RSI Oscillator</MenuItem>
						</Select>
					</FormControl>

					<Button
						variant="contained"
						startIcon={<PlayArrow />}
						onClick={handleStartTuning}
						fullWidth
					>
						Start Tuning
					</Button>

					<Box sx={{ mt: 2, p: 2, bgcolor: "grey.100", borderRadius: 1 }}>
						<Typography variant="body2" gutterBottom>
							튜닝 상태:
						</Typography>
						<Typography variant="caption" color="text.secondary">
							튜닝 결과가 여기에 표시됩니다.
						</Typography>
					</Box>
				</Box>
			</CardContent>
		</Card>
	);
};
