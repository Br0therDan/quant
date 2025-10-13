/**
 * ForecastMetrics Component
 *
 * 포트폴리오 예측 지표를 Grid 카드로 표시
 *
 * Features:
 * - 4개 핵심 지표 (예상 수익률, 변동성, 샤프 비율, 현재 가치)
 * - 색상 구분 (긍정/부정)
 * - 트렌드 아이콘
 * - Responsive Grid 레이아웃
 *
 * @author GitHub Copilot
 * @created 2025-01-16
 */

"use client";

import { usePortfolioForecast } from "@/hooks/usePortfolioForecast";
import {
  AccountBalance as PortfolioIcon,
  Speed as SharpeIcon,
  TrendingDown as TrendingDownIcon,
  TrendingUp as TrendingUpIcon,
  ShowChart as VolatilityIcon,
} from "@mui/icons-material";
import {
  Alert,
  Box,
  Card,
  CardContent,
  Chip,
  Grid,
  Skeleton,
  Typography,
} from "@mui/material";

// ============================================================================
// Types
// ============================================================================

export interface ForecastMetricsProps {
  /** 예측 기간 (일, 7-120일) */
  horizonDays?: number;
  /** 자동 조회 활성화 */
  enabled?: boolean;
}

/**
 * 메트릭 카드 Props
 */
interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactElement;
  color: "success" | "error" | "info" | "warning" | "default";
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * 통화 포맷팅 (천 단위 콤마)
 */
function formatCurrency(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

/**
 * 신뢰도 레벨 색상
 */
function getConfidenceLevelColor(
  level: "high" | "medium" | "low"
): "success" | "warning" | "error" {
  if (level === "high") return "success";
  if (level === "medium") return "warning";
  return "error";
}

// ============================================================================
// Sub-Components
// ============================================================================

/**
 * MetricCard - 단일 지표 카드
 */
function MetricCard({ title, value, subtitle, icon, color }: MetricCardProps) {
  return (
    <Card>
      <CardContent>
        <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
          <Box
            sx={{
              mr: 2,
              p: 1,
              borderRadius: 2,
              bgcolor: `${color}.lighter`,
              color: `${color}.main`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            {icon}
          </Box>
          <Typography variant="h6" color="text.secondary">
            {title}
          </Typography>
        </Box>

        <Typography variant="h4" fontWeight="bold" color={`${color}.main`}>
          {value}
        </Typography>

        {subtitle && (
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
            {subtitle}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}

// ============================================================================
// Main Component
// ============================================================================

/**
 * ForecastMetrics Component
 *
 * @example
 * ```tsx
 * <ForecastMetrics horizonDays={30} />
 * ```
 */
export default function ForecastMetrics({
  horizonDays = 30,
  enabled = true,
}: ForecastMetricsProps) {
  const {
    forecastData,
    isLoading,
    isError,
    error,
    calculateRiskAdjustedReturn,
    getConfidenceLevel,
  } = usePortfolioForecast({
    horizonDays,
    enabled,
  });

  // ============================================================================
  // Render: Loading State
  // ============================================================================

  if (isLoading) {
    return (
      <Box sx={{ flexGrow: 1 }}>
        <Grid container spacing={2}>
          {[1, 2, 3, 4].map((i) => (
            <Grid size={{ xs: 12, sm: 6, md: 3 }} key={i}>
              <Card>
                <CardContent>
                  <Skeleton variant="text" width="60%" />
                  <Skeleton variant="text" width="80%" height={40} />
                  <Skeleton variant="text" width="40%" />
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  }

  // ============================================================================
  // Render: Error State
  // ============================================================================

  if (isError) {
    return (
      <Alert severity="error">
        {error?.message || "포트폴리오 예측 데이터를 불러오는데 실패했습니다."}
      </Alert>
    );
  }

  // ============================================================================
  // Render: No Data State
  // ============================================================================

  if (!forecastData) {
    return <Alert severity="info">포트폴리오 예측 데이터가 없습니다.</Alert>;
  }

  // ============================================================================
  // Data Preparation
  // ============================================================================

  const {
    last_portfolio_value,
    expected_return_pct,
    expected_volatility_pct,
    horizon_days,
  } = forecastData;

  // 샤프 비율 계산
  const sharpeRatio = calculateRiskAdjustedReturn(
    expected_return_pct,
    expected_volatility_pct
  );

  // 신뢰도 레벨
  const confidenceLevel = getConfidenceLevel();
  const confidenceLevelColor = getConfidenceLevelColor(confidenceLevel);
  const confidenceLevelLabel =
    confidenceLevel === "high"
      ? "높음"
      : confidenceLevel === "medium"
      ? "중간"
      : "낮음";

  // 메트릭 카드 데이터
  const metrics: MetricCardProps[] = [
    {
      title: "예상 수익률",
      value: `${
        expected_return_pct >= 0 ? "+" : ""
      }${expected_return_pct.toFixed(2)}%`,
      subtitle: `${horizon_days}일 후 예상 수익률`,
      icon:
        expected_return_pct >= 0 ? <TrendingUpIcon /> : <TrendingDownIcon />,
      color: expected_return_pct >= 0 ? "success" : "error",
    },
    {
      title: "예상 변동성",
      value: `${expected_volatility_pct.toFixed(2)}%`,
      subtitle: `${horizon_days}일 기간 예상 변동성`,
      icon: <VolatilityIcon />,
      color: expected_volatility_pct > 20 ? "warning" : "info",
    },
    {
      title: "샤프 비율",
      value: sharpeRatio.toFixed(2),
      subtitle: "리스크 조정 수익률",
      icon: <SharpeIcon />,
      color:
        sharpeRatio > 1 ? "success" : sharpeRatio > 0.5 ? "warning" : "error",
    },
    {
      title: "현재 포트폴리오 가치",
      value: formatCurrency(last_portfolio_value),
      subtitle: `기준 시점 포트폴리오 가치`,
      icon: <PortfolioIcon />,
      color: "info",
    },
  ];

  // ============================================================================
  // Render: Metrics Grid
  // ============================================================================

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Grid container spacing={2}>
        {/* 메트릭 카드 4개 */}
        {metrics.map((metric, index) => (
          <Grid size={{ xs: 12, sm: 6, md: 3 }} key={index}>
            <MetricCard {...metric} />
          </Grid>
        ))}
      </Grid>

      {/* 신뢰도 레벨 Chip */}
      <Box sx={{ mt: 2, display: "flex", alignItems: "center", gap: 1 }}>
        <Typography variant="body2" color="text.secondary">
          예측 신뢰도:
        </Typography>
        <Chip
          label={confidenceLevelLabel}
          color={confidenceLevelColor}
          size="small"
        />
        <Typography variant="caption" color="text.secondary">
          (샤프 비율 기반)
        </Typography>
      </Box>
    </Box>
  );
}
