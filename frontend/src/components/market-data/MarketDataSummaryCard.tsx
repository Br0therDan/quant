"use client";

import {
  TrendingDown as TrendingDownIcon,
  TrendingUp as TrendingUpIcon,
} from "@mui/icons-material";
import {
  Box,
  Card,
  CardContent,
  Chip,
  Typography,
  useTheme,
} from "@mui/material";

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

interface MarketDataSummaryCardProps {
  data: MarketDataSummary | null;
  isLoading?: boolean;
}

export default function MarketDataSummaryCard({
  data,
  isLoading = false,
}: MarketDataSummaryCardProps) {
  const theme = useTheme();

  if (isLoading || !data) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            {isLoading ? "데이터 로딩 중..." : "종목을 선택하세요"}
          </Typography>
        </CardContent>
      </Card>
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
    if (volume >= 1_000_000) {
      return `${formatNumber(volume / 1_000_000, 1)}M`;
    } else if (volume >= 1_000) {
      return `${formatNumber(volume / 1_000, 1)}K`;
    }
    return formatNumber(volume, 0);
  };

  return (
    <Card>
      <CardContent>
        <Box
          display="flex"
          alignItems="center"
          justifyContent="space-between"
          mb={2}
        >
          <Typography variant="h5" component="h2">
            {data.symbol}
          </Typography>
          <Chip
            icon={isPositive ? <TrendingUpIcon /> : <TrendingDownIcon />}
            label={`${isPositive ? "+" : ""}${formatNumber(
              data.changePercent
            )}%`}
            color={isPositive ? "success" : "error"}
            variant="filled"
          />
        </Box>

        <Box display="flex" alignItems="baseline" gap={1} mb={3}>
          <Typography variant="h4" component="span">
            ${formatNumber(data.currentPrice)}
          </Typography>
          <Typography variant="h6" component="span" sx={{ color: changeColor }}>
            {isPositive ? "+" : ""}${formatNumber(data.change)}
          </Typography>
        </Box>

        <Box
          display="grid"
          gridTemplateColumns="repeat(auto-fit, minmax(120px, 1fr))"
          gap={2}
        >
          <Box>
            <Typography variant="caption" color="text.secondary">
              시가
            </Typography>
            <Typography variant="body2">${formatNumber(data.open)}</Typography>
          </Box>

          <Box>
            <Typography variant="caption" color="text.secondary">
              고가
            </Typography>
            <Typography
              variant="body2"
              sx={{ color: theme.palette.success.main }}
            >
              ${formatNumber(data.high)}
            </Typography>
          </Box>

          <Box>
            <Typography variant="caption" color="text.secondary">
              저가
            </Typography>
            <Typography
              variant="body2"
              sx={{ color: theme.palette.error.main }}
            >
              ${formatNumber(data.low)}
            </Typography>
          </Box>

          <Box>
            <Typography variant="caption" color="text.secondary">
              거래량
            </Typography>
            <Typography variant="body2">{formatVolume(data.volume)}</Typography>
          </Box>

          <Box>
            <Typography variant="caption" color="text.secondary">
              전일 종가
            </Typography>
            <Typography variant="body2">
              ${formatNumber(data.previousClose)}
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}
