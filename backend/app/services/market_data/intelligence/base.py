"""
Intelligence Service Base Module
인텔리전스 서비스 공통 베이스 클래스 및 유틸리티
"""

from typing import Optional
from decimal import Decimal
import logging

from ..base_service import BaseMarketDataService


logger = logging.getLogger(__name__)


class BaseIntelligenceService(BaseMarketDataService):
    """인텔리전스 서비스 기본 클래스

    뉴스, 감정 분석, 분석가 추천 등의 정성적 데이터를 처리하는
    서비스들의 공통 베이스 클래스입니다.
    """

    @staticmethod
    def _safe_decimal(value) -> Optional[Decimal]:
        """API 응답값을 Decimal로 안전하게 변환

        Args:
            value: 변환할 값 (str, int, float, Decimal 등)

        Returns:
            Decimal 객체 또는 None (변환 실패 시)

        Examples:
            >>> BaseIntelligenceService._safe_decimal("123.45")
            Decimal('123.45')
            >>> BaseIntelligenceService._safe_decimal("N/A")
            None
            >>> BaseIntelligenceService._safe_decimal("")
            None
        """
        if not value or value in ("", "None", "N/A"):
            return None
        try:
            # Decimal128 타입도 str로 변환하여 처리
            return Decimal(str(value))
        except Exception as e:
            logger.warning(f"Error converting to Decimal: {e}")
            return None
