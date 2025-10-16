import { Add } from "@mui/icons-material";
import {
	Box,
	Button,
	Card,
	CardContent,
	Switch,
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableRow,
	Typography,
} from "@mui/material";

/**
 * ValidationRules 컴포넌트
 * 데이터 검증 규칙 관리
 */
export const ValidationRules = () => {
	const rules = [
		{
			id: 1,
			field: "price",
			rule: "Range",
			condition: "0 < x < 10000",
			enabled: true,
		},
		{
			id: 2,
			field: "volume",
			rule: "NotNull",
			condition: "value != NULL",
			enabled: true,
		},
		{
			id: 3,
			field: "date",
			rule: "Format",
			condition: "YYYY-MM-DD",
			enabled: true,
		},
		{
			id: 4,
			field: "symbol",
			rule: "Length",
			condition: "length <= 10",
			enabled: false,
		},
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
					<Typography variant="h6">Validation Rules</Typography>
					<Button startIcon={<Add />} size="small">
						Add Rule
					</Button>
				</Box>

				<Table>
					<TableHead>
						<TableRow>
							<TableCell>Field</TableCell>
							<TableCell>Rule Type</TableCell>
							<TableCell>Condition</TableCell>
							<TableCell align="right">Enabled</TableCell>
						</TableRow>
					</TableHead>
					<TableBody>
						{rules.map((rule) => (
							<TableRow key={rule.id}>
								<TableCell>{rule.field}</TableCell>
								<TableCell>{rule.rule}</TableCell>
								<TableCell>{rule.condition}</TableCell>
								<TableCell align="right">
									<Switch defaultChecked={rule.enabled} size="small" />
								</TableCell>
							</TableRow>
						))}
					</TableBody>
				</Table>
			</CardContent>
		</Card>
	);
};
