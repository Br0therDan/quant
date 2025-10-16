import { Code, PlayArrow } from "@mui/icons-material";
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
 * CodeGenerator 컴포넌트
 * 전략 코드 생성 및 검증
 */
export const CodeGenerator = () => {
	const [code, setCode] = useState("");

	const handleValidate = () => {
		console.log("Validating code:", code);
	};

	const handleRun = () => {
		console.log("Running backtest:", code);
	};

	return (
		<Card>
			<CardContent>
				<Typography variant="h6" gutterBottom>
					Code Generator & Validator
				</Typography>

				<TextField
					fullWidth
					multiline
					rows={12}
					placeholder="# 전략 코드를 입력하거나 생성하세요
def strategy(data):
    # Your strategy logic here
    pass"
					value={code}
					onChange={(e) => setCode(e.target.value)}
					sx={{ mb: 2, fontFamily: "monospace" }}
				/>

				<Box sx={{ display: "flex", gap: 2 }}>
					<Button
						variant="contained"
						startIcon={<Code />}
						onClick={handleValidate}
					>
						Validate Code
					</Button>
					<Button
						variant="outlined"
						startIcon={<PlayArrow />}
						onClick={handleRun}
						disabled={!code.trim()}
					>
						Run Backtest
					</Button>
				</Box>

				{/* Validation Results */}
				<Box sx={{ mt: 3, p: 2, bgcolor: "grey.100", borderRadius: 1 }}>
					<Typography variant="caption" color="text.secondary">
						검증 결과가 여기에 표시됩니다.
					</Typography>
				</Box>
			</CardContent>
		</Card>
	);
};
