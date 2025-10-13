/**
 * Data Quality Indicator - 데이터 품질 세부 지표
 *
 * Epic 2: Story 2.2 - 결측치 비율, 이상값 등 데이터 품질 시각화
 */
"use client";

import {
  CheckCircle,
  Error as ErrorIcon,
  Info as InfoIcon,
  Warning,
} from "@mui/icons-material";
import {
  Box,
  Card,
  CardContent,
  Chip,
  LinearProgress,
  Stack,
  Tooltip,
  Typography,
} from "@mui/material";

interface DataQualityMetrics {
  completeness: number; // 0-100, 데이터 완전성 (결측치 역수)
  consistency: number; // 0-100, 데이터 일관성
  accuracy: number; // 0-100, 정확도 (이상값 역수)
  timeliness: number; // 0-100, 최신성
  overall_score: number; // 0-100, 종합 점수
  issues?: {
    missing_dates?: number;
    outliers?: number;
    duplicates?: number;
    stale_data_days?: number;
  };
}

interface DataQualityIndicatorProps {
  symbol: string;
  metrics?: DataQualityMetrics;
  isLoading?: boolean;
}

function QualityMetricBar({
  label,
  value,
  description,
}: {
  label: string;
  value: number;
  description: string;
}) {
  const getColor = (val: number) => {
    if (val >= 90) return "success";
    if (val >= 70) return "warning";
    return "error";
  };

  const getIcon = (val: number) => {
    if (val >= 90) return <CheckCircle fontSize="small" color="success" />;
    if (val >= 70) return <Warning fontSize="small" color="warning" />;
    return <ErrorIcon fontSize="small" color="error" />;
  };

  return (
    <Tooltip title={description} arrow>
      <Box>
        <Box
          display="flex"
          alignItems="center"
          justifyContent="space-between"
          mb={0.5}
        >
          <Box display="flex" alignItems="center" gap={1}>
            {getIcon(value)}
            <Typography variant="caption">{label}</Typography>
          </Box>
          <Typography variant="caption" fontWeight="medium">
            {value.toFixed(1)}%
          </Typography>
        </Box>
        <LinearProgress
          variant="determinate"
          value={value}
          color={getColor(value)}
          sx={{ height: 6, borderRadius: 3 }}
        />
      </Box>
    </Tooltip>
  );
}

export default function DataQualityIndicator({
  metrics,
  isLoading = false,
}: Omit<DataQualityIndicatorProps, "symbol">) {
  const getOverallGrade = (score: number) => {
    if (score >= 90) return { grade: "A", color: "success" };
    if (score >= 80) return { grade: "B", color: "info" };
    if (score >= 70) return { grade: "C", color: "warning" };
    if (score >= 60) return { grade: "D", color: "warning" };
    return { grade: "F", color: "error" };
  };

  const grade = metrics
    ? getOverallGrade(metrics.overall_score)
    : { grade: "-", color: "default" };

  return (
    <Card>
      <CardContent>
        <Box
          display="flex"
          alignItems="center"
          justifyContent="space-between"
          mb={2}
        >
          <Typography variant="h6">데이터 품질 지표</Typography>
          <Chip
            label={`등급: ${grade.grade}`}
            color={grade.color as any}
            sx={{ fontWeight: "bold", fontSize: "0.875rem" }}
          />
        </Box>

        {isLoading ? (
          <LinearProgress />
        ) : metrics ? (
          <Stack spacing={2}>
            {/* 종합 점수 */}
            <Box>
              <Box
                display="flex"
                alignItems="center"
                justifyContent="space-between"
                mb={1}
              >
                <Typography variant="body2" fontWeight="medium">
                  종합 품질 점수
                </Typography>
                <Typography
                  variant="h4"
                  color={`${grade.color}.main`}
                  fontWeight="bold"
                >
                  {metrics.overall_score.toFixed(1)}
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={metrics.overall_score}
                color={grade.color as any}
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Box>

            {/* 세부 지표 */}
            <Stack spacing={1.5}>
              <QualityMetricBar
                label="완전성"
                value={metrics.completeness}
                description="결측치가 없는 데이터의 비율"
              />
              <QualityMetricBar
                label="일관성"
                value={metrics.consistency}
                description="데이터 패턴의 일관성"
              />
              <QualityMetricBar
                label="정확도"
                value={metrics.accuracy}
                description="이상값이 없는 데이터의 비율"
              />
              <QualityMetricBar
                label="최신성"
                value={metrics.timeliness}
                description="데이터 업데이트 주기"
              />
            </Stack>

            {/* 이슈 요약 */}
            {metrics.issues && Object.keys(metrics.issues).length > 0 && (
              <Box
                sx={{
                  p: 1.5,
                  borderRadius: 1,
                  bgcolor: "warning.light",
                  color: "warning.contrastText",
                }}
              >
                <Box display="flex" alignItems="center" gap={1} mb={1}>
                  <InfoIcon fontSize="small" />
                  <Typography variant="caption" fontWeight="medium">
                    발견된 이슈
                  </Typography>
                </Box>
                <Stack spacing={0.5}>
                  {metrics.issues.missing_dates !== undefined &&
                    metrics.issues.missing_dates > 0 && (
                      <Typography variant="caption">
                        • 결측 날짜: {metrics.issues.missing_dates}개
                      </Typography>
                    )}
                  {metrics.issues.outliers !== undefined &&
                    metrics.issues.outliers > 0 && (
                      <Typography variant="caption">
                        • 이상값: {metrics.issues.outliers}개
                      </Typography>
                    )}
                  {metrics.issues.duplicates !== undefined &&
                    metrics.issues.duplicates > 0 && (
                      <Typography variant="caption">
                        • 중복 데이터: {metrics.issues.duplicates}개
                      </Typography>
                    )}
                  {metrics.issues.stale_data_days !== undefined &&
                    metrics.issues.stale_data_days > 0 && (
                      <Typography variant="caption">
                        • 데이터 지연: {metrics.issues.stale_data_days}일
                      </Typography>
                    )}
                </Stack>
              </Box>
            )}

            {/* 권장 사항 */}
            {metrics.overall_score < 80 && (
              <Box
                sx={{
                  p: 1.5,
                  borderRadius: 1,
                  bgcolor: "info.light",
                  color: "info.contrastText",
                }}
              >
                <Typography variant="caption" fontWeight="medium">
                  💡 권장 사항
                </Typography>
                <Typography variant="caption" display="block" sx={{ mt: 0.5 }}>
                  {metrics.completeness < 80 &&
                    "• 데이터 재수집을 권장합니다.\n"}
                  {metrics.timeliness < 80 &&
                    "• 데이터 업데이트가 필요합니다.\n"}
                  {metrics.accuracy < 80 && "• 이상값 검증이 필요합니다."}
                </Typography>
              </Box>
            )}
          </Stack>
        ) : (
          <Typography variant="body2" color="text.secondary">
            품질 지표를 불러올 수 없습니다.
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}
