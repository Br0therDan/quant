"use client";

import { DependencyMap } from "@/components/data-quality/lineage/DependencyMap";
import { ImpactAnalysis } from "@/components/data-quality/lineage/ImpactAnalysis";
import { LineageGraph } from "@/components/data-quality/lineage/LineageGraph";
import PageContainer from "@/components/layout/PageContainer";
import { AccountTree, Schema, Speed, Timeline } from "@mui/icons-material";
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
 * Data Lineage Tracker 페이지
 *
 * User Story: US-28 (데이터 계보 추적)
 * 기능:
 * - 데이터 계보 시각화
 * - 영향 분석 (변경 사항 추적)
 * - 의존성 맵
 */
export default function DataLineageTrackerPage() {
	const [tabValue, setTabValue] = useState(0);

	const breadcrumbs = [
		{ title: "Data Quality", href: "/data-quality" },
		{ title: "Lineage Tracker" },
	];

	const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
		setTabValue(newValue);
	};

	// Mock KPI data
	const kpiData = [
		{ label: "Data Sources", value: 23, icon: <AccountTree color="primary" /> },
		{ label: "Lineage Paths", value: 87, icon: <Timeline color="success" /> },
		{ label: "Tracking Speed", value: "0.9s", icon: <Speed color="info" /> },
		{ label: "Dependencies", value: 142, icon: <Schema color="warning" /> },
	];

	return (
		<PageContainer title="Data Lineage Tracker" breadcrumbs={breadcrumbs}>
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
							<Tab label="Lineage Graph" />
							<Tab label="Impact Analysis" />
							<Tab label="Dependency Map" />
						</Tabs>
					</Card>
				</Grid>

				{/* Tab Content */}
				<Grid size={12}>
					{tabValue === 0 && <LineageGraph />}
					{tabValue === 1 && <ImpactAnalysis />}
					{tabValue === 2 && <DependencyMap />}
				</Grid>
			</Grid>
		</PageContainer>
	);
}
