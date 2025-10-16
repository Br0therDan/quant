import {
	Box,
	Card,
	CardContent,
	Chip,
	LinearProgress,
	Typography,
} from "@mui/material";

/**
 * RiskAnalyzer 컴포넌트
 * AI 리스크 분석
 */
export const RiskAnalyzer = () => {
	const riskFactors = [
		{ name: "Market Risk", score: 75, severity: "high" },
		{ name: "Liquidity Risk", score: 45, severity: "medium" },
		{ name: "Operational Risk", score: 30, severity: "low" },
		{ name: "Model Risk", score: 60, severity: "medium" },
	];

	const getSeverityColor = (severity: string) => {
		switch (severity) {
			case "high":
				return "error";
			case "medium":
				return "warning";
			case "low":
				return "success";
			default:
				return "default";
		}
	};

	return (
		<Card>
			<CardContent>
				<Typography variant="h6" gutterBottom>
					AI Risk Analyzer
				</Typography>

				<Box sx={{ display: "flex", flexDirection: "column", gap: 3, mt: 2 }}>
					{riskFactors.map((factor) => (
						<Box key={factor.name}>
							<Box
								sx={{ display: "flex", justifyContent: "space-between", mb: 1 }}
							>
								<Typography variant="body2">{factor.name}</Typography>
								<Chip
									label={factor.severity.toUpperCase()}
									color={getSeverityColor(factor.severity) as any}
									size="small"
								/>
							</Box>
							<LinearProgress
								variant="determinate"
								value={factor.score}
								color={getSeverityColor(factor.severity) as any}
							/>
							<Typography variant="caption" color="text.secondary">
								Score: {factor.score}/100
							</Typography>
						</Box>
					))}
				</Box>
			</CardContent>
		</Card>
	);
};
