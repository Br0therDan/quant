import {
	Card,
	CardActionArea,
	CardContent,
	Chip,
	Grid,
	Typography,
} from "@mui/material";

/**
 * ReportTemplates 컴포넌트
 * 리포트 템플릿 라이브러리
 */
export const ReportTemplates = () => {
	const templates = [
		{ id: 1, name: "Monthly Performance", category: "Performance", usage: 45 },
		{ id: 2, name: "Risk Summary", category: "Risk", usage: 32 },
		{ id: 3, name: "Compliance Review", category: "Compliance", usage: 28 },
		{ id: 4, name: "Executive Summary", category: "Overview", usage: 67 },
	];

	return (
		<Card>
			<CardContent>
				<Typography variant="h6" gutterBottom>
					Report Templates
				</Typography>

				<Grid container spacing={2} sx={{ mt: 1 }}>
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
									<Chip label={`Used ${template.usage} times`} size="small" />
								</CardActionArea>
							</Card>
						</Grid>
					))}
				</Grid>
			</CardContent>
		</Card>
	);
};
