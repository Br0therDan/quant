/**
 * Prompt Template Editor Component
 *
 * 프롬프트 템플릿 생성 및 수정 에디터
 *
 * 주요 기능:
 * - Monaco Editor로 프롬프트 템플릿 편집
 * - 메타데이터 입력 (이름, 버전, 태그, 설명)
 * - 워크플로우 액션 (저장, 검토 요청, 승인, 거부)
 * - 프롬프트 품질 평가
 * - 버전 히스토리 표시
 *
 * @author AI MLOps Team
 * @since Phase 4 - Day 9
 */

"use client";

import type {
	PromptEvaluationRequest,
	PromptTemplateCreate,
	PromptTemplateUpdate,
} from "@/client";
import { usePromptGovernance } from "@/hooks/usePromptGovernance";
import {
	Assessment,
	Cancel,
	CheckCircle,
	Save,
	SendOutlined,
} from "@mui/icons-material";
import {
	Box,
	Button,
	Card,
	CardContent,
	Chip,
	FormControl,
	Grid,
	InputLabel,
	MenuItem,
	Paper,
	Select,
	TextField,
	Typography,
} from "@mui/material";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

// Monaco Editor (Client-side only)
import { useAuth } from "@/hooks/useAuth";
import dynamic from "next/dynamic";

const MonacoEditor = dynamic(() => import("@monaco-editor/react"), {
	ssr: false,
	loading: () => <div>Loading editor...</div>,
});

interface PromptTemplateEditorProps {
	promptId?: string; // 수정 모드일 때만 제공
	version?: string;
}

