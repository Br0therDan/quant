/**
 * Data Status Card - 종목별 데이터 커버리지 및 상태
 *
 * Epic 2: Story 2.2 - 데이터 수집 상태 모니터링
 */
"use client";

import {
	CheckCircle,
	Error as ErrorIcon,
	Info as InfoIcon,
	Refresh as RefreshIcon,
	Warning,
} from "@mui/icons-material";
import {
	Box,
	Card,
	CardContent,
	Chip,
	IconButton,
	LinearProgress,
	Stack,
	Tooltip,
	Typography,
} from "@mui/material";
import { useState } from "react";

interface DataStatusCardProps {
	symbol: string;
	coverageData?: {
		symbol: string;
		company_info: {
			available: boolean;
			last_update?: string | null;
			data_quality?: string;
			error?: string;
		};
		market_data: {
			available: boolean;
			last_update?: string | null;
			data_points?: number;
			date_range?: string | null;
			error?: string;
		};
		overall_status: "complete" | "partial" | "incomplete";
	};
	onRefresh?: () => Promise<void>;
	isLoading?: boolean;
}

export default function DataStatusCard({
	symbol,
	coverageData,
	onRefresh,
	isLoading = false,
}: DataStatusCardProps) {
	const [isRefreshing, setIsRefreshing] = useState(false);

	const getStatusColor = (status: string) => {
		switch (status) {
			case "complete":
				return "success";
			case "partial":
				return "warning";
			case "incomplete":
				return "error";
			default:
				return "default";
		}
	};

	const getStatusLabel = (status: string) => {
		switch (status) {
			case "complete":
				return "완료";
			case "partial":
				return "부분적";
			case "incomplete":
				return "미완료";
			default:
				return "확인 중";
		}
	};

	const getStatusIcon = (available: boolean, error?: string) => {
		if (error) return <ErrorIcon color="error" fontSize="small" />;
		if (available) return <CheckCircle color="success" fontSize="small" />;
		return <Warning color="warning" fontSize="small" />;
	};

	const formatDate = (dateString?: string | null) => {
		if (!dateString) return "-";
		try {
			return new Date(dateString).toLocaleString("ko-KR", {
				year: "numeric",
				month: "2-digit",
				day: "2-digit",
				hour: "2-digit",
				minute: "2-digit",
			});
		} catch {
			return dateString;
		}
	};

	const handleRefresh = async () => {
		if (!onRefresh || isRefreshing) return;
		setIsRefreshing(true);
		try {
			await onRefresh();
		} finally {
			setIsRefreshing(false);
		}
	};

	const dataQualityScore = coverageData
		? (coverageData.company_info.available ? 50 : 0) +
			(coverageData.market_data.available ? 50 : 0)
		: 0;

	return (
		<Card>
			<CardContent>
				<Box
					display="flex"
					alignItems="center"
					justifyContent="space-between"
					mb={2}
				>
					<Box display="flex" alignItems="center" gap={1}>
						<Typography variant="h6">{symbol}</Typography>
						{coverageData && (
							<Chip
								label={getStatusLabel(coverageData.overall_status)}
								size="small"
								color={getStatusColor(coverageData.overall_status) as any}
							/>
						)}
					</Box>
					<Tooltip title="데이터 새로고침">
						<IconButton
							size="small"
							onClick={handleRefresh}
							disabled={isRefreshing || isLoading}
						>
							<RefreshIcon fontSize="small" />
						</IconButton>
					</Tooltip>
				</Box>

				{isLoading || isRefreshing ? (
					<LinearProgress />
				) : coverageData ? (
					<Stack spacing={2}>
						{/* 데이터 품질 점수 */}
						<Box>
							<Box
								display="flex"
								alignItems="center"
								justifyContent="space-between"
								mb={1}
							>
								<Typography variant="caption" color="text.secondary">
									데이터 품질
								</Typography>
								<Typography variant="caption" fontWeight="medium">
									{dataQualityScore}%
								</Typography>
							</Box>
							<LinearProgress
								variant="determinate"
								value={dataQualityScore}
								color={dataQualityScore === 100 ? "success" : "warning"}
							/>
						</Box>

						{/* 기업 정보 */}
						<Box>
							<Box
								display="flex"
								alignItems="center"
								justifyContent="space-between"
							>
								<Box display="flex" alignItems="center" gap={1}>
									{getStatusIcon(
										coverageData.company_info.available,
										coverageData.company_info.error,
									)}
									<Typography variant="body2">기업 정보</Typography>
								</Box>
								<Box textAlign="right">
									<Typography variant="caption" color="text.secondary">
										{coverageData.company_info.available ? "수집됨" : "미수집"}
									</Typography>
									{coverageData.company_info.last_update && (
										<Typography
											variant="caption"
											display="block"
											color="text.secondary"
										>
											{formatDate(coverageData.company_info.last_update)}
										</Typography>
									)}
								</Box>
							</Box>
							{coverageData.company_info.error && (
								<Typography
									variant="caption"
									color="error.main"
									sx={{ mt: 0.5 }}
								>
									오류: {coverageData.company_info.error}
								</Typography>
							)}
						</Box>

						{/* 주가 데이터 */}
						<Box>
							<Box
								display="flex"
								alignItems="center"
								justifyContent="space-between"
							>
								<Box display="flex" alignItems="center" gap={1}>
									{getStatusIcon(
										coverageData.market_data.available,
										coverageData.market_data.error,
									)}
									<Typography variant="body2">주가 데이터</Typography>
								</Box>
								<Box textAlign="right">
									<Typography variant="caption" color="text.secondary">
										{coverageData.market_data.data_points
											? `${coverageData.market_data.data_points.toLocaleString()}개`
											: "미수집"}
									</Typography>
									{coverageData.market_data.last_update && (
										<Typography
											variant="caption"
											display="block"
											color="text.secondary"
										>
											{formatDate(coverageData.market_data.last_update)}
										</Typography>
									)}
								</Box>
							</Box>
							{coverageData.market_data.date_range && (
								<Typography
									variant="caption"
									color="text.secondary"
									sx={{ mt: 0.5 }}
								>
									기간: {coverageData.market_data.date_range}
								</Typography>
							)}
							{coverageData.market_data.error && (
								<Typography
									variant="caption"
									color="error.main"
									sx={{ mt: 0.5 }}
								>
									오류: {coverageData.market_data.error}
								</Typography>
							)}
						</Box>

						{/* 안내 메시지 */}
						{coverageData.overall_status !== "complete" && (
							<Box
								display="flex"
								gap={1}
								sx={{
									p: 1,
									borderRadius: 1,
									bgcolor: "info.light",
									color: "info.contrastText",
								}}
							>
								<InfoIcon fontSize="small" />
								<Typography variant="caption">
									{coverageData.overall_status === "incomplete"
										? "데이터 수집이 필요합니다. 새로고침 버튼을 눌러 수집을 시작하세요."
										: "일부 데이터가 누락되었습니다."}
								</Typography>
							</Box>
						)}
					</Stack>
				) : (
					<Typography variant="body2" color="text.secondary">
						데이터 정보를 불러올 수 없습니다.
					</Typography>
				)}
			</CardContent>
		</Card>
	);
}
