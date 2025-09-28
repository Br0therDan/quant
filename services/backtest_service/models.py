"""
백테스트 엔진 핵심 모델

백테스트 설정, 결과, 거래 기록 등의 데이터 모델을 정의합니다.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class TradeType(Enum):
    """거래 타입"""

    BUY = "BUY"
    SELL = "SELL"


class OrderType(Enum):
    """주문 타입"""

    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"


class Trade(BaseModel):
    """거래 기록"""

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
    """포지션 정보"""

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


class Portfolio(BaseModel):
    """포트폴리오 상태"""

    # 현금 및 자산
    cash: float = Field(..., description="현금")
    initial_cash: float = Field(..., description="초기 현금")

    # 포지션
    positions: dict[str, Position] = Field(default_factory=dict, description="포지션 목록")

    # 성과 지표
    total_value: float = Field(..., description="총 자산 가치")
    total_pnl: float = Field(default=0.0, description="총 손익")

    # 메타데이터
    timestamp: datetime = Field(default_factory=datetime.now, description="업데이트 시간")

    @property
    def cash_ratio(self) -> float:
        """현금 비율"""
        return self.cash / self.total_value if self.total_value > 0 else 0.0

    @property
    def return_rate(self) -> float:
        """수익률"""
        return (self.total_value - self.initial_cash) / self.initial_cash


class BacktestConfig(BaseModel):
    """백테스트 설정"""

    # 기본 설정
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

    # 메타데이터
    created_at: datetime = Field(default_factory=datetime.now, description="생성 시간")
    tags: list[str] = Field(default_factory=list, description="태그")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class BacktestResult(BaseModel):
    """백테스트 결과"""

    # 기본 정보
    backtest_id: str = Field(..., description="백테스트 ID")
    config: BacktestConfig = Field(..., description="백테스트 설정")

    # 실행 정보
    start_time: datetime = Field(..., description="실행 시작 시간")
    end_time: datetime = Field(..., description="실행 종료 시간")
    duration_seconds: float = Field(..., description="실행 시간(초)")

    # 성과 지표
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

    # 데이터 경로 (큰 데이터는 별도 저장)
    portfolio_history_path: str | None = Field(None, description="포트폴리오 히스토리 파일 경로")
    trades_history_path: str | None = Field(None, description="거래 히스토리 파일 경로")

    # 메타데이터
    status: str = Field(default="completed", description="상태")
    error_message: str | None = Field(None, description="오류 메시지")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
