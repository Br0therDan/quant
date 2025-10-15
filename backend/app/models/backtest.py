"""
Backtest Service Models
"""

from datetime import datetime

from .base_model import BaseDocument
from pydantic import BaseModel, Field
from app.schemas.enums import BacktestStatus, TradeType, OrderType


class BacktestConfig(BaseModel):
    """백테스트 설정 내장 모델"""

    name: str = Field(..., description="백테스트 이름")
    description: str = Field(default="", description="백테스트 설명")

    # 기간 및 대상
    start_date: datetime = Field(..., description="시작일")
    end_date: datetime = Field(..., description="종료일")
    symbols: list[str] = Field(..., description="대상 심볼 목록")

    # 자본 관리
    initial_cash: float = Field(default=100000.0, description="초기 자본금")
    max_position_size: float = Field(default=0.2, description="최대 포지션 크기 (비율)")

    # 거래 비용
    commission_rate: float = Field(default=0.001, description="수수료율")
    slippage_rate: float = Field(default=0.0005, description="슬리피지율")

    # 리밸런싱
    rebalance_frequency: str | None = Field(
        None, description="리밸런싱 주기 (daily, weekly, monthly)"
    )

    # 태그
    tags: list[str] = Field(default_factory=list, description="태그")


class Trade(BaseModel):
    """거래 기록 내장 모델"""

    trade_id: str = Field(..., description="거래 ID")
    symbol: str = Field(..., description="심볼")
    trade_type: TradeType = Field(..., description="거래 타입")
    order_type: OrderType = Field(default=OrderType.MARKET, description="주문 타입")

    # 거래 정보
    quantity: float = Field(..., description="수량")
    price: float = Field(..., description="체결 가격")
    timestamp: datetime = Field(..., description="거래 시간")

    # 비용 정보
    commission: float = Field(default=0.0, description="수수료")
    slippage: float = Field(default=0.0, description="슬리피지")

    # 메타데이터
    strategy_signal_id: str | None = Field(None, description="전략 신호 ID")
    notes: str | None = Field(None, description="메모")


class Position(BaseModel):
    """포지션 정보 내장 모델"""

    symbol: str = Field(..., description="심볼")
    quantity: float = Field(..., description="보유 수량")
    avg_price: float = Field(..., description="평균 단가")
    current_price: float = Field(..., description="현재 가격")

    # 손익 계산
    unrealized_pnl: float = Field(..., description="미실현 손익")
    realized_pnl: float = Field(default=0.0, description="실현 손익")

    # 메타데이터
    first_buy_date: datetime = Field(..., description="최초 매수일")
    last_update: datetime = Field(default_factory=datetime.now, description="마지막 업데이트")


class PerformanceMetrics(BaseModel):
    """성과 지표 내장 모델"""

    total_return: float = Field(..., description="총 수익률")
    annualized_return: float = Field(..., description="연환산 수익률")
    volatility: float = Field(..., description="변동성")
    sharpe_ratio: float = Field(..., description="샤프 비율")
    max_drawdown: float = Field(..., description="최대 낙폭")

    # 거래 통계
    total_trades: int = Field(..., description="총 거래 수")
    winning_trades: int = Field(..., description="승리 거래 수")
    losing_trades: int = Field(..., description="패배 거래 수")
    win_rate: float = Field(..., description="승률")


class Backtest(BaseDocument):
    """백테스트 문서 모델"""

    # 기본 정보
    name: str = Field(..., description="백테스트 이름")
    description: str = Field(default="", description="백테스트 설명")

    # 설정
    config: BacktestConfig = Field(..., description="백테스트 설정")

    # 전략 연결 (Phase 2: optional, Phase 3+: required)
    strategy_id: str | None = Field(None, description="전략 ID (Phase 3+)")

    # 실행 정보
    status: BacktestStatus = Field(default=BacktestStatus.PENDING, description="실행 상태")
    start_time: datetime | None = Field(None, description="실행 시작 시간")
    end_time: datetime | None = Field(None, description="실행 종료 시간")
    duration_seconds: float | None = Field(None, description="실행 시간(초)")

    # 성과 지표
    performance: PerformanceMetrics | None = Field(None, description="성과 지표")

    # 데이터 경로 (큰 데이터는 별도 저장)
    portfolio_history_path: str | None = Field(None, description="포트폴리오 히스토리 파일 경로")
    trades_history_path: str | None = Field(None, description="거래 히스토리 파일 경로")

    # 메타데이터
    error_message: str | None = Field(None, description="오류 메시지")
    created_by: str | None = Field(None, description="생성자")
    created_at: datetime = Field(default_factory=datetime.now, description="생성 시간")
    updated_at: datetime = Field(default_factory=datetime.now, description="수정 시간")
    tags: list[str] = Field(default_factory=list, description="태그")

    class Settings:
        name = "backtests"
        indexes = [
            [("name", 1)],
            [("status", 1)],
            [("created_at", -1)],
            [("config.symbols", 1)],
        ]


class BacktestExecution(BaseDocument):
    """백테스트 실행 내역"""

    backtest_id: str = Field(..., description="백테스트 ID")
    # 실행 정보
    execution_id: str = Field(..., description="실행 ID")
    start_time: datetime = Field(..., description="실행 시작 시간")
    end_time: datetime | None = Field(None, description="실행 종료 시간")
    status: BacktestStatus = Field(default=BacktestStatus.PENDING, description="실행 상태")

    # 결과
    portfolio_values: list[float] = Field(
        default_factory=list, description="포트폴리오 가치 히스토리"
    )
    trades: list[Trade] = Field(default_factory=list, description="거래 내역")
    positions: dict[str, Position] = Field(default_factory=dict, description="최종 포지션")

    # 메타데이터
    error_message: str | None = Field(None, description="오류 메시지")
    created_at: datetime = Field(default_factory=datetime.now, description="생성 시간")

    class Settings:
        name = "backtest_executions"
        indexes = [
            [("backtest_id", 1)],
            [("execution_id", 1)],
            [("start_time", -1)],
            [("status", 1)],
        ]


class BacktestResult(BaseDocument):
    """백테스트 결과"""

    backtest_id: str = Field(..., description="백테스트 ID")
    execution_id: str = Field(..., description="실행 ID")

    # 성과 지표
    performance: PerformanceMetrics = Field(..., description="성과 지표")

    # 포트폴리오 분석
    final_portfolio_value: float = Field(..., description="최종 포트폴리오 가치")
    cash_remaining: float = Field(..., description="잔여 현금")
    total_invested: float = Field(..., description="총 투자 금액")

    # 리스크 지표
    var_95: float | None = Field(None, description="95% VaR")
    var_99: float | None = Field(None, description="99% VaR")
    calmar_ratio: float | None = Field(None, description="칼마 비율")
    sortino_ratio: float | None = Field(None, description="소르티노 비율")

    # 벤치마크 비교
    benchmark_return: float | None = Field(None, description="벤치마크 수익률")
    alpha: float | None = Field(None, description="알파")
    beta: float | None = Field(None, description="베타")

    # 메타데이터
    created_at: datetime = Field(default_factory=datetime.now, description="생성 시간")

    class Settings:
        name = "backtest_results"
        indexes = [
            [("backtest_id", 1)],
            [("execution_id", 1)],
            [("created_at", -1)],
        ]
