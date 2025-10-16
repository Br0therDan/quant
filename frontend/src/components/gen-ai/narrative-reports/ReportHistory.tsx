import { Download, Visibility } from "@mui/icons-material";
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
 * ReportHistory 컴포넌트
 * 리포트 생성 히스토리
 */
export const ReportHistory = () => {
	const history = [
		{
			id: 1,
			name: "Q4 Performance",
			date: "2024-01-15",
			type: "Performance",
			status: "Completed",
		},
		{
			id: 2,
			name: "Risk Analysis",
			date: "2024-01-14",
			type: "Risk",
			status: "Completed",
		},
		{
			id: 3,
			name: "Compliance Review",
			date: "2024-01-13",
			type: "Compliance",
			status: "Processing",
		},
	];

	return (
		<Card>
			<CardContent>
				<Typography variant="h6" gutterBottom>
					Report History
				</Typography>

				<Table>
					<TableHead>
						<TableRow>
							<TableCell>Report Name</TableCell>
							<TableCell>Date</TableCell>
							<TableCell>Type</TableCell>
							<TableCell>Status</TableCell>
							<TableCell align="right">Actions</TableCell>
						</TableRow>
					</TableHead>
					<TableBody>
						{history.map((report) => (
							<TableRow key={report.id}>
								<TableCell>{report.name}</TableCell>
								<TableCell>{report.date}</TableCell>
								<TableCell>{report.type}</TableCell>
								<TableCell>
									<Chip
										label={report.status}
										color={
											report.status === "Completed" ? "success" : "warning"
										}
										size="small"
									/>
								</TableCell>
								<TableCell align="right">
									<IconButton size="small">
										<Visibility fontSize="small" />
									</IconButton>
									<IconButton size="small">
										<Download fontSize="small" />
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
