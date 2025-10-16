"use client";

import { ReportGenerator } from "@/components/gen-ai/narrative-reports/ReportGenerator";
import { ReportHistory } from "@/components/gen-ai/narrative-reports/ReportHistory";
import { ReportTemplates } from "@/components/gen-ai/narrative-reports/ReportTemplates";
import PageContainer from "@/components/layout/PageContainer";
import { useBacktest } from "@/hooks/useBacktests";
import { AutoAwesome, Description, Download, Speed } from "@mui/icons-material";
import {
  Box,
  Card,
  CardContent,
  CircularProgress,
  Grid,
  Tab,
  Tabs,
  Typography,
} from "@mui/material";
import { useState } from "react";

/**
 * Narrative Reports 페이지
 *
 * User Story: US-22 (AI 생성 리포트)
 * 기능:
 * - 자동 리포트 생성 (백테스트 결과, 전략 분석)
 * - 리포트 템플릿 관리
 * - 히스토리 및 내보내기
 */
export default function NarrativeReportsPage() {
  const [tabValue, setTabValue] = useState(0);

  const breadcrumbs = [
    { title: "GenAI Platform", href: "/gen-ai" },
    { title: "Narrative Reports" },
  ];

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  // Backend data from useBacktest hook
  const { backtestList, isLoading } = useBacktest();

  // KPI data from backend
  const totalReports = backtestList?.backtests?.length || 0;
  const reportsWithResults =
    backtestList?.backtests?.filter((bt) => bt.status === "completed").length ||
    0;

  const kpiData = [
    {
      label: "Generated Reports",
      value: totalReports,
      icon: <Description color="primary" />,
    },
    {
      label: "Completed Backtests",
      value: reportsWithResults,
      icon: <AutoAwesome color="success" />,
    },
    { label: "Avg Gen Time", value: "8.4s", icon: <Speed color="info" /> },
    { label: "Downloads", value: "-", icon: <Download color="warning" /> },
  ];

  if (isLoading) {
    return (
      <PageContainer title="Narrative Reports" breadcrumbs={breadcrumbs}>
        <Box sx={{ display: "flex", justifyContent: "center", py: 8 }}>
          <CircularProgress />
        </Box>
      </PageContainer>
    );
  }

  return (
    <PageContainer title="Narrative Reports" breadcrumbs={breadcrumbs}>
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
              <Tab label="Generate Report" />
              <Tab label="Templates" />
              <Tab label="History" />
            </Tabs>
          </Card>
        </Grid>

        {/* Tab Content */}
        <Grid size={12}>
          {tabValue === 0 && <ReportGenerator />}
          {tabValue === 1 && <ReportTemplates />}
          {tabValue === 2 && <ReportHistory />}
        </Grid>
      </Grid>
    </PageContainer>
  );
}
