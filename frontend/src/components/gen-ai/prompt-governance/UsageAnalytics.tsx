/**
 * UsageAnalytics 컴포넌트
 * 프롬프트 사용 분석 (토큰 소비, 성능 메트릭)
 */

import type { PromptTemplateResponse } from "@/client/types.gen";
import { useGenAI } from "@/hooks/useGenAI";
import {
  Analytics,
  Speed,
  TrendingDown,
  TrendingUp,
} from "@mui/icons-material";
import {
  Alert,
  Box,
  Card,
  CardContent,
  Chip,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import { useState } from "react";

export const UsageAnalytics = () => {
  const { promptTemplatesList, isLoadingTemplates, usePromptAuditLogs } =
    useGenAI();

  const [selectedTemplate, setSelectedTemplate] =
    useState<PromptTemplateResponse | null>(null);

  // Audit Logs Query (조건부)
  const auditLogsQuery = usePromptAuditLogs(
    selectedTemplate?.prompt_id || "",
    Number.parseInt(selectedTemplate?.version || "0", 10)
  );

  // 사용 통계 계산
  const usageStats = {
    totalCalls: auditLogsQuery.data?.length || 0,
    avgTokens: 1234, // TODO: 실제 계산 로직
    avgLatency: 234, // TODO: 실제 계산 로직
    successRate: 94.5, // TODO: 실제 계산 로직
  };

  // Mock 데이터 (TODO: 실제 API 연동)
  const topTemplates = promptTemplatesList?.slice(0, 5) || [];

  if (isLoadingTemplates) {
    return (
      <Card>
        <CardContent>
          <Typography>템플릿 로딩 중...</Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Grid container spacing={3}>
      {/* KPI Cards */}
      <Grid size={{ xs: 12, sm: 6, md: 3 }}>
        <Card>
          <CardContent>
            <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
              <Analytics color="primary" />
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Total Calls
                </Typography>
                <Typography variant="h5">{usageStats.totalCalls}</Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid size={{ xs: 12, sm: 6, md: 3 }}>
        <Card>
          <CardContent>
            <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
              <TrendingUp color="success" />
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Avg Tokens
                </Typography>
                <Typography variant="h5">{usageStats.avgTokens}</Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid size={{ xs: 12, sm: 6, md: 3 }}>
        <Card>
          <CardContent>
            <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
              <Speed color="info" />
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Avg Latency
                </Typography>
                <Typography variant="h5">{usageStats.avgLatency}ms</Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid size={{ xs: 12, sm: 6, md: 3 }}>
        <Card>
          <CardContent>
            <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
              <TrendingDown color="warning" />
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Success Rate
                </Typography>
                <Typography variant="h5">{usageStats.successRate}%</Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Template Selector */}
      <Grid size={12}>
        <Card>
          <CardContent>
            <FormControl fullWidth>
              <InputLabel>Select Template</InputLabel>
              <Select
                value={selectedTemplate?.prompt_id || ""}
                label="Select Template"
                onChange={(e) => {
                  const template = promptTemplatesList?.find(
                    (t) => t.prompt_id === e.target.value
                  );
                  setSelectedTemplate(template || null);
                }}
              >
                <MenuItem value="">
                  <em>All Templates</em>
                </MenuItem>
                {promptTemplatesList?.map((template) => (
                  <MenuItem
                    key={`${template.prompt_id}-${template.version}`}
                    value={template.prompt_id}
                  >
                    {template.prompt_id} (v{template.version})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </CardContent>
        </Card>
      </Grid>

      {/* Top Templates */}
      <Grid size={{ xs: 12, md: 6 }}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Top Templates by Usage
            </Typography>
            <TableContainer component={Paper}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Template</TableCell>
                    <TableCell>Version</TableCell>
                    <TableCell align="right">Calls</TableCell>
                    <TableCell align="right">Avg Tokens</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {topTemplates.map((template, index) => (
                    <TableRow key={`${template.prompt_id}-${template.version}`}>
                      <TableCell>{template.prompt_id}</TableCell>
                      <TableCell>
                        <Chip label={`v${template.version}`} size="small" />
                      </TableCell>
                      <TableCell align="right">
                        {(100 - index * 15).toLocaleString()}
                      </TableCell>
                      <TableCell align="right">
                        {(1500 - index * 100).toLocaleString()}
                      </TableCell>
                    </TableRow>
                  ))}
                  {topTemplates.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={4} align="center">
                        <Typography variant="body2" color="text.secondary">
                          데이터가 없습니다.
                        </Typography>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </Grid>

      {/* Usage Logs */}
      <Grid size={{ xs: 12, md: 6 }}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Recent Usage Logs
            </Typography>

            {!selectedTemplate ? (
              <Alert severity="info">
                템플릿을 선택하면 사용 로그를 확인할 수 있습니다.
              </Alert>
            ) : auditLogsQuery.isLoading ? (
              <Typography>로딩 중...</Typography>
            ) : auditLogsQuery.error ? (
              <Alert severity="error">
                로그를 불러오는 중 오류가 발생했습니다.
              </Alert>
            ) : (
              <TableContainer component={Paper}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Timestamp</TableCell>
                      <TableCell>Action</TableCell>
                      <TableCell>Reviewer</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {auditLogsQuery.data?.map((log, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Typography variant="caption">
                            {new Date(log.created_at).toLocaleString()}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip label={log.action} size="small" />
                        </TableCell>
                        <TableCell>{log.actor}</TableCell>
                      </TableRow>
                    ))}
                    {(!auditLogsQuery.data ||
                      auditLogsQuery.data.length === 0) && (
                      <TableRow>
                        <TableCell colSpan={3} align="center">
                          <Typography variant="body2" color="text.secondary">
                            로그가 없습니다.
                          </Typography>
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </CardContent>
        </Card>
      </Grid>

      {/* Performance Metrics */}
      <Grid size={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Performance Metrics
            </Typography>
            <Alert severity="info">
              성능 메트릭 차트는 향후 추가될 예정입니다. (Token usage over time,
              Latency trends, Error rates 등)
            </Alert>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};
