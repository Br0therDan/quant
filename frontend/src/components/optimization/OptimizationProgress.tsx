import type { OptimizationProgress as OptimizationProgressData } from "@/client/types.gen";
import { useOptimizationStudy } from "@/hooks/useOptimization";
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  PlayArrow as PlayArrowIcon,
  Stop as StopIcon,
} from "@mui/icons-material";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Grid,
  LinearProgress,
  Typography,
} from "@mui/material";
import { useMemo } from "react";

interface OptimizationProgressProps {
  studyName: string;
  pollInterval?: number;
  onStop?: () => void;
  showStopButton?: boolean;
}

/**
 * OptimizationProgress Component
 *
 * Real-time optimization progress tracking with:
 * - Progress bar and percentage
 * - Trial counter (completed/total)
 * - Current best value
 * - Estimated completion time
 * - Status indicators
 * - Stop button
 *
 * Uses useOptimizationStudy hook with 5-second polling.
 *
 * @example
 * ```tsx
 * <OptimizationProgress
 *   studyName="study_20240114_123456"
 *   pollInterval={5000}
 *   onStop={() => console.log("Stop requested")}
 *   showStopButton
 * />
 * ```
 */
export function OptimizationProgress({
  studyName,
  pollInterval = 5000,
  onStop,
  showStopButton = true,
}: OptimizationProgressProps) {
  const {
    progress: progressResponse,
    progressPercent,
    isCompleted,
    isFailed,
    isRunning,
    refetch,
  } = useOptimizationStudy(studyName, {
    pollInterval,
    enabled: true,
  });

  // Extract actual progress data
  const progress = progressResponse?.data as
    | OptimizationProgressData
    | undefined;

  // Calculate estimated completion time
  const estimatedCompletion = useMemo(() => {
    if (!progress?.trials_completed || !progress?.n_trials) {
      return null;
    }

    const trialsCompleted = progress.trials_completed;
    const totalTrials = progress.n_trials;

    if (trialsCompleted === 0) {
      return null;
    }

    // Estimate based on average trial time
    // Assuming we have start_time in the future (not in current API)
    // For now, return placeholder
    const remainingTrials = totalTrials - trialsCompleted;
    const averageTrialTime = 10; // seconds (placeholder)
    const estimatedSeconds = remainingTrials * averageTrialTime;

    return estimatedSeconds;
  }, [progress]);

  // Format estimated time
  const formatEstimatedTime = (seconds: number | null) => {
    if (!seconds) return "계산 중...";

    if (seconds < 60) {
      return `약 ${Math.round(seconds)}초`;
    }

    if (seconds < 3600) {
      return `약 ${Math.round(seconds / 60)}분`;
    }

    return `약 ${Math.round(seconds / 3600)}시간`;
  };

  // Render status icon
  const renderStatusIcon = () => {
    if (isCompleted) {
      return <CheckCircleIcon color="success" fontSize="large" />;
    }

    if (isFailed) {
      return <ErrorIcon color="error" fontSize="large" />;
    }

    if (isRunning) {
      return <PlayArrowIcon color="primary" fontSize="large" />;
    }

    return <CircularProgress size={32} />;
  };

  // Render status chip
  const renderStatusChip = () => {
    if (isCompleted) {
      return <Chip label="완료" color="success" size="small" />;
    }

    if (isFailed) {
      return <Chip label="실패" color="error" size="small" />;
    }

    if (isRunning) {
      return <Chip label="실행 중" color="primary" size="small" />;
    }

    return <Chip label="대기 중" color="default" size="small" />;
  };

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: "flex", alignItems: "center", mb: 3 }}>
          {renderStatusIcon()}
          <Box sx={{ ml: 2, flex: 1 }}>
            <Typography variant="h6" gutterBottom>
              {studyName}
            </Typography>
            {renderStatusChip()}
          </Box>
        </Box>

        {/* Progress Bar */}
        <Box sx={{ mb: 3 }}>
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              mb: 1,
            }}
          >
            <Typography variant="body2" color="text.secondary">
              진행률
            </Typography>
            <Typography variant="body2" fontWeight="bold">
              {progressPercent}%
            </Typography>
          </Box>

          <LinearProgress
            variant="determinate"
            value={progressPercent}
            sx={{
              height: 10,
              borderRadius: 5,
              backgroundColor: "action.hover",
              "& .MuiLinearProgress-bar": {
                borderRadius: 5,
              },
            }}
          />
        </Box>

        {/* Trial Counter */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid size={6}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="caption" color="text.secondary">
                  완료된 트라이얼
                </Typography>
                <Typography variant="h5" color="primary">
                  {progress?.trials_completed || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid size={6}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="caption" color="text.secondary">
                  전체 트라이얼
                </Typography>
                <Typography variant="h5">{progress?.n_trials || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Best Value */}
        {progress?.best_value !== undefined && (
          <Box sx={{ mb: 3 }}>
            <Card variant="outlined" sx={{ bgcolor: "success.light" }}>
              <CardContent>
                <Typography variant="caption" color="text.secondary">
                  현재 최적 값
                </Typography>
                <Typography variant="h4" color="success.dark">
                  {typeof progress?.best_value === "number"
                    ? progress.best_value.toFixed(4)
                    : progress?.best_value}
                </Typography>
                {progress?.best_params && (
                  <Box
                    sx={{ mt: 1, display: "flex", flexWrap: "wrap", gap: 1 }}
                  >
                    {Object.entries(progress.best_params).map(
                      ([key, value]) => (
                        <Chip
                          key={key}
                          label={`${key}: ${
                            typeof value === "number" ? value.toFixed(2) : value
                          }`}
                          size="small"
                          variant="outlined"
                        />
                      )
                    )}
                  </Box>
                )}
              </CardContent>
            </Card>
          </Box>
        )}

        {/* Estimated Completion Time */}
        {isRunning && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary">
              예상 완료 시간: {formatEstimatedTime(estimatedCompletion)}
            </Typography>
          </Box>
        )}

        {/* Recent Trials */}
        {progress?.recent_trials && progress.recent_trials.length > 0 && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              최근 트라이얼
            </Typography>
            {progress.recent_trials.slice(0, 3).map((trial) => (
              <Card
                key={trial.trial_number}
                variant="outlined"
                sx={{ mb: 1, p: 1 }}
              >
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    mb: 1,
                  }}
                >
                  <Typography variant="caption">
                    Trial #{trial.trial_number}
                  </Typography>
                  <Typography variant="caption" fontWeight="bold">
                    {typeof trial.value === "number"
                      ? trial.value.toFixed(4)
                      : trial.value}
                  </Typography>
                </Box>
                <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5 }}>
                  {Object.entries(trial.params).map(([key, value]) => (
                    <Chip
                      key={key}
                      label={`${key}: ${
                        typeof value === "number" ? value.toFixed(2) : value
                      }`}
                      size="small"
                      sx={{ fontSize: "0.7rem" }}
                    />
                  ))}
                </Box>
              </Card>
            ))}
          </Box>
        )}

        {/* Status Messages */}
        {isCompleted && (
          <Alert severity="success" sx={{ mb: 2 }}>
            최적화가 성공적으로 완료되었습니다!
          </Alert>
        )}

        {isFailed && (
          <Alert severity="error" sx={{ mb: 2 }}>
            최적화 실행 중 오류가 발생했습니다.
          </Alert>
        )}

        {/* Action Buttons */}
        <Box sx={{ display: "flex", gap: 2 }}>
          {showStopButton && isRunning && onStop && (
            <Button
              variant="contained"
              color="error"
              startIcon={<StopIcon />}
              onClick={onStop}
              fullWidth
            >
              중단
            </Button>
          )}

          {(isCompleted || isFailed) && (
            <Button
              variant="outlined"
              onClick={() => refetch.progress()}
              fullWidth
            >
              새로고침
            </Button>
          )}
        </Box>
      </CardContent>
    </Card>
  );
}
