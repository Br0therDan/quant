"use client";

import DashboardOverview from "@/components/dashboard/DashboardOverview";
import PopularStrategies from "@/components/dashboard/PopularStrategies";
import QuickActions from "@/components/dashboard/QuickActions";
import RecentBacktests from "@/components/dashboard/RecentBacktests";
import SystemStatus from "@/components/dashboard/SystemStatus";
import PageContainer from "@/components/layout/PageContainer";
import { Box } from "@mui/material";
import Grid from "@mui/material/Grid";

/**
 * Dashboard Page - Epic 1: Story 1.1
 *
 * Acceptance Criteria:
 * - [x] 전체 백테스트 수, 성공률, 평균 수익률 등 KPI 표시
 * - [x] 최근 실행한 백테스트 목록 (최대 5개)
 * - [x] 빠른 시작 가이드 (4단계 이내)
 * - [x] 시스템 상태 표시 (API 연결, 데이터 업데이트 상태)
 * - [x] 인기 전략 추천 섹션
 */
export default function DashboardPage() {
	return (
		<PageContainer title="Dashboard" breadcrumbs={[{ title: "Dashboard" }]}>
			<Box sx={{ flexGrow: 1 }}>
				<Grid container spacing={3}>
					{/* KPI 대시보드 개요 */}
					<Grid size={12}>
						<DashboardOverview />
					</Grid>

					{/* 빠른 시작 액션 */}
					<Grid size={12}>
						<QuickActions />
					</Grid>

					{/* 최근 백테스트 & 시스템 상태 */}
					<Grid size={{ xs: 12, lg: 8 }}>
						<RecentBacktests />
					</Grid>

					<Grid size={{ xs: 12, lg: 4 }}>
						<SystemStatus />
					</Grid>

					{/* 인기 전략 추천 */}
					<Grid size={12}>
						<PopularStrategies />
					</Grid>
				</Grid>
			</Box>
		</PageContainer>
	);
}
