"use client";

import {
  Add as AddIcon,
  StarBorder as StarBorderIcon,
  Star as StarIcon,
  TrendingDown as TrendingDownIcon,
  TrendingUp as TrendingUpIcon,
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
} from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import React from "react";

import {
  marketDataGetAvailableSymbolsOptions,
  pipelineListWatchlistsOptions,
} from "@/client/@tanstack/react-query.gen";

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
                    <TrendingDownIcon sx={{ fontSize: 12, color: changeColor }} />
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

  // 사용 가능한 심볼 목록 조회
  const { data: availableSymbols, isLoading: symbolsLoading } = useQuery(
    marketDataGetAvailableSymbolsOptions()
  );

  // 워치리스트 목록 조회
  const { data: watchlists, isLoading: watchlistsLoading } = useQuery(
    pipelineListWatchlistsOptions()
  );

  // 첫 번째 워치리스트의 심볼들을 즐겨찾기로 설정
  React.useEffect(() => {
    if (watchlists && Array.isArray(watchlists) && watchlists.length > 0) {
      const firstWatchlist = watchlists[0] as any;
      if (firstWatchlist.symbols && Array.isArray(firstWatchlist.symbols)) {
        setFavorites(new Set(firstWatchlist.symbols));
      }
    }
  }, [watchlists]);

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
    if (!availableSymbols || !Array.isArray(availableSymbols)) return [];

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
