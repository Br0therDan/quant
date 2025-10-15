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
from .trading.strategy_service import StrategyService
from .trading.backtest_service import BacktestService
from .backtest.orchestrator import BacktestOrchestrator
from .database_manager import DatabaseManager
from .user.watchlist_service import WatchlistService
from .trading.portfolio_service import PortfolioService
from .user.dashboard_service import DashboardService
from .ml_platform.ml_signal_service import MLSignalService
from .ml_platform.regime_detection_service import RegimeDetectionService
from .ml_platform.probabilistic_kpi_service import ProbabilisticKPIService
from .monitoring.data_quality_sentinel import DataQualitySentinel
from .llm.chatops_agent import ChatOpsAgent
from .ml.anomaly_detector import AnomalyDetectionService
from .trading.optimization_service import OptimizationService
from .gen_ai.narrative_report_service import NarrativeReportService
from .gen_ai.strategy_builder_service import StrategyBuilderService
from .gen_ai.chatops_advanced_service import ChatOpsAdvancedService
from .ml_platform.feature_store_service import FeatureStoreService
from .ml_platform.model_lifecycle_service import ModelLifecycleService
from .ml_platform.evaluation_harness_service import EvaluationHarnessService
from .llm.prompt_governance_service import PromptGovernanceService

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
    _backtest_orchestrator: Optional[BacktestOrchestrator] = None
    _database_manager: Optional[DatabaseManager] = None
    _watchlist_service: Optional[WatchlistService] = None
    _portfolio_service: Optional[PortfolioService] = None
    _dashboard_service: Optional[DashboardService] = None
    _ml_signal_service: Optional[MLSignalService] = None
    _regime_detection_service: Optional[RegimeDetectionService] = None
    _probabilistic_kpi_service: Optional[ProbabilisticKPIService] = None
    _data_quality_sentinel: Optional[DataQualitySentinel] = None
    _anomaly_detection_service: Optional[AnomalyDetectionService] = None
    _chatops_agent: Optional[ChatOpsAgent] = None
    _optimization_service: Optional[OptimizationService] = None
    _narrative_report_service: Optional[NarrativeReportService] = None
    _strategy_builder_service: Optional[StrategyBuilderService] = None
    _chatops_advanced_service: Optional[ChatOpsAdvancedService] = None
    _feature_store_service: Optional[FeatureStoreService] = None
    _model_lifecycle_service: Optional[ModelLifecycleService] = None
    _evaluation_harness_service: Optional[EvaluationHarnessService] = None
    _prompt_governance_service: Optional[PromptGovernanceService] = None

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
            data_quality_sentinel = self.get_data_quality_sentinel()
            self._market_data_service = MarketDataService(
                database_manager, data_quality_sentinel=data_quality_sentinel
            )
            logger.info("Created MarketDataService instance with DuckDB")
        return self._market_data_service

    def get_stock_service(self) -> StockService:
        """StockService 인스턴스 반환 (새로운 아키텍처)"""
        if self._stock_service is None:
            database_manager = self.get_database_manager()
            data_quality_sentinel = self.get_data_quality_sentinel()
            self._stock_service = StockService(
                database_manager=database_manager,
                data_quality_sentinel=data_quality_sentinel,
            )
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
        """BacktestService 인스턴스 반환 (Phase 2: CRUD only)"""
        if self._backtest_service is None:
            self._backtest_service = BacktestService()
            logger.info("Created BacktestService instance (CRUD only)")
        return self._backtest_service

    def get_backtest_orchestrator(self) -> BacktestOrchestrator:
        """BacktestOrchestrator 인스턴스 반환 (Phase 2: 실행 로직)"""
        if self._backtest_orchestrator is None:
            market_data_service = self.get_market_data_service()
            strategy_service = self.get_strategy_service()
            database_manager = self.get_database_manager()
            ml_signal_service = self.get_ml_signal_service()

            self._backtest_orchestrator = BacktestOrchestrator(
                market_data_service=market_data_service,
                strategy_service=strategy_service,
                database_manager=database_manager,
                ml_signal_service=ml_signal_service,
            )
            logger.info("Created BacktestOrchestrator instance (Phase 2)")
        return self._backtest_orchestrator

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
            probabilistic_service = self.get_probabilistic_kpi_service()
            self._portfolio_service = PortfolioService(
                database_manager, probabilistic_service=probabilistic_service
            )
            logger.info("Created PortfolioService instance")
        return self._portfolio_service

    def get_dashboard_service(self) -> DashboardService:
        """대시보드 서비스 인스턴스 반환"""
        if self._dashboard_service is None:
            database_manager = self.get_database_manager()
            portfolio_service = self.get_portfolio_service()
            strategy_service = self.get_strategy_service()
            backtest_service = self.get_backtest_service()  # CRUD 서비스만 사용
            market_data_service = self.get_market_data_service()
            watchlist_service = self.get_watchlist_service()
            ml_signal_service = self.get_ml_signal_service()
            regime_service = self.get_regime_detection_service()
            probabilistic_service = self.get_probabilistic_kpi_service()
            data_quality_sentinel = self.get_data_quality_sentinel()

            self._dashboard_service = DashboardService(
                database_manager=database_manager,
                portfolio_service=portfolio_service,
                strategy_service=strategy_service,
                backtest_service=backtest_service,
                market_data_service=market_data_service,
                watchlist_service=watchlist_service,
                ml_signal_service=ml_signal_service,
                regime_service=regime_service,
                probabilistic_service=probabilistic_service,
                data_quality_sentinel=data_quality_sentinel,
            )
            logger.info("Created DashboardService instance")
        return self._dashboard_service

    def get_anomaly_detection_service(self) -> AnomalyDetectionService:
        """AnomalyDetectionService 인스턴스 반환"""
        if self._anomaly_detection_service is None:
            self._anomaly_detection_service = AnomalyDetectionService()
            logger.info("Created AnomalyDetectionService instance")
        return self._anomaly_detection_service

    def get_data_quality_sentinel(self) -> DataQualitySentinel:
        """DataQualitySentinel 인스턴스 반환"""
        if self._data_quality_sentinel is None:
            anomaly_detector = self.get_anomaly_detection_service()
            self._data_quality_sentinel = DataQualitySentinel(anomaly_detector)
            logger.info("Created DataQualitySentinel instance")
        return self._data_quality_sentinel

    def get_ml_signal_service(self) -> MLSignalService:
        """MLSignalService 인스턴스 반환"""
        if self._ml_signal_service is None:
            database_manager = self.get_database_manager()
            self._ml_signal_service = MLSignalService(database_manager)
            logger.info("Created MLSignalService instance")
        return self._ml_signal_service

    def get_regime_detection_service(self) -> RegimeDetectionService:
        """RegimeDetectionService 인스턴스 반환"""
        if self._regime_detection_service is None:
            database_manager = self.get_database_manager()
            self._regime_detection_service = RegimeDetectionService(database_manager)
            logger.info("Created RegimeDetectionService instance")
        return self._regime_detection_service

    def get_probabilistic_kpi_service(self) -> ProbabilisticKPIService:
        """ProbabilisticKPIService 인스턴스 반환"""
        if self._probabilistic_kpi_service is None:
            database_manager = self.get_database_manager()
            self._probabilistic_kpi_service = ProbabilisticKPIService(database_manager)
            logger.info("Created ProbabilisticKPIService instance")
        return self._probabilistic_kpi_service

    def get_chatops_agent(self) -> ChatOpsAgent:
        """ChatOpsAgent 인스턴스 반환"""
        if self._chatops_agent is None:
            market_data_service = self.get_market_data_service()
            database_manager = self.get_database_manager()
            data_quality_sentinel = self.get_data_quality_sentinel()
            self._chatops_agent = ChatOpsAgent(
                market_data_service=market_data_service,
                database_manager=database_manager,
                data_quality_sentinel=data_quality_sentinel,
            )
            logger.info("Created ChatOpsAgent instance")
        return self._chatops_agent

    def get_optimization_service(self) -> OptimizationService:
        """최적화 서비스 (Phase 2 D1: Optuna 기반 하이퍼파라미터 최적화)"""
        if self._optimization_service is None:
            backtest_service = self.get_backtest_service()
            strategy_service = self.get_strategy_service()
            self._optimization_service = OptimizationService(
                backtest_service, strategy_service
            )
            logger.info("OptimizationService initialized (Phase 2 D1)")
        return self._optimization_service

    def get_narrative_report_service(self) -> NarrativeReportService:
        """내러티브 리포트 서비스 (Phase 3 D1: LLM 기반 리포트 생성)"""
        if self._narrative_report_service is None:
            # 필수: BacktestService
            backtest_service = self.get_backtest_service()

            # 선택: Phase 1 서비스 (있으면 주입, 없으면 None)
            ml_signal_service = self.get_ml_signal_service()
            regime_service = self.get_regime_detection_service()
            probabilistic_service = self.get_probabilistic_kpi_service()

            self._narrative_report_service = NarrativeReportService(
                backtest_service=backtest_service,
                ml_signal_service=ml_signal_service,
                regime_service=regime_service,
                probabilistic_service=probabilistic_service,
            )
            logger.info("NarrativeReportService initialized (Phase 3 D1)")
        return self._narrative_report_service

    def get_strategy_builder_service(self) -> StrategyBuilderService:
        """StrategyBuilderService 인스턴스 반환 (Phase 3 D2)"""
        if self._strategy_builder_service is None:
            strategy_service = self.get_strategy_service()
            self._strategy_builder_service = StrategyBuilderService(
                strategy_service=strategy_service
            )
            logger.info("StrategyBuilderService initialized (Phase 3 D2)")
        return self._strategy_builder_service

    def get_chatops_advanced_service(self) -> ChatOpsAdvancedService:
        """ChatOpsAdvancedService 인스턴스 반환 (Phase 3 D3)"""
        if self._chatops_advanced_service is None:
            backtest_service = self.get_backtest_service()
            self._chatops_advanced_service = ChatOpsAdvancedService(
                backtest_service=backtest_service
            )
            logger.info("ChatOpsAdvancedService initialized (Phase 3 D3)")
        return self._chatops_advanced_service

    def get_feature_store_service(self) -> FeatureStoreService:
        """FeatureStoreService 인스턴스 반환 (Phase 4 D1)"""
        if self._feature_store_service is None:
            self._feature_store_service = FeatureStoreService()
            logger.info("FeatureStoreService initialized (Phase 4 D1)")
        return self._feature_store_service

    def get_model_lifecycle_service(self) -> ModelLifecycleService:
        """ModelLifecycleService 인스턴스 반환 (Phase 4 D2)."""
        if self._model_lifecycle_service is None:
            self._model_lifecycle_service = ModelLifecycleService()
            logger.info("ModelLifecycleService initialized (Phase 4 D2)")
        return self._model_lifecycle_service

    def get_evaluation_harness_service(self) -> EvaluationHarnessService:
        """EvaluationHarnessService 인스턴스 반환 (Phase 4 D3)."""
        if self._evaluation_harness_service is None:
            self._evaluation_harness_service = EvaluationHarnessService()
            logger.info("EvaluationHarnessService initialized (Phase 4 D3)")
        return self._evaluation_harness_service

    def get_prompt_governance_service(self) -> PromptGovernanceService:
        """PromptGovernanceService 인스턴스 반환 (Phase 4 D4)."""
        if self._prompt_governance_service is None:
            self._prompt_governance_service = PromptGovernanceService()
            logger.info("PromptGovernanceService initialized (Phase 4 D4)")
        return self._prompt_governance_service

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
