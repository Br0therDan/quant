/**
 * PromptTemplateEditor 컴포넌트
 * 프롬프트 템플릿 CRUD 및 평가 기능
 */

import type { PromptTemplateResponse } from "@/client/types.gen";
import { useGenAI } from "@/hooks/useGenAI";
import { Add, Code, PlayArrow, Save } from "@mui/icons-material";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  Grid,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { useState } from "react";

export const PromptTemplateEditor = () => {
  const {
    promptTemplatesList,
    isLoadingTemplates,
    createPromptTemplate,
    isCreatingTemplate,
    updatePromptTemplate,
    isUpdatingTemplate,
    evaluatePrompt,
    isEvaluatingPrompt,
    evaluationResult,
  } = useGenAI();

  const [openDialog, setOpenDialog] = useState(false);
  const [editingTemplate, setEditingTemplate] =
    useState<PromptTemplateResponse | null>(null);
  const [formData, setFormData] = useState({
    prompt_id: "",
    content: "",
    version: "1",
    name: "",
    description: "",
    owner: "system",
    tags: [] as string[],
  });

  const handleCreateNew = () => {
    setEditingTemplate(null);
    setFormData({
      prompt_id: "",
      content: "",
      version: "1",
      name: "",
      description: "",
      owner: "system",
      tags: [],
    });
    setOpenDialog(true);
  };

  const handleEdit = (template: PromptTemplateResponse) => {
    setEditingTemplate(template);
    setFormData({
      prompt_id: template.prompt_id,
      content: template.content,
      version: template.version,
      name: template.name,
      description: template.description || "",
      owner: template.owner,
      tags: template.tags || [],
    });
    setOpenDialog(true);
  };

  const handleSave = () => {
    if (editingTemplate) {
      // 업데이트
      updatePromptTemplate({
        promptId: formData.prompt_id,
        version: Number.parseInt(formData.version, 10),
        data: {
          name: formData.name,
          description: formData.description,
          content: formData.content,
        },
      });
    } else {
      // 생성
      createPromptTemplate({
        prompt_id: formData.prompt_id,
        name: formData.name,
        content: formData.content,
        version: formData.version,
        description: formData.description,
        owner: formData.owner,
        tags: formData.tags,
      });
    }
    setOpenDialog(false);
  };

  const handleEvaluate = () => {
    evaluatePrompt({
      prompt_id: formData.prompt_id,
      version: formData.version,
      content: formData.content,
    });
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, "success" | "warning" | "error" | "default"> =
      {
        approved: "success",
        in_review: "warning",
        rejected: "error",
        draft: "default",
        archived: "default",
      };
    return colors[status] || "default";
  };

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
    <>
      <Card>
        <CardContent>
          <Box sx={{ display: "flex", justifyContent: "space-between", mb: 3 }}>
            <Typography variant="h6">Prompt Template Editor</Typography>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={handleCreateNew}
            >
              New Template
            </Button>
          </Box>

          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Prompt ID</TableCell>
                  <TableCell>Version</TableCell>
                  <TableCell>Tags</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Risk Level</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {promptTemplatesList?.map((template) => (
                  <TableRow key={`${template.prompt_id}-${template.version}`}>
                    <TableCell>
                      <Typography variant="body2" fontWeight="medium">
                        {template.prompt_id}
                      </Typography>
                      {template.description && (
                        <Typography variant="caption" color="text.secondary">
                          {template.description}
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      <Chip label={`v${template.version}`} size="small" />
                    </TableCell>
                    <TableCell>
                      {template.tags.length > 0 ? (
                        <Box
                          sx={{ display: "flex", gap: 0.5, flexWrap: "wrap" }}
                        >
                          {template.tags.slice(0, 2).map((tag) => (
                            <Chip key={tag} label={tag} size="small" />
                          ))}
                          {template.tags.length > 2 && (
                            <Chip
                              label={`+${template.tags.length - 2}`}
                              size="small"
                            />
                          )}
                        </Box>
                      ) : (
                        <Typography variant="caption" color="text.secondary">
                          No tags
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={template.status}
                        color={getStatusColor(template.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={template.risk_level}
                        color={
                          template.risk_level === "high"
                            ? "error"
                            : template.risk_level === "medium"
                            ? "warning"
                            : "success"
                        }
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Button size="small" onClick={() => handleEdit(template)}>
                        Edit
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
                {(!promptTemplatesList || promptTemplatesList.length === 0) && (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      <Typography variant="body2" color="text.secondary">
                        템플릿이 없습니다. 새 템플릿을 생성하세요.
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* 생성/수정 Dialog */}
      <Dialog
        open={openDialog}
        onClose={() => setOpenDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {editingTemplate ? "Edit Template" : "Create New Template"}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField
                fullWidth
                label="Prompt ID"
                value={formData.prompt_id}
                onChange={(e) =>
                  setFormData({ ...formData, prompt_id: e.target.value })
                }
                disabled={!!editingTemplate}
                required
              />
            </Grid>
            <Grid size={{ xs: 12, md: 3 }}>
              <TextField
                fullWidth
                label="Version"
                value={formData.version}
                onChange={(e) =>
                  setFormData({ ...formData, version: e.target.value })
                }
                disabled={!!editingTemplate}
                required
              />
            </Grid>
            <Grid size={{ xs: 12, md: 3 }}>
              <TextField
                fullWidth
                label="Owner"
                value={formData.owner}
                onChange={(e) =>
                  setFormData({ ...formData, owner: e.target.value })
                }
                required
              />
            </Grid>

            <Grid size={12}>
              <TextField
                fullWidth
                label="Name"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                required
              />
            </Grid>

            <Grid size={12}>
              <TextField
                fullWidth
                label="Description"
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
                multiline
                rows={2}
              />
            </Grid>

            <Grid size={12}>
              <TextField
                fullWidth
                label="Prompt Content"
                value={formData.content}
                onChange={(e) =>
                  setFormData({ ...formData, content: e.target.value })
                }
                multiline
                rows={8}
                required
                placeholder="Enter your prompt content here..."
                InputProps={{
                  startAdornment: (
                    <Code sx={{ mr: 1, color: "text.secondary" }} />
                  ),
                }}
              />
            </Grid>

            <Grid size={12}>
              <TextField
                fullWidth
                label="Tags (comma-separated)"
                value={formData.tags.join(", ")}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    tags: e.target.value
                      .split(",")
                      .map((t) => t.trim())
                      .filter(Boolean),
                  })
                }
                placeholder="strategy, trading, risk-management"
              />
            </Grid>

            {/* Evaluation Result */}
            {evaluationResult && (
              <Grid size={12}>
                <Divider sx={{ my: 2 }} />
                <Typography variant="subtitle2" gutterBottom>
                  Evaluation Result
                </Typography>
                <Alert
                  severity={
                    evaluationResult.evaluation.risk_level === "high"
                      ? "error"
                      : evaluationResult.evaluation.risk_level === "medium"
                      ? "warning"
                      : "info"
                  }
                >
                  <Typography variant="body2">
                    <strong>Risk Level:</strong>{" "}
                    {evaluationResult.evaluation.risk_level}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Toxicity Score:</strong>{" "}
                    {(evaluationResult.evaluation.toxicity_score * 100).toFixed(
                      1
                    )}
                    %
                  </Typography>
                  <Typography variant="body2">
                    <strong>Hallucination Score:</strong>{" "}
                    {(
                      evaluationResult.evaluation.hallucination_score * 100
                    ).toFixed(1)}
                    %
                  </Typography>
                  <Typography variant="body2">
                    <strong>Factual Consistency:</strong>{" "}
                    {(
                      evaluationResult.evaluation.factual_consistency * 100
                    ).toFixed(1)}
                    %
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    <strong>Evaluator:</strong>{" "}
                    {evaluationResult.evaluation.evaluator}
                  </Typography>
                  {evaluationResult.evaluation.evaluated_at && (
                    <Typography variant="caption" color="text.secondary">
                      Evaluated at:{" "}
                      {new Date(
                        evaluationResult.evaluation.evaluated_at
                      ).toLocaleString()}
                    </Typography>
                  )}
                </Alert>
              </Grid>
            )}
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button
            startIcon={<PlayArrow />}
            onClick={handleEvaluate}
            disabled={isEvaluatingPrompt || !formData.content}
          >
            Evaluate
          </Button>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button
            variant="contained"
            startIcon={<Save />}
            onClick={handleSave}
            disabled={
              isCreatingTemplate ||
              isUpdatingTemplate ||
              !formData.prompt_id ||
              !formData.content
            }
          >
            {editingTemplate ? "Update" : "Create"}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};
