import { CheckCircle } from "@mui/icons-material";
import {
	Box,
	Button,
	Card,
	CardContent,
	Chip,
	TextField,
	Typography,
} from "@mui/material";
import { useState } from "react";

/**
 * ComplianceChecker 컴포넌트
 * 규정 준수 검사
 */
export const ComplianceChecker = () => {
	const [strategyCode, setStrategyCode] = useState("");

	const handleCheck = () => {
		console.log("Checking compliance:", strategyCode);
	};

	return (
		<Card>
			<CardContent>
				<Typography variant="h6" gutterBottom>
					Compliance Checker
				</Typography>

				<TextField
					fullWidth
					multiline
					rows={8}
					placeholder="전략 코드를 입력하여 규정 준수 여부를 확인하세요..."
					value={strategyCode}
					onChange={(e) => setStrategyCode(e.target.value)}
					sx={{ mb: 2 }}
				/>

				<Button
					variant="contained"
					startIcon={<CheckCircle />}
					onClick={handleCheck}
					fullWidth
				>
					Check Compliance
				</Button>

				<Box sx={{ mt: 3, p: 2, bgcolor: "grey.100", borderRadius: 1 }}>
					<Typography variant="body2" gutterBottom>
						검사 항목:
					</Typography>
					<Box sx={{ display: "flex", gap: 1, flexWrap: "wrap", mt: 1 }}>
						<Chip label="Position Limits" size="small" color="success" />
						<Chip label="Leverage Rules" size="small" color="success" />
						<Chip label="Risk Controls" size="small" color="success" />
						<Chip label="Reporting Requirements" size="small" color="success" />
					</Box>
				</Box>
			</CardContent>
		</Card>
	);
};
