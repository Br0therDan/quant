"""
Intelligence Service - Analyst Module
분석가 추천 및 내부자 거래 정보
"""

from typing import List, Dict, Any
import logging

from .base import BaseIntelligenceService


logger = logging.getLogger(__name__)


class AnalystService(BaseIntelligenceService):
    """분석가 추천 및 내부자 거래 서비스

    Alpha Vantage INSIDER_TRANSACTIONS API를 사용하여
    내부자 거래 정보를 조회합니다.
    """

    async def get_analyst_recommendations(self, symbol: str) -> List[Dict[str, Any]]:
        """분석가 추천 의견 조회 (내부자 거래 정보 포함)

        Args:
            symbol: 주식 심볼

        Returns:
            분석가 추천 및 내부자 거래 리스트
        """
        logger.info(f"Getting analyst recommendations for {symbol}")

        try:
            # Alpha Vantage INSIDER_TRANSACTIONS API 호출
            response = await self.alpha_vantage.intelligence.insider_transactions(
                symbol=symbol
            )

            if not isinstance(response, dict) or "data" not in response:
                return []

            recommendations = []
            for transaction in response["data"]:
                recommendation = {
                    "symbol": symbol,
                    "insider_name": transaction.get("name", ""),
                    "title": transaction.get("title", ""),
                    "transaction_type": transaction.get("transaction_type", ""),
                    "transaction_date": transaction.get("transaction_date", ""),
                    "shares_traded": transaction.get("shares_traded"),
                    "price_per_share": transaction.get("price_per_share"),
                    "total_value": transaction.get("total_value"),
                    "shares_owned_after": transaction.get("shares_owned_after"),
                    "ownership_type": transaction.get("ownership_type", ""),
                    "filing_date": transaction.get("filing_date", ""),
                    "link": transaction.get("link", ""),
                }
                recommendations.append(recommendation)

            logger.info(
                f"Retrieved {len(recommendations)} insider transactions for {symbol}"
            )
            return recommendations

        except Exception as e:
            logger.error(f"Error getting analyst recommendations for {symbol}: {e}")
            return []

    async def refresh_data_from_source(self, **kwargs) -> List[Dict[str, Any]]:
        """BaseMarketDataService 추상 메서드 구현 (deprecated)"""
        logger.warning("refresh_data_from_source is deprecated for AnalystService")
        return []
