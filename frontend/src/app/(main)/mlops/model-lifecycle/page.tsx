"use client";

import PageContainer from "@/components/layout/PageContainer";
import { ExperimentList } from "@/components/mlops/model-lifecycle/ExperimentList";
import { ModelRegistry } from "@/components/mlops/model-lifecycle/ModelRegistry";
import { useModelLifecycle } from "@/hooks/useModelLifecycle";
import {
	CheckCircle,
	ModelTraining,
	Pending,
	Science,
} from "@mui/icons-material";
import { Box, Card, CardContent, Grid, Typography } from "@mui/material";
import { useRouter } from "next/navigation";

/**
 * Model Lifecycle 메인 페이지
 *
 * User Story: US-17 (모델 라이프사이클 관리)
 * 기능:
 * - Experiment 목록 (진행 상태별 필터)
 * - Model Registry (배포 상태별 필터)
 * - 실험 생성 버튼 → 생성 폼
 * - 모델 배포 파이프라인 접근
 * - KPI: 총 실험 수, 배포된 모델 수, 평균 성능
 */
export default function ModelLifecyclePage() {
	const router = useRouter();
	const { experimentsList: experiments, deploymentsList: deployments } =
		useModelLifecycle();

	// 통계 계산
	const totalExperiments = experiments?.length || 0;
	const activeExperiments =
		experiments?.filter((e) => e.status === "active").length || 0;
	const totalModels = deployments?.length || 0;
	const deployedModels =
		deployments?.filter(
			(d) => d.status === "deploying" || d.status === "validating",
		).length || 0;

	const handleExperimentClick = (experimentId: string) => {
		router.push(`/mlops/model-lifecycle/experiments/${experimentId}`);
	};

	const breadcrumbs = [
		{ title: "MLOps Platform", href: "/mlops" },
		{ title: "Model Lifecycle" },
	];

	return (
		<PageContainer title="Model Lifecycle" breadcrumbs={breadcrumbs}>
			<Grid container spacing={3}>
				{/* Statistics */}
				<Grid size={{ xs: 12, sm: 6, md: 3 }}>
					<Card>
						<CardContent>
							<Box
								sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}
							>
								<Science color="primary" />
								<Typography variant="h6">{totalExperiments}</Typography>
							</Box>
							<Typography variant="body2" color="text.secondary">
								Total Experiments
							</Typography>
						</CardContent>
					</Card>
				</Grid>

				<Grid size={{ xs: 12, sm: 6, md: 3 }}>
					<Card>
						<CardContent>
							<Box
								sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}
							>
								<Pending color="warning" />
								<Typography variant="h6">{activeExperiments}</Typography>
							</Box>
							<Typography variant="body2" color="text.secondary">
								Running Experiments
							</Typography>
						</CardContent>
					</Card>
				</Grid>

				<Grid size={{ xs: 12, sm: 6, md: 3 }}>
					<Card>
						<CardContent>
							<Box
								sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}
							>
								<ModelTraining color="info" />
								<Typography variant="h6">{totalModels}</Typography>
							</Box>
							<Typography variant="body2" color="text.secondary">
								Registered Models
							</Typography>
						</CardContent>
					</Card>
				</Grid>

				<Grid size={{ xs: 12, sm: 6, md: 3 }}>
					<Card>
						<CardContent>
							<Box
								sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}
							>
								<CheckCircle color="success" />
								<Typography variant="h6">{deployedModels}</Typography>
							</Box>
							<Typography variant="body2" color="text.secondary">
								Deployed Models
							</Typography>
						</CardContent>
					</Card>
				</Grid>

				{/* Experiments */}
				<Grid size={{ xs: 12, md: 6 }}>
					<ExperimentList onExperimentClick={handleExperimentClick} />
				</Grid>

				{/* Model Registry */}
				<Grid size={{ xs: 12, md: 6 }}>
					<ModelRegistry />
				</Grid>
			</Grid>
		</PageContainer>
	);
}
