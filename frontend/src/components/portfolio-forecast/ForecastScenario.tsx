/**
 * ForecastScenario Component
 *
 * 포트폴리오 예측 시나리오 분석 (Bull/Base/Bear)
 *
 * Features:
 * - 3개 시나리오 (강세/기본/약세)
 * - 백분위 기반 (95th/50th/5th)
 * - 색상 구분 (초록/회색/빨강)
 * - 상세 메트릭 (수익률, 확률, 리스크)
 *
 * @author GitHub Copilot
 * @created 2025-01-16
 */

"use client";

import type { ScenarioAnalysis } from "@/hooks/usePortfolioForecast";
import { usePortfolioForecast } from "@/hooks/usePortfolioForecast";
import {
  TrendingFlat as BaseIcon,
  TrendingDown as BearIcon,
  TrendingUp as BullIcon,
} from "@mui/icons-material";
import {
  Alert,
  Box,
  Card,
  CardContent,
  CardHeader,
  Chip,
  Skeleton,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";

// ============================================================================
// Types
// ============================================================================

export interface ForecastScenarioProps {
  /** 예측 기간 (일, 7-120일) */
  horizonDays?: number;
  /** 자동 조회 활성화 */
  enabled?: boolean;
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
 * 시나리오별 아이콘
 */
function getScenarioIcon(scenario: string) {
  if (scenario === "bull") return <BullIcon />;
  if (scenario === "bear") return <BearIcon />;
  return <BaseIcon />;
}

/**
 * 리스크 레벨 판단 (변동성 기반)
 */
function getRiskLevel(returnPct: number): string {
  const absReturn = Math.abs(returnPct);
  if (absReturn > 20) return "높음";
  if (absReturn > 10) return "중간";
  return "낮음";
}

/**
 * 리스크 레벨 색상
 */
function getRiskColor(riskLevel: string): "error" | "warning" | "success" {
  if (riskLevel === "높음") return "error";
  if (riskLevel === "중간") return "warning";
  return "success";
}

// ============================================================================
// Main Component
// ============================================================================

/**
 * ForecastScenario Component
 *
 * @example
 * ```tsx
 * <ForecastScenario horizonDays={30} />
 * ```
 */
export default function ForecastScenario({
  horizonDays = 30,
  enabled = true,
}: ForecastScenarioProps) {
  const { forecastData, scenarios, isLoading, isError, error } =
    usePortfolioForecast({
      horizonDays,
      enabled,
    });

  // ============================================================================
  // Render: Loading State
  // ============================================================================

  if (isLoading) {
    return (
      <Card>
        <CardHeader title="시나리오 분석" />
        <CardContent>
          <Skeleton variant="rectangular" height={250} />
        </CardContent>
      </Card>
    );
  }

  // ============================================================================
  // Render: Error State
  // ============================================================================

  if (isError) {
    return (
      <Card>
        <CardHeader title="시나리오 분석" />
        <CardContent>
          <Alert severity="error">
            {error?.message ||
              "포트폴리오 예측 데이터를 불러오는데 실패했습니다."}
          </Alert>
        </CardContent>
      </Card>
    );
  }

  // ============================================================================
  // Render: No Data State
  // ============================================================================

  if (!forecastData || scenarios.length === 0) {
    return (
      <Card>
        <CardHeader title="시나리오 분석" />
        <CardContent>
          <Alert severity="info">시나리오 데이터가 없습니다.</Alert>
        </CardContent>
      </Card>
    );
  }

  // ============================================================================
  // Data Preparation
  // ============================================================================

  const { last_portfolio_value, horizon_days } = forecastData;

  // ============================================================================
  // Render: Scenario Table
  // ============================================================================

  return (
    <Card>
      <CardHeader
        title="시나리오 분석"
        subheader={`${horizon_days}일 예측 기준 (백분위 기반)`}
      />
      <CardContent>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>시나리오</TableCell>
                <TableCell align="right">백분위</TableCell>
                <TableCell align="right">예상 가치</TableCell>
                <TableCell align="right">수익률</TableCell>
                <TableCell align="right">리스크</TableCell>
                <TableCell align="right">발생 확률</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {scenarios.map((scenario: ScenarioAnalysis) => {
                const riskLevel = getRiskLevel(scenario.returnPct);
                const riskColor = getRiskColor(riskLevel);

                return (
                  <TableRow key={scenario.scenario}>
                    {/* 시나리오 이름 */}
                    <TableCell>
                      <Stack direction="row" spacing={1} alignItems="center">
                        <Box sx={{ color: scenario.color }}>
                          {getScenarioIcon(scenario.scenario)}
                        </Box>
                        <Typography variant="body2" fontWeight="bold">
                          {scenario.label}
                        </Typography>
                      </Stack>
                    </TableCell>

                    {/* 백분위 */}
                    <TableCell align="right">
                      <Chip
                        label={`${scenario.percentile}th`}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>

                    {/* 예상 가치 */}
                    <TableCell align="right">
                      <Typography variant="body2" fontWeight="bold">
                        {formatCurrency(scenario.projectedValue)}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        (현재: {formatCurrency(last_portfolio_value)})
                      </Typography>
                    </TableCell>

                    {/* 수익률 */}
                    <TableCell align="right">
                      <Chip
                        label={`${
                          scenario.returnPct >= 0 ? "+" : ""
                        }${scenario.returnPct.toFixed(2)}%`}
                        size="small"
                        color={scenario.returnPct >= 0 ? "success" : "error"}
                      />
                    </TableCell>

                    {/* 리스크 */}
                    <TableCell align="right">
                      <Chip
                        label={riskLevel}
                        size="small"
                        color={riskColor}
                        variant="outlined"
                      />
                    </TableCell>

                    {/* 발생 확률 */}
                    <TableCell align="right">
                      <Typography variant="body2">
                        ~{scenario.probability}%
                      </Typography>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>

        {/* 주의사항 */}
        <Box sx={{ mt: 3 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            📌 시나리오 해석 가이드:
          </Typography>
          <Stack spacing={0.5} sx={{ ml: 2 }}>
            <Typography variant="caption" color="text.secondary">
              • <strong>강세 시나리오 (95th)</strong>: 상위 5% 확률로 발생하는
              최고 성과 시나리오
            </Typography>
            <Typography variant="caption" color="text.secondary">
              • <strong>기본 시나리오 (50th)</strong>: 중간값 (Median), 가장
              가능성 높은 결과
            </Typography>
            <Typography variant="caption" color="text.secondary">
              • <strong>약세 시나리오 (5th)</strong>: 하위 5% 확률로 발생하는
              최악 시나리오
            </Typography>
          </Stack>
        </Box>
      </CardContent>
    </Card>
  );
}
