import type { BacktestConfig, BacktestResponse, BacktestStatus } from "@/client";

const STATUS_LABELS: Record<BacktestStatus, string> = {
  pending: "대기 중",
  running: "실행 중",
  completed: "완료",
  failed: "실패",
  cancelled: "취소됨",
};

const STATUS_COLORS: Record<BacktestStatus, string> = {
  pending: "warning.main",
  running: "info.main",
  completed: "success.main",
  failed: "error.main",
  cancelled: "grey.500",
};

export const backtestUtils = {
  formatStatus(status?: BacktestStatus | null) {
    if (!status) {
      return "알 수 없음";
    }
    return STATUS_LABELS[status] ?? status;
  },
  getStatusColor(status?: BacktestStatus | null) {
    if (!status) {
      return "grey.500";
    }
    return STATUS_COLORS[status] ?? "grey.500";
  },
  isRunning(status?: BacktestStatus | null) {
    return status === "running" || status === "pending";
  },
  isCompleted(status?: BacktestStatus | null) {
    return status === "completed";
  },
  isFailed(status?: BacktestStatus | null) {
    return status === "failed" || status === "cancelled";
  },
  formatPercentage(value?: number | null, fractionDigits = 2) {
    if (value === undefined || value === null || Number.isNaN(value)) {
      return "-";
    }
    return `${(value * 100).toFixed(fractionDigits)}%`;
  },
  formatNumber(value?: number | null, fractionDigits = 2) {
    if (value === undefined || value === null || Number.isNaN(value)) {
      return "-";
    }
    return value.toFixed(fractionDigits);
  },
  formatCurrency(value?: number | null, currency = "USD") {
    if (value === undefined || value === null || Number.isNaN(value)) {
      return "-";
    }
    return new Intl.NumberFormat("ko-KR", {
      style: "currency",
      currency,
      maximumFractionDigits: 0,
    }).format(value);
  },
  formatDuration(start?: Date | string | null, end?: Date | string | null) {
    if (!start || !end) {
      return "-";
    }
    const startDate = new Date(start);
    const endDate = new Date(end);
    if (Number.isNaN(startDate.getTime()) || Number.isNaN(endDate.getTime())) {
      return "-";
    }
    const diffMs = Math.max(endDate.getTime() - startDate.getTime(), 0);
    const diffSeconds = Math.floor(diffMs / 1000);
    const hours = Math.floor(diffSeconds / 3600);
    const minutes = Math.floor((diffSeconds % 3600) / 60);
    const seconds = diffSeconds % 60;

    if (hours > 0) {
      return `${hours}시간 ${minutes}분`;
    }
    if (minutes > 0) {
      return `${minutes}분 ${seconds}초`;
    }
    return `${seconds}초`;
  },
  formatDate(value?: Date | string | null) {
    if (!value) {
      return "-";
    }
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
      return "-";
    }
    return date.toLocaleString("ko-KR");
  },
  extractSymbols(backtest?: BacktestResponse | null) {
    const symbols = backtest?.config?.symbols ?? [];
    if (!symbols.length) {
      return "심볼 정보 없음";
    }
    if (symbols.length <= 5) {
      return symbols.join(", ");
    }
    return `${symbols.slice(0, 5).join(", ")} +${symbols.length - 5}`;
  },
  validateConfig(config: BacktestConfig) {
    const errors: string[] = [];
    if (!config.name?.trim()) {
      errors.push("백테스트 이름을 입력해주세요");
    }
    if (!config.start_date || !config.end_date) {
      errors.push("시작일과 종료일을 모두 선택해주세요");
    } else if (new Date(config.start_date) >= new Date(config.end_date)) {
      errors.push("종료일은 시작일 이후여야 합니다");
    }
    if (!config.symbols?.length) {
      errors.push("최소 한 개 이상의 심볼을 입력해주세요");
    }
    if (config.initial_cash !== undefined && config.initial_cash <= 0) {
      errors.push("초기 자본은 0보다 커야 합니다");
    }
    if (
      config.max_position_size !== undefined &&
      (config.max_position_size <= 0 || config.max_position_size > 1)
    ) {
      errors.push("최대 포지션 크기는 0보다 크고 1 이하이어야 합니다");
    }
    return errors;
  },
};

export type BacktestListItem = BacktestResponse;
