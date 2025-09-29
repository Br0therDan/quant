"use client";

import { StrategyResponse, TemplateResponse } from "@/client/types.gen";
import {
  Assessment,
  ContentCopy,
  Delete,
  Edit,
  PlayArrow,
  Timeline,
} from "@mui/icons-material";
import {
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  Chip,
  Divider,
  IconButton,
  Rating,
  Stack,
  Tooltip,
  Typography,
} from "@mui/material";

// 템플릿과 전략을 위한 확장 타입
type ExtendedStrategy = StrategyResponse & {
  difficulty?: string;
  performance_rating?: number;
};

type ExtendedTemplate = TemplateResponse & {
  difficulty?: string;
  performance_rating?: number;
};

interface StrategyCardProps {
  strategy: ExtendedStrategy | ExtendedTemplate;
  isTemplate?: boolean;
  onEdit?: (strategy: ExtendedStrategy | ExtendedTemplate) => void;
  onClone?: (strategy: ExtendedStrategy | ExtendedTemplate) => void;
  onDelete?: (strategy: ExtendedStrategy | ExtendedTemplate) => void;
  onExecute?: (strategy: ExtendedStrategy | ExtendedTemplate) => void;
  onViewPerformance?: (strategy: ExtendedStrategy | ExtendedTemplate) => void;
  onViewDetails?: (strategy: ExtendedStrategy | ExtendedTemplate) => void;
}

export default function StrategyCard({
  strategy,
  isTemplate = false,
  onEdit,
  onClone,
  onDelete,
  onExecute,
  onViewPerformance,
  onViewDetails,
}: StrategyCardProps) {
  const getDifficultyColor = (difficulty?: string) => {
    switch (difficulty?.toLowerCase()) {
      case "초급":
        return "success";
      case "중급":
        return "warning";
      case "고급":
        return "error";
      default:
        return "default";
    }
  };

  const getStrategyTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case "sma_crossover":
        return "primary";
      case "rsi_mean_reversion":
        return "secondary";
      case "momentum":
        return "info";
      case "buy_and_hold":
        return "success";
      default:
        return "default";
    }
  };

  const formatStrategyType = (type: string) => {
    const typeMap: Record<string, string> = {
      sma_crossover: "SMA 크로스오버",
      rsi_mean_reversion: "RSI 평균회귀",
      momentum: "모멘텀",
      buy_and_hold: "매수후보유",
    };
    return typeMap[type] || type;
  };

  return (
    <Card
      sx={{
        height: "100%",
        display: "flex",
        flexDirection: "column",
        transition: "all 0.2s ease-in-out",
        "&:hover": {
          transform: "translateY(-4px)",
          boxShadow: 4,
        },
      }}
    >
      <CardContent sx={{ flexGrow: 1 }}>
        <Box sx={{ display: "flex", justifyContent: "space-between", mb: 1 }}>
          <Typography variant="h6" component="h3" noWrap>
            {strategy.name}
          </Typography>
          {isTemplate && (
            <Chip
              size="small"
              label="템플릿"
              color="primary"
              variant="outlined"
            />
          )}
        </Box>

        <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
          <Chip
            size="small"
            label={formatStrategyType(strategy.strategy_type)}
            color={getStrategyTypeColor(strategy.strategy_type) as any}
            variant="filled"
          />
          {strategy.tags?.map((tag) => (
            <Chip
              key={tag}
              size="small"
              label={tag}
              variant="outlined"
              color="default"
            />
          ))}
        </Stack>

        <Typography
          variant="body2"
          color="text.secondary"
          sx={{
            mb: 2,
            minHeight: "2.5em",
            display: "-webkit-box",
            WebkitLineClamp: 2,
            WebkitBoxOrient: "vertical",
            overflow: "hidden",
          }}
        >
          {strategy.description || "설명이 없습니다."}
        </Typography>

        {isTemplate && (
          <>
            <Divider sx={{ my: 1 }} />
            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
              <Typography variant="body2" color="text.secondary">
                난이도:
              </Typography>
              <Chip
                size="small"
                label={strategy.difficulty || "중급"}
                color={getDifficultyColor(strategy.difficulty) as any}
                variant="outlined"
              />
            </Box>
            {strategy.performance_rating && (
              <Box
                sx={{ display: "flex", alignItems: "center", gap: 1, mt: 1 }}
              >
                <Typography variant="body2" color="text.secondary">
                  성과 평가:
                </Typography>
                <Rating
                  value={strategy.performance_rating}
                  readOnly
                  size="small"
                />
              </Box>
            )}
          </>
        )}

        {!isTemplate && (
          <>
            <Divider sx={{ my: 1 }} />
            <Box sx={{ display: "flex", justifyContent: "space-between" }}>
              <Typography variant="body2" color="text.secondary">
                생성일: {new Date(strategy.created_at).toLocaleDateString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                수정일: {new Date(strategy.updated_at).toLocaleDateString()}
              </Typography>
            </Box>
          </>
        )}
      </CardContent>

      <CardActions sx={{ p: 2, pt: 0 }}>
        <Stack direction="row" spacing={1} sx={{ width: "100%" }}>
          {isTemplate ? (
            <>
              <Button
                size="small"
                variant="contained"
                startIcon={<ContentCopy />}
                onClick={() => onClone?.(strategy)}
                sx={{ flexGrow: 1 }}
              >
                사용하기
              </Button>
              <Tooltip title="미리보기">
                <IconButton
                  size="small"
                  onClick={() => onViewDetails?.(strategy)}
                >
                  <Assessment />
                </IconButton>
              </Tooltip>
            </>
          ) : (
            <>
              <Button
                size="small"
                variant="contained"
                startIcon={<PlayArrow />}
                onClick={() => onExecute?.(strategy)}
                color="primary"
              >
                실행
              </Button>
              <Tooltip title="편집">
                <IconButton size="small" onClick={() => onEdit?.(strategy)}>
                  <Edit />
                </IconButton>
              </Tooltip>
              <Tooltip title="복제">
                <IconButton size="small" onClick={() => onClone?.(strategy)}>
                  <ContentCopy />
                </IconButton>
              </Tooltip>
              <Tooltip title="성과 보기">
                <IconButton
                  size="small"
                  onClick={() => onViewPerformance?.(strategy)}
                >
                  <Timeline />
                </IconButton>
              </Tooltip>
              <Tooltip title="삭제">
                <IconButton
                  size="small"
                  onClick={() => onDelete?.(strategy)}
                  color="error"
                >
                  <Delete />
                </IconButton>
              </Tooltip>
            </>
          )}
        </Stack>
      </CardActions>
    </Card>
  );
}
