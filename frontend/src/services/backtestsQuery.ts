// TanStack Query hooks for backtests
export * from "@/client/@tanstack/react-query.gen";

// Re-export commonly used backtest hooks with better names
export {
  backtestsCreateBacktestMutation,
  backtestsDeleteBacktestMutation,
  backtestsUpdateBacktestMutation,
  backtestsExecuteBacktestMutation,
  backtestsCreateAndRunIntegratedBacktestMutation,
  backtestsGetBacktestOptions as useBacktestQuery,
  backtestsGetBacktestsOptions as useBacktestsQuery,
  backtestsGetBacktestExecutionsOptions as useBacktestExecutionsQuery,
  backtestsGetBacktestResultsOptions as useBacktestResultsQuery,
  backtestsGetPerformanceAnalyticsOptions as usePerformanceAnalyticsQuery,
  backtestsGetTradesAnalyticsOptions as useTradesAnalyticsQuery,
  backtestsGetBacktestSummaryAnalyticsOptions as useBacktestSummaryAnalyticsQuery,
} from "@/client/@tanstack/react-query.gen";

// Import types for better typing
import type {
  BacktestConfig,
  BacktestSummary,
  BacktestResults,
  BacktestExecution,
  BacktestStatus
} from "@/types/backtest";

// Utility functions for backtests
export const backtestUtils = {
  formatStatus: (status: BacktestStatus): string => {
    const statusMap: Record<BacktestStatus, string> = {
      QUEUED: "대기 중",
      INITIALIZING: "초기화 중",
      DATA_COLLECTION: "데이터 수집",
      SIGNAL_GENERATION: "신호 생성",
      SIMULATION: "시뮬레이션",
      ANALYSIS: "분석 중",
      COMPLETED: "완료",
      FAILED: "실패",
      CANCELLED: "취소됨",
    };
    return statusMap[status] || status;
  },

  formatDuration: (startTime: string, endTime?: string): string => {
    const start = new Date(startTime);
    const end = endTime ? new Date(endTime) : new Date();
    const diffMs = end.getTime() - start.getTime();

    const hours = Math.floor(diffMs / (1000 * 60 * 60));
    const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((diffMs % (1000 * 60)) / 1000);

    if (hours > 0) return `${hours}시간 ${minutes}분`;
    if (minutes > 0) return `${minutes}분 ${seconds}초`;
    return `${seconds}초`;
  },

  formatCurrency: (amount: number): string => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  },

  formatPercentage: (value: number, decimals: number = 2): string => {
    return `${(value * 100).toFixed(decimals)}%`;
  },

  formatNumber: (value: number, decimals: number = 2): string => {
    return new Intl.NumberFormat('ko-KR', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(value);
  },

  getStatusColor: (status: BacktestStatus): string => {
    const colorMap: Record<BacktestStatus, string> = {
      QUEUED: "#9e9e9e",
      INITIALIZING: "#2196f3",
      DATA_COLLECTION: "#2196f3",
      SIGNAL_GENERATION: "#2196f3",
      SIMULATION: "#2196f3",
      ANALYSIS: "#2196f3",
      COMPLETED: "#4caf50",
      FAILED: "#f44336",
      CANCELLED: "#ff9800",
    };
    return colorMap[status] || "#9e9e9e";
  },

  isRunning: (status: BacktestStatus): boolean => {
    return [
      "QUEUED",
      "INITIALIZING",
      "DATA_COLLECTION",
      "SIGNAL_GENERATION",
      "SIMULATION",
      "ANALYSIS"
    ].includes(status);
  },

  isCompleted: (status: BacktestStatus): boolean => {
    return status === "COMPLETED";
  },

  isFailed: (status: BacktestStatus): boolean => {
    return ["FAILED", "CANCELLED"].includes(status);
  },

  validateConfig: (config: BacktestConfig): string[] => {
    const errors: string[] = [];

    if (!config.name.trim()) {
      errors.push("백테스트 이름을 입력해주세요");
    }

    if (!config.strategy_id) {
      errors.push("전략을 선택해주세요");
    }

    if (!config.watchlist_id) {
      errors.push("워치리스트를 선택해주세요");
    }

    if (!config.start_date) {
      errors.push("시작 날짜를 선택해주세요");
    }

    if (!config.end_date) {
      errors.push("종료 날짜를 선택해주세요");
    }

    if (config.start_date && config.end_date && config.start_date >= config.end_date) {
      errors.push("종료 날짜는 시작 날짜보다 뒤여야 합니다");
    }

    if (config.initial_capital <= 0) {
      errors.push("초기 자본은 0보다 커야 합니다");
    }

    return errors;
  },

  getConfigSummary: (config: BacktestConfig): string => {
    return [
      `전략 ID: ${config.strategy_id}`,
      `워치리스트: ${config.watchlist_id}`,
      `기간: ${config.start_date} ~ ${config.end_date}`,
      `초기자본: ${backtestUtils.formatCurrency(config.initial_capital)}`,
    ].join(" | ");
  },

  getPerformanceSummary: (results: BacktestResults): string => {
    const totalReturn = backtestUtils.formatPercentage(results.total_return);
    const sharpeRatio = backtestUtils.formatNumber(results.sharpe_ratio);
    const maxDrawdown = backtestUtils.formatPercentage(Math.abs(results.max_drawdown));

    return [
      `수익률: ${totalReturn}`,
      `샤프비율: ${sharpeRatio}`,
      `최대낙폭: ${maxDrawdown}`,
    ].join(" | ");
  },

  sortBacktests: (backtests: BacktestSummary[], sortBy: "created_at" | "name" | "total_return" | "status", order: "asc" | "desc" = "desc") => {
    return [...backtests].sort((a, b) => {
      let aValue: any;
      let bValue: any;

      switch (sortBy) {
        case "created_at":
          aValue = new Date(a.created_at);
          bValue = new Date(b.created_at);
          break;
        case "name":
          aValue = a.name.toLowerCase();
          bValue = b.name.toLowerCase();
          break;
        case "total_return":
          aValue = a.total_return || 0;
          bValue = b.total_return || 0;
          break;
        case "status":
          aValue = a.status;
          bValue = b.status;
          break;
        default:
          return 0;
      }

      if (aValue < bValue) return order === "asc" ? -1 : 1;
      if (aValue > bValue) return order === "asc" ? 1 : -1;
      return 0;
    });
  },

  filterBacktests: (backtests: BacktestSummary[], filters: {
    status?: BacktestStatus[];
    strategy?: string;
    dateRange?: { start: string; end: string };
  }) => {
    return backtests.filter((backtest) => {
      if (filters.status && !filters.status.includes(backtest.status)) {
        return false;
      }

      if (filters.strategy && backtest.strategy_name !== filters.strategy) {
        return false;
      }

      if (filters.dateRange) {
        const createdAt = new Date(backtest.created_at);
        const start = new Date(filters.dateRange.start);
        const end = new Date(filters.dateRange.end);
        if (createdAt < start || createdAt > end) {
          return false;
        }
      }

      return true;
    });
  },

  getRiskLevel: (sharpeRatio: number): "LOW" | "MEDIUM" | "HIGH" => {
    if (sharpeRatio > 1.5) return "LOW";
    if (sharpeRatio > 0.5) return "MEDIUM";
    return "HIGH";
  },

  getRiskLevelColor: (riskLevel: "LOW" | "MEDIUM" | "HIGH"): string => {
    const colorMap = {
      LOW: "#4caf50",
      MEDIUM: "#ff9800",
      HIGH: "#f44336",
    };
    return colorMap[riskLevel];
  },
};

// Custom hooks for common patterns
export const useBacktestActions = () => {
  // These will be implemented as we create actual mutation hooks
  // For now, return placeholder functions that could be implemented later
  return {
    createBacktest: async (config: BacktestConfig) => {
      console.log("Create backtest:", config);
      // Will implement with actual mutation
    },
    executeBacktest: async (id: string) => {
      console.log("Execute backtest:", id);
      // Will implement with actual mutation
    },
    deleteBacktest: async (id: string) => {
      console.log("Delete backtest:", id);
      // Will implement with actual mutation
    },
    updateBacktest: async (id: string, updates: Partial<BacktestConfig>) => {
      console.log("Update backtest:", id, updates);
      // Will implement with actual mutation
    },
  };
};

// Export types for external use
export { type BacktestConfig, type BacktestSummary, type BacktestResults, type BacktestStatus };
