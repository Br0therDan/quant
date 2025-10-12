"use client";

import {
  Add as AddIcon,
  ExpandLess as ExpandLessIcon,
  ExpandMore as ExpandMoreIcon,
  List as ListIcon,
} from "@mui/icons-material";
import {
  Box,
  Card,
  CardContent,
  Chip,
  Collapse,
  Divider,
  InputAdornment,
  List,
  ListItem,
  ListItemButton,
  TextField,
  Typography,
  useTheme,
} from "@mui/material";
import React from "react";

import { useStockQuote } from "@/hooks/useStocks";
import { useWatchlist, useWatchlistDetail } from "@/hooks/useWatchList";

interface WatchlistBarProps {
  selectedSymbol: string;
  onSymbolChange: (symbol: string) => void;
}

// 심볼 아이템 컴포넌트 (실시간 데이터 표시)
function SymbolItem({
  symbol,
  selectedSymbol,
  onSymbolChange,
  theme,
}: {
  symbol: string;
  selectedSymbol: string;
  onSymbolChange: (symbol: string) => void;
  theme: any;
}) {
  const { data: quote } = useStockQuote(symbol);

  const formatNumber = (num: number, decimals = 2) => {
    return new Intl.NumberFormat("ko-KR", {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(num);
  };

  // 타입 안전성을 위한 타입 가드
  const price =
    typeof quote === "object" && quote && "price" in quote
      ? Number(quote.price) || 0
      : 0;
  const change =
    typeof quote === "object" && quote && "change" in quote
      ? Number(quote.change) || 0
      : 0;
  const changePercent =
    typeof quote === "object" && quote && "change_percent" in quote
      ? Number(quote.change_percent) || 0
      : 0;

  const isPositive = change >= 0;
  const changeColor = isPositive
    ? theme.palette.success.main
    : theme.palette.error.main;

  return (
    <ListItem disablePadding>
      <ListItemButton
        selected={selectedSymbol === symbol}
        onClick={() => onSymbolChange(symbol)}
        sx={{
          py: 1,
          px: 2,
          "&.Mui-selected": {
            backgroundColor: theme.palette.primary.main + "20",
          },
        }}
      >
        <Box display="flex" alignItems="center" width="100%" gap={0.5}>
          {/* 심볼 */}
          <Typography
            variant="body2"
            fontWeight="medium"
            sx={{ width: 45, flex: "0 0 45px" }}
          >
            {symbol}
          </Typography>

          {/* 가격 */}
          <Typography
            variant="body2"
            fontWeight="medium"
            sx={{ width: 55, flex: "0 0 55px", textAlign: "right" }}
          >
            {price ? formatNumber(price) : "--"}
          </Typography>

          {/* 변동 금액 */}
          <Typography
            variant="body2"
            sx={{
              color: changeColor,
              width: 50,
              flex: "0 0 50px",
              textAlign: "right",
            }}
          >
            {isPositive ? "+" : ""}
            {formatNumber(change, 2)}
          </Typography>

          {/* 변동률 */}
          <Typography
            variant="body2"
            sx={{
              color: changeColor,
              width: 50,
              flex: "0 0 50px",
              textAlign: "right",
            }}
          >
            {isPositive ? "+" : ""}
            {formatNumber(changePercent, 2)}%
          </Typography>
        </Box>
      </ListItemButton>
    </ListItem>
  );
}

// 워치리스트별 심볼 목록 컴포넌트
function WatchlistSymbols({
  watchlistId,
  selectedSymbol,
  onSymbolChange,
  searchTerm,
  theme,
}: {
  watchlistId: string;
  selectedSymbol: string;
  onSymbolChange: (symbol: string) => void;
  searchTerm: string;
  theme: any;
}) {
  const { data: watchlistDetail } = useWatchlistDetail(watchlistId);

  const symbols = watchlistDetail?.symbols || [];

  // 검색어로 필터링
  const filteredSymbols = symbols.filter((symbol: string) =>
    symbol.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (filteredSymbols.length === 0) {
    return (
      <Box sx={{ p: 2, textAlign: "center" }}>
        <Typography variant="caption" color="text.secondary">
          {searchTerm ? "검색 결과가 없습니다" : "심볼이 없습니다"}
        </Typography>
      </Box>
    );
  }

  return (
    <List dense sx={{ pl: 2 }}>
      {filteredSymbols.map((symbol: string) => (
        <SymbolItem
          key={symbol}
          symbol={symbol}
          selectedSymbol={selectedSymbol}
          onSymbolChange={onSymbolChange}
          theme={theme}
        />
      ))}
    </List>
  );
}

export default function WatchlistBar({
  selectedSymbol,
  onSymbolChange,
}: WatchlistBarProps) {
  const theme = useTheme();
  const [searchTerm, setSearchTerm] = React.useState("");
  const [expandedWatchlists, setExpandedWatchlists] = React.useState<
    Set<string>
  >(new Set());

  // 워치리스트 데이터 가져오기
  const {
    watchlistList,
    isLoading: { watchlistList: watchlistsLoading },
  } = useWatchlist();

  // API 응답 구조: { user_id, watchlists: [...] }
  const watchlists = React.useMemo(() => {
    if (!watchlistList) return [];

    // watchlistList가 배열이면 그대로 사용
    if (Array.isArray(watchlistList)) {
      return watchlistList;
    }

    // watchlistList가 객체이고 watchlists 속성이 있으면 사용
    if (typeof watchlistList === "object" && "watchlists" in watchlistList) {
      return Array.isArray((watchlistList as any).watchlists)
        ? (watchlistList as any).watchlists
        : [];
    }

    return [];
  }, [watchlistList]);

  // 첫 번째 워치리스트를 기본으로 확장
  React.useEffect(() => {
    if (watchlists.length > 0 && expandedWatchlists.size === 0) {
      const firstWatchlistId = watchlists[0]?.id || watchlists[0]?.name;
      if (firstWatchlistId) {
        setExpandedWatchlists(new Set([firstWatchlistId]));
      }
    }
  }, [watchlists, expandedWatchlists.size]);

  const toggleWatchlistExpansion = (watchlistId: string) => {
    setExpandedWatchlists((prev) => {
      const newExpanded = new Set(prev);
      if (newExpanded.has(watchlistId)) {
        newExpanded.delete(watchlistId);
      } else {
        newExpanded.add(watchlistId);
      }
      return newExpanded;
    });
  };

  return (
    <Card sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <CardContent
        sx={{ flexGrow: 1, display: "flex", flexDirection: "column" }}
      >
        <Box display="flex" alignItems="center" gap={1} mb={2}>
          <ListIcon sx={{ color: theme.palette.primary.main }} />
          <Typography variant="h6" component="h2">
            워치리스트
          </Typography>
        </Box>

        <TextField
          fullWidth
          size="small"
          placeholder="종목 검색..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <AddIcon sx={{ fontSize: 20 }} />
              </InputAdornment>
            ),
          }}
          sx={{ mb: 2 }}
        />

        <Box flexGrow={1} sx={{ overflowY: "auto" }}>
          {watchlistsLoading ? (
            <Box sx={{ p: 2, textAlign: "center" }}>
              <Typography variant="caption" color="text.secondary">
                로딩 중...
              </Typography>
            </Box>
          ) : watchlists.length === 0 ? (
            <Box sx={{ p: 2, textAlign: "center" }}>
              <Typography variant="caption" color="text.secondary">
                워치리스트가 없습니다
              </Typography>
            </Box>
          ) : (
            watchlists.map((watchlist: any, index: number) => {
              const watchlistId = watchlist.id || watchlist.name;
              const isExpanded = expandedWatchlists.has(watchlistId);

              return (
                <Box key={watchlistId} sx={{ mb: 1 }}>
                  <Box
                    display="flex"
                    alignItems="center"
                    justifyContent="space-between"
                    sx={{
                      cursor: "pointer",
                      p: 1,
                      borderRadius: 1,
                      "&:hover": {
                        backgroundColor: theme.palette.action.hover,
                      },
                    }}
                    onClick={() => toggleWatchlistExpansion(watchlistId)}
                  >
                    <Typography variant="subtitle2" fontWeight="medium">
                      {watchlist.name || `워치리스트 ${index + 1}`}
                    </Typography>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Chip
                        label={watchlist.symbols?.length || 0}
                        size="small"
                        variant="outlined"
                      />
                      {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                    </Box>
                  </Box>

                  <Collapse in={isExpanded}>
                    <WatchlistSymbols
                      watchlistId={watchlistId}
                      selectedSymbol={selectedSymbol}
                      onSymbolChange={onSymbolChange}
                      searchTerm={searchTerm}
                      theme={theme}
                    />
                  </Collapse>

                  {index !== watchlists.length - 1 && (
                    <Divider sx={{ my: 1 }} />
                  )}
                </Box>
              );
            })
          )}
        </Box>
      </CardContent>
    </Card>
  );
}
