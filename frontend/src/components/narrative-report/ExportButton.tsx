/**
 * ExportButton Component
 *
 * 내러티브 리포트 PDF 내보내기 버튼
 *
 * 기능:
 * - jsPDF 기반 PDF 생성
 * - 파일명 커스터마이징
 * - 내보내기 중 로딩 상태
 *
 * Phase: 3
 * 작성일: 2025-10-14
 */

import type { PDFExportOptions } from "@/hooks/useNarrativeReport";
import {
  Download as DownloadIcon,
  PictureAsPdf as PdfIcon,
} from "@mui/icons-material";
import {
  Button,
  CircularProgress,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
} from "@mui/material";
import type React from "react";
import { useState } from "react";

// ========================================================================================
// Props Interface
// ========================================================================================

export interface ExportButtonProps {
  backtestId: string;
  onExport: (options?: PDFExportOptions) => Promise<void>;
  disabled?: boolean;
}

// ========================================================================================
// Main Component
// ========================================================================================

export const ExportButton: React.FC<ExportButtonProps> = ({
  backtestId,
  onExport,
  disabled = false,
}) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [isExporting, setIsExporting] = useState(false);

  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleExport = async (options: PDFExportOptions) => {
    handleClose();
    setIsExporting(true);
    try {
      await onExport(options);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <>
      <Button
        variant="outlined"
        startIcon={
          isExporting ? <CircularProgress size={16} /> : <DownloadIcon />
        }
        onClick={handleClick}
        disabled={disabled || isExporting}
      >
        {isExporting ? "PDF 생성 중..." : "내보내기"}
      </Button>
      <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleClose}>
        <MenuItem
          onClick={() =>
            handleExport({
              filename: `backtest_report_${backtestId}.pdf`,
              pageSize: "a4",
              orientation: "portrait",
            })
          }
        >
          <ListItemIcon>
            <PdfIcon />
          </ListItemIcon>
          <ListItemText>PDF (A4, 세로)</ListItemText>
        </MenuItem>
        <MenuItem
          onClick={() =>
            handleExport({
              filename: `backtest_report_${backtestId}.pdf`,
              pageSize: "a4",
              orientation: "landscape",
            })
          }
        >
          <ListItemIcon>
            <PdfIcon />
          </ListItemIcon>
          <ListItemText>PDF (A4, 가로)</ListItemText>
        </MenuItem>
        <MenuItem
          onClick={() =>
            handleExport({
              filename: `backtest_report_${backtestId}.pdf`,
              pageSize: "letter",
              orientation: "portrait",
            })
          }
        >
          <ListItemIcon>
            <PdfIcon />
          </ListItemIcon>
          <ListItemText>PDF (Letter)</ListItemText>
        </MenuItem>
      </Menu>
    </>
  );
};
