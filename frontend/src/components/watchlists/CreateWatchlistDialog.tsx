"use client";

import { useStockSearchSymbols } from "@/hooks/useStocks";
import { Add as AddIcon } from "@mui/icons-material";
import {
  Autocomplete,
  Box,
  Button,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormHelperText,
  TextField,
  Typography,
} from "@mui/material";
import React from "react";

interface SymbolOption {
  symbol: string;
  name: string;
  currency: string;
  matchScore: string;
}

interface WatchlistFormData {
  name: string;
  description?: string;
  symbols: string[];
}

interface WatchlistFormErrors {
  name?: string;
  description?: string;
  symbols?: string;
}

interface CreateWatchlistDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: WatchlistFormData) => void;
  initialData?: Partial<WatchlistFormData>;
  isEdit?: boolean;
  loading?: boolean;
}

export default function CreateWatchlistDialog({
  open,
  onClose,
  onSubmit,
  initialData,
  isEdit = false,
  loading = false,
}: CreateWatchlistDialogProps) {
  const [formData, setFormData] = React.useState<WatchlistFormData>({
    name: "",
    description: "",
    symbols: [],
    ...initialData,
  });
  const [errors, setErrors] = React.useState<WatchlistFormErrors>({});
  const [searchTerm, setSearchTerm] = React.useState("");
  const [debouncedSearchTerm, setDebouncedSearchTerm] = React.useState("");

  // 디바운싱: 500ms 지연 후 검색 (사용자 경험 개선)
  React.useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchTerm(searchTerm);
    }, 500);

    return () => clearTimeout(timer);
  }, [searchTerm]);

  // 심볼 검색 훅 사용 (디바운싱된 검색어 사용)
  const { data: searchResults, isLoading: isSearching } =
    useStockSearchSymbols(debouncedSearchTerm);

  // 검색 결과에서 심볼 정보 추출 (표시용)
  const symbolDetails = React.useMemo(() => {
    if (!searchResults) return new Map<string, SymbolOption>();

    const detailsMap = new Map<string, SymbolOption>();

    const processItem = (item: any) => {
      // API 응답 구조에 맞게 파싱
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

    // API 응답이 { symbols: [...], count: number, search_term: string } 형태
    if (searchResults && typeof searchResults === "object") {
      const searchObj = searchResults as any;
      const symbols = searchObj.symbols || searchObj.data || [];

      if (Array.isArray(symbols)) {
        symbols.slice(0, 20).forEach(processItem);
      }
    } else if (Array.isArray(searchResults)) {
      // 혹시 배열로 오는 경우 대비
      (searchResults as any[]).slice(0, 20).forEach(processItem);
    }

    return detailsMap;
  }, [searchResults]);

  // 검색 결과에서 심볼 배열 추출
  const availableSymbols = React.useMemo(() => {
    return Array.from(symbolDetails.keys());
  }, [symbolDetails]);

  // 최종 옵션 리스트 - 검색 결과 표시
  const symbolOptions = React.useMemo(() => {
    // 검색어가 최소 2글자 이상일 때만 결과 표시
    if (debouncedSearchTerm && debouncedSearchTerm.trim().length >= 2) {
      return availableSymbols;
    }
    return []; // 검색어가 없거나 짧으면 빈 배열
  }, [debouncedSearchTerm, availableSymbols]);

  React.useEffect(() => {
    if (open) {
      setFormData({
        name: "",
        description: "",
        symbols: [],
        ...initialData,
      });
      setErrors({});
      setSearchTerm(""); // 검색어 초기화
      setDebouncedSearchTerm(""); // 디바운싱된 검색어도 초기화
    }
  }, [open, initialData]);

  const validateForm = (): boolean => {
    const newErrors: WatchlistFormErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = "워치리스트 이름을 입력해주세요.";
    }

    if (formData.symbols.length === 0) {
      newErrors.symbols = "최소 하나 이상의 종목을 추가해주세요.";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = () => {
    if (validateForm()) {
      onSubmit(formData);
    }
  };

  const handleSymbolChange = (_: any, newValue: string[]) => {
    setFormData((prev) => ({
      ...prev,
      symbols: newValue,
    }));
    if (errors.symbols) {
      setErrors((prev) => ({ ...prev, symbols: undefined }));
    }
  };

  const handleNameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setFormData((prev) => ({
      ...prev,
      name: event.target.value,
    }));
    if (errors.name) {
      setErrors((prev) => ({ ...prev, name: undefined }));
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        {isEdit ? "워치리스트 수정" : "새 워치리스트 만들기"}
      </DialogTitle>
      <DialogContent>
        <Box component="form" sx={{ mt: 1 }}>
          <TextField
            fullWidth
            variant='standard'
            label="워치리스트 이름"
            value={formData.name}
            onChange={handleNameChange}
            error={!!errors.name}
            helperText={errors.name}
            margin="normal"
            required
            autoFocus
          />

          <TextField
            fullWidth
            label="설명 (선택사항)"
            variant='standard'
            value={formData.description}
            onChange={(e) =>
              setFormData((prev) => ({ ...prev, description: e.target.value }))
            }
            margin="normal"
            rows={3}
            placeholder="이 워치리스트에 대한 간단한 설명을 입력하세요..."
          />

          <Box sx={{ mt: 2, mb: 1 }}>
            <Typography variant="subtitle2" gutterBottom>
              종목 선택 *
            </Typography>
            <Autocomplete
              multiple
              options={symbolOptions}
              value={formData.symbols}
              onChange={handleSymbolChange}
              inputValue={searchTerm}
              onInputChange={(_, newInputValue) => {
                setSearchTerm(newInputValue);
              }}
              filterOptions={(options) => options}
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

                // 상세 정보 표시
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
              filterSelectedOptions
              loading={isSearching && debouncedSearchTerm.length > 1}
              freeSolo={false}
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
                  {...(params as any)}
                  variant="standard"
                  placeholder={
                    isSearching && searchTerm.length > 1
                      ? "검색 중..."
                      : "종목 검색 (예: AAPL, Apple, 애플)"
                  }
                  error={!!errors.symbols}
                  helperText={
                    debouncedSearchTerm.length === 0
                      ? "종목을 검색하여 선택하세요 (최소 2글자 이상)"
                      : debouncedSearchTerm.length > 1 &&
                        availableSymbols.length === 0 &&
                        !isSearching
                      ? "검색 결과가 없습니다. 다른 키워드를 시도해보세요."
                      : undefined
                  }
                />
              )}
              noOptionsText={
                debouncedSearchTerm.length > 1
                  ? isSearching
                    ? "검색 중..."
                    : "검색 결과가 없습니다"
                  : "최소 2글자 이상 입력하여 검색하세요"
              }
            />
            {errors.symbols && (
              <FormHelperText error>{errors.symbols}</FormHelperText>
            )}
          </Box>

          {formData.symbols.length > 0 && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="caption" color="text.secondary">
                선택된 종목: {formData.symbols.length}개
              </Typography>
              <Box sx={{ mt: 1 }}>
                {formData.symbols.map((symbol) => (
                  <Chip
                    key={symbol}
                    label={symbol}
                    size="small"
                    sx={{ mr: 0.5, mb: 0.5 }}
                    onDelete={() =>
                      setFormData((prev) => ({
                        ...prev,
                        symbols: prev.symbols.filter((s) => s !== symbol),
                      }))
                    }
                  />
                ))}
              </Box>
            </Box>
          )}
        </Box>
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button onClick={onClose} disabled={loading}>
          취소
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={loading}
          startIcon={isEdit ? undefined : <AddIcon />}
        >
          {loading ? "처리 중..." : isEdit ? "수정" : "생성"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
