"use client";

import PageContainer from "@/components/layout/PageContainer";
import { DeploymentPipeline } from "@/components/mlops/model-lifecycle/DeploymentPipeline";
import { MetricsTracker } from "@/components/mlops/model-lifecycle/MetricsTracker";
import { useModelDetail } from "@/hooks/useModelLifecycle";
import {
	CalendarToday,
	Science,
	Settings,
	TrendingUp,
} from "@mui/icons-material";
import {
	Box,
	Card,
	CardContent,
	Chip,
	Grid,
	Tab,
	Tabs,
	Typography,
} from "@mui/material";
import { useParams } from "next/navigation";
import { useState } from "react";

/**
 * Model 상세 페이지
 *
 * User Story: US-17 (Drift 감지, 배포)
 * 기능:
 * - 모델 메타데이터 (버전, 알고리즘, 하이퍼파라미터)
 * - 메트릭 추적 (정확도, 손실, 커스텀 메트릭)
 * - 배포 파이프라인 (Staging → Production)
 * - Drift 감지 대시보드
 * - 모델 비교 (버전 간)
 */
export default function ModelDetailPage() {
	const params = useParams();
	const modelId = params.id as string;
	const [modelName, version] = modelId.split(":");

	const { modelDetail: model, isLoading } = useModelDetail(modelName, version);
	const [tabValue, setTabValue] = useState(0);

	const breadcrumbs = [
		{ title: "MLOps Platform", href: "/mlops" },
		{ title: "Model Lifecycle", href: "/mlops/model-lifecycle" },
		{ title: model?.model_name || modelId },
	];

	const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
		setTabValue(newValue);
	};

	if (isLoading) {
		return (
			<PageContainer title="Loading..." breadcrumbs={breadcrumbs}>
				<Card>
					<CardContent>
						<Typography>모델 정보를 불러오는 중...</Typography>
					</CardContent>
				</Card>
			</PageContainer>
		);
	}

	if (!model) {
		return (
			<PageContainer title="Model Not Found" breadcrumbs={breadcrumbs}>
				<Card>
					<CardContent>
						<Typography variant="h6" color="text.secondary">
							모델을 찾을 수 없습니다.
						</Typography>
						<Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
							Model ID: {modelId}
						</Typography>
					</CardContent>
				</Card>
			</PageContainer>
		);
	}

	return (
		<PageContainer
			title={`Model: ${model.model_name}`}
			breadcrumbs={breadcrumbs}
		>
			<Grid container spacing={3}>
				{/* Model 헤더 */}
				<Grid size={12}>
					<Card>
						<CardContent>
							<Box
								sx={{
									display: "flex",
									justifyContent: "space-between",
									alignItems: "flex-start",
								}}
							>
								<Box sx={{ flex: 1 }}>
									<Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
										<Science color="primary" sx={{ fontSize: 28 }} />
										<Typography variant="h5">{model.model_name}</Typography>
										<Chip
											label={model.stage}
											color={
												model.stage === "production" ? "success" : "default"
											}
											size="small"
										/>
									</Box>
									<Typography
										variant="body2"
										color="text.secondary"
										sx={{ mt: 1 }}
									>
										모델 버전 {model.version}
									</Typography>
								</Box>
							</Box>

							<Box sx={{ display: "flex", gap: 3, flexWrap: "wrap", mt: 2 }}>
								<Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
									<Settings fontSize="small" color="action" />
									<Typography variant="body2">
										<strong>Stage:</strong> {model.stage}
									</Typography>
								</Box>
								<Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
									<CalendarToday fontSize="small" color="action" />
									<Typography variant="body2">
										<strong>Created:</strong>{" "}
										{model.created_at
											? new Date(model.created_at).toLocaleDateString()
											: "N/A"}
									</Typography>
								</Box>
							</Box>
						</CardContent>
					</Card>
				</Grid>

				{/* 메트릭 카드 */}
				{model.metrics && model.metrics.length > 0 && (
					<Grid size={12}>
						<Card>
							<CardContent>
								<Box
									sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2 }}
								>
									<TrendingUp color="primary" />
									<Typography variant="h6">Performance Metrics</Typography>
								</Box>
								<Box sx={{ display: "flex", gap: 3, flexWrap: "wrap" }}>
									{model.metrics.map((metric) => (
										<Box key={metric.metric_name}>
											<Typography variant="body2" color="text.secondary">
												{metric.metric_name}
											</Typography>
											<Typography variant="h6">
												{metric.value.toFixed(4)}
											</Typography>
										</Box>
									))}
								</Box>
							</CardContent>
						</Card>
					</Grid>
				)}

				{/* Tabs */}
				<Grid size={12}>
					<Card>
						<Tabs
							value={tabValue}
							onChange={handleTabChange}
							sx={{ borderBottom: 1, borderColor: "divider" }}
						>
							<Tab label="Deployment Pipeline" />
							<Tab label="Metrics Tracking" />
							<Tab label="Hyperparameters" />
							<Tab label="Model Comparison" />
						</Tabs>
					</Card>
				</Grid>

				{/* Tab Content */}
				<Grid size={12}>
					{tabValue === 0 && <DeploymentPipeline deploymentId={model.run_id} />}
					{tabValue === 1 && <MetricsTracker experimentId={model.run_id} />}
					{tabValue === 2 && (
						<Card>
							<CardContent>
								<Typography variant="h6" gutterBottom>
									Hyperparameters
								</Typography>
								<Typography variant="body2" color="text.secondary">
									하이퍼파라미터 정보는 곧 추가됩니다.
								</Typography>
							</CardContent>
						</Card>
					)}
					{tabValue === 3 && (
						<Card>
							<CardContent>
								<Typography variant="h6" gutterBottom>
									Model Comparison
								</Typography>
								<Typography variant="body2" color="text.secondary">
									모델 비교 기능은 곧 추가됩니다.
								</Typography>
							</CardContent>
						</Card>
					)}
				</Grid>
			</Grid>
		</PageContainer>
	);
}
