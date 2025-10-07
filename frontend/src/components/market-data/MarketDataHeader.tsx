"use client";

import {
  Timeline as TimelineIcon,
  TrendingDown as TrendingDownIcon,
  TrendingUp as TrendingUpIcon,
} from "@mui/icons-material";
import { Box, Chip, Typography, useTheme } from "@mui/material";

interface MarketDataSummary {
  symbol: string;
  currentPrice: number;
  change: number;
  changePercent: number;
  volume: number;
  high: number;
  low: number;
  open: number;
  previousClose: number;
}

interface MarketDataHeaderProps {
  data: MarketDataSummary | null;
  isLoading?: boolean;
}

export default function MarketDataHeader({
  data,
  isLoading = false,
}: MarketDataHeaderProps) {
  const theme = useTheme();

  if (isLoading || !data) {
    return (
      <Box
        sx={{
          p: 2,
          borderBottom: 1,
          borderColor: "divider",
          backgroundColor: theme.palette.background.paper,
        }}
      >
        <Typography variant="h6">
          {isLoading ? "데이터 로딩 중..." : "종목을 선택하세요"}
        </Typography>
      </Box>
    );
  }

  const isPositive = data.change >= 0;
  const changeColor = isPositive
    ? theme.palette.success.main
    : theme.palette.error.main;

  const formatNumber = (num: number, decimals = 2) => {
    return new Intl.NumberFormat("ko-KR", {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(num);
  };

  const formatVolume = (volume: number) => {
    if (volume >= 1_000_000_000) {
      return `${formatNumber(volume / 1_000_000_000, 2)}B`;
    } else if (volume >= 1_000_000) {
      return `${formatNumber(volume / 1_000_000, 1)}M`;
    } else if (volume >= 1_000) {
      return `${formatNumber(volume / 1_000, 1)}K`;
    }
    return formatNumber(volume, 0);
  };

  return (
    <Box
      sx={{
        p: 2,
        borderBottom: 1,
        borderColor: "divider",
      }}
    >
      <Box display="flex" alignItems="center" justifyContent="space-between">
        {/* 왼쪽: 심볼 및 가격 정보 */}
        <Box display="flex" alignItems="center" gap={3}>
          {/* 심볼과 아이콘 */}
          <Box display="flex" alignItems="center" gap={1}>
            <TimelineIcon sx={{ color: theme.palette.primary.main }} />
            <Typography variant="h5" component="span" fontWeight="bold">
              {data.symbol}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              주식 · NASDAQ
            </Typography>
          </Box>

          {/* 현재 가격 */}
          <Box display="flex" alignItems="baseline" gap={1}>
            <Typography variant="h4" component="span" fontWeight="bold">
              {formatNumber(data.currentPrice)}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              USD
            </Typography>
          </Box>

          {/* 변동액과 변동률 */}
          <Box display="flex" alignItems="center" gap={1}>
            <Typography variant="h6" sx={{ color: changeColor }}>
              {isPositive ? "+" : ""}
              {formatNumber(data.change)}
            </Typography>
            <Chip
              icon={isPositive ? <TrendingUpIcon /> : <TrendingDownIcon />}
              label={`${isPositive ? "+" : ""}${formatNumber(
                data.changePercent
              )}%`}
              color={isPositive ? "success" : "error"}
              variant="filled"
              size="small"
            />
          </Box>
        </Box>

        {/* 오른쪽: 추가 정보 */}
        <Box display="flex" alignItems="center" gap={3}>
          <Box textAlign="center">
            <Typography variant="caption" color="text.secondary">
              시가
            </Typography>
            <Typography variant="body2" fontWeight="medium">
              {formatNumber(data.open)}
            </Typography>
          </Box>

          <Box textAlign="center">
            <Typography variant="caption" color="text.secondary">
              고가
            </Typography>
            <Typography
              variant="body2"
              fontWeight="medium"
              sx={{ color: theme.palette.success.main }}
            >
              {formatNumber(data.high)}
            </Typography>
          </Box>

          <Box textAlign="center">
            <Typography variant="caption" color="text.secondary">
              저가
            </Typography>
            <Typography
              variant="body2"
              fontWeight="medium"
              sx={{ color: theme.palette.error.main }}
            >
              {formatNumber(data.low)}
            </Typography>
          </Box>

          <Box textAlign="center">
            <Typography variant="caption" color="text.secondary">
              거래량
            </Typography>
            <Typography variant="body2" fontWeight="medium">
              {formatVolume(data.volume)}
            </Typography>
          </Box>
        </Box>
      </Box>
    </Box>
  );
}
