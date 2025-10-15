/**
 * DatasetExplorer Component
 *
 * Displays datasets with:
 * - Dataset cards in grid layout
 * - Sample data preview table
 * - Feature correlation heatmap
 * - Download functionality
 *
 * @module components/mlops/feature-store/DatasetExplorer
 */

import {
  useDatasetDetail,
  useFeatureStore,
  type Dataset,
} from "@/hooks/useFeatureStore";
import DownloadIcon from "@mui/icons-material/Download";
import TableChartIcon from "@mui/icons-material/TableChart";
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
  Grid,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import { useState } from "react";
import {
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

// ============================================================================
// Component Props
// ============================================================================

interface DatasetExplorerProps {
  /**
   * Callback when dataset is selected
   */
  onDatasetSelect?: (datasetId: string) => void;
}

// ============================================================================
// Helper Functions
// ============================================================================

const getCorrelationColor = (correlation: number): string => {
  const absCorr = Math.abs(correlation);
  if (absCorr > 0.7) return correlation > 0 ? "#2e7d32" : "#c62828";
  if (absCorr > 0.4) return correlation > 0 ? "#66bb6a" : "#e57373";
  return "#90a4ae";
};

// ============================================================================
// Component Implementation
// ============================================================================

export const DatasetExplorer: React.FC<DatasetExplorerProps> = ({
  onDatasetSelect,
}) => {
  // ============================================================================
  // State
  // ============================================================================

  const [selectedDatasetId, setSelectedDatasetId] = useState<string | null>(
    null
  );
  const [previewDialogOpen, setPreviewDialogOpen] = useState(false);

  // ============================================================================
  // Hooks
  // ============================================================================

  const { datasetsList, isLoadingDatasets, datasetsError } = useFeatureStore();
  const { dataset: selectedDataset, isLoading: isLoadingDetail } =
    useDatasetDetail(selectedDatasetId);

  // ============================================================================
  // Event Handlers
  // ============================================================================

  const handleDatasetClick = (datasetId: string) => {
    setSelectedDatasetId(datasetId);
    setPreviewDialogOpen(true);
    onDatasetSelect?.(datasetId);
  };

  const handleDownloadClick = (datasetId: string, datasetName: string) => {
    // TODO: Implement actual download
    console.log(`Downloading dataset: ${datasetId}`);

    // Mock download
    const blob = new Blob([`Dataset: ${datasetName}`], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${datasetName}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // ============================================================================
  // Render Loading State
  // ============================================================================

  if (isLoadingDatasets) {
    return (
      <Card>
        <CardContent>
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
        </CardContent>
      </Card>
    );
  }

  // ============================================================================
  // Render Error State
  // ============================================================================

  if (datasetsError) {
    return (
      <Card>
        <CardContent>
          <Alert severity="error">
            데이터셋 로딩 실패: {datasetsError.message}
          </Alert>
        </CardContent>
      </Card>
    );
  }

  // ============================================================================
  // Render Empty State
  // ============================================================================

  if (!datasetsList || datasetsList.length === 0) {
    return (
      <Card>
        <CardContent>
          <Box sx={{ textAlign: "center", py: 4 }}>
            <TableChartIcon
              sx={{ fontSize: 64, color: "text.secondary", mb: 2 }}
            />
            <Typography variant="h6" color="text.secondary">
              데이터셋이 없습니다
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              데이터셋을 업로드하여 시작하세요
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  // ============================================================================
  // Prepare Correlation Chart Data
  // ============================================================================

  const correlationData =
    selectedDataset?.correlation_matrix?.map((item) => ({
      x: item.feature1,
      y: item.feature2,
      correlation: item.correlation,
    })) || [];

  // ============================================================================
  // Render
  // ============================================================================

  return (
    <>
      <Card>
        <CardContent>
          {/* Header */}
          <Typography variant="h6" component="h3" gutterBottom>
            데이터셋 탐색
          </Typography>

          {/* Dataset Grid */}
          <Grid container spacing={2}>
            {datasetsList.map((dataset: Dataset) => (
              <Grid size={{ xs: 12, sm: 6, md: 4 }} key={dataset.id}>
                <Card
                  variant="outlined"
                  sx={{
                    cursor: "pointer",
                    transition: "all 0.2s",
                    "&:hover": {
                      borderColor: "primary.main",
                      boxShadow: 2,
                    },
                  }}
                  onClick={() => handleDatasetClick(dataset.id)}
                >
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {dataset.name}
                    </Typography>

                    <Typography
                      variant="body2"
                      color="text.secondary"
                      paragraph
                    >
                      {dataset.description}
                    </Typography>

                    <Box
                      sx={{ display: "flex", gap: 1, mb: 2, flexWrap: "wrap" }}
                    >
                      <Chip
                        label={`${dataset.features.length} 피처`}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                      <Chip
                        label={`${dataset.row_count.toLocaleString()} 행`}
                        size="small"
                        color="secondary"
                        variant="outlined"
                      />
                    </Box>

                    <Box
                      sx={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                      }}
                    >
                      <Typography variant="caption" color="text.secondary">
                        {new Date(dataset.updated_at).toLocaleDateString(
                          "ko-KR"
                        )}
                      </Typography>
                      <Button
                        size="small"
                        startIcon={<DownloadIcon />}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDownloadClick(dataset.id, dataset.name);
                        }}
                      >
                        다운로드
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>

      {/* Dataset Preview Dialog */}
      <Dialog
        open={previewDialogOpen}
        onClose={() => setPreviewDialogOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>데이터셋 미리보기</DialogTitle>
        <DialogContent>
          {isLoadingDetail ? (
            <Box sx={{ display: "flex", justifyContent: "center", py: 4 }}>
              <CircularProgress />
            </Box>
          ) : selectedDataset ? (
            <Box>
              {/* Dataset Info */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  {selectedDataset.name}
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  {selectedDataset.description}
                </Typography>
                <Box sx={{ display: "flex", gap: 1 }}>
                  <Chip
                    label={`${selectedDataset.features.length} 피처`}
                    size="small"
                  />
                  <Chip
                    label={`${selectedDataset.row_count.toLocaleString()} 행`}
                    size="small"
                  />
                </Box>
              </Box>

              {/* Features List */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  포함된 피처
                </Typography>
                <Box sx={{ display: "flex", gap: 0.5, flexWrap: "wrap" }}>
                  {selectedDataset.features.map((feature) => (
                    <Chip
                      key={feature}
                      label={feature}
                      size="small"
                      variant="outlined"
                    />
                  ))}
                </Box>
              </Box>

              {/* Sample Data Table */}
              {selectedDataset.sample_data &&
                selectedDataset.sample_data.length > 0 && (
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      샘플 데이터 (최대 10행)
                    </Typography>
                    <TableContainer
                      component={Paper}
                      variant="outlined"
                      sx={{ maxHeight: 300 }}
                    >
                      <Table size="small" stickyHeader>
                        <TableHead>
                          <TableRow>
                            {Object.keys(selectedDataset.sample_data[0]).map(
                              (key) => (
                                <TableCell key={key}>{key}</TableCell>
                              )
                            )}
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {selectedDataset.sample_data
                            .slice(0, 10)
                            .map((row, index) => (
                              <TableRow key={index}>
                                {Object.values(row).map((value, cellIndex) => (
                                  <TableCell key={cellIndex}>
                                    {typeof value === "number"
                                      ? value.toFixed(2)
                                      : String(value)}
                                  </TableCell>
                                ))}
                              </TableRow>
                            ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </Box>
                )}

              {/* Correlation Heatmap */}
              {correlationData.length > 0 && (
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    피처 상관관계
                  </Typography>
                  <ResponsiveContainer width="100%" height={400}>
                    <ScatterChart
                      margin={{ top: 20, right: 20, bottom: 80, left: 80 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        type="category"
                        dataKey="x"
                        name="Feature 1"
                        angle={-45}
                        textAnchor="end"
                        height={80}
                      />
                      <YAxis
                        type="category"
                        dataKey="y"
                        name="Feature 2"
                        width={80}
                      />
                      <Tooltip
                        content={({ payload }) => {
                          if (!payload || !payload[0]) return null;
                          const data = payload[0].payload;
                          return (
                            <Paper sx={{ p: 1 }}>
                              <Typography variant="body2">
                                {data.x} ↔ {data.y}
                              </Typography>
                              <Typography variant="body2" fontWeight="bold">
                                상관계수: {data.correlation.toFixed(3)}
                              </Typography>
                            </Paper>
                          );
                        }}
                      />
                      <Scatter data={correlationData}>
                        {correlationData.map((entry, index) => (
                          <Cell
                            key={`cell-${index}`}
                            fill={getCorrelationColor(entry.correlation)}
                          />
                        ))}
                      </Scatter>
                    </ScatterChart>
                  </ResponsiveContainer>

                  {/* Legend */}
                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "center",
                      gap: 2,
                      mt: 2,
                    }}
                  >
                    <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                      <Box
                        sx={{
                          width: 16,
                          height: 16,
                          bgcolor: "#2e7d32",
                          borderRadius: 1,
                        }}
                      />
                      <Typography variant="caption">
                        강한 양의 상관관계 (&gt;0.7)
                      </Typography>
                    </Box>
                    <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                      <Box
                        sx={{
                          width: 16,
                          height: 16,
                          bgcolor: "#c62828",
                          borderRadius: 1,
                        }}
                      />
                      <Typography variant="caption">
                        강한 음의 상관관계 (&lt;-0.7)
                      </Typography>
                    </Box>
                    <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                      <Box
                        sx={{
                          width: 16,
                          height: 16,
                          bgcolor: "#90a4ae",
                          borderRadius: 1,
                        }}
                      />
                      <Typography variant="caption">약한 상관관계</Typography>
                    </Box>
                  </Box>
                </Box>
              )}
            </Box>
          ) : (
            <Alert severity="error">데이터셋을 불러올 수 없습니다</Alert>
          )}
        </DialogContent>
        <DialogActions>
          {selectedDataset && (
            <Button
              startIcon={<DownloadIcon />}
              onClick={() =>
                handleDownloadClick(selectedDataset.id, selectedDataset.name)
              }
            >
              다운로드
            </Button>
          )}
          <Button onClick={() => setPreviewDialogOpen(false)}>닫기</Button>
        </DialogActions>
      </Dialog>
    </>
  );
};
