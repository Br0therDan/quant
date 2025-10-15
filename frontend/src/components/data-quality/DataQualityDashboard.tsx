import type { DataQualitySeverity } from "@/client/types.gen";
import { useDataQuality } from "@/hooks/useDataQuality";
import {
	CheckCircle as CheckCircleIcon,
	TrendingDown as CriticalIcon,
	Error as ErrorIcon,
	Info as InfoIcon,
	Warning as WarningIcon,
} from "@mui/icons-material";
import {
	Alert,
	Box,
	Card,
	CardContent,
	Chip,
	CircularProgress,
	Grid,
	Typography,
} from "@mui/material";

interface StatCardProps {
	title: string;
	value: number;
	severity: DataQualitySeverity;
	icon: React.ReactNode;
}

/**
 * StatCard Component (내부 컴포넌트)
 *
 * 데이터 품질 통계 카드
 */
function StatCard({ title, value, severity, icon }: StatCardProps) {
	const getColor = (sev: DataQualitySeverity) => {
		const colors = {
			critical: "error.dark",
			high: "error.main",
			medium: "warning.main",
			low: "info.main",
			normal: "success.main",
		};
		return colors[sev];
	};

	return (
		<Card>
			<CardContent>
				<Box
					sx={{
						display: "flex",
						alignItems: "center",
						justifyContent: "space-between",
					}}
				>
					<Box>
						<Typography variant="caption" color="text.secondary">
							{title}
						</Typography>
						<Typography variant="h4" sx={{ color: getColor(severity), mt: 1 }}>
							{value.toLocaleString()}
						</Typography>
					</Box>
					<Box sx={{ color: getColor(severity) }}>{icon}</Box>
				</Box>
			</CardContent>
		</Card>
	);
}

/**
 * DataQualityDashboard Component
 *
 * 데이터 품질 모니터링 대시보드
 *
 * Features:
 * - 주요 지표 카드 (총 이벤트, 심각도별 카운트)
 * - 최근 알림 타임라인 (AlertTimeline)
 * - 심각도 분포 차트 (SeverityPieChart)
 * - 이상 징후 상세 테이블 (AnomalyDetailTable)
 * - 자동 새로고침 (1분 간격)
 *
 * @example
 * ```tsx
 * import { DataQualityDashboard } from "@/components/data-quality/DataQualityDashboard";
 *
 * function DataQualityPage() {
 *   return <DataQualityDashboard />;
 * }
 * ```
 */
