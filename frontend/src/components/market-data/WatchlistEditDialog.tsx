"use client";

import {
  Add as AddIcon,
  Close as CloseIcon,
  Search as SearchIcon,
} from "@mui/icons-material";
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
  const [selectedSymbol, setSelectedSymbol] = React.useState<any>(null);

  const { createOrUpdateWatchlist, updateWatchlist } = useWatchlist();

  // 심볼 검색
  const { data: searchResults, isLoading: searchLoading } =
    useStockSearchSymbols(searchQuery);

  const symbolOptions = React.useMemo(() => {
    if (!searchResults || !Array.isArray(searchResults)) return [];
    return searchResults.map((item: any) => ({
      symbol: item.symbol,
      name: item.name,
      label: `${item.symbol} - ${item.name}`,
    }));
  }, [searchResults]);

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
  }, [open, watchlist]);

  const handleAddSymbol = () => {
    if (selectedSymbol && !symbols.includes(selectedSymbol.symbol)) {
      setSymbols([...symbols, selectedSymbol.symbol]);
      setSelectedSymbol(null);
      setSearchQuery("");
    }
  };

  const handleRemoveSymbol = (symbolToRemove: string) => {
    setSymbols(symbols.filter((s) => s !== symbolToRemove));
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
    setSelectedSymbol(null);
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
              심볼 추가
            </Typography>
            <Box display="flex" gap={1}>
              <Autocomplete
                fullWidth
                options={symbolOptions}
                value={selectedSymbol}
                onChange={(_, newValue) => setSelectedSymbol(newValue)}
                inputValue={searchQuery}
                onInputChange={(_, newInputValue) =>
                  setSearchQuery(newInputValue)
                }
                loading={searchLoading}
                filterOptions={(x) => x} // 서버에서 필터링
                getOptionLabel={(option) => option.label || ""}
                isOptionEqualToValue={(option, value) =>
                  option.symbol === value.symbol
                }
                renderInput={(params) => (
                  <TextField
                    {...params}
                    placeholder="심볼 또는 회사명 검색..."
                    InputProps={{
                      ...params.InputProps,
                      startAdornment: <SearchIcon sx={{ mr: 1 }} />,
                    }}
                  />
                )}
                renderOption={(props, option) => (
                  <li {...props} key={option.symbol}>
                    <Box>
                      <Typography variant="body2" fontWeight="medium">
                        {option.symbol}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {option.name}
                      </Typography>
                    </Box>
                  </li>
                )}
              />
              <Button
                variant="contained"
                onClick={handleAddSymbol}
                disabled={!selectedSymbol}
                sx={{ minWidth: 100 }}
              >
                <AddIcon />
              </Button>
            </Box>
          </Box>

          {/* 추가된 심볼 목록 */}
          {symbols.length > 0 && (
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                추가된 심볼 ({symbols.length})
              </Typography>
              <Box display="flex" flexWrap="wrap" gap={1}>
                {symbols.map((symbol) => (
                  <Chip
                    key={symbol}
                    label={symbol}
                    onDelete={() => handleRemoveSymbol(symbol)}
                    color="primary"
                    variant="outlined"
                  />
                ))}
              </Box>
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
