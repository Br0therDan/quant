"""
임시 TradingSignal 모델

실제로는 strategy_service에서 import해야 하지만, 임시로 정의합니다.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class TradingSignal(BaseModel):
    """거래 신호"""

    signal_id: str = Field(..., description="신호 ID")
    symbol: str = Field(..., description="심볼")
    action: str = Field(..., description="액션 (BUY/SELL)")
    quantity: float = Field(..., description="수량")
    quantity_type: str = Field(
        default="shares", description="수량 타입 (shares/percent/amount)"
    )
    timestamp: datetime = Field(..., description="신호 시간")
    confidence: float = Field(default=1.0, description="신뢰도")
    notes: str | None = Field(None, description="메모")


class DataLoader:
    """임시 DataLoader 클래스"""

    async def get_price_data(
        self, symbol: str, start_date: datetime, end_date: datetime
    ):
        """가격 데이터 로드 (임시 구현)"""
        import pandas as pd

        # 임시로 더미 데이터 반환
        date_range = pd.date_range(start=start_date, end=end_date, freq="D")
        data = pd.DataFrame(
            {
                "close": [100.0] * len(date_range),
                "open": [99.0] * len(date_range),
                "high": [101.0] * len(date_range),
                "low": [98.0] * len(date_range),
                "volume": [1000] * len(date_range),
            },
            index=date_range,
        )

        return data
