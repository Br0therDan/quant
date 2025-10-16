"use client";

import { AIAssistant } from "@/components/gen-ai/strategy-builder/AIAssistant";
import { CodeGenerator } from "@/components/gen-ai/strategy-builder/CodeGenerator";
import { StrategyTemplates } from "@/components/gen-ai/strategy-builder/StrategyTemplates";
import PageContainer from "@/components/layout/PageContainer";
import { AutoAwesome, CheckCircle, Code, Speed } from "@mui/icons-material";
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
 * Strategy Builder 페이지
 *
 * User Story: US-21 (AI 기반 전략 생성)
 * 기능:
 * - AI 어시스턴트 (자연어 → 전략 코드)
 * - 코드 생성 및 검증
 * - 전략 템플릿 라이브러리
 * - 백테스트 자동 실행
 */
export default function StrategyBuilderPage() {
	const [tabValue, setTabValue] = useState(0);

	const breadcrumbs = [
		{ title: "GenAI Platform", href: "/gen-ai" },
		{ title: "Strategy Builder" },
	];

	const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
		setTabValue(newValue);
	};

	// Mock KPI data
	const kpiData = [
		{
			label: "Generated Strategies",
			value: 23,
			icon: <Code color="primary" />,
		},
		{
			label: "AI Suggestions",
			value: 87,
			icon: <AutoAwesome color="success" />,
		},
		{ label: "Avg Gen Time", value: "3.2s", icon: <Speed color="info" /> },
		{
			label: "Success Rate",
			value: "94%",
			icon: <CheckCircle color="warning" />,
		},
	];

	return (
		<PageContainer title="AI Strategy Builder" breadcrumbs={breadcrumbs}>
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
							<Tab label="AI Assistant" />
							<Tab label="Code Generator" />
							<Tab label="Templates" />
						</Tabs>
					</Card>
				</Grid>

				{/* Tab Content */}
				<Grid size={12}>
					{tabValue === 0 && <AIAssistant />}
					{tabValue === 1 && <CodeGenerator />}
					{tabValue === 2 && <StrategyTemplates />}
				</Grid>
			</Grid>
		</PageContainer>
	);
}
