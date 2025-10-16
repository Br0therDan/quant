import {
	Box,
	Card,
	CardContent,
	FormControl,
	FormControlLabel,
	InputLabel,
	MenuItem,
	Select,
	Slider,
	Switch,
	Typography,
} from "@mui/material";
import { useState } from "react";

/**
 * ModelSelector 컴포넌트
 * AI 모델 선택 및 설정
 */
export const ModelSelector = () => {
	const [model, setModel] = useState("gpt-4");
	const [temperature, setTemperature] = useState(0.7);
	const [streaming, setStreaming] = useState(true);

	return (
		<Card sx={{ height: "600px" }}>
			<CardContent>
				<Typography variant="h6" gutterBottom>
					Model Settings
				</Typography>

				<Box sx={{ display: "flex", flexDirection: "column", gap: 3, mt: 2 }}>
					{/* Model Selection */}
					<FormControl fullWidth size="small">
						<InputLabel>Model</InputLabel>
						<Select
							value={model}
							onChange={(e) => setModel(e.target.value)}
							label="Model"
						>
							<MenuItem value="gpt-4">GPT-4</MenuItem>
							<MenuItem value="gpt-3.5-turbo">GPT-3.5 Turbo</MenuItem>
							<MenuItem value="claude-3">Claude 3</MenuItem>
						</Select>
					</FormControl>

					{/* Temperature */}
					<Box>
						<Typography variant="body2" gutterBottom>
							Temperature: {temperature}
						</Typography>
						<Slider
							value={temperature}
							onChange={(_, value) => setTemperature(value as number)}
							min={0}
							max={2}
							step={0.1}
							marks
							size="small"
						/>
					</Box>

					{/* Streaming */}
					<FormControlLabel
						control={
							<Switch
								checked={streaming}
								onChange={(e) => setStreaming(e.target.checked)}
							/>
						}
						label="Streaming Response"
					/>

					{/* Model Info */}
					<Box sx={{ mt: 2, p: 2, bgcolor: "grey.100", borderRadius: 1 }}>
						<Typography variant="caption" color="text.secondary">
							현재 선택된 모델: <strong>{model}</strong>
						</Typography>
						<Typography
							variant="caption"
							display="block"
							color="text.secondary"
							sx={{ mt: 1 }}
						>
							Temperature가 높을수록 더 창의적인 응답을 생성합니다.
						</Typography>
					</Box>
				</Box>
			</CardContent>
		</Card>
	);
};
