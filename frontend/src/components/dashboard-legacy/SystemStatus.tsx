/**
 * System Status - 시스템 상태 모니터링
 *
 * Epic 1: Story 1.1 - API 연결 상태, 데이터 최신성 확인
 */
"use client";

import type { HealthResponse } from "@/client";
import { useMarketData } from "@/hooks/useMarketData";
import { CheckCircle, Error as ErrorIcon, Warning } from "@mui/icons-material";
import { Box, Card, CardContent, Chip, Typography } from "@mui/material";

export default function SystemStatus() {
	const { healthCheck, isLoading } = useMarketData();
	const health = healthCheck as HealthResponse | undefined;

	const getStatusIcon = (status?: string) => {
		switch (status) {
			case "healthy":
				return <CheckCircle color="success" />;
			case "degraded":
				return <Warning color="warning" />;
			case "unhealthy":
				return <ErrorIcon color="error" />;
			default:
				return <Warning color="disabled" />;
		}
	};

	const getStatusLabel = (status?: string) => {
		switch (status) {
			case "healthy":
				return "정상";
			case "degraded":
				return "경고";
			case "unhealthy":
				return "오류";
			default:
				return "확인 중";
		}
	};

	const getStatusColor = (status?: string) => {
		switch (status) {
			case "healthy":
				return "success";
			case "degraded":
				return "warning";
			case "unhealthy":
				return "error";
			default:
				return "default";
		}
	};

	if (isLoading.healthCheck) {
		return (
			<Card>
				<CardContent>
					<Typography variant="h6" gutterBottom>
						시스템 상태
					</Typography>
					<Typography color="text.secondary">확인 중...</Typography>
				</CardContent>
			</Card>
		);
	}

	return (
		<Card>
			<CardContent>
				<Typography variant="h6" gutterBottom>
					시스템 상태
				</Typography>
				<Box display="flex" flexDirection="column" gap={2}>
					<Box
						display="flex"
						alignItems="center"
						justifyContent="space-between"
					>
						<Box display="flex" alignItems="center" gap={1}>
							{getStatusIcon(health?.status)}
							<Typography variant="body2">전체 상태</Typography>
						</Box>
						<Chip
							label={getStatusLabel(health?.status)}
							size="small"
							color={getStatusColor(health?.status) as any}
						/>
					</Box>

					{Object.entries(health?.checks || {}).map(
						([key, check]: [string, any]) => (
							<Box
								key={key}
								display="flex"
								alignItems="center"
								justifyContent="space-between"
							>
								<Box display="flex" alignItems="center" gap={1}>
									{getStatusIcon(check?.status)}
									<Typography variant="body2">
										{key === "database"
											? "데이터베이스"
											: key === "alpha_vantage"
												? "Alpha Vantage API"
												: key === "cache"
													? "캐시"
													: key}
									</Typography>
								</Box>
								<Chip
									label={getStatusLabel(check?.status)}
									size="small"
									color={getStatusColor(check?.status) as any}
								/>
							</Box>
						),
					)}
				</Box>
			</CardContent>
		</Card>
	);
}
