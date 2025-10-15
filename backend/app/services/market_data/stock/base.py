"""
Base Stock Service
주식 서비스 기본 클래스 - 공통 로직
"""

from typing import Optional
from datetime import datetime
from decimal import Decimal
import logging

from app.services.market_data.base_service import BaseMarketDataService
from app.services.database_manager import DatabaseManager
from app.services.monitoring.data_quality_sentinel import DataQualitySentinel
from app.schemas.market_data.stock import QuoteData

logger = logging.getLogger(__name__)


class BaseStockService(BaseMarketDataService):
    """주식 서비스 기본 클래스

    BaseMarketDataService를 상속받아 주식 관련 공통 로직을 제공합니다.

    Attributes:
        database_manager: DuckDB 캐시 매니저
        data_quality_sentinel: 데이터 품질 모니터링 서비스
    """

    def __init__(
        self,
        database_manager: Optional[DatabaseManager] = None,
        data_quality_sentinel: Optional[DataQualitySentinel] = None,
    ) -> None:
        """서비스 초기화

        Args:
            database_manager: DuckDB 캐시 매니저 (optional)
            data_quality_sentinel: 데이터 품질 센티널 (optional)
        """
        super().__init__(database_manager)
        self.data_quality_sentinel = data_quality_sentinel

    def _dict_to_quote_data(self, quote_dict: dict) -> QuoteData:
        """딕셔너리를 QuoteData 객체로 변환

        Args:
            quote_dict: Alpha Vantage quote 응답 딕셔너리

        Returns:
            QuoteData 객체
        """
        change_percent_str = str(quote_dict.get("change_percent", "0"))
        change_percent_value = change_percent_str.rstrip("%")

        # 타임스탬프 처리
        timestamp = datetime.now()
        if "latest_trading_day" in quote_dict:
            try:
                timestamp = datetime.fromisoformat(
                    str(quote_dict["latest_trading_day"])
                )
            except (ValueError, TypeError):
                pass

        return QuoteData(
            symbol=str(quote_dict.get("symbol", "")).upper(),
            timestamp=timestamp,
            price=Decimal(str(quote_dict.get("price", 0))),
            change=(
                Decimal(str(quote_dict.get("change", 0)))
                if quote_dict.get("change")
                else None
            ),
            change_percent=(
                Decimal(str(change_percent_value)) if change_percent_value else None
            ),
            previous_close=(
                Decimal(str(quote_dict.get("previous_close", 0)))
                if quote_dict.get("previous_close")
                else None
            ),
            open_price=(
                Decimal(str(quote_dict.get("open", 0)))
                if quote_dict.get("open")
                else None
            ),
            high_price=(
                Decimal(str(quote_dict.get("high", 0)))
                if quote_dict.get("high")
                else None
            ),
            low_price=(
                Decimal(str(quote_dict.get("low", 0)))
                if quote_dict.get("low")
                else None
            ),
            volume=(
                int(quote_dict.get("volume", 0)) if quote_dict.get("volume") else None
            ),
            # Alpha Vantage GLOBAL_QUOTE는 호가 정보를 제공하지 않으므로 None으로 설정
            bid_price=None,
            ask_price=None,
            bid_size=None,
            ask_size=None,
        )

    def _validate_symbol(self, symbol: str) -> str:
        """심볼 유효성 검사 및 정규화

        Args:
            symbol: 주식 심볼

        Returns:
            대문자로 변환되고 공백이 제거된 심볼

        Raises:
            ValueError: 심볼이 비어있거나 유효하지 않은 경우
        """
        if not symbol or not symbol.strip():
            raise ValueError("유효한 심볼이 필요합니다")

        return symbol.upper().strip()
