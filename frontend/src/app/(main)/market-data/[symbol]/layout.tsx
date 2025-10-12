"use client";

import { Box, Container, Tab, Tabs } from "@mui/material";
import { useParams, usePathname, useRouter } from "next/navigation";
import type React from "react";

import MarketDataSidebar from "@/components/market-data/MarketDataSidebar";

export default function SymbolLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const params = useParams();
  const pathname = usePathname();
  const router = useRouter();
  const symbol = params.symbol as string;

  // 현재 활성 탭 결정
  const getActiveTab = () => {
    if (pathname === `/market-data/${symbol}`) return "overview";
    if (pathname.includes("/financials")) return "financials";
    if (pathname.includes("/news")) return "news";
    if (pathname.includes("/chart")) return "chart";
    return "overview";
  };

  const activeTab = getActiveTab();

  const handleTabChange = (_event: React.SyntheticEvent, newValue: string) => {
    switch (newValue) {
      case "overview":
        router.push(`/market-data/${symbol}`);
        break;
      case "financials":
        router.push(`/market-data/${symbol}/financials`);
        break;
      case "news":
        router.push(`/market-data/${symbol}/news`);
        break;
      case "chart":
        router.push(`/market-data/${symbol}/chart`);
        break;
    }
  };

  return (
    <Box sx={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      {/* 탭 네비게이션 */}
      <Box
        sx={{
          borderBottom: 1,
          borderColor: "divider",
        }}
      >
        <Container maxWidth="xl">
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            aria-label="symbol navigation tabs"
            sx={{
              "& .MuiTab-root": {
                py: 2, // 위아래 패딩 증가
                minHeight: 56, // 최소 높이 증가
              },
            }}
          >
            <Tab label="개요" value="overview" />
            <Tab label="차트" value="chart" />
            <Tab label="재무제표" value="financials" />
            <Tab label="뉴스 & 분석" value="news" />
          </Tabs>
        </Container>
      </Box>

      {/* 메인 콘텐츠 + 우측 사이드바 */}
      <Box sx={{ display: "flex", flexGrow: 1, overflow: "hidden" }}>
        {/* 페이지 콘텐츠 */}
        <Box sx={{ flexGrow: 1, overflow: "auto" }}>{children}</Box>

        {/* 우측 사이드바 */}
        <Box
          sx={{
            width: 320,
            flexShrink: 0,
            overflow: "auto",
            display: { xs: "none", lg: "block" },
          }}
        >
          <MarketDataSidebar currentSymbol={symbol} />
        </Box>
      </Box>
    </Box>
  );
}
