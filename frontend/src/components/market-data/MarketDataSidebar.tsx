"use client";

import {
  Add as AddIcon,
  Edit as EditIcon,
  ExpandLess as ExpandLessIcon,
  ExpandMore as ExpandMoreIcon,
  TrendingDown as TrendingDownIcon,
  TrendingUp as TrendingUpIcon,
} from "@mui/icons-material";
import {
  Box,
  Button,
  Chip,
  Collapse,
  Divider,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  Stack,
  Typography,
  useTheme,
} from "@mui/material";
import { useRouter } from "next/navigation";
import React from "react";

import { useFundamentalCompanyOverview } from "@/hooks/useFundamental";
import { useStockQuote } from "@/hooks/useStocks";
import { useWatchlist, useWatchlistDetail } from "@/hooks/useWatchList";

import WatchlistEditDialog from "./WatchlistEditDialog";

interface MarketDataSidebarProps {
  currentSymbol: string;
  width?: number;
  onWidthChange?: (width: number) => void;
}

// 워치리스트 심볼 아이템
function WatchlistSymbolItem({
  symbol,
  isSelected,
  onClick,
}: {
  symbol: string;
  isSelected: boolean;
  onClick: () => void;
}) {
  const theme = useTheme();
  const { data: quote } = useStockQuote(symbol);

  const price = quote?.price ? Number(quote.price) : 0;
  const change = quote?.change ? Number(quote.change) : 0;
  const changePercent = quote?.change_percent
    ? Number(quote.change_percent)
    : 0;

  const isPositive = change >= 0;
  const changeColor = isPositive
    ? theme.palette.success.main
    : theme.palette.error.main;

  return (
    <ListItem disablePadding>
      <ListItemButton
        selected={isSelected}
        onClick={onClick}
        sx={{
          py: 1,
          px: 2,
          // borderLeft: `3px solid ${theme.palette.primary.main}`,
        }}
      >
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            width: "100%",
            gap: 1.5,
          }}
        >
          {/* 티커 */}
          <Typography
            variant="body2"
            fontWeight="600"
            sx={{
              minWidth: "60px",
            }}
          >
            {symbol}
          </Typography>

          {/* 현재가 */}
          <Typography
            variant="body2"
            fontWeight="500"
            sx={{
              minWidth: "70px",
              textAlign: "right",
              color: theme.palette.text.primary,
            }}
          >
            {price.toFixed(2)}
          </Typography>

          {/* 변동 */}
          <Typography
            variant="body2"
            sx={{
              minWidth: "50px",
              textAlign: "right",
              color: changeColor,
              fontWeight: 500,
            }}
          >
            {isPositive ? "+" : ""}
            {change.toFixed(2)}
          </Typography>

          {/* 변동률 */}
          <Typography
            variant="body2"
            sx={{
              minWidth: "60px",
              textAlign: "right",
              color: changeColor,
              fontWeight: 600,
            }}
          >
            {isPositive ? "+" : ""}
            {changePercent.toFixed(2)}%
          </Typography>
        </Box>
      </ListItemButton>
    </ListItem>
  );
}

