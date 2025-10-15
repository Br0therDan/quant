/**
 * useChatOps Hook
 *
 * WebSocket 기반 실시간 ChatOps 인터페이스
 * 백테스트 진행 상황, 명령 실행, 전략 비교
 *
 * Phase: 3 (Day 5-6)
 * 작성일: 2025-10-15
 */

import { useSnackbar } from "@/contexts/SnackbarContext";
import { useQueryClient } from "@tanstack/react-query";
import { useCallback, useEffect, useRef, useState } from "react";
import { io, type Socket } from "socket.io-client";

// 임시 타입 정의 (Backend API 스키마 대기)
interface ChatMessage {
	id: string;
	sessionId: string;
	role: "user" | "assistant" | "system";
	content: string;
	timestamp: Date;
	metadata?: Record<string, unknown>;
}

interface CommandRequest {
	sessionId: string;
	command: string;
	parameters?: Record<string, unknown>;
}

interface CommandResponse {
	success: boolean;
	message: string;
	data?: unknown;
}

interface BacktestStatus {
	backtestId: string;
	progress: number;
	status: "running" | "completed" | "failed";
	message?: string;
}

// WebSocket 이벤트 타입
interface ServerToClientEvents {
	message: (message: ChatMessage) => void;
	backtestProgress: (status: BacktestStatus) => void;
	commandResult: (response: CommandResponse) => void;
	error: (error: { message: string }) => void;
}

interface ClientToServerEvents {
	sendMessage: (data: { sessionId: string; content: string }) => void;
	executeCommand: (data: CommandRequest) => void;
	joinSession: (sessionId: string) => void;
	leaveSession: (sessionId: string) => void;
}

export const chatOpsQueryKeys = {
	all: ["chatops"] as const,
	sessions: () => [...chatOpsQueryKeys.all, "sessions"] as const,
	session: (id: string) => [...chatOpsQueryKeys.all, "session", id] as const,
	messages: (sessionId: string) =>
		[...chatOpsQueryKeys.all, "messages", sessionId] as const,
};

export const useChatOps = () => {
	const queryClient = useQueryClient();
	const { showSuccess, showError } = useSnackbar();
	const [isConnected, setIsConnected] = useState(false);
	const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
	const socketRef = useRef<Socket<
		ServerToClientEvents,
		ClientToServerEvents
	> | null>(null);

	// --------------------------------------------------------------------------------------
	// WebSocket 연결
	// --------------------------------------------------------------------------------------
	useEffect(() => {
		const socket = io(process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8500", {
			path: "/ws/chatops",
			transports: ["websocket"],
			reconnection: true,
			reconnectionAttempts: 5,
			reconnectionDelay: 1000,
		});

		socketRef.current = socket;

		socket.on("connect", () => {
			setIsConnected(true);
			showSuccess("ChatOps에 연결되었습니다");
		});

		socket.on("disconnect", () => {
			setIsConnected(false);
			showError("ChatOps 연결이 끊어졌습니다");
		});

		socket.on("message", (message) => {
			if (currentSessionId) {
				queryClient.setQueryData<ChatMessage[]>(
					chatOpsQueryKeys.messages(currentSessionId),
					(old) => [...(old || []), message],
				);
			}
		});

		socket.on("backtestProgress", (status) => {
			showSuccess(`백테스트 진행률: ${status.progress}%`);
		});

		socket.on("commandResult", (response) => {
			if (response.success) {
				showSuccess(response.message);
			} else {
				showError(response.message);
			}
		});

		socket.on("error", (error) => {
			showError(error.message);
		});

		return () => {
			socket.disconnect();
		};
	}, [currentSessionId, queryClient, showSuccess, showError]);

	// --------------------------------------------------------------------------------------
	// 세션 관리
	// --------------------------------------------------------------------------------------
	const createSession = useCallback((_name: string) => {
		const sessionId = `session_${Date.now()}`;
		setCurrentSessionId(sessionId);
		socketRef.current?.emit("joinSession", sessionId);
		return sessionId;
	}, []);

	const joinSession = useCallback((sessionId: string) => {
		setCurrentSessionId(sessionId);
		socketRef.current?.emit("joinSession", sessionId);
	}, []);

	const leaveSession = useCallback(() => {
		if (currentSessionId) {
			socketRef.current?.emit("leaveSession", currentSessionId);
			setCurrentSessionId(null);
		}
	}, [currentSessionId]);

	// --------------------------------------------------------------------------------------
	// 메시지 전송
	// --------------------------------------------------------------------------------------
	const sendMessage = useCallback(
		(content: string) => {
			if (!currentSessionId) {
				showError("세션에 참여해주세요");
				return;
			}

			socketRef.current?.emit("sendMessage", {
				sessionId: currentSessionId,
				content,
			});
		},
		[currentSessionId, showError],
	);

	// --------------------------------------------------------------------------------------
	// 명령 실행
	// --------------------------------------------------------------------------------------
	const executeCommand = useCallback(
		(command: string, params?: Record<string, unknown>) => {
			if (!currentSessionId) {
				showError("세션에 참여해주세요");
				return;
			}

			socketRef.current?.emit("executeCommand", {
				sessionId: currentSessionId,
				command,
				parameters: params,
			});
		},
		[currentSessionId, showError],
	);

	// --------------------------------------------------------------------------------------
	// 백테스트 트리거
	// --------------------------------------------------------------------------------------
	const triggerBacktest = useCallback(
		(strategyId: string, params?: Record<string, unknown>) => {
			executeCommand("run_backtest", {
				strategy_id: strategyId,
				...params,
			});
		},
		[executeCommand],
	);

	// --------------------------------------------------------------------------------------
	// 전략 비교
	// --------------------------------------------------------------------------------------
	const compareStrategies = useCallback(
		(strategyIds: string[]) => {
			executeCommand("compare_strategies", {
				strategy_ids: strategyIds,
			});
		},
		[executeCommand],
	);

	// --------------------------------------------------------------------------------------
	// Return
	// --------------------------------------------------------------------------------------
	return {
		// 연결 상태
		isConnected,
		currentSessionId,

		// 세션 관리
		createSession,
		joinSession,
		leaveSession,

		// 메시지
		sendMessage,

		// 명령 실행
		executeCommand,
		triggerBacktest,
		compareStrategies,

		// WebSocket 인스턴스 (고급 사용)
		socket: socketRef.current,
	};
};
