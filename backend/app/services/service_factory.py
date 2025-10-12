"""
통합 서비스 팩토리 - 서비스 간 의존성 관리
"""

import logging
from typing import Optional

from .market_data_service import MarketDataService
from .market_data_service.stock import StockService
from .market_data_service.fundamental import FundamentalService
from .market_data_service.economic_indicator import EconomicIndicatorService
from .market_data_service.intelligence import IntelligenceService
from .market_data_service.technical_indicator import TechnicalIndicatorService
from .strategy_service import StrategyService
from .backtest_service import BacktestService
from .database_manager import DatabaseManager
from .watchlist_service import WatchlistService
from .portfolio_service import PortfolioService
from .dashboard_service import DashboardService

logger = logging.getLogger(__name__)


class ServiceFactory:
    """서비스 팩토리 - 서비스 간 의존성 주입 관리"""

    _instance = None
    _market_data_service: Optional[MarketDataService] = None
    _stock_service: Optional[StockService] = None
    _fundamental_service: Optional[FundamentalService] = None
    _economic_indicator_service: Optional[EconomicIndicatorService] = None
    _intelligence_service: Optional[IntelligenceService] = None
    _technical_indicator_service: Optional[TechnicalIndicatorService] = None
    _strategy_service: Optional[StrategyService] = None
    _backtest_service: Optional[BacktestService] = None
    _database_manager: Optional[DatabaseManager] = None
    _watchlist_service: Optional[WatchlistService] = None
    _portfolio_service: Optional[PortfolioService] = None
    _dashboard_service: Optional[DashboardService] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_database_manager(self) -> DatabaseManager:
        """DatabaseManager 인스턴스 반환 (DuckDB 캐시)"""
        if self._database_manager is None:
            self._database_manager = DatabaseManager()
            # 연결은 lazy loading으로 처리하여 동시성 문제 방지
            logger.info(
                "Created DatabaseManager instance (connection will be lazy-loaded)"
            )
        return self._database_manager

    def get_market_data_service(self) -> MarketDataService:
        """MarketDataService 인스턴스 반환 (DuckDB 연동)"""
        if self._market_data_service is None:
            database_manager = self.get_database_manager()
            self._market_data_service = MarketDataService(database_manager)
            logger.info("Created MarketDataService instance with DuckDB")
        return self._market_data_service

    def get_stock_service(self) -> StockService:
        """StockService 인스턴스 반환 (새로운 아키텍처)"""
        if self._stock_service is None:
            self._stock_service = StockService()
            logger.info("Created StockService instance")
        return self._stock_service

    def get_fundamental_service(self) -> FundamentalService:
        """FundamentalService 인스턴스 반환"""
        if self._fundamental_service is None:
            self._fundamental_service = FundamentalService()
            logger.info("Created FundamentalService instance")
        return self._fundamental_service

    def get_economic_indicator_service(self) -> EconomicIndicatorService:
        """EconomicIndicatorService 인스턴스 반환"""
        if self._economic_indicator_service is None:
            self._economic_indicator_service = EconomicIndicatorService()
            logger.info("Created EconomicIndicatorService instance")
        return self._economic_indicator_service

    def get_intelligence_service(self) -> IntelligenceService:
        """IntelligenceService 인스턴스 반환"""
        if self._intelligence_service is None:
            self._intelligence_service = IntelligenceService()
            logger.info("Created IntelligenceService instance")
        return self._intelligence_service

    def get_technical_indicator_service(self) -> TechnicalIndicatorService:
        """TechnicalIndicatorService 인스턴스 반환 (DuckDB 연동)"""
        if self._technical_indicator_service is None:
            database_manager = self.get_database_manager()
            self._technical_indicator_service = TechnicalIndicatorService(
                database_manager
            )
            logger.info("Created TechnicalIndicatorService instance with DuckDB")
        return self._technical_indicator_service

    def get_strategy_service(self) -> StrategyService:
        """StrategyService 인스턴스 반환"""
        if self._strategy_service is None:
            self._strategy_service = StrategyService()
            logger.info("Created StrategyService instance")
        return self._strategy_service

    def get_backtest_service(self) -> BacktestService:
        """BacktestService 인스턴스 반환 (DuckDB 연동 의존성 주입)"""
        if self._backtest_service is None:
            market_data_service = self.get_market_data_service()
            strategy_service = self.get_strategy_service()
            database_manager = self.get_database_manager()

            self._backtest_service = BacktestService(
                market_data_service=market_data_service,
                strategy_service=strategy_service,
                database_manager=database_manager,
            )
            logger.info("Created BacktestService instance with DuckDB integration")
        return self._backtest_service

    def get_watchlist_service(self) -> WatchlistService:
        """WatchlistService 인스턴스 반환"""
        if self._watchlist_service is None:
            self._watchlist_service = WatchlistService()
            logger.info("Created WatchlistService instance")
        return self._watchlist_service

    def get_portfolio_service(self) -> PortfolioService:
        """포트폴리오 서비스 인스턴스 반환"""
        if self._portfolio_service is None:
            database_manager = self.get_database_manager()
            self._portfolio_service = PortfolioService(database_manager)
            logger.info("Created PortfolioService instance")
        return self._portfolio_service

    def get_dashboard_service(self) -> DashboardService:
        """대시보드 서비스 인스턴스 반환"""
        if self._dashboard_service is None:
            database_manager = self.get_database_manager()
            portfolio_service = self.get_portfolio_service()
            strategy_service = self.get_strategy_service()
            backtest_service = self.get_backtest_service()
            market_data_service = self.get_market_data_service()
            watchlist_service = self.get_watchlist_service()

            self._dashboard_service = DashboardService(
                database_manager=database_manager,
                portfolio_service=portfolio_service,
                strategy_service=strategy_service,
                backtest_service=backtest_service,
                market_data_service=market_data_service,
                watchlist_service=watchlist_service,
            )
            logger.info("Created DashboardService instance")
        return self._dashboard_service

    async def cleanup(self):
        """모든 서비스 정리"""
        if self._market_data_service:
            await self._market_data_service.close()

        if self._stock_service:
            # StockService cleanup if needed
            pass

        if self._database_manager:
            self._database_manager.close()
            self._database_manager = None

        # 다른 서비스들도 필요시 정리
        logger.info("Services cleaned up")


# 전역 팩토리 인스턴스
service_factory = ServiceFactory()
