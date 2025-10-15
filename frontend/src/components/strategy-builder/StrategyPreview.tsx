/**
 * StrategyPreview Component
 *
 * Monaco 에디터 기반 생성된 전략 코드 미리보기
 *
 * Phase: 3
 * 작성일: 2025-10-14
 */

import type { GeneratedStrategyConfig } from "@/client";
import { useSnackbar } from "@/contexts/SnackbarContext";
import Editor from "@monaco-editor/react";
import {
	Code as CodeIcon,
	ContentCopy as ContentCopyIcon,
	Download as DownloadIcon,
} from "@mui/icons-material";
import {
	Box,
	Card,
	CardContent,
	IconButton,
	Stack,
	Tooltip,
	Typography,
} from "@mui/material";
import type React from "react";
import { useState } from "react";

export interface StrategyPreviewProps {
	strategy: GeneratedStrategyConfig;
}

export const StrategyPreview: React.FC<StrategyPreviewProps> = ({
	strategy,
}) => {
	const { showSuccess } = useSnackbar();
	const [editorHeight] = useState(400);

	// GeneratedStrategyConfig를 Python 코드로 변환
	const generateCode = () => {
		return `# ${strategy.strategy_name}
# ${strategy.description}

from typing import Dict, Any, List

class ${strategy.strategy_name.replace(/\s+/g, "")}:
    """
    전략 타입: ${strategy.strategy_type}

    진입 조건:
    ${strategy.entry_conditions}

    청산 조건:
    ${strategy.exit_conditions}
    ${
			strategy.risk_management
				? `\n    리스크 관리:\n    ${strategy.risk_management}`
				: ""
		}
    """

    def __init__(self):
        self.parameters = ${JSON.stringify(
					strategy.parameters,
					null,
					8,
				).replace(/"/g, "'")}
        self.indicators = [
${strategy.indicators
	.map((ind) => `            "${ind.indicator_name}",  # ${ind.indicator_type}`)
	.join("\n")}
        ]

    def generate_signals(self, data: Dict[str, Any]) -> List[str]:
        """매매 신호 생성"""
        signals = []
        # TODO: 신호 로직 구현
        return signals
`;
	};

	const code = generateCode();

	const handleCopy = async () => {
		try {
			await navigator.clipboard.writeText(code);
			showSuccess("전략 코드가 클립보드에 복사되었습니다");
		} catch (error) {
			console.error("복사 실패:", error);
		}
	};

	const handleDownload = () => {
		const blob = new Blob([code], { type: "text/plain" });

		const url = URL.createObjectURL(blob);
		const a = document.createElement("a");
		a.href = url;
		a.download = `${strategy.strategy_name || "strategy"}.py`;
		a.click();
		URL.revokeObjectURL(url);
		showSuccess("전략 코드가 다운로드되었습니다");
	};

	return (
		<Card sx={{ mb: 2, bgcolor: "background.paper" }}>
			<CardContent>
				<Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
					<CodeIcon color="primary" />
					<Box sx={{ flexGrow: 1 }}>
						<Typography variant="subtitle2">생성된 전략 코드</Typography>
						<Typography variant="caption" color="text.secondary">
							{strategy.strategy_name}
						</Typography>
					</Box>
					<Tooltip title="복사">
						<IconButton size="small" onClick={handleCopy}>
							<ContentCopyIcon fontSize="small" />
						</IconButton>
					</Tooltip>
					<Tooltip title="다운로드">
						<IconButton size="small" onClick={handleDownload}>
							<DownloadIcon fontSize="small" />
						</IconButton>
					</Tooltip>
				</Stack>

				<Box sx={{ border: 1, borderColor: "divider", borderRadius: 1 }}>
					<Editor
						height={editorHeight}
						defaultLanguage="python"
						value={code}
						theme="vs-dark"
						options={{
							readOnly: true,
							minimap: { enabled: false },
							scrollBeyondLastLine: false,
							fontSize: 13,
							lineNumbers: "on",
							renderLineHighlight: "none",
						}}
					/>
				</Box>

				{strategy.parameter_validations?.some((v) => !v.is_valid) && (
					<Typography
						variant="caption"
						color="error.main"
						sx={{ mt: 1, display: "block" }}
					>
						⚠️ 파라미터 검증 오류{" "}
						{strategy.parameter_validations.filter((v) => !v.is_valid).length}개
					</Typography>
				)}
			</CardContent>
		</Card>
	);
};
