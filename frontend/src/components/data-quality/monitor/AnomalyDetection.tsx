import { Visibility, Warning } from "@mui/icons-material";
import {
	Card,
	CardContent,
	Chip,
	IconButton,
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableRow,
	Typography,
} from "@mui/material";

/**
 * AnomalyDetection 컴포넌트
 * 이상 탐지 및 알림
 */
export const AnomalyDetection = () => {
	const anomalies = [
		{
			id: 1,
			field: "price",
			type: "Outlier",
			severity: "High",
			value: "15000",
			expected: "100-500",
			timestamp: "2024-01-15 14:30",
		},
		{
			id: 2,
			field: "volume",
			type: "Missing",
			severity: "Medium",
			value: "NULL",
			expected: "> 0",
			timestamp: "2024-01-15 14:25",
		},
		{
			id: 3,
			field: "date",
			type: "Format",
			severity: "Low",
			value: "01/15/24",
			expected: "YYYY-MM-DD",
			timestamp: "2024-01-15 14:20",
		},
	];

	const getSeverityColor = (severity: string) => {
		switch (severity) {
			case "High":
				return "error";
			case "Medium":
				return "warning";
			case "Low":
				return "info";
			default:
				return "default";
		}
	};

	return (
		<Card>
			<CardContent>
				<Typography variant="h6" gutterBottom>
					Anomaly Detection
				</Typography>

				<Table>
					<TableHead>
						<TableRow>
							<TableCell>Field</TableCell>
							<TableCell>Type</TableCell>
							<TableCell>Severity</TableCell>
							<TableCell>Value</TableCell>
							<TableCell>Expected</TableCell>
							<TableCell>Timestamp</TableCell>
							<TableCell align="right">Actions</TableCell>
						</TableRow>
					</TableHead>
					<TableBody>
						{anomalies.map((anomaly) => (
							<TableRow key={anomaly.id}>
								<TableCell>{anomaly.field}</TableCell>
								<TableCell>{anomaly.type}</TableCell>
								<TableCell>
									<Chip
										label={anomaly.severity}
										color={getSeverityColor(anomaly.severity) as any}
										size="small"
										icon={<Warning />}
									/>
								</TableCell>
								<TableCell>{anomaly.value}</TableCell>
								<TableCell>{anomaly.expected}</TableCell>
								<TableCell>{anomaly.timestamp}</TableCell>
								<TableCell align="right">
									<IconButton size="small">
										<Visibility fontSize="small" />
									</IconButton>
								</TableCell>
							</TableRow>
						))}
					</TableBody>
				</Table>
			</CardContent>
		</Card>
	);
};
