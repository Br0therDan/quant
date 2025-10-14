import type { DataQualityAlert, DataQualitySeverity } from "@/client/types.gen";
import {
  TrendingDown as CriticalIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  Warning as WarningIcon,
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
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Table,
  TableBody,
  TableCell,
  TableRow,
  Typography,
} from "@mui/material";
import { useState } from "react";

interface AlertTimelineProps {
  alerts: DataQualityAlert[];
  maxItems?: number;
}

/**
 * AlertTimeline Component
 *
 * 데이터 품질 알림 타임라인
 *
 * Features:
 * - MUI Timeline 컴포넌트 사용
 * - 심각도별 색상 코딩 (CRITICAL 🔴, HIGH 🟠, MEDIUM 🟡, LOW 🔵, NORMAL 🟢)
 * - 클릭 시 상세 정보 모달 표시
 * - 최대 표시 개수 제한 (기본 10개)
 *
 * @example
 * ```tsx
 * import { AlertTimeline } from "@/components/data-quality/AlertTimeline";
 * import { useDataQuality } from "@/hooks/useDataQuality";
 *
 * function AlertsPage() {
 *   const { recentAlerts } = useDataQuality();
 *   return <AlertTimeline alerts={recentAlerts} maxItems={20} />;
 * }
 * ```
 */
