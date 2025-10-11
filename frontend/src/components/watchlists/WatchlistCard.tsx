"use client";

import {
  Delete as DeleteIcon,
  Edit as EditIcon,
  MoreVert as MoreVertIcon,
} from "@mui/icons-material";
import {
  Box,
  Card,
  CardContent,
  Chip,
  IconButton,
  Menu,
  MenuItem,
  Paper,
  Skeleton,
  Typography,
} from "@mui/material";
import React from "react";

import { useStockQuote } from "@/hooks/useStocks";
import { useWatchlistDetail } from "@/hooks/useWatchList";

interface WatchlistCardProps {
  watchlist: {
    name: string;
    description?: string;
    symbol_count: number;
    auto_update: boolean;
    last_updated: string;
    created_at: string;
  };
  onEdit?: (watchlist: any) => void;
  onDelete?: (watchlistName: string) => void;
}

// 개별 티커 정보 컴포넌트 (리스트 형태)
const TickerListItem = ({ symbol }: { symbol: string }) => {
  const { data: quoteData, isLoading } = useStockQuote(symbol);

  if (isLoading) {
    return (
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          py: 1,
          px: 2,
        }}
      >
        <Skeleton variant="text" width="60px" height={20} />
        <Skeleton variant="text" width="60px" height={20} />
        <Skeleton variant="text" width="80px" height={20} />
      </Box>
    );
  }

  // quoteData 처리
  let quoteInfo: any = null;
  if (quoteData) {
    // quote API 응답 구조에 맞게 처리
    if (typeof quoteData === "object" && "data" in quoteData) {
      quoteInfo = (quoteData as any).data;
    } else if (typeof quoteData === "object") {
      quoteInfo = quoteData;
    }
  }

  if (!quoteInfo) {
    return (
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          py: 1,
          px: 2,
        }}
      >
        <Typography variant="body2" fontWeight="bold">
          {symbol}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          데이터 없음
        </Typography>
      </Box>
    );
  }

  // Quote API에서 일반적으로 사용하는 필드들
  const price =
    quoteInfo?.price || quoteInfo?.close || quoteInfo?.current_price || 0;
  const change = quoteInfo?.change || quoteInfo?.price_change || 0;
  const changePercent =
    quoteInfo?.change_percent || quoteInfo?.percent_change || 0;

  const isPositive = change >= 0;

  return (
    <Box
      sx={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        py: 1,
        px: 2,
        borderBottom: "1px solid",
        borderColor: "divider",
        "&:last-child": {
          borderBottom: "none",
        },
        "&:hover": {
          backgroundColor: "action.hover",
        },
      }}
    >
      <Typography variant="body2" fontWeight="bold" sx={{ minWidth: "60px" }}>
        {symbol}
      </Typography>
      <Typography
        variant="body2"
        fontWeight="medium"
        sx={{ minWidth: "80px", textAlign: "right" }}
      >
        $
        {typeof price === "number"
          ? price.toFixed(2)
          : parseFloat(price || "0").toFixed(2)}
      </Typography>

      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          gap: 0.5,
          minWidth: "100px",
          justifyContent: "flex-end",
        }}
      >
        <Typography
          variant="caption"
          sx={{
            color: isPositive ? "success.main" : "error.main",
            fontWeight: "medium",
          }}
        >
          {isPositive ? "+" : ""}
          {typeof change === "number"
            ? change.toFixed(2)
            : parseFloat(change || "0").toFixed(2)}
        </Typography>
        <Typography
          variant="caption"
          sx={{
            color: isPositive ? "success.main" : "error.main",
            fontWeight: "medium",
          }}
        >
          ({isPositive ? "+" : ""}
          {typeof changePercent === "number"
            ? changePercent.toFixed(2)
            : parseFloat(changePercent || "0").toFixed(2)}
          %)
        </Typography>
      </Box>
    </Box>
  );
};

export default function WatchlistCard({
  watchlist,
  onEdit,
  onDelete,
}: WatchlistCardProps) {
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);

  // 워치리스트 상세 정보 가져오기
  const { data: watchlistDetails } = useWatchlistDetail(watchlist.name);

  // 실제 심볼 리스트 (상세 정보에서 가져오거나 빈 배열)
  const symbols = (watchlistDetails as any)?.symbols || [];

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleEdit = () => {
    handleMenuClose();
    onEdit?.(watchlist);
  };

  const handleDelete = () => {
    handleMenuClose();
    onDelete?.(watchlist.name);
  };

  return (
    <Card
      sx={{
        height: "100%",
        display: "flex",
        flexDirection: "column",
        transition: "all 0.2s ease-in-out",
        "&:hover": {
          transform: "translateY(-2px)",
          boxShadow: (theme) => theme.shadows[4],
        },
      }}
    >
      <CardContent sx={{ flexGrow: 1, pb: 1 }}>
        <Box
          display="flex"
          justifyContent="space-between"
          alignItems="flex-start"
          mb={1}
        >
          <Typography
            variant="h6"
            component="h3"
            noWrap
            sx={{ flexGrow: 1, mr: 1 }}
          >
            {watchlist.name}
          </Typography>
          <IconButton
            size="small"
            onClick={handleMenuClick}
            aria-label="워치리스트 옵션"
          >
            <MoreVertIcon />
          </IconButton>
        </Box>

        {watchlist.description && (
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{
              mb: 2,
              display: "-webkit-box",
              WebkitLineClamp: 2,
              WebkitBoxOrient: "vertical",
              overflow: "hidden",
            }}
          >
            {watchlist.description}
          </Typography>
        )}

        {watchlist.auto_update && (
          <Box mb={2}>
            <Chip
              label="자동 업데이트"
              size="small"
              variant="outlined"
              color="success"
            />
          </Box>
        )}

        {/* 티커 정보 리스트 */}
        {symbols.length > 0 && (
          <Box mb={2}>
            <Typography variant="caption" color="text.secondary" gutterBottom>
              포함 종목 ({symbols.length}개)
            </Typography>
            <Paper
              elevation={1}
              sx={{
                border: "1px solid",
                borderColor: "divider",
                borderRadius: 1,
                mt: 0.5,
                overflow: "hidden",
              }}
            >
              {symbols.slice(0, 6).map((symbol: string) => (
                <TickerListItem key={symbol} symbol={symbol} />
              ))}
              {symbols.length > 6 && (
                <Box
                  sx={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    py: 1.5,
                    backgroundColor: "action.hover",
                    borderTop: "1px solid",
                    borderColor: "divider",
                  }}
                >
                  <Typography variant="body2" color="text.secondary">
                    +{symbols.length - 6}개 더보기
                  </Typography>
                </Box>
              )}
            </Paper>
          </Box>
        )}
      </CardContent>

      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleMenuClose}
        anchorOrigin={{
          vertical: "top",
          horizontal: "right",
        }}
        transformOrigin={{
          vertical: "top",
          horizontal: "right",
        }}
      >
        <MenuItem onClick={handleEdit}>
          <EditIcon fontSize="small" sx={{ mr: 1 }} />
          수정
        </MenuItem>
        <MenuItem onClick={handleDelete} sx={{ color: "error.main" }}>
          <DeleteIcon fontSize="small" sx={{ mr: 1 }} />
          삭제
        </MenuItem>
      </Menu>
    </Card>
  );
}
