import { AutoAwesome } from "@mui/icons-material";
import {
	Box,
	Button,
	Card,
	CardContent,
	TextField,
	Typography,
} from "@mui/material";
import { useState } from "react";

/**
 * AIAssistant 컴포넌트
 * 자연어 입력으로 전략 생성
 */
export const AIAssistant = () => {
	const [prompt, setPrompt] = useState("");

	const handleGenerate = () => {
		console.log("Generating strategy from:", prompt);
	};

	return (
		<Card>
			<CardContent>
				<Typography variant="h6" gutterBottom>
					AI Strategy Assistant
				</Typography>
				<Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
					자연어로 원하는 전략을 설명하면 AI가 코드를 생성합니다.
				</Typography>

				<TextField
					fullWidth
					multiline
					rows={6}
					placeholder="예: RSI가 30 이하일 때 매수하고 70 이상일 때 매도하는 전략을 만들어줘"
					value={prompt}
					onChange={(e) => setPrompt(e.target.value)}
					sx={{ mb: 2 }}
				/>

				<Box sx={{ display: "flex", gap: 2 }}>
					<Button
						variant="contained"
						startIcon={<AutoAwesome />}
						onClick={handleGenerate}
						disabled={!prompt.trim()}
					>
						Generate Strategy
					</Button>
					<Button variant="outlined" onClick={() => setPrompt("")}>
						Clear
					</Button>
				</Box>

				{/* Generated Code Preview */}
				<Box sx={{ mt: 3, p: 2, bgcolor: "grey.100", borderRadius: 1 }}>
					<Typography variant="caption" color="text.secondary">
						생성된 전략 코드가 여기에 표시됩니다.
					</Typography>
				</Box>
			</CardContent>
		</Card>
	);
};
