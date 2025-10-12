"use client";

import { Box } from "@mui/material";
import type React from "react";

import MarketDataSidebar from "@/components/market-data/MarketDataSidebar";
import { useParams } from 'next/navigation';
import SymbolTabs from '@/components/market-data/SymbolTabs';

export default function SymbolLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const params = useParams();
  const symbol = params.symbol as string;

  return (
    <Box sx={{ display: "flex", flexDirection: "column"}}>
      <SymbolTabs symbol={symbol} />
      {/* 메인 콘텐츠 + 우측 사이드바 */}
      <Box sx={{ display: "flex", flexGrow: 1, overflow: "hidden" }}>
        {/* 페이지 콘텐츠 */}
        <Box sx={{ flexGrow: 1, overflow: "auto" }}>{children}</Box>

        {/* 우측 사이드바 */}
        <Box
          sx={{
            width: 300,
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
