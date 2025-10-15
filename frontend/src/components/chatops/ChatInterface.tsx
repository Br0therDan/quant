/**
 * ChatInterface Component
 *
 * WebSocket 기반 실시간 ChatOps 인터페이스
 *
 * Phase: 3 (Day 5-6)
 * 작성일: 2025-10-15
 */

import { useChatOps } from "@/hooks/useChatOps";
import {
	Circle as CircleIcon,
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

export interface ChatInterfaceProps {
	sessionId?: string;
	onSessionCreated?: (sessionId: string) => void;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
	sessionId: initialSessionId,
	onSessionCreated,
}) => {
	const messagesEndRef = useRef<HTMLDivElement>(null);
	const [userInput, setUserInput] = useState("");
	const [messages, setMessages] = useState<
		Array<{
			role: "user" | "assistant" | "system";
			content: string;
			timestamp: Date;
		}>
	>([]);

	const {
		isConnected,
		currentSessionId,
		createSession,
		joinSession,
		sendMessage,
		executeCommand,
	} = useChatOps();

	// 세션 초기화
	useEffect(() => {
		if (initialSessionId) {
			joinSession(initialSessionId);
		} else {
			const newSessionId = createSession("New ChatOps Session");
			onSessionCreated?.(newSessionId);
		}
	}, [initialSessionId, createSession, joinSession, onSessionCreated]);

	// 자동 스크롤
	useEffect(() => {
		if (messages.length > 0) {
			messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
		}
	}, [messages.length]);

	// --------------------------------------------------------------------------------------
	// 메시지 전송
	// --------------------------------------------------------------------------------------
	const handleSend = () => {
		if (!userInput.trim() || !isConnected) return;

		const userMessage = userInput.trim();
		setUserInput("");

		// 사용자 메시지 추가
		setMessages((prev) => [
			...prev,
			{ role: "user", content: userMessage, timestamp: new Date() },
		]);

		// 명령어 파싱
		if (userMessage.startsWith("/")) {
			const [command, ...args] = userMessage.slice(1).split(" ");
			executeCommand(command, { args });
		} else {
			sendMessage(userMessage);
		}
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
	const renderMessage = (
		role: "user" | "assistant" | "system",
		content: string,
		timestamp: Date,
	) => {
		const isUser = role === "user";
		const isSystem = role === "system";

		return (
			<Stack
				direction="row"
				spacing={2}
				alignItems="flex-start"
				sx={{ justifyContent: isUser ? "flex-end" : "flex-start" }}
			>
				{!isUser && (
					<Avatar
						sx={{ bgcolor: isSystem ? "warning.main" : "secondary.main" }}
					>
						<SmartToyIcon />
					</Avatar>
				)}
				<Box sx={{ maxWidth: "70%" }}>
					<Paper
						sx={{
							p: 2,
							bgcolor: isUser
								? "primary.light"
								: isSystem
									? "warning.light"
									: "secondary.light",
						}}
					>
						<Typography variant="body1">{content}</Typography>
					</Paper>
					<Typography
						variant="caption"
						color="text.secondary"
						sx={{ mt: 0.5, display: "block" }}
					>
						{timestamp.toLocaleTimeString()}
					</Typography>
				</Box>
				{isUser && (
					<Avatar sx={{ bgcolor: "primary.main" }}>
						<PersonIcon />
					</Avatar>
				)}
			</Stack>
		);
	};

	// --------------------------------------------------------------------------------------
	// UI 렌더링
	// --------------------------------------------------------------------------------------
	return (
		<Card sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
			{/* 헤더 */}
			<Box sx={{ p: 2, borderBottom: 1, borderColor: "divider" }}>
				<Stack direction="row" spacing={2} alignItems="center">
					<Typography variant="h6">ChatOps</Typography>
					<Chip
						icon={<CircleIcon sx={{ fontSize: 12 }} />}
						label={isConnected ? "연결됨" : "연결 끊김"}
						color={isConnected ? "success" : "error"}
						size="small"
					/>
					{currentSessionId && (
						<Chip
							label={`세션: ${currentSessionId.slice(0, 12)}...`}
							variant="outlined"
							size="small"
						/>
					)}
				</Stack>
			</Box>

			{/* 메시지 목록 */}
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
							ChatOps에 오신 것을 환영합니다!
						</Typography>
						<Typography variant="body2" textAlign="center">
							명령어를 입력하거나 자연어로 대화해보세요.
							<br />
							예: "/run_backtest strategy_123" 또는 "최근 백테스트 결과를
							보여줘"
						</Typography>
					</Box>
				)}

				<Stack spacing={3}>
					{messages.map((msg, idx) => (
						<Box key={idx}>
							{renderMessage(msg.role, msg.content, msg.timestamp)}
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
						placeholder="메시지를 입력하거나 /명령어를 사용하세요..."
						disabled={!isConnected}
					/>
					<Button
						variant="contained"
						onClick={handleSend}
						disabled={!userInput.trim() || !isConnected}
						sx={{ minWidth: 100 }}
					>
						{!isConnected ? (
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
