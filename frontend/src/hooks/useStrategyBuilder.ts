/**
 * useStrategyBuilder Hook
 *
 * LLM 기반 대화형 전략 빌더를 위한 Custom Hook
 *
 * 기능:
 * - 자연어 쿼리 → LLM 의도 파싱
 * - 지표 추천 (임베딩 기반 유사도)
 * - 전략 생성 (GeneratedStrategyConfig)
 * - 전략 승인 (Human-in-the-Loop)
 * - 대화 히스토리 관리
 *
 * Phase: 3
 * 작성일: 2025-10-14
 */

import type {
	IndicatorSearchRequest,
	StrategyApprovalRequest,
	StrategyBuilderRequest,
	StrategyBuilderResponse,
} from "@/client";
import { GenAiService } from "@/client";
import { useSnackbar } from "@/contexts/SnackbarContext";
import { useMutation } from "@tanstack/react-query";
import { useCallback, useState } from "react";

// ========================================================================================
// Types & Interfaces
// ========================================================================================

export interface Message {
	id: string;
	role: "user" | "assistant";
	content: string;
	timestamp: Date;
	metadata?: {
		intent?: string;
		confidence?: number;
		indicators?: string[];
	};
}

export interface Conversation {
	id: string;
	messages: Message[];
	currentStrategy?: StrategyBuilderResponse;
}

export interface IndicatorRecommendation {
	name: string;
	description: string;
	similarity_score: number;
	category?: string;
}

// ========================================================================================
// Main Hook
// ========================================================================================

