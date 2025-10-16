"use client";

import { PromptTemplateEditor } from "@/components/gen-ai/prompt-governance/PromptTemplateEditor";
import { UsageAnalytics } from "@/components/gen-ai/prompt-governance/UsageAnalytics";
import { VersionControl } from "@/components/gen-ai/prompt-governance/VersionControl";
import PageContainer from "@/components/layout/PageContainer";
import { useGenAI } from "@/hooks/useGenAI";
import { Analytics, Edit, Storage, Verified } from "@mui/icons-material";
import {
  Alert,
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
 * Prompt Governance 페이지
 *
 * User Story: US-19 (프롬프트 템플릿 관리, 버전 제어, 사용 분석)
 * 도메인: GenAI (backend/app/api/routes/gen_ai/prompt_governance.py)
 * 기능:
 * - 프롬프트 템플릿 에디터 (생성, 수정, 테스트)
 * - 버전 제어 (히스토리, 롤백)
 * - 사용 분석 (토큰 소비, 성능 메트릭)
 */
export default function PromptGovernancePage() {
  const [tabValue, setTabValue] = useState(0);

  // GenAI Hook: Prompt Governance
  const { promptTemplatesList, isLoadingTemplates, templatesError } =
    useGenAI();

  const breadcrumbs = [
    { title: "GenAI Platform", href: "/gen-ai" },
    { title: "Prompt Governance" },
  ];

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  // KPI 데이터 계산 (실제 데이터 기반)
  const kpiData = [
    {
      label: "Active Templates",
      value: promptTemplatesList?.length || 0,
      icon: <Edit color="primary" />,
    },
    {
      label: "Template Versions",
      value: "87", // TODO: 버전 수 계산 필요
      icon: <Storage color="success" />,
    },
    {
      label: "Avg Token Usage",
      value: "1.2K", // TODO: 실제 메트릭으로 대체
      icon: <Analytics color="info" />,
    },
    {
      label: "Approval Rate",
      value: "94%", // TODO: 실제 메트릭으로 대체
      icon: <Verified color="warning" />,
    },
  ];

  return (
    <PageContainer title="Prompt Governance" breadcrumbs={breadcrumbs}>
      <Grid container spacing={3}>
        {/* 로딩 및 에러 처리 */}
        {isLoadingTemplates && (
          <Grid size={12}>
            <Box sx={{ display: "flex", justifyContent: "center", p: 4 }}>
              <CircularProgress />
            </Box>
          </Grid>
        )}

        {templatesError && (
          <Grid size={12}>
            <Alert severity="error">
              프롬프트 템플릿 데이터를 불러오는 중 오류가 발생했습니다.
            </Alert>
          </Grid>
        )}

        {/* KPI 카드 */}
        {!isLoadingTemplates && !templatesError && (
          <>
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
          </>
        )}
      </Grid>
    </PageContainer>
  );
}
