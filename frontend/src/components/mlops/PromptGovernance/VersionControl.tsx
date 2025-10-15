/**
 * Prompt Template Version Control Component
 */

"use client";

import { usePromptAuditLogs } from "@/hooks/usePromptGovernance";
import {
	Cancel,
	CheckCircle,
	Create,
	Edit,
	SendOutlined,
} from "@mui/icons-material";
import {
	Timeline,
	TimelineConnector,
	TimelineContent,
	TimelineDot,
	TimelineItem,
	TimelineOppositeContent,
	TimelineSeparator,
} from "@mui/lab";
import { Box, Card, CardContent, Chip, Paper, Typography } from "@mui/material";

interface VersionControlProps {
	promptId: string;
	version: string;
}

const ACTION_ICONS: Record<string, React.ReactElement> = {
	created: <Create />,
	updated: <Edit />,
	submitted: <SendOutlined />,
	approved: <CheckCircle />,
	rejected: <Cancel />,
};

const ACTION_COLORS: Record<
	string,
	"grey" | "primary" | "warning" | "success" | "error"
> = {
	created: "grey",
	updated: "primary",
	submitted: "warning",
	approved: "success",
	rejected: "error",
};

const ACTION_LABELS: Record<string, string> = {
	created: "생성됨",
	updated: "수정됨",
	submitted: "검토 요청",
	approved: "승인됨",
	rejected: "거부됨",
};

export default function VersionControl({
	promptId,
	version,
}: VersionControlProps) {
	const { auditLogs, isLoading, error } = usePromptAuditLogs(promptId, version);

	if (error) {
		return (
			<Card>
				<CardContent>
					<Typography color="error">
						감사 로그를 불러오는 중 오류가 발생했습니다.
					</Typography>
				</CardContent>
			</Card>
		);
	}

	if (isLoading) {
		return (
			<Card>
				<CardContent>
					<Typography>로딩 중...</Typography>
				</CardContent>
			</Card>
		);
	}

	if (!auditLogs || auditLogs.length === 0) {
		return (
			<Card>
				<CardContent>
					<Typography color="text.secondary">
						아직 감사 로그가 없습니다.
					</Typography>
				</CardContent>
			</Card>
		);
	}

	return (
		<Paper sx={{ p: 3 }}>
			<Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
				버전 히스토리
			</Typography>

			<Timeline position="right">
				{auditLogs.map((log, index) => {
					const action = log.action || "updated";
					const icon = ACTION_ICONS[action] || <Edit />;
					const color = ACTION_COLORS[action] || "primary";
					const label = ACTION_LABELS[action] || action;

					return (
						<TimelineItem key={`${log.prompt_id}-${log.version}-${index}`}>
							<TimelineOppositeContent
								color="text.secondary"
								sx={{ flex: 0.3 }}
							>
								<Typography variant="body2">
									{log.created_at
										? new Date(log.created_at).toLocaleString("ko-KR", {
												month: "short",
												day: "numeric",
												hour: "2-digit",
												minute: "2-digit",
											})
										: "N/A"}
								</Typography>
								<Typography variant="caption" color="text.disabled">
									{log.actor || "System"}
								</Typography>
							</TimelineOppositeContent>

							<TimelineSeparator>
								<TimelineDot color={color}>{icon}</TimelineDot>
								{index < auditLogs.length - 1 && <TimelineConnector />}
							</TimelineSeparator>

							<TimelineContent sx={{ py: "12px", px: 2 }}>
								<Box>
									<Box
										sx={{
											display: "flex",
											alignItems: "center",
											gap: 1,
											mb: 1,
										}}
									>
										<Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
											{label}
										</Typography>
										<Chip label={`v${log.version}`} size="small" />
									</Box>

									{log.details &&
										typeof log.details === "object" &&
										Object.keys(log.details).length > 0 && (
											<Card
												variant="outlined"
												sx={{ mt: 1, bgcolor: "grey.50" }}
											>
												<CardContent sx={{ p: 2, "&:last-child": { pb: 2 } }}>
													<Typography variant="caption" color="text.secondary">
														변경 내용:
													</Typography>
													{Object.entries(
														log.details as Record<string, unknown>,
													).map(([key, value]) => {
														if (key === "notes") return null;
														return (
															<Typography
																key={key}
																variant="body2"
																sx={{
																	mt: 0.5,
																	fontFamily: "monospace",
																	fontSize: 12,
																}}
															>
																<strong>{key}:</strong>{" "}
																{typeof value === "object"
																	? JSON.stringify(value)
																	: String(value)}
															</Typography>
														);
													})}
												</CardContent>
											</Card>
										)}

									{log.details &&
										typeof log.details === "object" &&
										"notes" in log.details &&
										typeof (log.details as Record<string, unknown>).notes ===
											"string" && (
											<Typography
												variant="body2"
												color="text.secondary"
												sx={{ mt: 1, fontStyle: "italic" }}
											>
												"
												{String((log.details as Record<string, unknown>).notes)}
												"
											</Typography>
										)}
								</Box>
							</TimelineContent>
						</TimelineItem>
					);
				})}
			</Timeline>

			<Box
				sx={{
					mt: 3,
					pt: 2,
					borderTop: 1,
					borderColor: "divider",
					display: "flex",
					justifyContent: "space-between",
				}}
			>
				<Typography variant="body2" color="text.secondary">
					총 {auditLogs.length}개의 이벤트
				</Typography>
				<Typography variant="body2" color="text.secondary">
					마지막 업데이트:{" "}
					{auditLogs[0]?.created_at
						? new Date(auditLogs[0].created_at).toLocaleString("ko-KR")
						: "N/A"}
				</Typography>
			</Box>
		</Paper>
	);
}
