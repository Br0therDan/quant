"""
Performance Models using Beanie (MongoDB ODM)
"""

from datetime import datetime, UTC

from .base_model import BaseDocument
from pydantic import Field


class StrategyPerformance(BaseDocument):
    """전략 성과 정보 문서 모델"""

    strategy_id: str = Field(..., description="전략 ID")
    strategy_name: str = Field(..., description="전략 이름")

    # 기본 통계
    total_signals: int = Field(default=0, description="총 신호 수")
    buy_signals: int = Field(default=0, description="매수 신호 수")
    sell_signals: int = Field(default=0, description="매도 신호 수")
    hold_signals: int = Field(default=0, description="보유 신호 수")

    # 성과 지표
    total_return: float | None = Field(None, description="총 수익률")
    win_rate: float | None = Field(None, ge=0.0, le=1.0, description="승률")
    avg_return_per_trade: float | None = Field(None, description="거래당 평균 수익률")
    max_drawdown: float | None = Field(None, description="최대 낙폭")

    # 리스크 지표
    sharpe_ratio: float | None = Field(None, description="샤프 비율")
    calmar_ratio: float | None = Field(None, description="칼마 비율")
    volatility: float | None = Field(None, description="변동성")

    # 기간 정보
    start_date: datetime | None = Field(None, description="시작일")
    end_date: datetime | None = Field(None, description="종료일")

    # 백테스트 정보
    backtest_id: str | None = Field(None, description="백테스트 ID")

    # 추가 지표
    accuracy: float | None = Field(None, ge=0.0, le=1.0, description="정확도")
    avg_signal_strength: float | None = Field(
        None, ge=0.0, le=1.0, description="평균 신호 강도"
    )

    # 메타데이터
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "strategy_performance"
        indexes = [
            "strategy_id",
            "strategy_name",
            "backtest_id",
            [("total_return", -1)],
            [("sharpe_ratio", -1)],
            "created_at",
        ]
