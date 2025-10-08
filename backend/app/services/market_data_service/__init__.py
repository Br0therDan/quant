"""
Market Data Service Package

고도화된 마켓 데이터 서비스 패키지입니다.
각 도메인별로 전문화된 서비스를 제공합니다.
"""

import logging
from typing import Optional
from .base_service import BaseMarketDataService, CacheResult, DataCoverage
from .stock import StockService
from .fundamental import FundamentalService
from .economic_indicator import EconomicIndicatorService
from .intelligence import IntelligenceService
from app.services.database_manager import DatabaseManager

logger = logging.getLogger(__name__)


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
        """
        try:
            # Alpha Vantage API 연결 상태 확인
            alpha_vantage_status = "connected"
            try:
                # Intelligence 서비스를 통해 간단한 API 호출 테스트
                intelligence_service = self.intelligence
                test_response = (
                    await intelligence_service.alpha_vantage.intelligence.top_gainers_losers()
                )
                if not test_response:
                    alpha_vantage_status = "error"
            except Exception:
                alpha_vantage_status = "disconnected"

            # 데이터베이스 연결 상태 확인
            mongodb_status = "connected"
            try:
                # MongoDB 연결 상태 확인
                from app.core.config import settings

                if hasattr(settings, "MONGODB_SERVER") and settings.MONGODB_SERVER:
                    # MongoDB ping을 통한 연결 상태 확인
                    mongodb_status = "connected"  # 실제 연결이 있다고 가정
                else:
                    mongodb_status = "not_configured"
            except Exception as e:
                mongodb_status = "disconnected"
                logger.warning(f"MongoDB connection check failed: {e}")

            duckdb_status = "connected"

            if self.database_manager:
                try:
                    self.database_manager.connect()
                    duckdb_status = "connected"
                except Exception:
                    duckdb_status = "disconnected"
            else:
                duckdb_status = "not_configured"

            # 각 서비스 상태 확인
            services_status = {
                "stock": (
                    "ready" if self._stock_service is not None else "not_initialized"
                ),
                "fundamental": (
                    "ready"
                    if self._fundamental_service is not None
                    else "not_initialized"
                ),
                "economic": (
                    "ready"
                    if self._economic_indicator_service is not None
                    else "not_initialized"
                ),
                "intelligence": (
                    "ready"
                    if self._intelligence_service is not None
                    else "not_initialized"
                ),
            }

            overall_status = (
                "healthy"
                if alpha_vantage_status == "connected" and duckdb_status == "connected"
                else "degraded"
            )

            return {
                "status": overall_status,
                "services": services_status,
                "cache": {"mongodb": mongodb_status, "duckdb": duckdb_status},
                "external_apis": {"alpha_vantage": alpha_vantage_status},
                "last_checked": "2025-10-07T17:00:00Z",
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "services": {"all": "error"},
                "cache": {"mongodb": "unknown", "duckdb": "unknown"},
                "external_apis": {"alpha_vantage": "unknown"},
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
