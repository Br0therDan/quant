import { Visibility } from "@mui/icons-material";
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
 * TuningHistory 컴포넌트
 * 튜닝 작업 히스토리
 */
export const TuningHistory = () => {
	const history = [
		{
			id: 1,
			strategy: "Momentum",
			algorithm: "Bayesian",
			performance: "94.2%",
			date: "2024-01-15",
			status: "Completed",
		},
		{
			id: 2,
			strategy: "Mean Reversion",
			algorithm: "Grid Search",
			performance: "89.5%",
			date: "2024-01-14",
			status: "Completed",
		},
		{
			id: 3,
			strategy: "RSI Oscillator",
			algorithm: "Random Search",
			performance: "91.8%",
			date: "2024-01-13",
			status: "Running",
		},
	];

	return (
		<Card>
			<CardContent>
				<Typography variant="h6" gutterBottom>
					Tuning History
				</Typography>

				<Table>
					<TableHead>
						<TableRow>
							<TableCell>Strategy</TableCell>
							<TableCell>Algorithm</TableCell>
							<TableCell>Performance</TableCell>
							<TableCell>Date</TableCell>
							<TableCell>Status</TableCell>
							<TableCell align="right">Actions</TableCell>
						</TableRow>
					</TableHead>
					<TableBody>
						{history.map((job) => (
							<TableRow key={job.id}>
								<TableCell>{job.strategy}</TableCell>
								<TableCell>{job.algorithm}</TableCell>
								<TableCell>{job.performance}</TableCell>
								<TableCell>{job.date}</TableCell>
								<TableCell>
									<Chip
										label={job.status}
										color={job.status === "Completed" ? "success" : "warning"}
										size="small"
									/>
								</TableCell>
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
