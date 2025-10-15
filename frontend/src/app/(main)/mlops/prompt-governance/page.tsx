"use client";

import PageContainer from "@/components/layout/PageContainer";
import { PromptTemplateEditor } from "@/components/mlops/prompt-governance/PromptTemplateEditor";
import { UsageAnalytics } from "@/components/mlops/prompt-governance/UsageAnalytics";
import { VersionControl } from "@/components/mlops/prompt-governance/VersionControl";
import { Analytics, Edit, Storage, Verified } from "@mui/icons-material";
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
 * Prompt Governance 페이지
 *
 * User Story: US-19 (프롬프트 템플릿 관리, 버전 제어, 사용 분석)
 * 기능:
 * - 프롬프트 템플릿 에디터 (생성, 수정, 테스트)
 * - 버전 제어 (히스토리, 롤백)
 * - 사용 분석 (토큰 소비, 성능 메트릭)
 */
export default function PromptGovernancePage() {
  const [tabValue, setTabValue] = useState(0);

  const breadcrumbs = [
    { title: "MLOps Platform", href: "/mlops" },
    { title: "Prompt Governance" },
  ];

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  // Mock KPI data
  const kpiData = [
    { label: "Active Templates", value: 23, icon: <Edit color="primary" /> },
    {
      label: "Template Versions",
      value: 87,
      icon: <Storage color="success" />,
    },
    {
      label: "Avg Token Usage",
      value: "1.2K",
      icon: <Analytics color="info" />,
    },
    {
      label: "Approval Rate",
      value: "94%",
      icon: <Verified color="warning" />,
    },
  ];

  return (
    <PageContainer title="Prompt Governance" breadcrumbs={breadcrumbs}>
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
              <Tab label="Template Editor" />
              <Tab label="Version Control" />
              <Tab label="Usage Analytics" />
            </Tabs>
          </Card>
        </Grid>

        {/* Tab Content */}
        <Grid size={12}>
          {tabValue === 0 && <PromptTemplateEditor />}
          {tabValue === 1 && <VersionControl />}
          {tabValue === 2 && <UsageAnalytics />}
        </Grid>
      </Grid>
    </PageContainer>
  );
}
