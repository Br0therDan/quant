"""
Market Data Service Package

고도화된 마켓 데이터 서비스 패키지입니다.
각 도메인별로 전문화된 서비스를 제공합니다.
"""

from typing import Optional
from .base_service import BaseMarketDataService, CacheResult, DataCoverage
from .stock_service import StockService
from .fundamental import FundamentalService
from .economic_indicator import EconomicIndicatorService
from .intelligence import IntelligenceService
from app.services.database_manager import DatabaseManager


class MarketDataService:
    """통합 마켓 데이터 서비스

    모든 마켓 데이터 서비스의 진입점 역할을 합니다.
    각 도메인별 서비스에 대한 접근을 제공합니다.
    """

    def __init__(self, database_manager: Optional[DatabaseManager] = None):
        self.database_manager = database_manager

        # 각 도메인별 서비스 인스턴스
        self._stock_service = None
        self._fundamental_service = None
        self._economic_indicator_service = None
        self._intelligence_service = None

    @property
    def stock(self) -> StockService:
        """주식 데이터 서비스 접근"""
        if self._stock_service is None:
            self._stock_service = StockService(self.database_manager)
        return self._stock_service

    @property
    def fundamental(self) -> FundamentalService:
        """기업 재무 데이터 서비스 접근"""
        if self._fundamental_service is None:
            self._fundamental_service = FundamentalService(self.database_manager)
        return self._fundamental_service

    @property
    def economic(self) -> EconomicIndicatorService:
        """경제 지표 서비스 접근"""
        if self._economic_indicator_service is None:
            self._economic_indicator_service = EconomicIndicatorService(
                self.database_manager
            )
        return self._economic_indicator_service

    @property
    def intelligence(self) -> IntelligenceService:
        """인텔리전스 데이터 서비스 접근"""
        if self._intelligence_service is None:
            self._intelligence_service = IntelligenceService(self.database_manager)
        return self._intelligence_service

    async def close(self):
        """모든 서비스 종료 및 리소스 정리"""
        services = [
            self._stock_service,
            self._fundamental_service,
            self._economic_indicator_service,
            self._intelligence_service,
        ]

        for service in services:
            if service is not None:
                await service.close()

    async def health_check(self) -> dict:
        """서비스 상태 확인

        Returns:
            각 서비스의 상태 정보

        TODO: 구현 예정
        1. 각 서비스별 상태 체크
        2. AlphaVantage API 연결 상태
        3. 데이터베이스 연결 상태
        4. 캐시 상태
        """
        return {
            "status": "healthy",
            "services": {
                "stock": "ready",
                "fundamental": "ready",
                "economic": "ready",
                "intelligence": "ready",
            },
            "cache": {"mongodb": "connected", "duckdb": "connected"},
            "external_apis": {"alpha_vantage": "connected"},
        }


__all__ = [
    "MarketDataService",
    "BaseMarketDataService",
    "StockService",
    "FundamentalService",
    "EconomicIndicatorService",
    "IntelligenceService",
    "CacheResult",
    "DataCoverage",
]
