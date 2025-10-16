import { Error as ErrorIcon, Info, Warning } from "@mui/icons-material";
import {
	Box,
	Card,
	CardContent,
	Chip,
	List,
	ListItem,
	ListItemText,
	Typography,
} from "@mui/material";

/**
 * RegulatoryAlerts 컴포넌트
 * 규제 알림 및 경고
 */
export const RegulatoryAlerts = () => {
	const alerts = [
		{
			id: 1,
			severity: "error",
			title: "Position Limit Exceeded",
			date: "2024-01-15",
		},
		{
			id: 2,
			severity: "warning",
			title: "Leverage Approaching Limit",
			date: "2024-01-14",
		},
		{
			id: 3,
			severity: "info",
			title: "New Regulatory Update Available",
			date: "2024-01-13",
		},
	];

	const getSeverityIcon = (severity: string) => {
		switch (severity) {
			case "error":
				return <ErrorIcon color="error" />;
			case "warning":
				return <Warning color="warning" />;
			case "info":
				return <Info color="info" />;
			default:
				return null;
		}
	};

	return (
		<Card>
			<CardContent>
				<Typography variant="h6" gutterBottom>
					Regulatory Alerts
				</Typography>

				<List>
					{alerts.map((alert) => (
						<ListItem
							key={alert.id}
							sx={{ border: 1, borderColor: "divider", borderRadius: 1, mb: 1 }}
						>
							<Box sx={{ mr: 2 }}>{getSeverityIcon(alert.severity)}</Box>
							<ListItemText primary={alert.title} secondary={alert.date} />
							<Chip
								label={alert.severity.toUpperCase()}
								color={alert.severity as any}
								size="small"
							/>
						</ListItem>
					))}
				</List>
			</CardContent>
		</Card>
	);
};
