/**
 * SectionRenderer Component
 *
 * 내러티브 리포트 섹션 타입별 렌더링
 *
 * 지원 섹션 타입:
 * - executive_summary: 요약 + 핵심 발견사항 + 결론
 * - performance_analysis: 성과 분석 (수익률, 리스크, 샤프, 낙폭, 거래 통계)
 * - strategy_insights: 전략 인사이트
 * - risk_assessment: 리스크 평가
 * - market_context: 시장 맥락
 * - recommendations: 권장사항
 *
 * Phase: 3
 * 작성일: 2025-10-14
 */

import { CheckCircle as CheckCircleIcon } from "@mui/icons-material";
import {
	Box,
	Card,
	CardContent,
	CardHeader,
	Chip,
	Divider,
	List,
	ListItem,
	ListItemText,
	Stack,
	Typography,
} from "@mui/material";
import type React from "react";

// ========================================================================================
// Types
// ========================================================================================

export interface SectionContent {
	type:
		| "executive_summary"
		| "performance_analysis"
		| "strategy_insights"
		| "risk_assessment"
		| "market_context"
		| "recommendations";
	[key: string]: unknown;
}

export interface SectionRendererProps {
	title: string;
	icon?: React.ReactNode;
	content: SectionContent;
}

// ========================================================================================
// Main Component
// ========================================================================================

export const SectionRenderer: React.FC<SectionRendererProps> = ({
	title,
	icon,
	content,
}) => {
	// --------------------------------------------------------------------------------------
	// Executive Summary 렌더링
	// --------------------------------------------------------------------------------------

	const renderExecutiveSummary = () => {
		const { overview, key_findings } = content as unknown as {
			overview: string;
			key_findings?: string[];
		};

		return (
			<>
				<Typography variant="body1" paragraph>
					{overview}
				</Typography>

				{key_findings && key_findings.length > 0 && (
					<>
						<Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
							핵심 발견사항
						</Typography>
						<List dense>
							{key_findings.map((finding, idx) => (
								<ListItem key={idx} sx={{ py: 0.5 }}>
									<ListItemText
										primary={
											<Stack
												direction="row"
												spacing={1}
												alignItems="flex-start"
											>
												<Chip
													label={idx + 1}
													size="small"
													color="primary"
													sx={{ minWidth: 32 }}
												/>
												<Typography variant="body2">{finding}</Typography>
											</Stack>
										}
									/>
								</ListItem>
							))}
						</List>
					</>
				)}
			</>
		);
	};

	// --------------------------------------------------------------------------------------
	// Performance Analysis 렌더링
	// --------------------------------------------------------------------------------------

	const renderPerformanceAnalysis = () => {
		const {
			summary,
			return_analysis,
			risk_analysis,
			sharpe_interpretation,
			drawdown_commentary,
			trade_statistics_summary,
		} = content as unknown as {
			summary: string;
			return_analysis: string;
			risk_analysis: string;
			sharpe_interpretation: string;
			drawdown_commentary: string;
			trade_statistics_summary: string;
		};

		return (
			<>
				<Typography variant="body1" paragraph fontWeight="medium">
					{summary}
				</Typography>
				<Divider sx={{ my: 2 }} />

				{/* 수익률 분석 */}
				<Box sx={{ mb: 2 }}>
					<Typography variant="subtitle2" color="primary" gutterBottom>
						📊 수익률 분석
					</Typography>
					<Typography variant="body2" paragraph>
						{return_analysis}
					</Typography>
				</Box>

				{/* 리스크 분석 */}
				<Box sx={{ mb: 2 }}>
					<Typography variant="subtitle2" color="error" gutterBottom>
						⚠️ 리스크 분석
					</Typography>
					<Typography variant="body2" paragraph>
						{risk_analysis}
					</Typography>
				</Box>

				{/* 샤프 비율 */}
				<Box sx={{ mb: 2 }}>
					<Typography variant="subtitle2" color="success.main" gutterBottom>
						📈 샤프 비율
					</Typography>
					<Typography variant="body2" paragraph>
						{sharpe_interpretation}
					</Typography>
				</Box>

				{/* 낙폭 */}
				<Box sx={{ mb: 2 }}>
					<Typography variant="subtitle2" color="warning.main" gutterBottom>
						📉 낙폭 (Drawdown)
					</Typography>
					<Typography variant="body2" paragraph>
						{drawdown_commentary}
					</Typography>
				</Box>

				{/* 거래 통계 */}
				<Box>
					<Typography variant="subtitle2" color="info.main" gutterBottom>
						🔄 거래 통계
					</Typography>
					<Typography variant="body2">{trade_statistics_summary}</Typography>
				</Box>
			</>
		);
	};

	// --------------------------------------------------------------------------------------
	// Generic Object 렌더링 (Strategy Insights, Risk, Market, Recommendations)
	// --------------------------------------------------------------------------------------

	const renderGenericObject = () => {
		const data = content.data as Record<string, unknown>;

		if (!data) {
			return (
				<Typography variant="body2" color="text.secondary">
					데이터가 없습니다.
				</Typography>
			);
		}

		return (
			<Box>
				{Object.entries(data).map(([key, value]) => {
					// 키 포맷팅 (snake_case → Title Case)
					const formattedKey = key
						.split("_")
						.map((word) => word.charAt(0).toUpperCase() + word.slice(1))
						.join(" ");

					return (
						<Box key={key} sx={{ mb: 2 }}>
							<Typography variant="subtitle2" color="primary" gutterBottom>
								{formattedKey}
							</Typography>
							<Typography variant="body2" paragraph>
								{typeof value === "string" ? (
									value
								) : Array.isArray(value) ? (
									<List dense>
										{value.map((item, idx) => (
											<ListItem key={idx} sx={{ py: 0.5 }}>
												<CheckCircleIcon
													fontSize="small"
													color="success"
													sx={{ mr: 1 }}
												/>
												<ListItemText primary={String(item)} />
											</ListItem>
										))}
									</List>
								) : (
									JSON.stringify(value, null, 2)
								)}
							</Typography>
						</Box>
					);
				})}
			</Box>
		);
	};

	// --------------------------------------------------------------------------------------
	// Render Logic
	// --------------------------------------------------------------------------------------

	const renderContent = () => {
		switch (content.type) {
			case "executive_summary":
				return renderExecutiveSummary();
			case "performance_analysis":
				return renderPerformanceAnalysis();
			case "strategy_insights":
			case "risk_assessment":
			case "market_context":
			case "recommendations":
				return renderGenericObject();
			default:
				return (
					<Typography variant="body2" color="error">
						알 수 없는 섹션 타입: {content.type}
					</Typography>
				);
		}
	};

	// --------------------------------------------------------------------------------------
	// Component Render
	// --------------------------------------------------------------------------------------

	return (
		<Card sx={{ mb: 2 }}>
			<CardHeader
				avatar={icon}
				title={title}
				titleTypographyProps={{ variant: "h6" }}
			/>
			<Divider />
			<CardContent>{renderContent()}</CardContent>
		</Card>
	);
};
