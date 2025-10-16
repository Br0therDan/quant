"use client";

import PageContainer from "@/components/layout/PageContainer";
import { AutoTuner } from "@/components/optimization/hyperparameter/AutoTuner";
import { ParameterGrid } from "@/components/optimization/hyperparameter/ParameterGrid";
import { TuningHistory } from "@/components/optimization/hyperparameter/TuningHistory";
import { useOptimization } from "@/hooks/useOptimization";
import { CheckCircle, Psychology, Speed, Tune } from "@mui/icons-material";
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
 * Hyperparameter Tuning 페이지
 *
 * User Story: US-25 (자동 하이퍼파라미터 최적화)
 * 기능:
 * - 자동 튜닝 (Grid Search, Random Search, Bayesian Optimization)
 * - 파라미터 그리드 설정
 * - 튜닝 히스토리 및 결과
 */
export default function HyperparameterTuningPage() {
  const [tabValue, setTabValue] = useState(0);

  const breadcrumbs = [
    { title: "Optimization", href: "/optimization" },
    { title: "Hyperparameter Tuning" },
  ];

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  // Backend data from useOptimization hook
  const { studies, isLoading } = useOptimization();

  // KPI data from backend
  const activeStudies =
    studies?.studies?.filter((s) => s.status === "running").length || 0;
  const completedStudies =
    studies?.studies?.filter((s) => s.status === "completed").length || 0;

  const kpiData = [
    {
      label: "Active Tuning Jobs",
      value: activeStudies,
      icon: <Tune color="primary" />,
    },
    {
      label: "Best Performance",
      value: "-",
      icon: <Psychology color="success" />,
    },
    { label: "Avg Tuning Time", value: "-", icon: <Speed color="info" /> },
    {
      label: "Completed Jobs",
      value: completedStudies,
      icon: <CheckCircle color="warning" />,
    },
  ];

  if (isLoading) {
    return (
      <PageContainer title="Hyperparameter Tuning" breadcrumbs={breadcrumbs}>
        <Box sx={{ display: "flex", justifyContent: "center", py: 8 }}>
          <CircularProgress />
        </Box>
      </PageContainer>
    );
  }

  return (
    <PageContainer title="Hyperparameter Tuning" breadcrumbs={breadcrumbs}>
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
              <Tab label="Auto Tuner" />
              <Tab label="Parameter Grid" />
              <Tab label="Tuning History" />
            </Tabs>
          </Card>
        </Grid>

        {/* Tab Content */}
        <Grid size={12}>
          {tabValue === 0 && <AutoTuner />}
          {tabValue === 1 && <ParameterGrid />}
          {tabValue === 2 && <TuningHistory />}
        </Grid>
      </Grid>
    </PageContainer>
  );
}
