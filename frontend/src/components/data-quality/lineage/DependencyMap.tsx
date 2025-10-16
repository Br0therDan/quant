import { ArrowForward } from "@mui/icons-material";
import {
	Box,
	Card,
	CardContent,
	Chip,
	List,
	ListItem,
	Typography,
} from "@mui/material";

/**
 * DependencyMap 컴포넌트
 * 의존성 맵
 */
export const DependencyMap = () => {
	const dependencies = [
		{
			id: 1,
			source: "raw_market_data",
			target: "cleaned_market_data",
			type: "Table → Table",
			status: "Active",
		},
		{
			id: 2,
			source: "cleaned_market_data",
			target: "strategy_backtest",
			type: "Table → Pipeline",
			status: "Active",
		},
		{
			id: 3,
			source: "strategy_backtest",
			target: "performance_dashboard",
			type: "Pipeline → Dashboard",
			status: "Active",
		},
		{
			id: 4,
			source: "market_sentiment_api",
			target: "ml_prediction_model",
			type: "API → Model",
			status: "Inactive",
		},
	];

	return (
		<Card>
			<CardContent>
				<Typography variant="h6" gutterBottom>
					Dependency Map
				</Typography>

				<List>
					{dependencies.map((dep) => (
						<ListItem
							key={dep.id}
							sx={{
								border: 1,
								borderColor: "divider",
								borderRadius: 1,
								mb: 1,
								display: "flex",
								alignItems: "center",
							}}
						>
							<Box
								sx={{ flex: 1, display: "flex", alignItems: "center", gap: 2 }}
							>
								<Typography variant="body2" sx={{ fontWeight: 500 }}>
									{dep.source}
								</Typography>
								<ArrowForward color="action" fontSize="small" />
								<Typography variant="body2" sx={{ fontWeight: 500 }}>
									{dep.target}
								</Typography>
							</Box>
							<Box sx={{ display: "flex", gap: 1 }}>
								<Chip label={dep.type} size="small" variant="outlined" />
								<Chip
									label={dep.status}
									size="small"
									color={dep.status === "Active" ? "success" : "default"}
								/>
							</Box>
						</ListItem>
					))}
				</List>
			</CardContent>
		</Card>
	);
};
