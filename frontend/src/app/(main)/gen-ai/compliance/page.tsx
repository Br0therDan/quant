"use client";

import { AuditTrail } from "@/components/gen-ai/compliance/AuditTrail";
import { ComplianceChecker } from "@/components/gen-ai/compliance/ComplianceChecker";
import { RegulatoryAlerts } from "@/components/gen-ai/compliance/RegulatoryAlerts";
import PageContainer from "@/components/layout/PageContainer";
import { CheckCircle, Gavel, VerifiedUser, Warning } from "@mui/icons-material";
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
 * Compliance 페이지
 *
 * User Story: US-23 (규정 준수 검증)
 * 기능:
 * - 전략 규정 준수 검사
 * - 규제 알림 및 경고
 * - 감사 추적 (Audit Trail)
 */
export default function CompliancePage() {
	const [tabValue, setTabValue] = useState(0);

	const breadcrumbs = [
		{ title: "GenAI Platform", href: "/gen-ai" },
		{ title: "Compliance" },
	];

	const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
		setTabValue(newValue);
	};

	// Mock KPI data
	const kpiData = [
		{
			label: "Compliance Checks",
			value: 234,
			icon: <VerifiedUser color="primary" />,
		},
		{ label: "Active Alerts", value: 3, icon: <Warning color="error" /> },
		{ label: "Pass Rate", value: "97%", icon: <CheckCircle color="success" /> },
		{ label: "Audit Events", value: 1256, icon: <Gavel color="info" /> },
	];

	return (
		<PageContainer title="Compliance & Regulatory" breadcrumbs={breadcrumbs}>
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
							<Tab label="Compliance Checker" />
							<Tab label="Regulatory Alerts" />
							<Tab label="Audit Trail" />
						</Tabs>
					</Card>
				</Grid>

				{/* Tab Content */}
				<Grid size={12}>
					{tabValue === 0 && <ComplianceChecker />}
					{tabValue === 1 && <RegulatoryAlerts />}
					{tabValue === 2 && <AuditTrail />}
				</Grid>
			</Grid>
		</PageContainer>
	);
}