// 워치리스트 그룹
function WatchlistGroup({
  watchlist,
  currentSymbol,
  onSymbolClick,
  onEdit,
}: {
  watchlist: any;
  currentSymbol: string;
  onSymbolClick: (symbol: string) => void;
  onEdit: (watchlist: any) => void;
}) {
  const theme = useTheme();
  const [expanded, setExpanded] = React.useState(true);
  const { data: watchlistDetail } = useWatchlistDetail(
    watchlist.name || watchlist.id
  );

  const symbols = watchlistDetail?.symbols || watchlist.symbols || [];

  return (
    <Box sx={{ mb: 1 }}>
      <Box
        display="flex"
        alignItems="center"
        justifyContent="space-between"
        sx={{
          px: 2,
          py: 1,
          cursor: "pointer",
          "&:hover": {
            backgroundColor: theme.palette.action.hover,
          },
        }}
        onClick={() => setExpanded(!expanded)}
      >
        <Box display="flex" alignItems="center" gap={1}>
          <Typography variant="subtitle2" fontWeight="600">
            {watchlist.name}
          </Typography>
          <Chip label={symbols.length} size="small" />
        </Box>
        <Box display="flex" alignItems="center">
          <IconButton
            size="small"
            onClick={(e) => {
              e.stopPropagation();
              onEdit(watchlist);
            }}
          >
            <EditIcon fontSize="small" />
          </IconButton>
          {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
        </Box>
      </Box>
      <Collapse in={expanded}>
        <List dense disablePadding>
          {symbols.map((symbol: string) => (
            <WatchlistSymbolItem
              key={symbol}
              symbol={symbol}
              isSelected={currentSymbol === symbol}
              onClick={() => onSymbolClick(symbol)}
            />
          ))}
        </List>
      </Collapse>
    </Box>
  );
}

// 심볼 개요 섹션
function SymbolOverview({ symbol }: { symbol: string }) {
  const theme = useTheme();
  const { data: quote } = useStockQuote(symbol);
  const { data: overview } = useFundamentalCompanyOverview(symbol);

  const price = quote?.price ? Number(quote.price) : 0;
  const change = quote?.change ? Number(quote.change) : 0;
  const changePercent = quote?.change_percent
    ? Number(quote.change_percent)
    : 0;
  const volume = quote?.volume ? Number(quote.volume) : 0;

  const isPositive = change >= 0;
  const changeColor = isPositive
    ? theme.palette.success.main
    : theme.palette.error.main;

  const formatNumber = (num: number) => {
    if (num >= 1e12) return `${(num / 1e12).toFixed(2)}T`;
    if (num >= 1e9) return `${(num / 1e9).toFixed(2)}B`;
    if (num >= 1e6) return `${(num / 1e6).toFixed(2)}M`;
    if (num >= 1e3) return `${(num / 1e3).toFixed(2)}K`;
    return num.toFixed(2);
  };

  const companyData = overview?.data;

  return (
    <Box>
      <Box sx={{ px: 2, pb: 2 }}>
        {/* 회사 정보 */}
        <Box sx={{ mb: 2 }}>
          <Typography variant="h6" fontWeight="bold">
            {symbol}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {companyData?.name || "Loading..."}
          </Typography>
        </Box>

        {/* 가격 정보 */}
        <Box sx={{ mb: 2 }}>
          <Typography variant="h4" fontWeight="bold">
            ${price.toFixed(2)}
          </Typography>
          <Box display="flex" alignItems="center" gap={1}>
            {isPositive ? (
              <TrendingUpIcon sx={{ fontSize: 20, color: changeColor }} />
            ) : (
              <TrendingDownIcon sx={{ fontSize: 20, color: changeColor }} />
            )}
            <Typography variant="body2" sx={{ color: changeColor }}>
              {isPositive ? "+" : ""}
              {change.toFixed(2)} ({isPositive ? "+" : ""}
              {changePercent.toFixed(2)}%)
            </Typography>
          </Box>
        </Box>

        <Divider sx={{ my: 2 }} />

        {/* 주요 지표 */}
        <Stack spacing={1.5}>
          <Box display="flex" justifyContent="space-between">
            <Typography variant="caption" color="text.secondary">
              시가총액
            </Typography>
            <Typography variant="caption" fontWeight="medium">
              {companyData?.market_capitalization
                ? `$${formatNumber(Number(companyData.market_capitalization))}`
                : "--"}
            </Typography>
          </Box>

          <Box display="flex" justifyContent="space-between">
            <Typography variant="caption" color="text.secondary">
              거래량
            </Typography>
            <Typography variant="caption" fontWeight="medium">
              {formatNumber(volume)}
            </Typography>
          </Box>

          <Box display="flex" justifyContent="space-between">
            <Typography variant="caption" color="text.secondary">
              P/E Ratio
            </Typography>
            <Typography variant="caption" fontWeight="medium">
              {companyData?.pe_ratio || "--"}
            </Typography>
          </Box>

          <Box display="flex" justifyContent="space-between">
            <Typography variant="caption" color="text.secondary">
              52주 최고
            </Typography>
            <Typography variant="caption" fontWeight="medium">
              {companyData?.fifty_two_week_high
                ? `$${Number(companyData.fifty_two_week_high).toFixed(2)}`
                : "--"}
            </Typography>
          </Box>

          <Box display="flex" justifyContent="space-between">
            <Typography variant="caption" color="text.secondary">
              52주 최저
            </Typography>
            <Typography variant="caption" fontWeight="medium">
              {companyData?.fifty_two_week_low
                ? `$${Number(companyData.fifty_two_week_low).toFixed(2)}`
                : "--"}
            </Typography>
          </Box>

          <Box display="flex" justifyContent="space-between">
            <Typography variant="caption" color="text.secondary">
              배당수익률
            </Typography>
            <Typography variant="caption" fontWeight="medium">
              {companyData?.dividend_yield
                ? `${(Number(companyData.dividend_yield) * 100).toFixed(2)}%`
                : "--"}
            </Typography>
          </Box>

          <Box display="flex" justifyContent="space-between">
            <Typography variant="caption" color="text.secondary">
              EPS
            </Typography>
            <Typography variant="caption" fontWeight="medium">
              {companyData?.eps || "--"}
            </Typography>
          </Box>
        </Stack>

        {companyData?.description && (
          <>
            <Divider sx={{ my: 2 }} />
            <Box>
              <Typography
                variant="caption"
                color="text.secondary"
                sx={{ mb: 1, display: "block" }}
              >
                회사 설명
              </Typography>
              <Typography
                variant="caption"
                sx={{
                  display: "-webkit-box",
                  WebkitLineClamp: 4,
                  WebkitBoxOrient: "vertical",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  lineHeight: 1.5,
                }}
              >
                {companyData.description}
              </Typography>
            </Box>
          </>
        )}
      </Box>
    </Box>
  );
}

export default function MarketDataSidebar({
  currentSymbol,
  width = 320,
  onWidthChange,
}: MarketDataSidebarProps) {
  const theme = useTheme();
  const router = useRouter();
  const [editDialogOpen, setEditDialogOpen] = React.useState(false);
  const [selectedWatchlist, setSelectedWatchlist] = React.useState<any>(null);
  const [isResizing, setIsResizing] = React.useState(false);

  const {
    watchlistList,
    isLoading: { watchlistList: watchlistsLoading },
  } = useWatchlist();

  // API 응답 파싱
  const watchlists = React.useMemo(() => {
    if (!watchlistList) return [];
    if (Array.isArray(watchlistList)) return watchlistList;
    if (typeof watchlistList === "object" && "watchlists" in watchlistList) {
      return Array.isArray((watchlistList as any).watchlists)
        ? (watchlistList as any).watchlists
        : [];
    }
    return [];
  }, [watchlistList]);

  const handleSymbolClick = (symbol: string) => {
    router.push(`/market-data/stock/${symbol}`);
  };

  const handleEditWatchlist = (watchlist: any) => {
    setSelectedWatchlist(watchlist);
    setEditDialogOpen(true);
  };

  const handleCreateWatchlist = () => {
    setSelectedWatchlist(null);
    setEditDialogOpen(true);
  };

  // 리사이저 핸들러
  const handleMouseDown = React.useCallback(() => {
    setIsResizing(true);
  }, []);

  React.useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing) return;

      // 화면 오른쪽에서부터의 거리 계산
      const newWidth = window.innerWidth - e.clientX;

      // 최소/최대 폭 제한
      const minWidth = 250;
      const maxWidth = 600;
      const clampedWidth = Math.min(Math.max(newWidth, minWidth), maxWidth);

      if (onWidthChange) {
        onWidthChange(clampedWidth);
      }
    };

    const handleMouseUp = () => {
      setIsResizing(false);
    };

    if (isResizing) {
      document.addEventListener("mousemove", handleMouseMove);
      document.addEventListener("mouseup", handleMouseUp);
      document.body.style.cursor = "col-resize";
      document.body.style.userSelect = "none";
    }

    return () => {
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
    };
  }, [isResizing, onWidthChange]);

  return (
    <>
      <Box
        sx={{
          position: "relative",
          height: "100%",
          width: width,
          display: "flex",
          flexDirection: "column",
          borderLeft: 1,
          borderColor: "divider",
          overflow: "hidden",
        }}
      >
        {/* 리사이저 핸들 */}
        <Box
          onMouseDown={handleMouseDown}
          sx={{
            position: "absolute",
            left: 0,
            top: 0,
            bottom: 0,
            width: "4px",
            cursor: "col-resize",
            zIndex: 1000,
            backgroundColor: isResizing
              ? theme.palette.primary.main
              : "transparent",
            transition: "background-color 0.2s",
            "&:hover": {
              backgroundColor: theme.palette.primary.light,
            },
          }}
        />
        {/* 워치리스트 섹션 */}
        <Box sx={{ overflow: "auto", flexShrink: 0 }}>
          <Box
            display="flex"
            alignItems="center"
            justifyContent="start"
            sx={{ px: 2, py: 1.5 }}
          >
            <Typography variant="subtitle2" fontWeight="600">
              워치리스트
            </Typography>
            <IconButton size="small" onClick={handleCreateWatchlist}>
              <AddIcon fontSize="small" />
            </IconButton>
          </Box>

          {watchlistsLoading ? (
            <Box sx={{ p: 2, textAlign: "center" }}>
              <Typography variant="caption" color="text.secondary">
                로딩 중...
              </Typography>
            </Box>
          ) : watchlists.length === 0 ? (
            <Box sx={{ p: 2, textAlign: "center" }}>
              <Typography
                variant="caption"
                color="text.secondary"
                sx={{ mb: 1, display: "block" }}
              >
                워치리스트가 없습니다
              </Typography>
              <Button
                size="small"
                variant="outlined"
                startIcon={<AddIcon />}
                onClick={handleCreateWatchlist}
              >
                워치리스트 생성
              </Button>
            </Box>
          ) : (
            watchlists.map((watchlist: any) => (
              <WatchlistGroup
                key={watchlist.id || watchlist.name}
                watchlist={watchlist}
                currentSymbol={currentSymbol}
                onSymbolClick={handleSymbolClick}
                onEdit={handleEditWatchlist}
              />
            ))
          )}
        </Box>

        <Divider />

        {/* 심볼 개요 */}
        <Box sx={{ pt: 2, overflow: "auto", flexShrink: 0 }}>
          <SymbolOverview symbol={currentSymbol} />
        </Box>
      </Box>

      {/* 워치리스트 편집 다이얼로그 */}
      <WatchlistEditDialog
        open={editDialogOpen}
        onClose={() => {
          setEditDialogOpen(false);
          setSelectedWatchlist(null);
        }}
        watchlist={selectedWatchlist}
      />
    </>
  );
}
