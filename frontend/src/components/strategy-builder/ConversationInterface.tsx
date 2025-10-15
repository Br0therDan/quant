/**
 * ConversationInterface Component
 *
 * LLM 기반 전략 빌더 대화형 UI
 * useStrategyBuilder 훅과 통합
 *
 * Phase: 3
 * 작성일: 2025-10-15
 */

import { useStrategyBuilder } from "@/hooks/useStrategyBuilder";
import {
	Person as PersonIcon,
	Send as SendIcon,
	SmartToy as SmartToyIcon,
} from "@mui/icons-material";
import {
	Avatar,
	Box,
	Button,
	Card,
	Chip,
	CircularProgress,
	Paper,
	Stack,
	TextField,
	Typography,
} from "@mui/material";
import type React from "react";
import { useEffect, useRef, useState } from "react";
import { IndicatorRecommendation } from "./IndicatorRecommendation";
import { IntentParser } from "./IntentParser";
import { StrategyPreview } from "./StrategyPreview";
import { ValidationFeedback } from "./ValidationFeedback";

export interface ConversationInterfaceProps {
	onStrategyGenerated?: () => void;
}

export const ConversationInterface: React.FC<ConversationInterfaceProps> = ({
	onStrategyGenerated,
}) => {
	const messagesEndRef = useRef<HTMLDivElement>(null);
	const [userInput, setUserInput] = useState("");

	const { messages, currentStrategy, isGenerating, sendMessage } =
		useStrategyBuilder();

	// 자동 스크롤 (메시지 추가 시)
	useEffect(() => {
		if (messages.length > 0) {
			messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
		}
	}, [messages.length]);

	// 전략 생성 완료 시 콜백
	useEffect(() => {
		if (currentStrategy) {
			onStrategyGenerated?.();
		}
	}, [currentStrategy, onStrategyGenerated]);

	// --------------------------------------------------------------------------------------
	// 메시지 전송
	// --------------------------------------------------------------------------------------
	const handleSend = () => {
		if (!userInput.trim() || isGenerating) return;

		const userMessage = userInput.trim();
		setUserInput("");
		sendMessage(userMessage);
	};

	const handleKeyPress = (e: React.KeyboardEvent) => {
		if (e.key === "Enter" && !e.shiftKey) {
			e.preventDefault();
			handleSend();
		}
	};

	// --------------------------------------------------------------------------------------
	// 메시지 렌더링
	// --------------------------------------------------------------------------------------
	const renderUserMessage = (content: string) => (
		<Stack direction="row" spacing={2} alignItems="flex-start">
			<Avatar sx={{ bgcolor: "primary.main" }}>
				<PersonIcon />
			</Avatar>
			<Paper sx={{ p: 2, maxWidth: "70%", bgcolor: "primary.light" }}>
				<Typography variant="body1">{content}</Typography>
			</Paper>
		</Stack>
	);

	const renderAiMessage = (content: string, isLastMessage: boolean) => (
		<Stack direction="row" spacing={2} alignItems="flex-start">
			<Avatar sx={{ bgcolor: "secondary.main" }}>
				<SmartToyIcon />
			</Avatar>
			<Box sx={{ flexGrow: 1, maxWidth: "80%" }}>
				{/* AI 응답 메시지 */}
				<Paper sx={{ p: 2, mb: 2, bgcolor: "secondary.light" }}>
					<Typography variant="body1">{content}</Typography>
				</Paper>

				{/* 마지막 메시지에만 currentStrategy 정보 표시 */}
				{isLastMessage && currentStrategy && (
					<>
						{/* 의도 파싱 */}
						{currentStrategy.parsed_intent && (
							<IntentParser intent={currentStrategy.parsed_intent} />
						)}

						{/* 전략 생성 결과 */}
						{currentStrategy.generated_strategy && (
							<>
								{currentStrategy.generated_strategy.indicators.length > 0 && (
									<IndicatorRecommendation
										indicators={currentStrategy.generated_strategy.indicators}
									/>
								)}
								<StrategyPreview
									strategy={currentStrategy.generated_strategy}
								/>
								{currentStrategy.generated_strategy.parameter_validations
									.length > 0 && (
									<ValidationFeedback
										validations={
											currentStrategy.generated_strategy.parameter_validations
										}
									/>
								)}
							</>
						)}

						{/* 메타데이터 */}
						<Stack direction="row" spacing={1} sx={{ mt: 1 }}>
							<Chip
								label={`신뢰도: ${(
									currentStrategy.overall_confidence * 100
								).toFixed(0)}%`}
								color={
									currentStrategy.overall_confidence > 0.7
										? "success"
										: "warning"
								}
								size="small"
							/>
							<Chip
								label={currentStrategy.llm_model}
								variant="outlined"
								size="small"
							/>
							<Chip
								label={`${currentStrategy.processing_time_ms}ms`}
								variant="outlined"
								size="small"
							/>
						</Stack>

						{/* 검증 오류 */}
						{currentStrategy.validation_errors &&
							currentStrategy.validation_errors.length > 0 && (
								<Paper sx={{ p: 2, mt: 2, bgcolor: "error.light" }}>
									<Typography
										variant="subtitle2"
										color="error.dark"
										gutterBottom
									>
										⚠️ 검증 오류
									</Typography>
									{currentStrategy.validation_errors.map((error, idx) => (
										<Typography key={idx} variant="caption" display="block">
											• {error}
										</Typography>
									))}
								</Paper>
							)}

						{/* 대안 제안 */}
						{currentStrategy.alternative_suggestions &&
							currentStrategy.alternative_suggestions.length > 0 && (
								<Paper sx={{ p: 2, mt: 2, bgcolor: "info.light" }}>
									<Typography
										variant="subtitle2"
										color="info.dark"
										gutterBottom
									>
										💡 대안 제안
									</Typography>
									{currentStrategy.alternative_suggestions.map(
										(suggestion, idx) => (
											<Typography key={idx} variant="caption" display="block">
												• {suggestion}
											</Typography>
										),
									)}
								</Paper>
							)}
					</>
				)}
			</Box>
		</Stack>
	);

	// --------------------------------------------------------------------------------------
	// UI 렌더링
	// --------------------------------------------------------------------------------------
	return (
		<Card sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
			{/* 대화 기록 */}
			<Box
				sx={{
					flexGrow: 1,
					p: 2,
					overflowY: "auto",
					maxHeight: "calc(100vh - 300px)",
				}}
			>
				{messages.length === 0 && (
					<Box
						sx={{
							display: "flex",
							flexDirection: "column",
							alignItems: "center",
							justifyContent: "center",
							height: "100%",
							color: "text.secondary",
						}}
					>
						<SmartToyIcon sx={{ fontSize: 64, mb: 2 }} />
						<Typography variant="h6" gutterBottom>
							전략 빌더에 오신 것을 환영합니다!
						</Typography>
						<Typography variant="body2" textAlign="center">
							원하는 전략을 자연어로 설명해주세요.
							<br />
							예: "RSI 30 이하일 때 매수하고 70 이상일 때 매도하는 전략을
							만들어줘"
						</Typography>
					</Box>
				)}

				<Stack spacing={3}>
					{messages.map((msg, idx) => (
						<Box key={idx}>
							{msg.role === "user"
								? renderUserMessage(msg.content)
								: renderAiMessage(msg.content, idx === messages.length - 1)}
						</Box>
					))}
				</Stack>

				<div ref={messagesEndRef} />
			</Box>

			{/* 입력 영역 */}
			<Box sx={{ p: 2, borderTop: 1, borderColor: "divider" }}>
				<Stack direction="row" spacing={1}>
					<TextField
						fullWidth
						multiline
						maxRows={4}
						value={userInput}
						onChange={(e) => setUserInput(e.target.value)}
						onKeyPress={handleKeyPress}
						placeholder="전략을 설명해주세요... (Shift+Enter: 줄바꿈)"
						disabled={isGenerating}
					/>
					<Button
						variant="contained"
						onClick={handleSend}
						disabled={!userInput.trim() || isGenerating}
						sx={{ minWidth: 100 }}
					>
						{isGenerating ? (
							<CircularProgress size={24} color="inherit" />
						) : (
							<>
								<SendIcon sx={{ mr: 1 }} />
								전송
							</>
						)}
					</Button>
				</Stack>
			</Box>
		</Card>
	);
};
