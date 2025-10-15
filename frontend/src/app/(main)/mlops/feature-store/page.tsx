"use client";

import { useState } from "react";
import { Box, Grid, Card, CardContent, Typography } from "@mui/material";
import { AccountTree, Dataset, Update, TrendingUp } from "@mui/icons-material";
import PageContainer from "@/components/layout/PageContainer";
import { FeatureList } from "@/components/mlops/feature-store/FeatureList";
import { DatasetExplorer } from "@/components/mlops/feature-store/DatasetExplorer";
import { useFeatureStore } from "@/hooks/useFeatureStore";
import { useRouter } from "next/navigation";

/**
 * Feature Store 메인 페이지
 *
 * User Story: US-16 (피처 스토어 탐색)
 * 기능:
 * - Feature 목록 조회 (필터링, 정렬)
 * - Dataset 탐색
 * - Feature 생성 버튼 → 상세 페이지 이동
 * - 통계 대시보드
 */
export default function FeatureStorePage() {
  const router = useRouter();
  const {
    featuresList: features,
  } = useFeatureStore();
  const [, setSelectedDataset] = useState<string | null>(null);  // 통계 계산
  const totalFeatures = features?.length || 0;
  const activeFeatures = features?.filter((f) => f.status === "active").length || 0;
  const totalVersions = features?.length || 0; // 버전 수는 Feature 모델에 versions 필드가 없으므로 단순화
  const recentlyUpdated = features?.filter((f) => {
    if (!f.updated_at) return false;
    const daysSinceUpdate = (Date.now() - new Date(f.updated_at).getTime()) / (1000 * 60 * 60 * 24);
    return daysSinceUpdate < 7;
  }).length || 0;

  const handleFeatureClick = (featureId: string) => {
    router.push(`/mlops/feature-store/${featureId}`);
  };

  const handleCreateClick = () => {
    router.push("/mlops/feature-store/create");
  };

  const breadcrumbs = [
    { title: "MLOps Platform", href: "/mlops" },
    { title: "Feature Store" },
  ];

  return (
    <PageContainer title="Feature Store" breadcrumbs={breadcrumbs}>
      <Grid container spacing={3}>
        {/* KPI Cards */}
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}>
                <AccountTree color="primary" />
                <Typography variant="h6">{totalFeatures}</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Total Features
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}>
                <TrendingUp color="success" />
                <Typography variant="h6">{activeFeatures}</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Active Features
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}>
                <Dataset color="info" />
                <Typography variant="h6">{totalVersions}</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Total Versions
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}>
                <Update color="warning" />
                <Typography variant="h6">{recentlyUpdated}</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Updated This Week
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Main Content */}
        <Grid size={{ xs: 12, md: 8 }}>
          <FeatureList
            onFeatureClick={handleFeatureClick}
            onCreateClick={handleCreateClick}
          />
        </Grid>

        {/* Side Panel */}
        <Grid size={{ xs: 12, md: 4 }}>
          <DatasetExplorer onDatasetSelect={setSelectedDataset} />
        </Grid>
      </Grid>
    </PageContainer>
  );
}
