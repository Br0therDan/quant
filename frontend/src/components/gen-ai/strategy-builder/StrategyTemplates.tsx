import {
	Card,
	CardActionArea,
	CardContent,
	Chip,
	Grid,
	Typography,
} from "@mui/material";

/**
 * StrategyTemplates 컴포넌트
 * 전략 템플릿 라이브러리
 */
export const StrategyTemplates = () => {
	// Mock templates
	const templates = [
		{
			id: 1,
			name: "Momentum Strategy",
			category: "Trend Following",
			complexity: "Medium",
		},
		{
			id: 2,
			name: "Mean Reversion",
			category: "Statistical Arbitrage",
			complexity: "Advanced",
		},
		{
			id: 3,
			name: "RSI Oscillator",
			category: "Technical Indicators",
			complexity: "Beginner",
		},
		{
			id: 4,
			name: "Bollinger Bands",
			category: "Volatility",
			complexity: "Medium",
		},
	];

	const getComplexityColor = (complexity: string) => {
		switch (complexity) {
			case "Beginner":
				return "success";
			case "Medium":
				return "warning";
			case "Advanced":
				return "error";
			default:
				return "default";
		}
	};

	return (
		<Card>
			<CardContent>
				<Typography variant="h6" gutterBottom>
					Strategy Templates
				</Typography>
				<Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
					검증된 전략 템플릿을 선택하여 빠르게 시작하세요.
				</Typography>

				<Grid container spacing={2}>
					{templates.map((template) => (
						<Grid key={template.id} size={{ xs: 12, sm: 6, md: 3 }}>
							<Card variant="outlined">
								<CardActionArea sx={{ p: 2 }}>
									<Typography variant="h6" gutterBottom>
										{template.name}
									</Typography>
									<Typography
										variant="body2"
										color="text.secondary"
										sx={{ mb: 1 }}
									>
										{template.category}
									</Typography>
									<Chip
										label={template.complexity}
										color={getComplexityColor(template.complexity) as any}
										size="small"
									/>
								</CardActionArea>
							</Card>
						</Grid>
					))}
				</Grid>
			</CardContent>
		</Card>
	);
};
