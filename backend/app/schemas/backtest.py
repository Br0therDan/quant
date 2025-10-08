"""
Backtest API Schemas
"""

from datetime import datetime
from typing import Any

from pydantic import Field
from .base_schema import BaseSchema
from app.models.backtest import (
    BacktestConfig,
    BacktestStatus,
    PerformanceMetrics,
    Position,
    Trade,
)


# Request Schemas
class BacktestCreate(BaseSchema):
    """백테스트 생성 요청"""

    name: str = Field(..., description="백테스트 이름")
    description: str = Field(default="", description="백테스트 설명")
    config: BacktestConfig = Field(..., description="백테스트 설정")


class BacktestUpdate(BaseSchema):
    """백테스트 수정 요청"""

    name: str | None = Field(None, description="백테스트 이름")
    description: str | None = Field(None, description="백테스트 설명")
    config: BacktestConfig | None = Field(None, description="백테스트 설정")


class BacktestExecutionRequest(BaseSchema):
    """백테스트 실행 요청"""

    signals: list[dict[str, Any]] = Field(..., description="트레이딩 시그널 목록")

    class Config:
        json_schema_extra = {
            "example": {
                "signals": [
                    {
                        "symbol": "AAPL",
                        "action": "BUY",
                        "quantity": 10,
                        "timestamp": "2023-01-01T00:00:00",
                    },
                    {
                        "symbol": "AAPL",
                        "action": "SELL",
                        "quantity": 5,
                        "timestamp": "2023-01-02T00:00:00",
                    },
                ]
            }
        }


# Response Schemas
class BacktestResponse(BaseSchema):
    """백테스트 응답"""

    id: str = Field(..., description="백테스트 ID")
    name: str = Field(..., description="백테스트 이름")
    description: str = Field(..., description="백테스트 설명")
    config: BacktestConfig = Field(..., description="백테스트 설정")
    status: BacktestStatus = Field(..., description="실행 상태")
    start_time: datetime | None = Field(None, description="실행 시작 시간")
    end_time: datetime | None = Field(None, description="실행 종료 시간")
    duration_seconds: float | None = Field(None, description="실행 시간(초)")
    performance: PerformanceMetrics | None = Field(None, description="성과 지표")
    created_at: datetime = Field(..., description="생성 시간")
    updated_at: datetime | None = Field(None, description="수정 시간")


class BacktestListResponse(BaseSchema):
    """백테스트 목록 응답"""

    backtests: list[BacktestResponse] = Field(..., description="백테스트 목록")
    total: int = Field(..., description="총 개수")


class BacktestExecutionResponse(BaseSchema):
    """백테스트 실행 응답"""

    id: str = Field(..., description="실행 ID")
    backtest_id: str = Field(..., description="백테스트 ID")
    execution_id: str = Field(..., description="실행 ID")
    start_time: datetime = Field(..., description="실행 시작 시간")
    end_time: datetime | None = Field(None, description="실행 종료 시간")
    status: BacktestStatus = Field(..., description="실행 상태")
    portfolio_values: list[float] = Field(..., description="포트폴리오 가치 히스토리")
    trades: list[Trade] = Field(..., description="거래 내역")
    positions: dict[str, Position] = Field(..., description="최종 포지션")
    error_message: str | None = Field(None, description="오류 메시지")
    created_at: datetime = Field(..., description="생성 시간")


class BacktestExecutionListResponse(BaseSchema):
    """백테스트 실행 목록 응답"""

    executions: list[BacktestExecutionResponse] = Field(..., description="실행 목록")
    total: int = Field(..., description="총 개수")


class BacktestResultResponse(BaseSchema):
    """백테스트 결과 응답"""

    id: str = Field(..., description="결과 ID")
    backtest_id: str = Field(..., description="백테스트 ID")
    execution_id: str = Field(..., description="실행 ID")

    # 성과 지표
    total_return: float = Field(..., description="총 수익률")
    annualized_return: float = Field(..., description="연환산 수익률")
    volatility: float = Field(..., description="변동성")
    sharpe_ratio: float = Field(..., description="샤프 비율")
    max_drawdown: float = Field(..., description="최대 낙폭")

    # 추가 지표
    calmar_ratio: float | None = Field(None, description="칼마 비율")
    sortino_ratio: float | None = Field(None, description="소르티노 비율")

    # 벤치마크 비교
    benchmark_return: float | None = Field(None, description="벤치마크 수익률")
    alpha: float | None = Field(None, description="알파")
    beta: float | None = Field(None, description="베타")

    # 거래 통계
    total_trades: int = Field(..., description="총 거래 수")
    winning_trades: int = Field(..., description="승리 거래 수")
    losing_trades: int = Field(..., description="패배 거래 수")
    win_rate: float = Field(..., description="승률")

    # 데이터 경로
    portfolio_history_path: str | None = Field(None, description="포트폴리오 히스토리 파일 경로")
    trades_history_path: str | None = Field(None, description="거래 히스토리 파일 경로")

    created_at: datetime = Field(..., description="생성 시간")


class BacktestResultListResponse(BaseSchema):
    """백테스트 결과 목록 응답"""

    results: list[BacktestResultResponse] = Field(..., description="결과 목록")
    total: int = Field(..., description="총 개수")


# Integrated Backtest Schemas
class IntegratedBacktestRequest(BaseSchema):
    """통합 백테스트 요청"""

    name: str = Field(..., description="백테스트 이름")
    description: str = Field(default="", description="백테스트 설명")
    symbols: list[str] = Field(..., description="심볼 목록")
    start_date: datetime = Field(..., description="시작일")
    end_date: datetime = Field(..., description="종료일")
    strategy_type: str = Field(..., description="전략 타입")
    strategy_params: dict[str, Any] = Field(default_factory=dict, description="전략 매개변수")
    initial_capital: float = Field(default=100000.0, description="초기 자본")


class IntegratedBacktestResponse(BaseSchema):
    """통합 백테스트 응답"""

    backtest_id: str = Field(..., description="백테스트 ID")
    execution_id: str | None = Field(None, description="실행 ID")
    result_id: str | None = Field(None, description="결과 ID")
    status: BacktestStatus = Field(..., description="상태")
    message: str = Field(..., description="메시지")
    performance: PerformanceMetrics | None = Field(None, description="성과 지표")
    start_time: datetime | None = Field(None, description="시작 시간")
    end_time: datetime | None = Field(None, description="종료 시간")