export function DataQualityDashboard() {
	const { qualitySummary, totalEventsBySeverity, isLoading, isError, error } =
		useDataQuality();

	// Loading state
	if (isLoading) {
		return (
			<Box
				sx={{
					display: "flex",
					justifyContent: "center",
					alignItems: "center",
					minHeight: 400,
				}}
			>
				<CircularProgress />
			</Box>
		);
	}

	// Error state
	if (isError) {
		return (
			<Alert severity="error">
				데이터 품질 정보를 불러오는 중 오류가 발생했습니다:{" "}
				{error?.message || "알 수 없는 오류"}
			</Alert>
		);
	}

	// No data state
	if (!qualitySummary) {
		return (
			<Alert severity="info">
				데이터 품질 정보가 없습니다. 데이터를 업데이트해 주세요.
			</Alert>
		);
	}

	const totalAlerts = qualitySummary.total_alerts || 0;
	const lastUpdated = qualitySummary.last_updated
		? new Date(qualitySummary.last_updated).toLocaleString("ko-KR")
		: "정보 없음";

	return (
		<Box>
			{/* 헤더 */}
			<Box
				sx={{
					display: "flex",
					justifyContent: "space-between",
					alignItems: "center",
					mb: 3,
				}}
			>
				<Box>
					<Typography variant="h4" gutterBottom>
						데이터 품질 모니터링
					</Typography>
					<Typography variant="body2" color="text.secondary">
						마지막 업데이트: {lastUpdated}
					</Typography>
				</Box>

				{/* 상태 칩 */}
				<Chip
					label={
						totalEventsBySeverity.critical + totalEventsBySeverity.high === 0
							? "정상"
							: "주의 필요"
					}
					color={
						totalEventsBySeverity.critical + totalEventsBySeverity.high === 0
							? "success"
							: "error"
					}
					icon={
						totalEventsBySeverity.critical + totalEventsBySeverity.high ===
						0 ? (
							<CheckCircleIcon />
						) : (
							<ErrorIcon />
						)
					}
				/>
			</Box>

			{/* 주요 지표 카드 */}
			<Box sx={{ flexGrow: 1 }}>
				<Grid container spacing={3}>
					{/* 총 이벤트 */}
					<Grid size={{ xs: 12, sm: 6, md: 2.4 }}>
						<StatCard
							title="총 이벤트"
							value={totalAlerts}
							severity="normal"
							icon={<InfoIcon sx={{ fontSize: 40 }} />}
						/>
					</Grid>

					{/* 긴급 */}
					<Grid size={{ xs: 12, sm: 6, md: 2.4 }}>
						<StatCard
							title="긴급"
							value={totalEventsBySeverity.critical}
							severity="critical"
							icon={<CriticalIcon sx={{ fontSize: 40 }} />}
						/>
					</Grid>

					{/* 높음 */}
					<Grid size={{ xs: 12, sm: 6, md: 2.4 }}>
						<StatCard
							title="높음"
							value={totalEventsBySeverity.high}
							severity="high"
							icon={<ErrorIcon sx={{ fontSize: 40 }} />}
						/>
					</Grid>

					{/* 중간 */}
					<Grid size={{ xs: 12, sm: 6, md: 2.4 }}>
						<StatCard
							title="중간"
							value={totalEventsBySeverity.medium}
							severity="medium"
							icon={<WarningIcon sx={{ fontSize: 40 }} />}
						/>
					</Grid>

					{/* 낮음 */}
					<Grid size={{ xs: 12, sm: 6, md: 2.4 }}>
						<StatCard
							title="낮음"
							value={totalEventsBySeverity.low}
							severity="low"
							icon={<InfoIcon sx={{ fontSize: 40 }} />}
						/>
					</Grid>
				</Grid>
			</Box>

			{/* 최근 알림 요약 */}
			<Box sx={{ mt: 4 }}>
				<Card>
					<CardContent>
						<Typography variant="h6" gutterBottom>
							최근 알림 요약
						</Typography>

						{qualitySummary.recent_alerts &&
						qualitySummary.recent_alerts.length > 0 ? (
							<Box>
								<Typography variant="body2" color="text.secondary">
									최근 {qualitySummary.recent_alerts.length}개의 알림이
									감지되었습니다.
								</Typography>

								{/* 최근 알림 3개 미리보기 */}
								<Box sx={{ mt: 2 }}>
									{qualitySummary.recent_alerts
										.slice(0, 3)
										.map((alert, index) => (
											<Box
												key={`${alert.symbol}-${index}`}
												sx={{
													p: 2,
													mb: 1,
													border: 1,
													borderColor: "divider",
													borderRadius: 1,
												}}
											>
												<Box
													sx={{
														display: "flex",
														alignItems: "center",
														justifyContent: "space-between",
													}}
												>
													<Box
														sx={{
															display: "flex",
															alignItems: "center",
															gap: 1,
														}}
													>
														<Chip
															label={alert.symbol}
															size="small"
															variant="outlined"
														/>
														<Chip
															label={alert.severity}
															size="small"
															color={
																alert.severity === "critical" ||
																alert.severity === "high"
																	? "error"
																	: alert.severity === "medium"
																		? "warning"
																		: "info"
															}
														/>
													</Box>
													<Typography variant="caption" color="text.secondary">
														{new Date(alert.occurred_at).toLocaleString(
															"ko-KR",
														)}
													</Typography>
												</Box>
												<Typography variant="body2" sx={{ mt: 1 }}>
													{alert.message}
												</Typography>
											</Box>
										))}
								</Box>

								{qualitySummary.recent_alerts.length > 3 && (
									<Typography
										variant="caption"
										color="primary"
										sx={{ mt: 2, display: "block", textAlign: "center" }}
									>
										+ {qualitySummary.recent_alerts.length - 3}개 더 보기
									</Typography>
								)}
							</Box>
						) : (
							<Typography variant="body2" color="text.secondary">
								최근 알림이 없습니다.
							</Typography>
						)}
					</CardContent>
				</Card>
			</Box>

			{/* TODO: AlertTimeline, SeverityPieChart, AnomalyDetailTable 추가 예정 */}
			<Box sx={{ mt: 4 }}>
				<Alert severity="info">
					AlertTimeline, SeverityPieChart, AnomalyDetailTable 컴포넌트는 다음
					단계에서 추가될 예정입니다.
				</Alert>
			</Box>
		</Box>
	);
}
