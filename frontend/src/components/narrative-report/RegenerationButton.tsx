/**
 * RegenerationButton Component
 *
 * 내러티브 리포트 재생성 버튼
 *
 * 기능:
 * - 리포트 재생성 (새로운 LLM 호출)
 * - 생성 옵션 (언어, 상세도)
 * - 생성 중 로딩 상태
 *
 * Phase: 3
 * 작성일: 2025-10-14
 */

import { Refresh as RefreshIcon } from "@mui/icons-material";
import { Button, CircularProgress } from "@mui/material";
import type React from "react";

// ========================================================================================
// Props Interface
// ========================================================================================

export interface RegenerationButtonProps {
  backtestId: string;
  onRegenerate: () => void;
  isGenerating: boolean;
  label?: string;
  variant?: "text" | "outlined" | "contained";
  disabled?: boolean;
}

// ========================================================================================
// Main Component
// ========================================================================================

export const RegenerationButton: React.FC<RegenerationButtonProps> = ({
  onRegenerate,
  isGenerating,
  label = "재생성",
  variant = "outlined",
  disabled = false,
}) => {
  return (
    <Button
      variant={variant}
      startIcon={
        isGenerating ? <CircularProgress size={16} /> : <RefreshIcon />
      }
      onClick={onRegenerate}
      disabled={disabled || isGenerating}
    >
      {isGenerating ? "LLM 생성 중..." : label}
    </Button>
  );
};
