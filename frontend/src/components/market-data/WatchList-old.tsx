"use client";

import {
  Add as AddIcon,
  StarBorder as StarBorderIcon,
  Star as StarIcon,
  TrendingDown as TrendingDownIcon,
  TrendingUp as TrendingUpIcon,
  ExpandLess as ExpandLessIcon,
  ExpandMore as ExpandMoreIcon,
  List as ListIcon,
} from "@mui/icons-material";
import {
  Box,
  Card,
  CardContent,
  Divider,
  IconButton,
  InputAdornment,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  TextField,
  Typography,
  useTheme,
  Collapse,
  Chip,
} from "@mui/material";
import React from "react";

import { useWatchlist, useWatchlistDetail } from "@/hooks/useWatchList";
import { useStockQuote } from "@/hooks/useStocks";

interface WatchListItem {
  symbol: string;
  price?: number;
  change?: number;
  changePercent?: number;
  isFavorite?: boolean;
  volume?: number;
}

interface WatchListProps {
  selectedSymbol: string;
  onSymbolChange: (symbol: string) => void;
}

// WatchListItem 컴포넌트를 별도로 분리
function WatchListItemComponent({
  item,
  selectedSymbol,
  onSymbolChange,
  favorites,
  toggleFavorite,
  theme,
}: {
  item: WatchListItem;
  selectedSymbol: string;
  onSymbolChange: (symbol: string) => void;
  favorites: Set<string>;
  toggleFavorite: (symbol: string) => void;
  theme: any;
}) {
  const formatNumber = (num: number, decimals = 2) => {
    return new Intl.NumberFormat("ko-KR", {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(num);
  };

  const isPositive = item.change ? item.change >= 0 : true;
  const changeColor = isPositive
    ? theme.palette.success.main
    : theme.palette.error.main;

  return (
    <ListItem disablePadding>
      <ListItemButton
        selected={selectedSymbol === item.symbol}
        onClick={() => onSymbolChange(item.symbol)}
        sx={{
          py: 1,
          "&.Mui-selected": {
            backgroundColor: theme.palette.primary.main + "20",
          },
        }}
      >
        <Box display="flex" alignItems="center" width="100%" gap={1}>
          <IconButton
            size="small"
            onClick={(e) => {
              e.stopPropagation();
              toggleFavorite(item.symbol);
            }}
          >
            {favorites.has(item.symbol) ? (
              <StarIcon
                sx={{ color: theme.palette.warning.main, fontSize: 16 }}
              />
            ) : (
              <StarBorderIcon sx={{ fontSize: 16 }} />
            )}
          </IconButton>

          <Box flexGrow={1}>
            <Box
              display="flex"
              justifyContent="space-between"
              alignItems="center"
            >
              <Typography variant="body2" fontWeight="medium">
                {item.symbol}
              </Typography>
              <Typography variant="body2" fontWeight="medium">
                {item.price ? formatNumber(item.price) : "--"}
              </Typography>
            </Box>
            <Box
              display="flex"
              justifyContent="space-between"
              alignItems="center"
            >
              <Typography variant="caption" color="text.secondary">
                {item.symbol}
              </Typography>
              {item.changePercent !== undefined ? (
                <Box display="flex" alignItems="center" gap={0.5}>
                  {isPositive ? (
                    <TrendingUpIcon sx={{ fontSize: 12, color: changeColor }} />
                  ) : (
                    <TrendingDownIcon
                      sx={{ fontSize: 12, color: changeColor }}
                    />
                  )}
                  <Typography variant="caption" sx={{ color: changeColor }}>
                    {isPositive ? "+" : ""}
                    {formatNumber(item.changePercent)}%
                  </Typography>
                </Box>
              ) : (
                <Typography variant="caption" color="text.secondary">
                  --%
                </Typography>
              )}
            </Box>
          </Box>
        </Box>
      </ListItemButton>
    </ListItem>
  );
}

export default function WatchList({
  selectedSymbol,
  onSymbolChange,
}: WatchListProps) {
  const theme = useTheme();
  const [searchTerm, setSearchTerm] = React.useState("");
  const [favorites, setFavorites] = React.useState<Set<string>>(new Set());

  // 새로운 훅들 사용
  const {
    watchlistList,
    isLoading: { watchlistList: watchlistsLoading },
  } = useWatchlist();
  const { data: defaultWatchlist } = useWatchlistDetail("default");

  // 워치리스트에서 사용 가능한 심볼들 가져오기
  const availableSymbols = React.useMemo(() => {
    // 우선순위: defaultWatchlist > watchlistList 첫번째 아이템
    const targetWatchlist =
      defaultWatchlist ||
      (Array.isArray(watchlistList) && watchlistList.length > 0
        ? watchlistList[0]
        : null);

    if (
      targetWatchlist &&
      (targetWatchlist as any)?.symbols &&
      Array.isArray((targetWatchlist as any).symbols)
    ) {
      return (targetWatchlist as any).symbols;
    }

    // 기본 인기 심볼 리스트 (워치리스트가 없는 경우)
    return ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "NVDA", "META", "NFLX"];
  }, [defaultWatchlist, watchlistList]);

  const symbolsLoading = watchlistsLoading;

  // 워치리스트에서 즐겨찾기 심볼 설정
  React.useEffect(() => {
    // 우선순위: defaultWatchlist > watchlistList 첫번째 아이템
    const targetWatchlist =
      defaultWatchlist ||
      (Array.isArray(watchlistList) && watchlistList.length > 0
        ? watchlistList[0]
        : null);

    if (
      targetWatchlist &&
      (targetWatchlist as any)?.symbols &&
      Array.isArray((targetWatchlist as any).symbols)
    ) {
      setFavorites(new Set((targetWatchlist as any).symbols));
    }
  }, [watchlistList, defaultWatchlist]);

  const toggleFavorite = (symbol: string) => {
    setFavorites((prev) => {
      const newFavorites = new Set(prev);
      if (newFavorites.has(symbol)) {
        newFavorites.delete(symbol);
      } else {
        newFavorites.add(symbol);
      }
      return newFavorites;
    });
  };

  // 사용 가능한 심볼을 WatchListItem 형태로 변환
  const watchListItems: WatchListItem[] = React.useMemo(() => {
    if (!Array.isArray(availableSymbols)) return [];

    return availableSymbols.map((symbol: string) => ({
      symbol,
      price: undefined, // 실제 가격 데이터는 별도 API 호출 필요
      change: undefined,
      changePercent: undefined,
      isFavorite: favorites.has(symbol),
      volume: undefined,
    }));
  }, [availableSymbols, favorites]);

  const filteredItems = watchListItems.filter((item) =>
    item.symbol.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const favoriteItems = filteredItems.filter((item) =>
    favorites.has(item.symbol)
  );
  const otherItems = filteredItems.filter(
    (item) => !favorites.has(item.symbol)
  );

  const isLoading = symbolsLoading || watchlistsLoading;

  return (
    <Card sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <CardContent sx={{ flexGrow: 1, p: 2, "&:last-child": { pb: 2 } }}>
        <Typography variant="h6" gutterBottom>
          워치리스트
        </Typography>

        {/* 검색 필드 */}
        <TextField
          fullWidth
          size="small"
          placeholder="심볼 검색..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <AddIcon sx={{ fontSize: 18 }} />
              </InputAdornment>
            ),
          }}
          sx={{ mb: 2 }}
        />

        <List
          sx={{
            flexGrow: 1,
            overflow: "auto",
            maxHeight: "calc(100vh - 300px)",
          }}
        >
          {isLoading ? (
            <ListItem>
              <ListItemText
                primary="로딩 중..."
                primaryTypographyProps={{
                  variant: "body2",
                  color: "text.secondary",
                  textAlign: "center",
                }}
              />
            </ListItem>
          ) : (
            <>
              {/* 즐겨찾기 섹션 */}
              {favoriteItems.length > 0 && (
                <>
                  <ListItem>
                    <Typography
                      variant="caption"
                      color="text.secondary"
                      fontWeight="medium"
                    >
                      즐겨찾기
                    </Typography>
                  </ListItem>
                  {favoriteItems.map((item) => (
                    <WatchListItemComponent
                      key={item.symbol}
                      item={item}
                      selectedSymbol={selectedSymbol}
                      onSymbolChange={onSymbolChange}
                      favorites={favorites}
                      toggleFavorite={toggleFavorite}
                      theme={theme}
                    />
                  ))}
                  {otherItems.length > 0 && <Divider sx={{ my: 1 }} />}
                </>
              )}

              {/* 기타 종목 섹션 */}
              {otherItems.length > 0 && (
                <>
                  {favoriteItems.length > 0 && (
                    <ListItem>
                      <Typography
                        variant="caption"
                        color="text.secondary"
                        fontWeight="medium"
                      >
                        전체
                      </Typography>
                    </ListItem>
                  )}
                  {otherItems.map((item) => (
                    <WatchListItemComponent
                      key={item.symbol}
                      item={item}
                      selectedSymbol={selectedSymbol}
                      onSymbolChange={onSymbolChange}
                      favorites={favorites}
                      toggleFavorite={toggleFavorite}
                      theme={theme}
                    />
                  ))}
                </>
              )}

              {filteredItems.length === 0 && (
                <ListItem>
                  <ListItemText
                    primary="검색 결과가 없습니다"
                    primaryTypographyProps={{
                      variant: "body2",
                      color: "text.secondary",
                      textAlign: "center",
                    }}
                  />
                </ListItem>
              )}
            </>
          )}
        </List>
      </CardContent>
    </Card>
  );
}
