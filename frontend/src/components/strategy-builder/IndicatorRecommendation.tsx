/**
 * IndicatorRecommendation Component
 *
 * 벡터 유사도 기반 추천 지표 표시
 *
 * Phase: 3
 * 작성일: 2025-10-14
 */

import type { IndicatorRecommendation as IndicatorRecommendationType } from "@/client";
import { ShowChart as ShowChartIcon } from "@mui/icons-material";
import {
	Box,
	Card,
	CardContent,
	Chip,
	LinearProgress,
	Stack,
	Typography,
} from "@mui/material";
import type React from "react";

export interface IndicatorRecommendationProps {
	indicators: IndicatorRecommendationType[];
}

export const IndicatorRecommendation: React.FC<
	IndicatorRecommendationProps
> = ({ indicators }) => {
	return (
		<Card sx={{ mb: 2, bgcolor: "success.light" }}>
			<CardContent>
				<Stack direction="row" spacing={2} alignItems="flex-start">
					<ShowChartIcon color="success" />
					<Box sx={{ flexGrow: 1 }}>
						<Typography variant="subtitle2" gutterBottom>
							추천 지표 ({indicators.length})
						</Typography>
						<Stack spacing={2}>
							{indicators.map((indicator, index) => (
								<Box key={index}>
									<Stack
										direction="row"
										spacing={1}
										alignItems="center"
										sx={{ mb: 1 }}
									>
										<Typography variant="body2" fontWeight="bold">
											{indicator.indicator_name}
										</Typography>
										<Chip
											label={`${(indicator.similarity_score * 100).toFixed(
												0,
											)}%`}
											color={
												indicator.similarity_score > 0.7 ? "success" : "default"
											}
											size="small"
										/>
									</Stack>
									<LinearProgress
										variant="determinate"
										value={indicator.similarity_score * 100}
										color={
											indicator.similarity_score > 0.7 ? "success" : "info"
										}
										sx={{ height: 6, borderRadius: 1 }}
									/>
									{indicator.rationale && (
										<Typography
											variant="caption"
											color="text.secondary"
											sx={{ mt: 1, display: "block" }}
										>
											{indicator.rationale}
										</Typography>
									)}
								</Box>
							))}
						</Stack>
					</Box>
				</Stack>
			</CardContent>
		</Card>
	);
};
