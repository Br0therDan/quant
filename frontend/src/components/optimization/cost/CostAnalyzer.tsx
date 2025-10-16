import {
	Box,
	Card,
	CardContent,
	LinearProgress,
	Typography,
} from "@mui/material";
import {
	Bar,
	BarChart,
	CartesianGrid,
	Legend,
	ResponsiveContainer,
	Tooltip,
	XAxis,
	YAxis,
} from "recharts";

/**
 * CostAnalyzer 컴포넌트
 * 비용 분석 및 예측
 */
export const CostAnalyzer = () => {
	// Mock data
	const costData = [
		{ month: "Jan", compute: 800, storage: 200, network: 150 },
		{ month: "Feb", compute: 900, storage: 220, network: 160 },
		{ month: "Mar", compute: 850, storage: 210, network: 155 },
		{ month: "Apr", compute: 950, storage: 230, network: 170 },
	];

	const totalCost = costData.reduce(
		(sum, item) => sum + item.compute + item.storage + item.network,
		0,
	);

	return (
		<Card>
			<CardContent>
				<Typography variant="h6" gutterBottom>
					Cost Analysis
				</Typography>

				<Box sx={{ mb: 3 }}>
					<Typography variant="body2" color="text.secondary" gutterBottom>
						Total Cost (Last 4 Months)
					</Typography>
					<Typography variant="h4">${totalCost.toLocaleString()}</Typography>
				</Box>

				<Box sx={{ display: "flex", flexDirection: "column", gap: 2, mb: 3 }}>
					<Box>
						<Box
							sx={{ display: "flex", justifyContent: "space-between", mb: 1 }}
						>
							<Typography variant="body2">Compute</Typography>
							<Typography variant="body2">68%</Typography>
						</Box>
						<LinearProgress variant="determinate" value={68} color="primary" />
					</Box>
					<Box>
						<Box
							sx={{ display: "flex", justifyContent: "space-between", mb: 1 }}
						>
							<Typography variant="body2">Storage</Typography>
							<Typography variant="body2">20%</Typography>
						</Box>
						<LinearProgress variant="determinate" value={20} color="success" />
					</Box>
					<Box>
						<Box
							sx={{ display: "flex", justifyContent: "space-between", mb: 1 }}
						>
							<Typography variant="body2">Network</Typography>
							<Typography variant="body2">12%</Typography>
						</Box>
						<LinearProgress variant="determinate" value={12} color="info" />
					</Box>
				</Box>

				<ResponsiveContainer width="100%" height={300}>
					<BarChart data={costData}>
						<CartesianGrid strokeDasharray="3 3" />
						<XAxis dataKey="month" />
						<YAxis />
						<Tooltip />
						<Legend />
						<Bar dataKey="compute" fill="#1976d2" />
						<Bar dataKey="storage" fill="#2e7d32" />
						<Bar dataKey="network" fill="#0288d1" />
					</BarChart>
				</ResponsiveContainer>
			</CardContent>
		</Card>
	);
};
