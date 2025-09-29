"use client";

import { StrategyType } from "@/client/types.gen";
import { FilterList, Search } from "@mui/icons-material";
import {
  Box,
  Chip,
  FormControl,
  InputAdornment,
  InputLabel,
  MenuItem,
  Select,
  SelectChangeEvent,
  Stack,
  TextField,
} from "@mui/material";
import React from "react";

interface StrategyFiltersProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  selectedType?: StrategyType | "all";
  onTypeChange: (type: StrategyType | "all") => void;
  selectedDifficulty?: string;
  onDifficultyChange: (difficulty: string) => void;
  selectedTags?: string[];
  onTagsChange: (tags: string[]) => void;
  availableTags?: string[];
  isTemplate?: boolean;
}

const STRATEGY_TYPES = [
  { value: "all", label: "전체" },
  { value: "sma_crossover", label: "SMA 크로스오버" },
  { value: "rsi_mean_reversion", label: "RSI 평균회귀" },
  { value: "momentum", label: "모멘텀" },
  { value: "buy_and_hold", label: "매수후보유" },
] as const;

const DIFFICULTY_LEVELS = [
  { value: "all", label: "전체" },
  { value: "초급", label: "초급" },
  { value: "중급", label: "중급" },
  { value: "고급", label: "고급" },
] as const;

export default function StrategyFilters({
  searchQuery,
  onSearchChange,
  selectedType = "all",
  onTypeChange,
  selectedDifficulty = "all",
  onDifficultyChange,
  selectedTags = [],
  onTagsChange,
  availableTags = [],
  isTemplate = false,
}: StrategyFiltersProps) {
  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    onSearchChange(event.target.value);
  };

  const handleTypeChange = (event: SelectChangeEvent) => {
    onTypeChange(event.target.value as StrategyType | "all");
  };

  const handleDifficultyChange = (event: SelectChangeEvent) => {
    onDifficultyChange(event.target.value);
  };

  const handleTagToggle = (tag: string) => {
    const newTags = selectedTags.includes(tag)
      ? selectedTags.filter((t) => t !== tag)
      : [...selectedTags, tag];
    onTagsChange(newTags);
  };

  const clearTag = (tagToRemove: string) => {
    onTagsChange(selectedTags.filter((tag) => tag !== tagToRemove));
  };

  return (
    <Box sx={{ mb: 3 }}>
      <Stack spacing={2}>
        {/* 검색 및 기본 필터 */}
        <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
          <TextField
            fullWidth
            placeholder={`${isTemplate ? "템플릿" : "전략"} 검색...`}
            value={searchQuery}
            onChange={handleSearchChange}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search />
                </InputAdornment>
              ),
            }}
            sx={{ flex: 1 }}
          />

          <FormControl sx={{ minWidth: 180 }}>
            <InputLabel>전략 타입</InputLabel>
            <Select
              value={selectedType}
              label="전략 타입"
              onChange={handleTypeChange}
            >
              {STRATEGY_TYPES.map((type) => (
                <MenuItem key={type.value} value={type.value}>
                  {type.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {isTemplate && (
            <FormControl sx={{ minWidth: 120 }}>
              <InputLabel>난이도</InputLabel>
              <Select
                value={selectedDifficulty}
                label="난이도"
                onChange={handleDifficultyChange}
              >
                {DIFFICULTY_LEVELS.map((level) => (
                  <MenuItem key={level.value} value={level.value}>
                    {level.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          )}
        </Stack>

        {/* 태그 필터 */}
        {availableTags.length > 0 && (
          <Box>
            <Stack
              direction="row"
              spacing={1}
              alignItems="center"
              sx={{ mb: 1 }}
            >
              <FilterList fontSize="small" />
              <Box
                component="span"
                sx={{ fontSize: "0.875rem", color: "text.secondary" }}
              >
                태그:
              </Box>
            </Stack>
            <Stack
              direction="row"
              spacing={1}
              sx={{ flexWrap: "wrap", gap: 1 }}
            >
              {availableTags.map((tag) => (
                <Chip
                  key={tag}
                  label={tag}
                  onClick={() => handleTagToggle(tag)}
                  color={selectedTags.includes(tag) ? "primary" : "default"}
                  variant={selectedTags.includes(tag) ? "filled" : "outlined"}
                  size="small"
                />
              ))}
            </Stack>
          </Box>
        )}

        {/* 선택된 태그 표시 */}
        {selectedTags.length > 0 && (
          <Box>
            <Stack
              direction="row"
              spacing={1}
              alignItems="center"
              sx={{ mb: 1 }}
            >
              <Box
                component="span"
                sx={{ fontSize: "0.875rem", color: "text.secondary" }}
              >
                선택된 태그:
              </Box>
            </Stack>
            <Stack
              direction="row"
              spacing={1}
              sx={{ flexWrap: "wrap", gap: 1 }}
            >
              {selectedTags.map((tag) => (
                <Chip
                  key={tag}
                  label={tag}
                  onDelete={() => clearTag(tag)}
                  color="primary"
                  size="small"
                />
              ))}
            </Stack>
          </Box>
        )}
      </Stack>
    </Box>
  );
}
