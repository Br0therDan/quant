/**
 * VersionControl 컴포넌트
 * 프롬프트 버전 히스토리 및 롤백, 승인 워크플로우
 */

import type { PromptTemplateResponse } from "@/client/types.gen";
import { useGenAI } from "@/hooks/useGenAI";
import { CheckCircle, History, RemoveCircle, Send } from "@mui/icons-material";
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

export const VersionControl = () => {
  const {
    promptTemplatesList,
    isLoadingTemplates,
    submitPromptForReview,
    isSubmittingForReview,
    approvePrompt,
    isApprovingPrompt,
    rejectPrompt,
    isRejectingPrompt,
    usePromptAuditLogs,
  } = useGenAI();

  const [selectedTemplate, setSelectedTemplate] =
    useState<PromptTemplateResponse | null>(null);
  const [openWorkflowDialog, setOpenWorkflowDialog] = useState(false);
  const [workflowAction, setWorkflowAction] = useState<
    "submit" | "approve" | "reject"
  >("submit");
  const [reviewer, setReviewer] = useState("");
  const [notes, setNotes] = useState("");

  // Audit Logs Query (조건부)
  const auditLogsQuery = usePromptAuditLogs(
    selectedTemplate?.prompt_id || "",
    Number.parseInt(selectedTemplate?.version || "0")
  );

  const handleWorkflowAction = (
    template: PromptTemplateResponse,
    action: "submit" | "approve" | "reject"
  ) => {
    setSelectedTemplate(template);
    setWorkflowAction(action);
    setReviewer("");
    setNotes("");
    setOpenWorkflowDialog(true);
  };

  const handleSubmitWorkflow = () => {
    if (!selectedTemplate) return;

    const promptId = selectedTemplate.prompt_id;
    const version = Number.parseInt(selectedTemplate.version);

    switch (workflowAction) {
      case "submit":
        submitPromptForReview({
          promptId,
          version,
          reviewer,
          notes,
        });
        break;
      case "approve":
        approvePrompt({
          promptId,
          version,
          reviewer,
          notes,
        });
        break;
      case "reject":
        rejectPrompt({
          promptId,
          version,
          reviewer,
          notes,
        });
        break;
    }

    setOpenWorkflowDialog(false);
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, "success" | "warning" | "error" | "default"> =
      {
        approved: "success",
        pending: "warning",
        rejected: "error",
        draft: "default",
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
      <Grid container spacing={3}>
        {/* Template List */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Template Versions
              </Typography>
              <TableContainer component={Paper}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Prompt ID</TableCell>
                      <TableCell>Version</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {promptTemplatesList?.map((template) => (
                      <TableRow
                        key={`${template.prompt_id}-${template.version}`}
                        selected={
                          selectedTemplate?.prompt_id === template.prompt_id &&
                          selectedTemplate?.version === template.version
                        }
                        onClick={() => setSelectedTemplate(template)}
                        sx={{ cursor: "pointer" }}
                      >
                        <TableCell>{template.prompt_id}</TableCell>
                        <TableCell>
                          <Chip label={`v${template.version}`} size="small" />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={template.status}
                            color={getStatusColor(template.status)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          {template.status === "draft" && (
                            <Button
                              size="small"
                              startIcon={<Send />}
                              onClick={(e) => {
                                e.stopPropagation();
                                handleWorkflowAction(template, "submit");
                              }}
                            >
                              Submit
                            </Button>
                          )}
                          {template.status === "pending" && (
                            <>
                              <Button
                                size="small"
                                startIcon={<CheckCircle />}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleWorkflowAction(template, "approve");
                                }}
                                color="success"
                              >
                                Approve
                              </Button>
                              <Button
                                size="small"
                                startIcon={<RemoveCircle />}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleWorkflowAction(template, "reject");
                                }}
                                color="error"
                              >
                                Reject
                              </Button>
                            </>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                    {(!promptTemplatesList ||
                      promptTemplatesList.length === 0) && (
                      <TableRow>
                        <TableCell colSpan={4} align="center">
                          <Typography variant="body2" color="text.secondary">
                            템플릿이 없습니다.
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

        {/* Audit Trail */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card>
            <CardContent>
              <Box
                sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2 }}
              >
                <History />
                <Typography variant="h6">Audit Trail</Typography>
              </Box>

              {!selectedTemplate ? (
                <Alert severity="info">
                  왼쪽에서 템플릿을 선택하면 변경 이력을 확인할 수 있습니다.
                </Alert>
              ) : auditLogsQuery.isLoading ? (
                <Typography>로딩 중...</Typography>
              ) : auditLogsQuery.error ? (
                <Alert severity="error">
                  감사 로그를 불러오는 중 오류가 발생했습니다.
                </Alert>
              ) : (
                <>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    gutterBottom
                  >
                    {selectedTemplate.prompt_id} v{selectedTemplate.version}
                  </Typography>

                  {auditLogsQuery.data &&
                  auditLogsQuery.data.logs?.length > 0 ? (
                    <List>
                      {auditLogsQuery.data.logs.map((log, index) => (
                        <Box key={index}>
                          <ListItem alignItems="flex-start">
                            <ListItemIcon>
                              {log.action === "approved" ? (
                                <CheckCircle color="success" />
                              ) : log.action === "rejected" ? (
                                <RemoveCircle color="error" />
                              ) : (
                                <Send color="primary" />
                              )}
                            </ListItemIcon>
                            <ListItemText
                              primary={
                                <Typography variant="body2" fontWeight="medium">
                                  {log.action}
                                </Typography>
                              }
                              secondary={
                                <>
                                  <Typography
                                    variant="caption"
                                    color="text.secondary"
                                    component="span"
                                    display="block"
                                  >
                                    {log.reviewer} -{" "}
                                    {new Date(log.timestamp).toLocaleString()}
                                  </Typography>
                                  {log.notes && (
                                    <Typography variant="body2" sx={{ mt: 0.5 }}>
                                      {log.notes}
                                    </Typography>
                                  )}
                                </>
                              }
                            />
                          </ListItem>
                          {index < auditLogsQuery.data.logs.length - 1 && (
                            <Divider variant="inset" component="li" />
                          )}
                        </Box>
                      ))}
                    </List>
                  ) : (
                    <Alert severity="info">변경 이력이 없습니다.</Alert>
                  )}
                </>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Workflow Dialog */}
      <Dialog
        open={openWorkflowDialog}
        onClose={() => setOpenWorkflowDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          {workflowAction === "submit" && "Submit for Review"}
          {workflowAction === "approve" && "Approve Template"}
          {workflowAction === "reject" && "Reject Template"}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid size={12}>
              <TextField
                fullWidth
                label="Reviewer"
                value={reviewer}
                onChange={(e) => setReviewer(e.target.value)}
                required
                placeholder="Enter reviewer name or email"
              />
            </Grid>
            <Grid size={12}>
              <TextField
                fullWidth
                label="Notes"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                multiline
                rows={4}
                placeholder={
                  workflowAction === "reject"
                    ? "Please provide reason for rejection"
                    : "Add any comments or notes"
                }
                required={workflowAction === "reject"}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenWorkflowDialog(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleSubmitWorkflow}
            disabled={
              isSubmittingForReview ||
              isApprovingPrompt ||
              isRejectingPrompt ||
              !reviewer ||
              (workflowAction === "reject" && !notes)
            }
            color={
              workflowAction === "approve"
                ? "success"
                : workflowAction === "reject"
                ? "error"
                : "primary"
            }
          >
            {workflowAction === "submit" && "Submit"}
            {workflowAction === "approve" && "Approve"}
            {workflowAction === "reject" && "Reject"}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};
