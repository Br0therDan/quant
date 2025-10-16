"use client";

import { ChatHistoryPanel } from "@/components/gen-ai/chatops/ChatHistoryPanel";
import { ChatInterface } from "@/components/gen-ai/chatops/ChatInterface";
import { ModelSelector } from "@/components/gen-ai/chatops/ModelSelector";
import PageContainer from "@/components/layout/PageContainer";
import { useChatOps } from "@/hooks/useChatOps";
import { Chat, History, SmartToy, Speed } from "@mui/icons-material";
import { Box, Card, CardContent, Grid, Typography } from "@mui/material";

/**
 * ChatOps 페이지
 *
 * User Story: US-20 (GenAI 채팅 인터페이스)
 * 기능:
 * - 대화형 AI 채팅 인터페이스
 * - 모델 선택 (GPT-4, Claude, etc.)
 * - 채팅 히스토리 관리
 * - Context-aware 응답
 */
export default function ChatOpsPage() {
  const breadcrumbs = [
    { title: "GenAI Platform", href: "/gen-ai" },
    { title: "ChatOps" },
  ];

  // Real-time ChatOps hook (WebSocket 기반)
  const { isConnected, currentSessionId } = useChatOps();

  // KPI data from hook (placeholder for WebSocket stats)
  const kpiData = [
    {
      label: "Connection Status",
      value: isConnected ? "Connected" : "Disconnected",
      icon: <Chat color={isConnected ? "success" : "error"} />,
    },
    {
      label: "Current Session",
      value: currentSessionId ? "Active" : "None",
      icon: <SmartToy color="primary" />,
    },
    {
      label: "Avg Response Time",
      value: "1.2s",
      icon: <Speed color="info" />,
    },
    { label: "Chat History", value: "-", icon: <History color="warning" /> },
  ];

  return (
    <PageContainer title="ChatOps" breadcrumbs={breadcrumbs}>
      <Grid container spacing={3}>
        {/* KPI 카드 */}
        {kpiData.map((kpi, index) => (
          <Grid key={index} size={{ xs: 12, sm: 6, md: 3 }}>
            <Card>
              <CardContent>
                <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                  {kpi.icon}
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="body2" color="text.secondary">
                      {kpi.label}
                    </Typography>
                    <Typography variant="h5">{kpi.value}</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}

        {/* 메인 컨텐츠 */}
        <Grid size={{ xs: 12, md: 3 }}>
          {/* 채팅 히스토리 */}
          <ChatHistoryPanel />
        </Grid>

        <Grid size={{ xs: 12, md: 6 }}>
          {/* 채팅 인터페이스 */}
          <ChatInterface />
        </Grid>

        <Grid size={{ xs: 12, md: 3 }}>
          {/* 모델 선택 및 설정 */}
          <ModelSelector />
        </Grid>
      </Grid>
    </PageContainer>
  );
}
