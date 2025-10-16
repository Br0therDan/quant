import {
	Card,
	CardContent,
	Chip,
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableRow,
	Typography,
} from "@mui/material";

/**
 * AuditTrail 컴포넌트
 * 감사 추적 로그
 */
export const AuditTrail = () => {
	const auditLogs = [
		{
			id: 1,
			action: "Strategy Created",
			user: "John Doe",
			timestamp: "2024-01-15 14:30",
			status: "Success",
		},
		{
			id: 2,
			action: "Compliance Check",
			user: "System",
			timestamp: "2024-01-15 14:25",
			status: "Success",
		},
		{
			id: 3,
			action: "Position Modified",
			user: "Jane Smith",
			timestamp: "2024-01-15 14:20",
			status: "Success",
		},
		{
			id: 4,
			action: "Risk Limit Update",
			user: "Admin",
			timestamp: "2024-01-15 14:15",
			status: "Failed",
		},
	];

	return (
		<Card>
			<CardContent>
				<Typography variant="h6" gutterBottom>
					Audit Trail
				</Typography>

				<Table>
					<TableHead>
						<TableRow>
							<TableCell>Action</TableCell>
							<TableCell>User</TableCell>
							<TableCell>Timestamp</TableCell>
							<TableCell>Status</TableCell>
						</TableRow>
					</TableHead>
					<TableBody>
						{auditLogs.map((log) => (
							<TableRow key={log.id}>
								<TableCell>{log.action}</TableCell>
								<TableCell>{log.user}</TableCell>
								<TableCell>{log.timestamp}</TableCell>
								<TableCell>
									<Chip
										label={log.status}
										color={log.status === "Success" ? "success" : "error"}
										size="small"
									/>
								</TableCell>
							</TableRow>
						))}
					</TableBody>
				</Table>
			</CardContent>
		</Card>
	);
};
