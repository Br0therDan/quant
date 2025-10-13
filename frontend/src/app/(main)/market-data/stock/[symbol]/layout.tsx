"use client";
import { Box } from "@mui/material";
import React from "react";

import MarketDataSidebar from "@/components/market-data/MarketDataSidebar";

export default function SymbolLayout({
	children,
	params,
}: {
	children: React.ReactNode;
	params: Promise<{ symbol: string }>;
}) {
	const { symbol } = React.use(params);
	const [sidebarWidth, setSidebarWidth] = React.useState(320);

	return (
		<Box sx={{ display: "flex", flexDirection: "column" }}>
			{/* 메인 콘텐츠 + 우측 사이드바 */}
			<Box sx={{ display: "flex", flexGrow: 1, overflow: "hidden" }}>
				{/* 페이지 콘텐츠 */}
				<Box
					sx={{
						flexGrow: 1,
						overflow: "auto",
						width: `calc(100% - ${sidebarWidth}px)`,
						transition: "width 0.1s ease-out",
					}}
				>
					{children}
				</Box>

				{/* 우측 사이드바 */}
				<Box
					sx={{
						width: sidebarWidth,
						flexShrink: 0,
						overflow: "auto",
						display: { xs: "none", lg: "block" },
						transition: "width 0.1s ease-out",
					}}
				>
					<MarketDataSidebar
						currentSymbol={symbol}
						width={sidebarWidth}
						onWidthChange={setSidebarWidth}
					/>
				</Box>
			</Box>
		</Box>
	);
}