export default function PromptTemplateEditor({
	promptId,
	version,
}: PromptTemplateEditorProps) {
	const router = useRouter();
	const { user } = useAuth();
	const isEditMode = !!promptId && !!version;
	const {
		createTemplate,
		updateTemplate,
		submitForReview,
		approveTemplate,
		rejectTemplate,
		evaluatePrompt,
		evaluationResult,
		isCreatingTemplate,
		isUpdatingTemplate,
		isSubmittingForReview,
		isApprovingTemplate,
		isRejectingTemplate,
		isEvaluatingPrompt,
		findTemplate,
	} = usePromptGovernance();

	// ============================================================================
	// State
	// ============================================================================

	const [name, setName] = useState("");
	const [versionInput, setVersionInput] = useState("1.0.0");
	const [description, setDescription] = useState("");
	const [tags, setTags] = useState<string[]>([]);
	const [templateContent, setTemplateContent] = useState("");
	const [reviewerNotes, setReviewerNotes] = useState("");

	// ============================================================================
	// Load existing template (Edit Mode)
	// ============================================================================

	useEffect(() => {
		if (isEditMode && promptId && version) {
			const template = findTemplate(promptId, version);
			if (template) {
				setName(template.name);
				setVersionInput(template.version);
				setDescription(template.description || "");
				setTags(template.tags || []);
				setTemplateContent(template.content || "");
			}
		}
	}, [isEditMode, promptId, version, findTemplate]); // ============================================================================
	// Event Handlers
	// ============================================================================

	const handleSave = async () => {
		if (isEditMode && promptId && version) {
			// Update existing template
			const data: PromptTemplateUpdate = {
				description,
				tags,
				content: templateContent,
			};
			await updateTemplate({ promptId, version, data });
		} else {
			// Create new template
			const data: PromptTemplateCreate = {
				prompt_id: `prompt_${Date.now()}`,
				version: versionInput,
				name,
				description,
				content: templateContent,
				owner: user?.full_name || "unknown",
				tags,
			};
			await createTemplate(data);
			router.push("/mlops/prompt-governance");
		}
	};
	const handleSubmitForReview = async () => {
		if (!isEditMode || !promptId || !version) return;

		await submitForReview({
			promptId,
			version,
			action: {
				reviewer: user?.full_name || "admin",
				notes: reviewerNotes || "검토를 요청합니다.",
			},
		});
	};

	const handleApprove = async () => {
		if (!isEditMode || !promptId || !version) return;

		await approveTemplate({
			promptId,
			version,
			action: {
				reviewer: user?.full_name || "admin",
				notes: reviewerNotes || "승인되었습니다.",
			},
		});
	};

	const handleReject = async () => {
		if (!isEditMode || !promptId || !version) return;

		await rejectTemplate({
			promptId,
			version,
			action: {
				reviewer: user?.full_name || "admin",
				notes: reviewerNotes || "거부되었습니다.",
			},
		});
	};

	const handleEvaluate = async () => {
		if (!promptId || !version) return;

		const request: PromptEvaluationRequest = {
			prompt_id: promptId,
			version: version,
			content: templateContent,
			evaluator: user?.full_name || "system",
		};
		await evaluatePrompt(request);
	}; // ============================================================================
	// Render
	// ============================================================================

	const currentTemplate =
		isEditMode && promptId && version ? findTemplate(promptId, version) : null;
	const currentStatus = currentTemplate?.status;

	return (
		<Box sx={{ p: 3 }}>
			{/* Header */}
			<Typography variant="h5" sx={{ fontWeight: 600, mb: 3 }}>
				{isEditMode ? "프롬프트 템플릿 수정" : "새 프롬프트 템플릿"}
			</Typography>

			<Grid container spacing={3}>
				{/* Left Column: Editor */}
				<Grid size={8}>
					<Paper sx={{ p: 3 }}>
						<Typography variant="h6" sx={{ mb: 2 }}>
							템플릿 내용
						</Typography>

						{/* Monaco Editor */}
						<Box
							sx={{ height: 500, border: "1px solid #ddd", borderRadius: 1 }}
						>
							<MonacoEditor
								height="100%"
								defaultLanguage="markdown"
								value={templateContent}
								onChange={(value) => setTemplateContent(value || "")}
								options={{
									minimap: { enabled: false },
									fontSize: 14,
									wordWrap: "on",
									lineNumbers: "on",
									scrollBeyondLastLine: false,
								}}
							/>
						</Box>

						{/* Evaluation Result */}
						{evaluationResult && (
							<Card sx={{ mt: 2, bgcolor: "info.lighter" }}>
								<CardContent>
									<Typography
										variant="subtitle2"
										sx={{ mb: 1, fontWeight: 600 }}
									>
										평가 결과
									</Typography>
									<Grid container spacing={2}>
										<Grid size={4}>
											<Typography variant="body2" color="text.secondary">
												유해성 점수
											</Typography>
											<Typography variant="h6">
												{evaluationResult.evaluation.toxicity_score.toFixed(2)}
											</Typography>
										</Grid>
										<Grid size={4}>
											<Typography variant="body2" color="text.secondary">
												환각 점수
											</Typography>
											<Typography variant="h6">
												{evaluationResult.evaluation.hallucination_score.toFixed(
													2,
												)}
											</Typography>
										</Grid>
										<Grid size={4}>
											<Typography variant="body2" color="text.secondary">
												사실 일치도
											</Typography>
											<Typography variant="h6">
												{evaluationResult.evaluation.factual_consistency.toFixed(
													2,
												)}
											</Typography>
										</Grid>
										<Grid size={12}>
											<Typography variant="body2" color="text.secondary">
												위험도
											</Typography>
											<Chip
												label={evaluationResult.evaluation.risk_level.toUpperCase()}
												color={
													evaluationResult.evaluation.risk_level === "low"
														? "success"
														: evaluationResult.evaluation.risk_level ===
																"medium"
															? "warning"
															: "error"
												}
												size="small"
											/>
										</Grid>
									</Grid>
								</CardContent>
							</Card>
						)}
					</Paper>
				</Grid>

				{/* Right Column: Metadata & Actions */}
				<Grid size={4}>
					{/* Metadata */}
					<Paper sx={{ p: 3, mb: 2 }}>
						<Typography variant="h6" sx={{ mb: 2 }}>
							메타데이터
						</Typography>

						<TextField
							fullWidth
							label="템플릿 이름"
							value={name}
							onChange={(e) => setName(e.target.value)}
							disabled={isEditMode}
							sx={{ mb: 2 }}
						/>

						<TextField
							fullWidth
							label="버전"
							value={versionInput}
							onChange={(e) => setVersionInput(e.target.value)}
							disabled={isEditMode}
							sx={{ mb: 2 }}
						/>

						<TextField
							fullWidth
							multiline
							rows={3}
							label="설명"
							value={description}
							onChange={(e) => setDescription(e.target.value)}
							sx={{ mb: 2 }}
						/>

						<FormControl fullWidth sx={{ mb: 2 }}>
							<InputLabel>태그</InputLabel>
							<Select
								multiple
								value={tags}
								onChange={(e) =>
									setTags(
										typeof e.target.value === "string"
											? e.target.value.split(",")
											: e.target.value,
									)
								}
								label="태그"
								renderValue={(selected) => (
									<Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5 }}>
										{selected.map((value) => (
											<Chip key={value} label={value} size="small" />
										))}
									</Box>
								)}
							>
								<MenuItem value="classification">Classification</MenuItem>
								<MenuItem value="summarization">Summarization</MenuItem>
								<MenuItem value="generation">Generation</MenuItem>
								<MenuItem value="analysis">Analysis</MenuItem>
								<MenuItem value="qa">Question Answering</MenuItem>
								<MenuItem value="translation">Translation</MenuItem>
							</Select>
						</FormControl>

						{currentStatus && (
							<Box sx={{ mb: 2 }}>
								<Typography
									variant="body2"
									color="text.secondary"
									sx={{ mb: 1 }}
								>
									현재 상태
								</Typography>
								<Chip
									label={
										currentStatus === "draft"
											? "초안"
											: currentStatus === "in_review"
												? "검토 중"
												: currentStatus === "approved"
													? "승인됨"
													: "거부됨"
									}
									color={
										currentStatus === "approved"
											? "success"
											: currentStatus === "in_review"
												? "warning"
												: currentStatus === "rejected"
													? "error"
													: "default"
									}
								/>
							</Box>
						)}
					</Paper>

					{/* Workflow Actions */}
					{isEditMode && (
						<Paper sx={{ p: 3, mb: 2 }}>
							<Typography variant="h6" sx={{ mb: 2 }}>
								워크플로우 액션
							</Typography>

							<TextField
								fullWidth
								multiline
								rows={2}
								label="검토자 메모"
								value={reviewerNotes}
								onChange={(e) => setReviewerNotes(e.target.value)}
								sx={{ mb: 2 }}
								placeholder="승인/거부/검토 요청 시 메모를 남기세요"
							/>

							<Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
								{currentStatus === "draft" && (
									<Button
										variant="outlined"
										startIcon={<SendOutlined />}
										onClick={handleSubmitForReview}
										disabled={isSubmittingForReview}
										fullWidth
									>
										검토 요청
									</Button>
								)}

								{currentStatus === "in_review" && (
									<>
										<Button
											variant="contained"
											color="success"
											startIcon={<CheckCircle />}
											onClick={handleApprove}
											disabled={isApprovingTemplate}
											fullWidth
										>
											승인
										</Button>
										<Button
											variant="outlined"
											color="error"
											startIcon={<Cancel />}
											onClick={handleReject}
											disabled={isRejectingTemplate}
											fullWidth
										>
											거부
										</Button>
									</>
								)}
							</Box>
						</Paper>
					)}

					{/* Main Actions */}
					<Paper sx={{ p: 3 }}>
						<Typography variant="h6" sx={{ mb: 2 }}>
							액션
						</Typography>

						<Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
							<Button
								variant="contained"
								startIcon={<Save />}
								onClick={handleSave}
								disabled={isCreatingTemplate || isUpdatingTemplate}
								fullWidth
							>
								저장
							</Button>

							<Button
								variant="outlined"
								startIcon={<Assessment />}
								onClick={handleEvaluate}
								disabled={isEvaluatingPrompt || !templateContent}
								fullWidth
							>
								품질 평가
							</Button>

							<Button
								variant="outlined"
								onClick={() => router.back()}
								fullWidth
							>
								취소
							</Button>
						</Box>
					</Paper>
				</Grid>
			</Grid>
		</Box>
	);
}
