import { Add } from "@mui/icons-material";
import {
	Box,
	Button,
	Card,
	CardContent,
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableRow,
	TextField,
	Typography,
} from "@mui/material";

/**
 * ParameterGrid 컴포넌트
 * 파라미터 그리드 설정
 */
export const ParameterGrid = () => {
	const parameters = [
		{ name: "learning_rate", type: "float", min: 0.001, max: 0.1, step: 0.01 },
		{ name: "batch_size", type: "int", min: 16, max: 128, step: 16 },
		{ name: "epochs", type: "int", min: 10, max: 100, step: 10 },
		{ name: "dropout", type: "float", min: 0.1, max: 0.5, step: 0.1 },
	];

	return (
		<Card>
			<CardContent>
				<Box
					sx={{
						display: "flex",
						justifyContent: "space-between",
						alignItems: "center",
						mb: 2,
					}}
				>
					<Typography variant="h6">Parameter Grid</Typography>
					<Button startIcon={<Add />} size="small">
						Add Parameter
					</Button>
				</Box>

				<Table>
					<TableHead>
						<TableRow>
							<TableCell>Parameter Name</TableCell>
							<TableCell>Type</TableCell>
							<TableCell>Min</TableCell>
							<TableCell>Max</TableCell>
							<TableCell>Step</TableCell>
						</TableRow>
					</TableHead>
					<TableBody>
						{parameters.map((param) => (
							<TableRow key={param.name}>
								<TableCell>{param.name}</TableCell>
								<TableCell>{param.type}</TableCell>
								<TableCell>
									<TextField
										size="small"
										defaultValue={param.min}
										type="number"
									/>
								</TableCell>
								<TableCell>
									<TextField
										size="small"
										defaultValue={param.max}
										type="number"
									/>
								</TableCell>
								<TableCell>
									<TextField
										size="small"
										defaultValue={param.step}
										type="number"
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
