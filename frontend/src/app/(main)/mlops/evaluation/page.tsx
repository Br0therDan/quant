"use client";

import PageContainer from "@/components/layout/PageContainer";
import { ABTestingPanel } from "@/components/mlops/evaluation/ABTestingPanel";
import { BenchmarkSuite } from "@/components/mlops/evaluation/BenchmarkSuite";
import { FairnessAuditor } from "@/components/mlops/evaluation/FairnessAuditor";
import { Assessment, Science, Speed, VerifiedUser } from "@mui/icons-material";
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
 * Evaluation 페이지
 *
 * User Story: US-18 (벤치마크, A/B 테스트, 공정성 감사)
 * 기능:
 * - 벤치마크 스위트 (성능 비교)
 * - A/B 테스트 패널 (실험 비교)
 * - 공정성 감사 (Bias Detection)
 */
export default function EvaluationPage() {
  const [tabValue, setTabValue] = useState(0);

  const breadcrumbs = [
    { title: "MLOps Platform", href: "/mlops" },
    { title: "Evaluation & Testing" },
  ];

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  // Mock KPI data
  const kpiData = [
    {
      label: "Active Benchmarks",
      value: 12,
      icon: <Science color="primary" />,
    },
    {
      label: "A/B Tests Running",
      value: 5,
      icon: <Assessment color="success" />,
    },
    { label: "Models Evaluated", value: 48, icon: <Speed color="info" /> },
    {
      label: "Fairness Score",
      value: "95%",
      icon: <VerifiedUser color="warning" />,
    },
  ];

  return (
    <PageContainer title="Evaluation & Testing" breadcrumbs={breadcrumbs}>
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
              <Tab label="Benchmarks" />
              <Tab label="A/B Testing" />
              <Tab label="Fairness Audit" />
            </Tabs>
          </Card>
        </Grid>

        {/* Tab Content */}
        <Grid size={12}>
          {tabValue === 0 && <BenchmarkSuite />}
          {tabValue === 1 && <ABTestingPanel />}
          {tabValue === 2 && <FairnessAuditor />}
        </Grid>
      </Grid>
    </PageContainer>
  );
}
