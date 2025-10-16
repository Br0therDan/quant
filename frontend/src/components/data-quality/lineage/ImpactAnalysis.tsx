import { Search } from "@mui/icons-material";
import {
	Box,
	Button,
	Card,
	CardContent,
	Chip,
	List,
	ListItem,
	ListItemText,
	TextField,
	Typography,
} from "@mui/material";
import { useState } from "react";

/**
 * ImpactAnalysis 컴포넌트
 * 변경 사항 영향 분석
 */
export const ImpactAnalysis = () => {
	const [selectedEntity, setSelectedEntity] = useState("");

	const impactedItems = [
		{ id: 1, name: "downstream_table_1", type: "Table", impact: "High" },
		{ id: 2, name: "report_dashboard", type: "Dashboard", impact: "Medium" },
		{ id: 3, name: "etl_pipeline_2", type: "Pipeline", impact: "High" },
		{ id: 4, name: "ml_model_v3", type: "Model", impact: "Low" },
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
					Impact Analysis
				</Typography>

				<Box sx={{ display: "flex", gap: 2, mb: 3 }}>
					<TextField
						fullWidth
						size="small"
						placeholder="Enter data entity name..."
						value={selectedEntity}
						onChange={(e) => setSelectedEntity(e.target.value)}
					/>
					<Button variant="contained" startIcon={<Search />}>
						Analyze
					</Button>
				</Box>

				<Typography variant="subtitle2" gutterBottom>
					Impacted Items (4)
				</Typography>

				<List>
					{impactedItems.map((item) => (
						<ListItem
							key={item.id}
							sx={{ border: 1, borderColor: "divider", borderRadius: 1, mb: 1 }}
						>
							<ListItemText primary={item.name} secondary={item.type} />
							<Chip
								label={`Impact: ${item.impact}`}
								color={getImpactColor(item.impact) as any}
								size="small"
							/>
						</ListItem>
					))}
				</List>
			</CardContent>
		</Card>
	);
};
