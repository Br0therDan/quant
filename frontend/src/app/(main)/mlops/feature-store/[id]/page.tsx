"use client";

import { Box, Grid, Card, CardContent, Typography, Chip, Tab, Tabs } from "@mui/material";
import { AccountTree, CalendarToday, Code, DataObject } from "@mui/icons-material";
import PageContainer from "@/components/layout/PageContainer";
import { FeatureDetail } from "@/components/mlops/feature-store/FeatureDetail";
import { VersionHistory } from "@/components/mlops/feature-store/VersionHistory";
import { useFeatureStore } from "@/hooks/useFeatureStore";
import { useParams } from "next/navigation";
import { useState } from "react";

/**
 * Feature 상세 페이지
 *
 * User Story: US-16 (버전 관리, 통계)
 * 기능:
 * - Feature 메타데이터 (이름, 설명, 타입, 상태)
 * - 버전 히스토리 (타임라인)
 * - 통계 정보 (분포, 결측치, 이상치)
 * - 계보 추적 (Lineage)
 * - CRUD 작업 (수정, 삭제, 버전 생성)
 */
export default function FeatureDetailPage() {
  const params = useParams();
  const featureId = params.id as string;
  const { featuresList: features } = useFeatureStore();
  const [tabValue, setTabValue] = useState(0);

  // 현재 Feature 찾기
  const feature = features?.find((f) => f.id === featureId);

  const breadcrumbs = [
    { title: "MLOps Platform", href: "/mlops" },
    { title: "Feature Store", href: "/mlops/feature-store" },
    { title: feature?.feature_name || featureId },
  ];

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  if (!feature) {
    return (
      <PageContainer title="Feature Not Found" breadcrumbs={breadcrumbs}>
        <Card>
          <CardContent>
            <Typography variant="h6" color="text.secondary">
              Feature를 찾을 수 없습니다.
            </Typography>
          </CardContent>
        </Card>
      </PageContainer>
    );
  }

  return (
    <PageContainer title={feature.feature_name} breadcrumbs={breadcrumbs}>
      <Grid container spacing={3}>
        {/* Feature Overview Card */}
        <Grid size={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", gap: 2, mb: 2 }}>
                <AccountTree fontSize="large" color="primary" />
                <Box sx={{ flexGrow: 1 }}>
                  <Typography variant="h5" gutterBottom>
                    {feature.feature_name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {feature.description || "설명 없음"}
                  </Typography>
                </Box>
                <Chip
                  label={feature.status}
                  color={feature.status === "active" ? "success" : "default"}
                  size="small"
                />
              </Box>

              <Box sx={{ display: "flex", gap: 3, flexWrap: "wrap" }}>
                <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                  <DataObject fontSize="small" color="action" />
                  <Typography variant="body2">
                    <strong>Type:</strong> {feature.feature_type}
                  </Typography>
                </Box>
                <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                  <Code fontSize="small" color="action" />
                  <Typography variant="body2">
                    <strong>Data Type:</strong> {feature.data_type}
                  </Typography>
                </Box>
                <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                  <CalendarToday fontSize="small" color="action" />
                  <Typography variant="body2">
                    <strong>Created:</strong>{" "}
                    {feature.created_at
                      ? new Date(feature.created_at).toLocaleDateString()
                      : "N/A"}
                  </Typography>
                </Box>
                {feature.updated_at && (
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                    <CalendarToday fontSize="small" color="action" />
                    <Typography variant="body2">
                      <strong>Updated:</strong>{" "}
                      {new Date(feature.updated_at).toLocaleDateString()}
                    </Typography>
                  </Box>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Tabs */}
        <Grid size={12}>
          <Card>
            <Tabs value={tabValue} onChange={handleTabChange} sx={{ borderBottom: 1, borderColor: "divider" }}>
              <Tab label="Details" />
              <Tab label="Version History" />
              <Tab label="Statistics" />
              <Tab label="Lineage" />
            </Tabs>
          </Card>
        </Grid>

        {/* Feature Detail */}
        <Grid size={{ xs: 12, md: 8 }}>
          {tabValue === 0 && <FeatureDetail featureId={featureId} />}
          {tabValue === 1 && <VersionHistory featureId={featureId} />}
          {tabValue === 2 && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Statistics
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  통계 정보는 곧 추가됩니다.
                </Typography>
              </CardContent>
            </Card>
          )}
          {tabValue === 3 && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Lineage
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  계보 추적 기능은 곧 추가됩니다.
                </Typography>
              </CardContent>
            </Card>
          )}
        </Grid>

        {/* Side Panel - Quick Actions */}
        <Grid size={{ xs: 12, md: 4 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  • Edit Feature
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  • Create New Version
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  • Delete Feature
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  • Export Metadata
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </PageContainer>
  );
}
