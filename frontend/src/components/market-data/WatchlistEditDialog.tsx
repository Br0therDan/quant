"use client";

import { Close as CloseIcon, Search as SearchIcon } from "@mui/icons-material";
import {
  Autocomplete,
  Box,
  Button,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import React from "react";

import { useStockSearchSymbols } from "@/hooks/useStocks";
import { useWatchlist } from "@/hooks/useWatchList";

interface SymbolOption {
  symbol: string;
  name: string;
  currency: string;
  matchScore: string;
}

interface WatchlistEditDialogProps {
  open: boolean;
  onClose: () => void;
  watchlist?: any; // null이면 새로 생성, 있으면 편집
}

export default function WatchlistEditDialog({
  open,
  onClose,
  watchlist,
}: WatchlistEditDialogProps) {
  const isEdit = !!watchlist;

  const [name, setName] = React.useState("");
  const [description, setDescription] = React.useState("");
  const [symbols, setSymbols] = React.useState<string[]>([]);
  const [searchQuery, setSearchQuery] = React.useState("");
  const [debouncedSearchQuery, setDebouncedSearchQuery] = React.useState("");

  const { createOrUpdateWatchlist, updateWatchlist } = useWatchlist();

  // 디바운싱: 500ms 지연 후 검색
  React.useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchQuery(searchQuery);
    }, 500);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  // 심볼 검색 (디바운싱된 검색어 사용)
  const { data: searchResults, isLoading: searchLoading } =
    useStockSearchSymbols(debouncedSearchQuery);

  // 검색 결과에서 심볼 정보 추출
  const symbolDetails = React.useMemo(() => {
    if (!searchResults) return new Map<string, SymbolOption>();

    const detailsMap = new Map<string, SymbolOption>();

    const processItem = (item: any) => {
      const symbol = item?.symbol || "";
      if (!symbol) return;

      detailsMap.set(symbol, {
        symbol,
        name: item?.name || symbol,
        currency: item?.currency || "USD",
        matchScore:
          item?.match_score?.toString() ||
          item?.matchScore?.toString() ||
          "1.0000",
      });
    };

    // API 응답이 { symbols: [...], count: number } 형태일 수 있음
    if (searchResults && typeof searchResults === "object") {
      const searchObj = searchResults as any;
      const symbolsArray = searchObj.symbols || searchObj.data || [];

      if (Array.isArray(symbolsArray)) {
        symbolsArray.slice(0, 20).forEach(processItem);
      }
    } else if (Array.isArray(searchResults)) {
      (searchResults as any[]).slice(0, 20).forEach(processItem);
    }

    return detailsMap;
  }, [searchResults]);

  // 검색 결과에서 심볼 배열 추출
  const availableSymbols = React.useMemo(() => {
    return Array.from(symbolDetails.keys());
  }, [symbolDetails]);

  // 최종 옵션 리스트 - 검색어가 최소 2글자 이상일 때만 표시
  const symbolOptions = React.useMemo(() => {
    if (debouncedSearchQuery && debouncedSearchQuery.trim().length >= 2) {
      return availableSymbols;
    }
    return [];
  }, [debouncedSearchQuery, availableSymbols]);

  // 워치리스트 데이터로 폼 초기화
  React.useEffect(() => {
    if (open && watchlist) {
      setName(watchlist.name || "");
      setDescription(watchlist.description || "");
      setSymbols(watchlist.symbols || []);
    } else if (open && !watchlist) {
      // 새로 생성하는 경우 초기화
      setName("");
      setDescription("");
      setSymbols([]);
    }
    // 검색어 초기화
    setSearchQuery("");
    setDebouncedSearchQuery("");
  }, [open, watchlist]);

  const handleSymbolChange = (_: any, newValue: string[]) => {
    setSymbols(newValue);
  };

  const handleSubmit = () => {
    const data = {
      name,
      description,
      symbols,
    };

    if (isEdit) {
      updateWatchlist({
        name: watchlist.name,
        updateData: data,
      });
    } else {
      createOrUpdateWatchlist(data);
    }

    onClose();
  };

  const handleClose = () => {
    setName("");
    setDescription("");
    setSymbols([]);
    setSearchQuery("");
    setDebouncedSearchQuery("");
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Typography variant="h6">
            {isEdit ? "워치리스트 편집" : "새 워치리스트"}
          </Typography>
          <IconButton size="small" onClick={handleClose}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent dividers>
        <Stack spacing={3}>
          {/* 이름 */}
          <TextField
            label="워치리스트 이름"
            value={name}
            onChange={(e) => setName(e.target.value)}
            fullWidth
            required
            placeholder="예: 기술주 포트폴리오"
          />

          {/* 설명 */}
          <TextField
            label="설명 (선택사항)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            fullWidth
            multiline
            rows={2}
            placeholder="이 워치리스트에 대한 간단한 설명을 입력하세요"
          />

          {/* 심볼 검색 및 추가 */}
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              종목 선택 *
            </Typography>
            <Autocomplete
              multiple
              fullWidth
              options={symbolOptions}
              value={symbols}
              onChange={handleSymbolChange}
              inputValue={searchQuery}
              onInputChange={(_, newInputValue) => {
                setSearchQuery(newInputValue);
              }}
              filterOptions={(options) => options}
              filterSelectedOptions
              loading={searchLoading && debouncedSearchQuery.length > 1}
              freeSolo={false}
              renderOption={(props, option) => {
                const details = symbolDetails.get(option);
                const { key, ...otherProps } = props;

                if (!details) {
                  return (
                    <Box component="li" key={key} {...otherProps}>
                      <Typography variant="body2">{option}</Typography>
                    </Box>
                  );
                }

                return (
                  <Box
                    component="li"
                    key={key}
                    {...otherProps}
                    sx={{
                      flexDirection: "column",
                      alignItems: "flex-start",
                      py: 1,
                    }}
                  >
                    <Box
                      sx={{
                        display: "flex",
                        alignItems: "center",
                        width: "100%",
                        justifyContent: "space-between",
                      }}
                    >
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="body2" sx={{ fontWeight: "bold" }}>
                          {details.symbol}
                        </Typography>
                        <Typography
                          variant="caption"
                          color="text.secondary"
                          sx={{ display: "block", lineHeight: 1.2 }}
                        >
                          {details.name}
                        </Typography>
                      </Box>
                      <Box sx={{ textAlign: "right", ml: 1 }}>
                        <Typography
                          variant="caption"
                          color="primary"
                          sx={{ fontWeight: "medium" }}
                        >
                          {details.currency}
                        </Typography>
                        <Typography
                          variant="caption"
                          color="text.secondary"
                          sx={{ display: "block", lineHeight: 1.2 }}
                        >
                          매치:{" "}
                          {(parseFloat(details.matchScore) * 100).toFixed(1)}%
                        </Typography>
                      </Box>
                    </Box>
                  </Box>
                );
              }}
              renderTags={(value, getTagProps) =>
                value.map((option, index) => {
                  const details = symbolDetails.get(option);
                  const chipLabel = details
                    ? `${details.symbol} (${details.currency})`
                    : option;

                  return (
                    <Chip
                      variant="outlined"
                      label={chipLabel}
                      {...getTagProps({ index })}
                      key={option}
                      sx={{
                        "& .MuiChip-label": {
                          fontSize: "0.875rem",
                        },
                      }}
                    />
                  );
                })
              }
              renderInput={(params) => (
                <TextField
                  {...params}
                  placeholder={
                    searchLoading && searchQuery.length > 1
                      ? "검색 중..."
                      : "종목 검색 (예: AAPL, Apple, 애플)"
                  }
                  helperText={
                    debouncedSearchQuery.length === 0
                      ? "종목을 검색하여 선택하세요 (최소 2글자 이상)"
                      : debouncedSearchQuery.length > 1 &&
                        availableSymbols.length === 0 &&
                        !searchLoading
                      ? "검색 결과가 없습니다. 다른 키워드를 시도해보세요."
                      : undefined
                  }
                  InputProps={{
                    ...(params.InputProps as any),
                    startAdornment: (
                      <>
                        <SearchIcon sx={{ mr: 1, color: "action.active" }} />
                        {params.InputProps?.startAdornment}
                      </>
                    ),
                  }}
                />
              )}
              noOptionsText={
                debouncedSearchQuery.length > 1
                  ? searchLoading
                    ? "검색 중..."
                    : "검색 결과가 없습니다"
                  : "최소 2글자 이상 입력하여 검색하세요"
              }
            />
          </Box>

          {/* 선택된 심볼 개수 표시 */}
          {symbols.length > 0 && (
            <Box>
              <Typography variant="caption" color="text.secondary">
                선택된 종목: {symbols.length}개
              </Typography>
            </Box>
          )}
        </Stack>
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose}>취소</Button>
        <Button
          variant="contained"
          onClick={handleSubmit}
          disabled={!name.trim() || symbols.length === 0}
        >
          {isEdit ? "업데이트" : "생성"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
