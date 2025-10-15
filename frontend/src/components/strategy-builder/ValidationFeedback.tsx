/**
 * ValidationFeedback Component
 *
 * 파라미터 검증 결과 표시
 *
 * Phase: 3
 * 작성일: 2025-10-14
 */

import type { ParameterValidation } from "@/client";
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
} from "@mui/icons-material";
import {
  Alert,
  Box,
  Card,
  CardContent,
  Chip,
  Stack,
  Typography,
} from "@mui/material";
import type React from "react";

export interface ValidationFeedbackProps {
  validations: ParameterValidation[];
}

export const ValidationFeedback: React.FC<ValidationFeedbackProps> = ({
  validations,
}) => {
  const errors = validations.filter((v) => !v.is_valid);
  const warnings = validations.filter(
    (v) => v.is_valid && v.validation_status === "warning"
  );
  const success = validations.filter(
    (v) => v.is_valid && v.validation_status === "valid"
  );

  return (
    <Card sx={{ mb: 2, bgcolor: "background.paper" }}>
      <CardContent>
        <Typography variant="subtitle2" gutterBottom>
          파라미터 검증 결과
        </Typography>

        <Stack spacing={1}>
          {/* 성공 */}
          {success.length > 0 && (
            <Alert
              severity="success"
              icon={<CheckCircleIcon />}
              sx={{ py: 0.5 }}
            >
              <Stack direction="row" spacing={1} alignItems="center">
                <Typography variant="body2">
                  {success.length}개 파라미터 검증 통과
                </Typography>
                <Stack direction="row" spacing={0.5}>
                  {success.map((v) => (
                    <Chip
                      key={String(v.parameter_name)}
                      label={String(v.parameter_name)}
                      size="small"
                      color="success"
                      variant="outlined"
                    />
                  ))}
                </Stack>
              </Stack>
            </Alert>
          )}

          {/* 경고 */}
          {warnings.map((v) => (
            <Alert
              key={String(v.parameter_name)}
              severity="warning"
              icon={<WarningIcon />}
              sx={{ py: 0.5 }}
            >
              <Typography variant="body2" fontWeight="bold">
                {String(v.parameter_name)}
              </Typography>
              {v.message && (
                <Typography variant="caption" display="block">
                  • {v.message}
                </Typography>
              )}
              {v.suggested_value ? (
                <Typography
                  variant="caption"
                  color="success.main"
                  display="block"
                  sx={{ mt: 0.5 }}
                >
                  💡 제안값: {String(JSON.stringify(v.suggested_value))}
                </Typography>
              ) : null}
            </Alert>
          ))}

          {/* 오류 */}
          {errors.map((v) => (
            <Alert
              key={String(v.parameter_name)}
              severity="error"
              icon={<ErrorIcon />}
              sx={{ py: 0.5 }}
            >
              <Typography variant="body2" fontWeight="bold">
                {String(v.parameter_name)}
              </Typography>
              {v.message && (
                <Typography variant="caption" display="block">
                  • {v.message}
                </Typography>
              )}
              {v.suggested_value ? (
                <Typography
                  variant="caption"
                  color="info.main"
                  display="block"
                  sx={{ mt: 0.5 }}
                >
                  💡 제안값: {String(JSON.stringify(v.suggested_value))}
                </Typography>
              ) : null}
              {v.value_range ? (
                <Typography
                  variant="caption"
                  color="text.secondary"
                  display="block"
                  sx={{ mt: 0.5 }}
                >
                  허용 범위: {String(JSON.stringify(v.value_range))}
                </Typography>
              ) : null}
            </Alert>
          ))}
        </Stack>

        {/* 요약 통계 */}
        <Box sx={{ mt: 2, pt: 1, borderTop: 1, borderColor: "divider" }}>
          <Stack direction="row" spacing={2} justifyContent="center">
            <Chip
              icon={<CheckCircleIcon />}
              label={`성공 ${success.length}`}
              color="success"
              size="small"
            />
            <Chip
              icon={<WarningIcon />}
              label={`경고 ${warnings.length}`}
              color="warning"
              size="small"
            />
            <Chip
              icon={<ErrorIcon />}
              label={`오류 ${errors.length}`}
              color="error"
              size="small"
            />
          </Stack>
        </Box>
      </CardContent>
    </Card>
  );
};
