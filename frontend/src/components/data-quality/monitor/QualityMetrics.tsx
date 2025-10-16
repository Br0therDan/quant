import {
	Box,
	Card,
	CardContent,
	Grid,
	LinearProgress,
	Typography,
} from "@mui/material";

/**
 * QualityMetrics 컴포넌트
 * 데이터 품질 메트릭
 */
export const QualityMetrics = () => {
	const metrics = [
		{
			name: "Completeness",
			score: 95,
			description: "Missing values in dataset",
		},
		{
			name: "Accuracy",
			score: 92,
			description: "Data accuracy and correctness",
		},
		{
			name: "Consistency",
			score: 88,
			description: "Data consistency across sources",
		},
		{
			name: "Timeliness",
			score: 97,
			description: "Data freshness and currency",
		},
		{ name: "Validity", score: 94, description: "Data conformance to rules" },
		{ name: "Uniqueness", score: 99, description: "Duplicate detection" },
	];

	const getScoreColor = (score: number) => {
		if (score >= 90) return "success";
		if (score >= 70) return "warning";
		return "error";
	};

	return (
		<Card>
			<CardContent>
				<Typography variant="h6" gutterBottom>
					Quality Metrics
				</Typography>

				<Grid container spacing={3} sx={{ mt: 1 }}>
					{metrics.map((metric) => (
						<Grid key={metric.name} size={{ xs: 12, sm: 6 }}>
							<Box
								sx={{
									p: 2,
									border: 1,
									borderColor: "divider",
									borderRadius: 1,
								}}
							>
								<Box
									sx={{
										display: "flex",
										justifyContent: "space-between",
										mb: 1,
									}}
								>
									<Typography variant="subtitle1">{metric.name}</Typography>
									<Typography
										variant="h6"
										color={`${getScoreColor(metric.score)}.main`}
									>
										{metric.score}%
									</Typography>
								</Box>
								<LinearProgress
									variant="determinate"
									value={metric.score}
									color={getScoreColor(metric.score) as any}
									sx={{ mb: 1 }}
								/>
								<Typography variant="caption" color="text.secondary">
									{metric.description}
								</Typography>
							</Box>
						</Grid>
					))}
				</Grid>
			</CardContent>
		</Card>
	);
};
