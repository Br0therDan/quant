"use client";

import { VerifiedUser as VerifiedIcon } from "@mui/icons-material";
import { Box, Chip, Typography, useTheme } from "@mui/material";
import dayjs from "dayjs";

interface SymbolOverviewHeaderProps {
  symbol: string;
  companyName: string;
  exchange?: string;
  priceChange: number;
  priceChangePercent: number;
  currentPrice: number;
}

export default function SymbolOverviewHeader({
  symbol,
  companyName,
  priceChange,
  priceChangePercent,
  currentPrice,
  exchange,
}: SymbolOverviewHeaderProps) {
  const theme = useTheme();
  const isPositive = priceChange >= 0;
  const changeColor = isPositive
    ? theme.palette.success.main
    : theme.palette.error.main;

  return (
    <Box sx={{ p: 3, pb: 0 }}>
      <Box alignItems="flex-start" mb={2}>
        {/* 왼쪽: 회사명 & 메타 정보 */}
        <Box alignItems="baseline">
          <Box alignItems="baseline" display={"flex"} gap={2}>
            <Typography fontWeight="800" fontSize={32} gutterBottom>
              {companyName}
            </Typography>
            <Box display="flex" gap={1} alignItems="center">
              <Typography color="text.secondary" fontWeight="600">
                {symbol}
              </Typography>
              <VerifiedIcon
                sx={{ fontSize: 16, color: "primary.main" }}
                titleAccess="Nasdaq Stock Market"
              />
              <Chip
                label={exchange}
                size="small"
                variant="outlined"
                sx={{ height: 20 }}
              />
            </Box>
          </Box>
        </Box>
        <Box>
          <Box display="flex" gap={2}>
            <Box display="flex" alignItems="baseline" gap={0.5} mt={0.5}>
              <Typography variant="h3" fontWeight="700">
                {currentPrice.toFixed(2)}
              </Typography>
              <Typography fontSize={14} color="text.secondary">
                USD
              </Typography>
            </Box>
            <Box display="flex" alignItems="flex-end" gap={1.5}>
              <Typography variant="h6" fontWeight="600" color={changeColor}>
                {isPositive ? "+" : "-"}
                {Math.abs(priceChange).toFixed(2)}
              </Typography>
              <Typography variant="h6" fontWeight="600" color={changeColor}>
                {isPositive ? "+" : "-"}
                {Math.abs(priceChangePercent).toFixed(2)}%
              </Typography>
            </Box>
          </Box>
          <Typography
            variant="caption"
            color="text.secondary"
            display="block"
            mt={0.5}
          >
            {dayjs().format("M월 D일 HH:mm")} 에 마감
          </Typography>
        </Box>
      </Box>
    </Box>
  );
}
