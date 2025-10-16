"use client";

import { AnomalyDetection } from "@/components/data-quality/monitor/AnomalyDetection";
import { QualityMetrics } from "@/components/data-quality/monitor/QualityMetrics";
import { ValidationRules } from "@/components/data-quality/monitor/ValidationRules";
import PageContainer from "@/components/layout/PageContainer";
import { useDataQuality } from "@/hooks/useDataQuality";
import {
  BugReport,
  CheckCircle,
  Speed,
  VerifiedUser,
} from "@mui/icons-material";
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
 * Data Quality Monitor 페이지
 *
 * User Story: US-27 (데이터 품질 모니터링)
 * 기능:
 * - 데이터 품질 메트릭 (완전성, 정확성, 일관성)
 * - 이상 탐지 및 알림
 * - 검증 규칙 관리
 */
export default function DataQualityMonitorPage() {
  const [tabValue, setTabValue] = useState(0);

  const breadcrumbs = [
    { title: "Data Quality", href: "/data-quality" },
    { title: "Quality Monitor" },
  ];

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  // Backend data from useDataQuality hook
  const { qualitySummary, isLoading } = useDataQuality();

  // KPI data from backend
  const totalAlerts = qualitySummary?.total_alerts || 0;
  const criticalAlerts = qualitySummary?.severity_breakdown?.critical || 0;

  const kpiData = [
    {
      label: "Data Quality Score",
      value: "-",
      icon: <VerifiedUser color="primary" />,
    },
    {
      label: "Anomalies Detected",
      value: totalAlerts,
      icon: <BugReport color="error" />,
    },
    { label: "Validation Speed", value: "1.8s", icon: <Speed color="info" /> },
    {
      label: "Critical Alerts",
      value: criticalAlerts,
      icon: <CheckCircle color={criticalAlerts > 0 ? "error" : "success"} />,
    },
  ];

  if (isLoading) {
    return (
      <PageContainer title="Data Quality Monitor" breadcrumbs={breadcrumbs}>
        <Box sx={{ display: "flex", justifyContent: "center", py: 8 }}>
          <CircularProgress />
        </Box>
      </PageContainer>
    );
  }

  return (
    <PageContainer title="Data Quality Monitor" breadcrumbs={breadcrumbs}>
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
              <Tab label="Quality Metrics" />
              <Tab label="Anomaly Detection" />
              <Tab label="Validation Rules" />
            </Tabs>
          </Card>
        </Grid>

        {/* Tab Content */}
        <Grid size={12}>
          {tabValue === 0 && <QualityMetrics />}
          {tabValue === 1 && <AnomalyDetection />}
          {tabValue === 2 && <ValidationRules />}
        </Grid>
      </Grid>
    </PageContainer>
  );
}
