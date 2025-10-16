import { Info, Warning } from "@mui/icons-material";
import {
	Box,
	Card,
	CardContent,
	Chip,
	LinearProgress,
	List,
	ListItem,
	ListItemText,
	Typography,
} from "@mui/material";

/**
 * BudgetAlerts 컴포넌트
 * 예산 알림 및 제한
 */
export const BudgetAlerts = () => {
	const budgetStatus = {
		monthly: 3000,
		current: 2345,
		percentage: 78,
	};

	const alerts = [
		{
			id: 1,
			severity: "warning",
			message: "Approaching monthly budget limit (78%)",
			date: "2024-01-15",
		},
		{
			id: 2,
			severity: "info",
			message: "Storage costs increased by 15% this month",
			date: "2024-01-14",
		},
		{
			id: 3,
			severity: "warning",
			message: "Compute usage spike detected in region us-west-2",
			date: "2024-01-13",
		},
	];

	return (
		<Card>
			<CardContent>
				<Typography variant="h6" gutterBottom>
					Budget Status & Alerts
				</Typography>

				{/* Budget Overview */}
				<Box sx={{ mb: 4, p: 2, bgcolor: "grey.100", borderRadius: 1 }}>
					<Box sx={{ display: "flex", justifyContent: "space-between", mb: 1 }}>
						<Typography variant="body2">Monthly Budget</Typography>
						<Typography variant="body2">
							${budgetStatus.current} / ${budgetStatus.monthly}
						</Typography>
					</Box>
					<LinearProgress
						variant="determinate"
						value={budgetStatus.percentage}
						color={budgetStatus.percentage > 80 ? "error" : "warning"}
						sx={{ height: 8, borderRadius: 1 }}
					/>
					<Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
						{budgetStatus.percentage}% of monthly budget used
					</Typography>
				</Box>

				{/* Alerts */}
				<Typography variant="subtitle1" gutterBottom>
					Recent Alerts
				</Typography>
				<List>
					{alerts.map((alert) => (
						<ListItem
							key={alert.id}
							sx={{ border: 1, borderColor: "divider", borderRadius: 1, mb: 1 }}
						>
							<Box sx={{ mr: 2 }}>
								{alert.severity === "warning" ? (
									<Warning color="warning" />
								) : (
									<Info color="info" />
								)}
							</Box>
							<ListItemText primary={alert.message} secondary={alert.date} />
							<Chip
								label={alert.severity.toUpperCase()}
								color={alert.severity === "warning" ? "warning" : "info"}
								size="small"
							/>
						</ListItem>
					))}
				</List>
			</CardContent>
		</Card>
	);
};
