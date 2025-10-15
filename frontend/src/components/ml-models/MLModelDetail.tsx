/**
 * MLModelDetail Component
 *
 * Phase 1 Day 4: ML Model Detail View
 * - Performance metrics chart (Recharts LineChart)
 * - Accuracy, Precision, Recall, F1 Score
 * - Feature Importance bar chart
 * - Delete model button
 */

"use client";

import { useDeleteModel, useModelDetail } from "@/hooks/useMLModel";
import CloseIcon from "@mui/icons-material/Close";
import DeleteIcon from "@mui/icons-material/Delete";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  Stack,
  Typography,
} from "@mui/material";
import Grid from "@mui/material/Grid";
import { useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface MLModelDetailProps {
  version: string;
  onClose: () => void;
  open?: boolean;
}

export const MLModelDetail = ({
  version,
  onClose,
  open = true,
}: MLModelDetailProps) => {
  const { modelDetail, isLoading, error } = useModelDetail(version);
  const { deleteModel, isDeleting } = useDeleteModel();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  // Prepare metrics data for chart
  const metricsData = modelDetail?.metrics
    ? [
        {
          name: "Accuracy",
          value: (modelDetail.metrics.accuracy || 0) * 100,
        },
        {
          name: "Precision",
          value: (modelDetail.metrics.precision || 0) * 100,
        },
        {
          name: "Recall",
          value: (modelDetail.metrics.recall || 0) * 100,
        },
        {
          name: "F1 Score",
          value: (modelDetail.metrics.f1_score || 0) * 100,
        },
      ]
    : [];

  // Prepare feature importance data (mock data for now)
  const featureImportanceData = modelDetail?.feature_names
    ? modelDetail.feature_names.slice(0, 10).map((name) => ({
        feature: name,
        importance: Math.random() * 0.3 + 0.1, // Mock importance
      }))
    : [];

  const handleDelete = async () => {
    try {
      await deleteModel.mutateAsync({
        path: { version },
        url: "/api/v1/ml/train/models/{version}",
      });
      setDeleteDialogOpen(false);
      onClose();
    } catch {
      // Error handled by mutation (Snackbar)
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          minHeight: "80vh",
        },
      }}
    >
      <DialogTitle>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
            <Typography variant="h6">모델 상세</Typography>
            {modelDetail && (
              <Chip label={modelDetail.version} color="primary" />
            )}
          </Box>
          <Button onClick={onClose} startIcon={<CloseIcon />}>
            닫기
          </Button>
        </Box>
      </DialogTitle>

      <DialogContent dividers>
        {/* Loading State */}
        {isLoading && (
          <Box
            sx={{
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              minHeight: 400,
            }}
          >
            <CircularProgress />
          </Box>
        )}

        {/* Error State */}
        {error && (
          <Alert severity="error">모델 상세 조회 실패: {error.message}</Alert>
        )}

        {/* Model Details */}
        {modelDetail && (
          <Box sx={{ flexGrow: 1 }}>
            {/* Basic Information */}
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  기본 정보
                </Typography>
                <Grid container spacing={2}>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <Stack spacing={1}>
                      <Box>
                        <Typography variant="caption" color="text.secondary">
                          버전
                        </Typography>
                        <Typography variant="body1">
                          {modelDetail.version}
                        </Typography>
                      </Box>
                      <Box>
                        <Typography variant="caption" color="text.secondary">
                          모델 타입
                        </Typography>
                        <Typography variant="body1">
                          {modelDetail.model_type}
                        </Typography>
                      </Box>
                    </Stack>
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <Stack spacing={1}>
                      <Box>
                        <Typography variant="caption" color="text.secondary">
                          생성일
                        </Typography>
                        <Typography variant="body1">
                          {new Date(modelDetail.created_at).toLocaleString(
                            "ko-KR"
                          )}
                        </Typography>
                      </Box>
                      <Box>
                        <Typography variant="caption" color="text.secondary">
                          특징 수
                        </Typography>
                        <Typography variant="body1">
                          {modelDetail.feature_count}개
                        </Typography>
                      </Box>
                      <Box>
                        <Typography variant="caption" color="text.secondary">
                          반복 횟수
                        </Typography>
                        <Typography variant="body1">
                          {modelDetail.num_iterations}
                        </Typography>
                      </Box>
                    </Stack>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>

            {/* Performance Metrics Chart */}
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  성능 지표
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={metricsData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis domain={[0, 100]} />
                    <Tooltip
                      formatter={(value: number) => `${value.toFixed(2)}%`}
                    />
                    <Legend />
                    <Bar dataKey="value" fill="#1976d2" name="점수 (%)" />
                  </BarChart>
                </ResponsiveContainer>

                <Divider sx={{ my: 2 }} />

                {/* Detailed Metrics */}
                <Grid container spacing={2}>
                  <Grid size={{ xs: 6, sm: 3 }}>
                    <Box sx={{ textAlign: "center" }}>
                      <Typography variant="h4" color="primary">
                        {((modelDetail.metrics?.accuracy || 0) * 100).toFixed(
                          2
                        )}
                        %
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Accuracy
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid size={{ xs: 6, sm: 3 }}>
                    <Box sx={{ textAlign: "center" }}>
                      <Typography variant="h4" color="secondary">
                        {((modelDetail.metrics?.precision || 0) * 100).toFixed(
                          2
                        )}
                        %
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Precision
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid size={{ xs: 6, sm: 3 }}>
                    <Box sx={{ textAlign: "center" }}>
                      <Typography variant="h4" color="success.main">
                        {((modelDetail.metrics?.recall || 0) * 100).toFixed(2)}%
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Recall
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid size={{ xs: 6, sm: 3 }}>
                    <Box sx={{ textAlign: "center" }}>
                      <Typography variant="h4" color="warning.main">
                        {((modelDetail.metrics?.f1_score || 0) * 100).toFixed(
                          2
                        )}
                        %
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        F1 Score
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>

            {/* Feature Importance Chart */}
            {featureImportanceData.length > 0 && (
              <Card sx={{ mb: 3 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    특징 중요도 (상위 10개)
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart
                      data={featureImportanceData}
                      layout="vertical"
                      margin={{ left: 100 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" domain={[0, 0.5]} />
                      <YAxis type="category" dataKey="feature" width={100} />
                      <Tooltip
                        formatter={(value: number) => value.toFixed(4)}
                      />
                      <Legend />
                      <Bar dataKey="importance" fill="#82ca9d" name="중요도" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            )}

            {/* Feature List */}
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  전체 특징 ({modelDetail.feature_names?.length || 0}개)
                </Typography>
                <Box
                  sx={{
                    display: "flex",
                    flexWrap: "wrap",
                    gap: 1,
                    maxHeight: 200,
                    overflowY: "auto",
                  }}
                >
                  {modelDetail.feature_names?.map((feature, index) => (
                    <Chip key={index} label={feature} size="small" />
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Box>
        )}
      </DialogContent>

      <DialogActions>
        <Button
          color="error"
          startIcon={<DeleteIcon />}
          onClick={() => setDeleteDialogOpen(true)}
          disabled={isDeleting}
        >
          모델 삭제
        </Button>
      </DialogActions>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogTitle>모델 삭제 확인</DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            이 작업은 되돌릴 수 없습니다.
          </Alert>
          <Typography>
            정말로 모델 <strong>{version}</strong>을(를) 삭제하시겠습니까?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>취소</Button>
          <Button
            color="error"
            variant="contained"
            onClick={handleDelete}
            disabled={isDeleting}
          >
            {isDeleting ? "삭제 중..." : "삭제"}
          </Button>
        </DialogActions>
      </Dialog>
    </Dialog>
  );
};
