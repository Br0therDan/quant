import { CheckCircle, TrendingDown } from "@mui/icons-material";
import {
	Box,
	Button,
	Card,
	CardContent,
	Chip,
	List,
	ListItem,
	ListItemText,
	Typography,
} from "@mui/material";

/**
 * ResourceOptimizer 컴포넌트
 * 리소스 최적화 제안
 */
export const ResourceOptimizer = () => {
	const recommendations = [
		{
			id: 1,
			title: "Reduce Compute Instance Size",
			description:
				"Current instance is over-provisioned. Downsize to save $450/month.",
			savings: "$450",
			impact: "Medium",
		},
		{
			id: 2,
			title: "Enable Auto-Scaling",
			description:
				"Configure auto-scaling to optimize resource usage during off-peak hours.",
			savings: "$280",
			impact: "High",
		},
		{
			id: 3,
			title: "Archive Old Data",
			description: "Move data older than 90 days to cheaper storage tier.",
			savings: "$120",
			impact: "Low",
		},
	];

	const getImpactColor = (impact: string) => {
		switch (impact) {
			case "High":
				return "error";
			case "Medium":
				return "warning";
			case "Low":
				return "success";
			default:
				return "default";
		}
	};

	return (
		<Card>
			<CardContent>
				<Typography variant="h6" gutterBottom>
					Optimization Recommendations
				</Typography>

				<List>
					{recommendations.map((rec) => (
						<ListItem
							key={rec.id}
							sx={{
								border: 1,
								borderColor: "divider",
								borderRadius: 1,
								mb: 2,
								flexDirection: "column",
								alignItems: "flex-start",
							}}
						>
							<Box
								sx={{
									display: "flex",
									justifyContent: "space-between",
									width: "100%",
									mb: 1,
								}}
							>
								<Typography variant="subtitle1">{rec.title}</Typography>
								<Chip
									label={`Save ${rec.savings}`}
									color="success"
									size="small"
									icon={<TrendingDown />}
								/>
							</Box>
							<ListItemText secondary={rec.description} />
							<Box sx={{ display: "flex", gap: 2, mt: 1, width: "100%" }}>
								<Chip
									label={`Impact: ${rec.impact}`}
									color={getImpactColor(rec.impact) as any}
									size="small"
								/>
								<Button
									size="small"
									variant="outlined"
									startIcon={<CheckCircle />}
								>
									Apply
								</Button>
							</Box>
						</ListItem>
					))}
				</List>
			</CardContent>
		</Card>
	);
};
