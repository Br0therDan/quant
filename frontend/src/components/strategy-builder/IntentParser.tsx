/**
 * IntentParser Component
 *
 * LLM 의도 파싱 결과 표시
 *
 * Phase: 3
 * 작성일: 2025-10-14
 */

import type { ParsedIntent } from "@/client";
import { Psychology as PsychologyIcon } from "@mui/icons-material";
import { Box, Card, CardContent, Chip, Stack, Typography } from "@mui/material";
import type React from "react";

export interface IntentParserProps {
	intent: ParsedIntent;
}

export const IntentParser: React.FC<IntentParserProps> = ({ intent }) => {
	return (
		<Card sx={{ mb: 2, bgcolor: "info.light" }}>
			<CardContent>
				<Stack direction="row" spacing={2} alignItems="center">
					<PsychologyIcon color="info" />
					<Box sx={{ flexGrow: 1 }}>
						<Typography variant="subtitle2" gutterBottom>
							AI 의도 파싱 결과
						</Typography>
						<Stack direction="row" spacing={1} flexWrap="wrap">
							<Chip
								label={`의도: ${intent.intent_type}`}
								color="info"
								size="small"
							/>
							<Chip
								label={`신뢰도: ${(intent.confidence * 100).toFixed(0)}%`}
								color={intent.confidence > 0.7 ? "success" : "warning"}
								size="small"
							/>
							{intent.extracted_entities &&
								Object.keys(intent.extracted_entities).length > 0 && (
									<Chip
										label={`엔티티: ${
											Object.keys(intent.extracted_entities).length
										}개`}
										variant="outlined"
										size="small"
									/>
								)}
						</Stack>
					</Box>
				</Stack>
			</CardContent>
		</Card>
	);
};
