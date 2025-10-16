"use client";

import { MarketSentiment } from "@/components/gen-ai/risk-insights/MarketSentiment";
import { RiskAnalyzer } from "@/components/gen-ai/risk-insights/RiskAnalyzer";
import { StressTest } from "@/components/gen-ai/risk-insights/StressTest";
import PageContainer from "@/components/layout/PageContainer";
import { Insights, Security, Speed, TrendingDown } from "@mui/icons-material";
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
 * Risk Insights 페이지
 *
 * User Story: US-24 (AI 리스크 분석)
 * 기능:
 * - 리스크 분석 및 예측
 * - 시장 센티먼트 분석
 * - 스트레스 테스트 시뮬레이션
 */
export default function RiskInsightsPage() {
	const [tabValue, setTabValue] = useState(0);

	const breadcrumbs = [
		{ title: "GenAI Platform", href: "/gen-ai" },
		{ title: "Risk Insights" },
	];

	const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
		setTabValue(newValue);
	};

	// Mock KPI data
	const kpiData = [
		{
			label: "Risk Score",
			value: "6.8/10",
			icon: <TrendingDown color="warning" />,
		},
		{ label: "AI Insights", value: 42, icon: <Insights color="primary" /> },
		{ label: "Analysis Speed", value: "2.1s", icon: <Speed color="success" /> },
		{ label: "Stress Tests", value: 18, icon: <Security color="info" /> },
	];

	return (
		<PageContainer title="Risk Insights" breadcrumbs={breadcrumbs}>
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
							<Tab label="Risk Analyzer" />
							<Tab label="Market Sentiment" />
							<Tab label="Stress Test" />
						</Tabs>
					</Card>
				</Grid>

				{/* Tab Content */}
				<Grid size={12}>
					{tabValue === 0 && <RiskAnalyzer />}
					{tabValue === 1 && <MarketSentiment />}
					{tabValue === 2 && <StressTest />}
				</Grid>
			</Grid>
		</PageContainer>
	);
}