export function AlertTimeline({ alerts, maxItems = 10 }: AlertTimelineProps) {
  const [selectedAlert, setSelectedAlert] = useState<DataQualityAlert | null>(
    null
  );
  const [dialogOpen, setDialogOpen] = useState(false);

  // 알림 클릭 핸들러
  const handleAlertClick = (alert: DataQualityAlert) => {
    setSelectedAlert(alert);
    setDialogOpen(true);
  };

  // 모달 닫기
  const handleCloseDialog = () => {
    setDialogOpen(false);
    setSelectedAlert(null);
  };

  // 심각도별 아이콘 반환
  const getSeverityIcon = (severity: DataQualitySeverity) => {
    const icons = {
      critical: <CriticalIcon />,
      high: <ErrorIcon />,
      medium: <WarningIcon />,
      low: <InfoIcon />,
      normal: <InfoIcon />,
    };
    return icons[severity] || <InfoIcon />;
  };

  // 심각도별 색상 반환
  const getSeverityColor = (
    severity: DataQualitySeverity
  ): "error" | "warning" | "info" | "success" => {
    const colors = {
      critical: "error" as const,
      high: "error" as const,
      medium: "warning" as const,
      low: "info" as const,
      normal: "success" as const,
    };
    return colors[severity] || "info";
  };

  // 심각도 라벨 반환
  const getSeverityLabel = (severity: DataQualitySeverity) => {
    const labels = {
      critical: "긴급",
      high: "높음",
      medium: "중간",
      low: "낮음",
      normal: "정상",
    };
    return labels[severity] || severity;
  };

  // 알림이 없을 때
  if (!alerts || alerts.length === 0) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            알림 타임라인
          </Typography>
          <Box
            sx={{
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              height: 200,
            }}
          >
            <Typography variant="body2" color="text.secondary">
              최근 알림이 없습니다.
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  // 최대 개수만큼 표시
  const displayedAlerts = alerts.slice(0, maxItems);

  return (
    <>
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            알림 타임라인 ({alerts.length}개)
          </Typography>

          <Timeline position="right">
            {displayedAlerts.map((alert, index) => (
              <TimelineItem
                key={`${alert.symbol}-${index}`}
                onClick={() => handleAlertClick(alert)}
                sx={{
                  cursor: "pointer",
                  "&:hover": { bgcolor: "action.hover" },
                }}
              >
                <TimelineOppositeContent
                  color="text.secondary"
                  sx={{ flex: 0.3 }}
                >
                  <Typography variant="caption">
                    {new Date(alert.occurred_at).toLocaleDateString("ko-KR")}
                  </Typography>
                  <Typography variant="caption" display="block">
                    {new Date(alert.occurred_at).toLocaleTimeString("ko-KR")}
                  </Typography>
                </TimelineOppositeContent>

                <TimelineSeparator>
                  <TimelineDot color={getSeverityColor(alert.severity)}>
                    {getSeverityIcon(alert.severity)}
                  </TimelineDot>
                  {index < displayedAlerts.length - 1 && <TimelineConnector />}
                </TimelineSeparator>

                <TimelineContent>
                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      gap: 1,
                      mb: 0.5,
                    }}
                  >
                    <Chip
                      label={alert.symbol}
                      size="small"
                      variant="outlined"
                    />
                    <Chip
                      label={getSeverityLabel(alert.severity)}
                      size="small"
                      color={getSeverityColor(alert.severity)}
                    />
                    <Chip label={alert.data_type} size="small" />
                  </Box>
                  <Typography variant="body2">{alert.message}</Typography>
                </TimelineContent>
              </TimelineItem>
            ))}
          </Timeline>

          {alerts.length > maxItems && (
            <Typography
              variant="caption"
              color="primary"
              sx={{ mt: 2, display: "block", textAlign: "center" }}
            >
              + {alerts.length - maxItems}개 더 보기
            </Typography>
          )}
        </CardContent>
      </Card>

      {/* 상세 정보 모달 */}
      <Dialog
        open={dialogOpen}
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            {selectedAlert && getSeverityIcon(selectedAlert.severity)}
            <Typography variant="h6">알림 상세 정보</Typography>
          </Box>
        </DialogTitle>

        <DialogContent>
          {selectedAlert && (
            <Box>
              {/* 기본 정보 */}
              <Box sx={{ mb: 3 }}>
                <Typography
                  variant="subtitle2"
                  color="text.secondary"
                  gutterBottom
                >
                  기본 정보
                </Typography>
                <Table size="small">
                  <TableBody>
                    <TableRow>
                      <TableCell width="30%">심볼</TableCell>
                      <TableCell>
                        <Chip label={selectedAlert.symbol} size="small" />
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>심각도</TableCell>
                      <TableCell>
                        <Chip
                          label={getSeverityLabel(selectedAlert.severity)}
                          size="small"
                          color={getSeverityColor(selectedAlert.severity)}
                        />
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>데이터 타입</TableCell>
                      <TableCell>{selectedAlert.data_type}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>발생 시각</TableCell>
                      <TableCell>
                        {new Date(selectedAlert.occurred_at).toLocaleString(
                          "ko-KR"
                        )}
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </Box>

              {/* 메시지 */}
              <Box sx={{ mb: 3 }}>
                <Typography
                  variant="subtitle2"
                  color="text.secondary"
                  gutterBottom
                >
                  알림 메시지
                </Typography>
                <Typography variant="body2">{selectedAlert.message}</Typography>
              </Box>

              {/* 지표 */}
              <Box>
                <Typography
                  variant="subtitle2"
                  color="text.secondary"
                  gutterBottom
                >
                  이상 탐지 지표
                </Typography>
                <Table size="small">
                  <TableBody>
                    <TableRow>
                      <TableCell width="40%">Isolation Forest 점수</TableCell>
                      <TableCell>
                        {selectedAlert.iso_score.toFixed(4)}
                      </TableCell>
                    </TableRow>
                    {selectedAlert.prophet_score !== null && (
                      <TableRow>
                        <TableCell>Prophet 기반 잔차 점수</TableCell>
                        <TableCell>
                          {selectedAlert.prophet_score?.toFixed(4) || "N/A"}
                        </TableCell>
                      </TableRow>
                    )}
                    <TableRow>
                      <TableCell>전일 대비 변동률</TableCell>
                      <TableCell>
                        {selectedAlert.price_change_pct.toFixed(2)}%
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>거래량 Z-Score</TableCell>
                      <TableCell>
                        {selectedAlert.volume_z_score.toFixed(2)}
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </Box>
            </Box>
          )}
        </DialogContent>

        <DialogActions>
          <Button onClick={handleCloseDialog}>닫기</Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
