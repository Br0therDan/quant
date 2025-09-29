// 백테스트 관련 TypeScript 타입 정의

export type BacktestStatus =
    | 'QUEUED'
    | 'INITIALIZING'
    | 'DATA_COLLECTION'
    | 'SIGNAL_GENERATION'
    | 'SIMULATION'
    | 'ANALYSIS'
    | 'COMPLETED'
    | 'FAILED'
    | 'CANCELLED';

export interface BacktestConfig {
    name: string;
    description?: string;
    watchlist_id: string;
    strategy_id: string;
    start_date: string;
    end_date: string;
    initial_capital: number;
    commission: number;
    slippage: number;
    position_sizing: 'equal_weight' | 'market_cap' | 'volatility_adjusted';
    rebalancing_frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly';
    risk_management?: RiskManagementConfig;
}

export interface RiskManagementConfig {
    max_position_size: number;
    stop_loss?: number;
    take_profit?: number;
    max_drawdown_limit?: number;
}

export interface BacktestSummary {
    id: string;
    name: string;
    status: BacktestStatus;
    strategy_name: string;
    strategy_type: string;
    total_return?: number;
    sharpe_ratio?: number;
    max_drawdown?: number;
    created_at: string;
    updated_at: string;
    completed_at?: string;
    duration?: number;
    is_favorite: boolean;
    tags: string[];
}

export interface BacktestDetail extends BacktestSummary {
    description?: string;
    watchlist_name: string;
    watchlist_symbols: string[];
    config: BacktestConfig;
    results?: BacktestResults;
    executions: BacktestExecution[];
}

export interface BacktestResults {
    total_return: number;
    annual_return: number;
    sharpe_ratio: number;
    max_drawdown: number;
    volatility: number;
    win_rate: number;
    total_trades: number;
    profit_factor: number;
    sortino_ratio?: number;
    calmar_ratio?: number;
    var_95?: number;
    cvar_95?: number;
    performance_data: PerformanceDataPoint[];
    trade_history: Trade[];
    monthly_returns: MonthlyReturn[];
}

export interface PerformanceDataPoint {
    date: string;
    portfolio_value: number;
    benchmark_value?: number;
    drawdown: number;
    returns: number;
}

export interface Trade {
    id: string;
    date: string;
    symbol: string;
    side: 'BUY' | 'SELL';
    quantity: number;
    price: number;
    commission: number;
    pnl: number;
    cumulative_pnl: number;
}

export interface MonthlyReturn {
    month: string;
    return: number;
    benchmark_return?: number;
}

export interface BacktestExecution {
    id: string;
    backtest_id: string;
    status: BacktestStatus;
    started_at: string;
    completed_at?: string;
    error_message?: string;
    progress: ExecutionProgress;
    logs: ExecutionLog[];
    intermediate_results?: IntermediateResults;
}

export interface ExecutionProgress {
    current_step: string;
    total_steps: number;
    completed_steps: number;
    percentage: number;
    estimated_completion?: string;
}

export interface ExecutionLog {
    timestamp: string;
    level: 'INFO' | 'WARNING' | 'ERROR' | 'DEBUG';
    message: string;
    details?: Record<string, any>;
}

export interface IntermediateResults {
    data_points_processed: number;
    signals_generated: number;
    trades_executed: number;
    current_portfolio_value?: number;
    current_return?: number;
}

export interface BacktestFilters {
    status?: BacktestStatus[];
    strategy_types?: string[];
    date_range?: {
        start: string;
        end: string;
    };
    performance_range?: {
        min_return?: number;
        max_return?: number;
    };
    tags?: string[];
    favorites_only?: boolean;
    search?: string;
}

export interface BacktestListParams extends BacktestFilters {
    page?: number;
    limit?: number;
    sort_by?: 'created_at' | 'updated_at' | 'total_return' | 'name';
    sort_order?: 'asc' | 'desc';
}

export interface BacktestListResponse {
    backtests: BacktestSummary[];
    total: number;
    page: number;
    pages: number;
    has_next: boolean;
    has_prev: boolean;
}

export interface CreateBacktestResponse {
    backtest_id: string;
    status: BacktestStatus;
    estimated_duration?: number;
    queue_position?: number;
}

export interface BacktestUpdate {
    name?: string;
    description?: string;
    is_favorite?: boolean;
    tags?: string[];
}

// API 응답 타입
export interface BacktestEstimateResponse {
    estimated_duration: number; // seconds
    estimated_cost?: number;
    resource_requirements: {
        cpu: number;
        memory: number;
        storage: number;
    };
}

// 프리셋 설정 타입
export interface BacktestPreset {
    id: string;
    name: string;
    description: string;
    config: Partial<BacktestConfig>;
    is_default: boolean;
}

// 비교 분석 타입
export interface BacktestComparison {
    backtests: BacktestSummary[];
    correlation_matrix: number[][];
    performance_comparison: PerformanceComparison[];
}

export interface PerformanceComparison {
    metric: string;
    values: Record<string, number>; // backtest_id -> value
    best_performer: string;
    worst_performer: string;
}

// 상태 관리 타입
export interface BacktestState {
    // 목록 관리
    backtests: BacktestSummary[];
    filters: BacktestFilters;
    loading: boolean;
    error?: string;

    // 실행 상태
    activeExecutions: Record<string, BacktestExecution>;

    // 선택된 백테스트
    selectedBacktest?: BacktestDetail;

    // 비교 모드
    comparisonMode: boolean;
    selectedForComparison: string[];

    // UI 상태
    viewMode: 'card' | 'table';
    showFilters: boolean;
}

export interface BacktestActions {
    // 목록 관리
    fetchBacktests: (params?: BacktestListParams) => Promise<void>;
    updateFilters: (filters: Partial<BacktestFilters>) => void;
    clearFilters: () => void;

    // 백테스트 실행
    createBacktest: (config: BacktestConfig) => Promise<string>;
    estimateBacktest: (config: Partial<BacktestConfig>) => Promise<BacktestEstimateResponse>;
    cancelBacktest: (id: string) => Promise<void>;

    // 상세 조회
    fetchBacktestDetail: (id: string) => Promise<void>;
    subscribeToExecution: (id: string) => void;
    unsubscribeFromExecution: (id: string) => void;

    // 관리 기능
    toggleFavorite: (id: string) => Promise<void>;
    updateTags: (id: string, tags: string[]) => Promise<void>;
    deleteBacktest: (id: string) => Promise<void>;
    cloneBacktest: (id: string) => Promise<string>;

    // 비교 기능
    toggleComparison: (id: string) => void;
    clearComparison: () => void;
    compareBacktests: (ids: string[]) => Promise<BacktestComparison>;

    // UI 액션
    setViewMode: (mode: 'card' | 'table') => void;
    toggleFilters: () => void;
}

// 폼 관련 타입
export interface BacktestFormData extends Omit<BacktestConfig, 'watchlist_id' | 'strategy_id'> {
    watchlist: { id: string; name: string } | null;
    strategy: { id: string; name: string; type: string } | null;
}

export interface BacktestFormErrors {
    name?: string;
    watchlist?: string;
    strategy?: string;
    start_date?: string;
    end_date?: string;
    initial_capital?: string;
    commission?: string;
    slippage?: string;
}