export const useStrategyBuilder = () => {
	const { showSuccess, showError, showWarning } = useSnackbar();
	const [conversation, setConversation] = useState<Conversation>({
		id: `conv_${Date.now()}`,
		messages: [],
	});
	const [recommendations, setRecommendations] = useState<
		IndicatorRecommendation[]
	>([]);

	// --------------------------------------------------------------------------------------
	// 메시지 전송 (전략 생성)
	// --------------------------------------------------------------------------------------

	const generateStrategyMutation = useMutation({
		mutationFn: async (query: string) => {
			const request: StrategyBuilderRequest = {
				query,
				context: {
					conversation_history: conversation.messages.slice(-5).map((m) => ({
						role: m.role,
						content: m.content,
					})),
				},
			};

			const response = await GenAiService.generateStrategy({
				body: request,
			});
			return response.data;
		},
		onSuccess: (data, query) => {
			if (!data) return;

			// 사용자 메시지 추가
			const userMessage: Message = {
				id: `msg_${Date.now()}_user`,
				role: "user",
				content: query,
				timestamp: new Date(),
			};

			// AI 응답 메시지 추가
			const assistantMessage: Message = {
				id: `msg_${Date.now()}_assistant`,
				role: "assistant",
				content: generateResponseMessage(data),
				timestamp: new Date(),
				metadata: {
					intent: data.parsed_intent?.intent_type,
					confidence: data.overall_confidence,
					indicators: data.generated_strategy?.indicators?.map(
						(i) => i.indicator_name,
					),
				},
			};

			setConversation((prev) => ({
				...prev,
				messages: [...prev.messages, userMessage, assistantMessage],
				currentStrategy: data,
			}));

			if (data.status === "success") {
				showSuccess("전략이 생성되었습니다");
			} else if (data.status === "warning") {
				showWarning("전략이 생성되었으나 확인이 필요합니다");
			}
		},
		onError: (error) => {
			showError(
				`전략 생성 실패: ${error instanceof Error ? error.message : "알 수 없는 오류"}`,
			);
		},
	});

	// --------------------------------------------------------------------------------------
	// 지표 검색
	// --------------------------------------------------------------------------------------

	const searchIndicatorsMutation = useMutation({
		mutationFn: async (query: string) => {
			const request: IndicatorSearchRequest = {
				query,
				top_k: 5,
			};

			const response = await GenAiService.searchIndicators({
				body: request,
			});
			return response.data;
		},
		onSuccess: (data) => {
			if (data?.indicators) {
				setRecommendations(
					data.indicators as unknown as IndicatorRecommendation[],
				);
			}
		},
		onError: (error) => {
			showError(
				`지표 검색 실패: ${error instanceof Error ? error.message : "알 수 없는 오류"}`,
			);
		},
	});

	// --------------------------------------------------------------------------------------
	// 전략 승인
	// --------------------------------------------------------------------------------------

	const approveStrategyMutation = useMutation({
		mutationFn: async (request: StrategyApprovalRequest) => {
			const response = await GenAiService.approveStrategy({
				body: request,
			});
			return response.data;
		},
		onSuccess: (data) => {
			if (!data) return;

			if (data.status === "approved" || data.status === "modified") {
				showSuccess(`전략이 승인되었습니다 (ID: ${data.strategy_id})`);
				// 대화 초기화 (새 전략 시작)
				setConversation({
					id: `conv_${Date.now()}`,
					messages: [],
				});
			} else {
				showWarning("전략이 거부되었습니다");
			}
		},
		onError: (error) => {
			showError(
				`승인 처리 실패: ${error instanceof Error ? error.message : "알 수 없는 오류"}`,
			);
		},
	});

	// --------------------------------------------------------------------------------------
	// 유틸리티: AI 응답 메시지 생성
	// --------------------------------------------------------------------------------------

	const generateResponseMessage = (
		response: StrategyBuilderResponse,
	): string => {
		const parts: string[] = [];

		// 의도 파싱 결과
		if (response.parsed_intent) {
			const intent = response.parsed_intent;
			parts.push(
				`💡 **의도**: ${intent.intent_type} (신뢰도: ${(intent.confidence * 100).toFixed(0)}%)`,
			);

			if (
				intent.extracted_entities &&
				Object.keys(intent.extracted_entities).length > 0
			) {
				const entities = Object.entries(intent.extracted_entities)
					.map(([key, value]) => `${key}: ${value}`)
					.join(", ");
				parts.push(`📋 **추출된 정보**: ${entities}`);
			}
		}

		// 생성된 전략
		if (response.generated_strategy) {
			const strategy = response.generated_strategy;
			parts.push(`\n🎯 **전략 생성 완료**`);
			parts.push(`이름: ${strategy.strategy_name}`);
			parts.push(`설명: ${strategy.description}`);

			if (strategy.indicators && strategy.indicators.length > 0) {
				const indicators = strategy.indicators
					.map((i) => i.indicator_name)
					.join(", ");
				parts.push(`지표: ${indicators}`);
			}
		}

		// 승인 필요
		if (response.human_approval?.requires_approval) {
			parts.push(`\n⚠️ **승인 필요**`);
			if (
				response.human_approval.approval_reasons &&
				response.human_approval.approval_reasons.length > 0
			) {
				parts.push(
					`사유: ${response.human_approval.approval_reasons.join(", ")}`,
				);
			}

			if (response.human_approval.suggested_modifications) {
				const mods = Object.entries(
					response.human_approval.suggested_modifications,
				)
					.map(([key, value]) => `${key}: ${value}`)
					.join(", ");
				parts.push(`권장 수정: ${mods}`);
			}
		}

		// 전체 신뢰도
		parts.push(
			`\n📊 전체 신뢰도: ${(response.overall_confidence * 100).toFixed(0)}%`,
		);

		return parts.join("\n");
	};

	// --------------------------------------------------------------------------------------
	// 메시지 전송 (통합)
	// --------------------------------------------------------------------------------------

	const sendMessage = useCallback(
		(message: string) => {
			if (!message.trim()) {
				showWarning("메시지를 입력해주세요");
				return;
			}

			// 지표 검색 쿼리 판별 (간단한 휴리스틱)
			if (
				message.toLowerCase().includes("지표") ||
				message.toLowerCase().includes("indicator")
			) {
				searchIndicatorsMutation.mutate(message);
			} else {
				generateStrategyMutation.mutate(message);
			}
		},
		[generateStrategyMutation, searchIndicatorsMutation, showWarning],
	);

	// --------------------------------------------------------------------------------------
	// 대화 초기화
	// --------------------------------------------------------------------------------------

	const clearConversation = useCallback(() => {
		setConversation({
			id: `conv_${Date.now()}`,
			messages: [],
		});
		setRecommendations([]);
	}, []);

	// --------------------------------------------------------------------------------------
	// Return Hook Interface
	// --------------------------------------------------------------------------------------

	return {
		// 상태
		conversation,
		messages: conversation.messages,
		currentStrategy: conversation.currentStrategy,
		recommendations,
		isGenerating: generateStrategyMutation.isPending,
		isSearching: searchIndicatorsMutation.isPending,
		isApproving: approveStrategyMutation.isPending,

		// 액션
		sendMessage,
		searchIndicators: (query: string) => searchIndicatorsMutation.mutate(query),
		approveStrategy: (request: StrategyApprovalRequest) =>
			approveStrategyMutation.mutate(request),
		clearConversation,

		// 편의 함수
		parseIntent: () => conversation.currentStrategy?.parsed_intent,
		getGeneratedStrategy: () =>
			conversation.currentStrategy?.generated_strategy,
		getHumanApproval: () => conversation.currentStrategy?.human_approval,
	};
};
