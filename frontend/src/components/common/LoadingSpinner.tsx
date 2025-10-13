"use client";

import { TrendingUp as TrendingUpIcon } from "@mui/icons-material";
import { Box, CircularProgress, Skeleton, Typography } from "@mui/material";
import type { SxProps, Theme } from "@mui/material/styles";
import { MyLogo } from './logo';

interface LoadingSpinnerProps {
  message?: string;
  size?: number;
  variant?: "default" | "minimal" | "skeleton" | "chart";
  height?: number | string;
  sx?: SxProps<Theme>;
}

export default function LoadingSpinner({
  message = "Loading...",
  size = 60,
  variant = "default",
  height = 400,
  sx,
}: LoadingSpinnerProps) {
  // 스켈레톤 변형
  if (variant === "skeleton") {
    return (
      <Box sx={{ width: "100%", ...sx }}>
        <Skeleton variant="rectangular" height={height} animation="wave" />
      </Box>
    );
  }

  // 차트 로딩 변형
  if (variant === "chart") {
    return (
      <Box
        sx={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          height: height,
          gap: 3,
          ...sx,
        }}
      >
        <Box sx={{ position: "relative", display: "inline-flex" }}>
          <CircularProgress
            size={size}
            thickness={4}
            sx={{
              color: (theme) => theme.palette.primary.main,
            }}
          />
          <Box
            sx={{
              top: 0,
              left: 0,
              bottom: 0,
              right: 0,
              position: "absolute",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <MyLogo icon={true} width={30} />
          </Box>
        </Box>
        <Typography variant="body2" color="text.secondary">
          {message}
        </Typography>
      </Box>
    );
  }

  // 미니멀 변형
  if (variant === "minimal") {
    return (
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          p: 2,
          ...sx,
        }}
      >
        <CircularProgress size={size} />
      </Box>
    );
  }

  // 기본 변형
  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        height: height,
        gap: 2,
        ...sx,
      }}
    >
      <CircularProgress size={size} thickness={4} />
      {message && (
        <Typography variant="body1" color="text.secondary">
          {message}
        </Typography>
      )}
    </Box>
  );
}

// 페이지 전체 로딩
export function PageLoading({
  message = "Loading page...",
}: {
  message?: string;
}) {
  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        minHeight: "100vh",
        gap: 3,
      }}
    >
      <Box sx={{ position: "relative", display: "inline-flex" }}>
        <CircularProgress
          size={80}
          thickness={4}
          sx={{
            color: (theme) => theme.palette.primary.main,
          }}
        />
        <Box
          sx={{
            top: 0,
            left: 0,
            bottom: 0,
            right: 0,
            position: "absolute",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <TrendingUpIcon
            sx={{
              fontSize: 40,
              color: (theme) => theme.palette.primary.main,
              animation: "pulse 1.5s ease-in-out infinite",
              "@keyframes pulse": {
                "0%, 100%": { opacity: 1 },
                "50%": { opacity: 0.5 },
              },
            }}
          />
        </Box>
      </Box>
      <Typography variant="h6" color="text.secondary">
        {message}
      </Typography>
    </Box>
  );
}

// 인라인 로딩 (작은 공간용)
export function InlineLoading({ message }: { message?: string }) {
  return (
    <Box sx={{ display: "flex", alignItems: "center", gap: 1, p: 1 }}>
      <CircularProgress size={20} />
      {message && (
        <Typography variant="caption" color="text.secondary">
          {message}
        </Typography>
      )}
    </Box>
  );
}
