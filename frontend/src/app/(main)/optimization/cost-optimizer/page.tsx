"use client";

import PageContainer from "@/components/layout/PageContainer";
import { BudgetAlerts } from "@/components/optimization/cost/BudgetAlerts";
import { CostAnalyzer } from "@/components/optimization/cost/CostAnalyzer";
import { ResourceOptimizer } from "@/components/optimization/cost/ResourceOptimizer";
import { AttachMoney, Savings, Speed, TrendingDown } from "@mui/icons-material";
import {
	Box,
	Card,
	CardContent,
	Grid,
	Tab,
	Tabs,
	Typography,
} from "@mui/material";
import { useState } from "react";

/**
 * Cost Optimizer 페이지
 *
 * User Story: US-26 (비용 최적화)
 * 기능:
 * - 비용 분석 및 예측
 * - 리소스 최적화 제안
 * - 예산 알림 및 제한
 */
export default function CostOptimizerPage() {
	const [tabValue, setTabValue] = useState(0);

	const breadcrumbs = [
		{ title: "Optimization", href: "/optimization" },
		{ title: "Cost Optimizer" },
	];

	const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
		setTabValue(newValue);
	};

	// Mock KPI data
	const kpiData = [
		{
			label: "Monthly Cost",
			value: "$2,345",
			icon: <AttachMoney color="primary" />,
		},
		{
			label: "Cost Reduction",
			value: "18%",
			icon: <TrendingDown color="success" />,
		},
		{
			label: "Optimization Score",
			value: "8.4/10",
			icon: <Speed color="info" />,
		},
		{
			label: "Savings YTD",
			value: "$12.8K",
			icon: <Savings color="warning" />,
		},
	];

	return (
		<PageContainer title="Cost Optimizer" breadcrumbs={breadcrumbs}>
			<Grid container spacing={3}>
				{/* KPI 카드 */}
				{kpiData.map((kpi, index) => (
					<Grid key={index} size={{ xs: 12, sm: 6, md: 3 }}>
						<Card>
							<CardContent>
								<Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
									{kpi.icon}
									<Box sx={{ flex: 1 }}>
										<Typography variant="body2" color="text.secondary">
											{kpi.label}
										</Typography>
										<Typography variant="h5">{kpi.value}</Typography>
									</Box>
								</Box>
							</CardContent>
						</Card>
					</Grid>
				))}

				{/* Tabs */}
				<Grid size={12}>
					<Card>
						<Tabs
							value={tabValue}
							onChange={handleTabChange}
							sx={{ borderBottom: 1, borderColor: "divider" }}
						>
							<Tab label="Cost Analyzer" />
							<Tab label="Resource Optimizer" />
							<Tab label="Budget Alerts" />
						</Tabs>
					</Card>
				</Grid>

				{/* Tab Content */}
				<Grid size={12}>
					{tabValue === 0 && <CostAnalyzer />}
					{tabValue === 1 && <ResourceOptimizer />}
					{tabValue === 2 && <BudgetAlerts />}
				</Grid>
			</Grid>
		</PageContainer>
	);
}
