"""
Intelligence Service Module
뉴스, 감정 분석 등 인텔리전스 데이터를 처리하는 통합 서비스

이 모듈은 Delegation 패턴을 사용하여 기능별 서브 모듈로 분산된
인텔리전스 서비스를 통합합니다:
- NewsService: 뉴스 수집 및 영향 분석
- SentimentService: 감정 분석 (뉴스 기반)
- AnalystService: 분석가 추천 및 내부자 거래
- IntelligenceCacheManager: DuckDB 캐싱
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from ..base_service import BaseMarketDataService
from .news import NewsService
from .sentiment import SentimentService
from .analyst import AnalystService
from .cache import IntelligenceCacheManager


logger = logging.getLogger(__name__)


class IntelligenceService(BaseMarketDataService):
    """인텔리전스 데이터 통합 서비스

    뉴스, 감정 분석, 분석가 추천 등의 정성적 데이터를 처리합니다.
    각 기능은 전문화된 서브 모듈로 위임(delegation)됩니다.
    """

    def __init__(self, database_manager=None):
        """IntelligenceService 초기화

        Args:
            database_manager: 데이터베이스 매니저 (DuckDB)
        """
        super().__init__(database_manager)

        # 전문화된 서브 모듈 인스턴스 생성 (의존성 주입)
        self._news = NewsService(database_manager)
        self._sentiment = SentimentService(database_manager)
        self._analyst = AnalystService(database_manager)
        self._cache = IntelligenceCacheManager(database_manager)

        logger.info("IntelligenceService initialized with modular architecture")

    # ==================== 뉴스 메서드 위임 ====================

    async def get_news(
        self,
        symbol: Optional[str] = None,
        topics: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """뉴스 데이터 조회 (캐시 우선, Alpha Vantage fallback)

        Args:
            symbol: 특정 종목 (None이면 전체 시장)
            topics: 토픽 필터
            start_date: 시작 날짜
            end_date: 종료 날짜
            limit: 최대 결과 수

        Returns:
            뉴스 데이터 리스트
        """
        return await self._news.get_news(symbol, topics, start_date, end_date, limit)

    async def get_market_buzz(
        self, timeframe: str = "1day", limit: int = 10
    ) -> List[Dict[str, Any]]:
        """시장 화제 종목 조회 (상승/하락률 기반)

        Args:
            timeframe: 분석 기간
            limit: 최대 결과 수

        Returns:
            화제 종목 리스트
        """
        return await self._news.get_market_buzz(timeframe, limit)

    async def analyze_news_impact(
        self, symbol: str, news_url: str = ""
    ) -> Dict[str, Any]:
        """뉴스가 주가에 미친 영향 분석 (최근 뉴스 기반)

        Args:
            symbol: 주식 심볼
            news_url: 뉴스 URL (선택사항)

        Returns:
            영향 분석 결과
        """
        return await self._news.analyze_news_impact(symbol, news_url)

    # ==================== 감정 분석 메서드 위임 ====================

    async def get_sentiment_analysis(
        self, symbol: str, timeframe: str = "1day"
    ) -> Optional[Dict[str, Any]]:
        """감정 분석 데이터 조회 (캐시 우선, Alpha Vantage fallback)

        Args:
            symbol: 주식 심볼
            timeframe: 분석 기간

        Returns:
            감정 분석 결과
        """
        return await self._sentiment.get_sentiment_analysis(symbol, timeframe)

    async def get_social_sentiment(
        self, symbol: str, platforms: List[str] = ["twitter", "reddit", "stocktwits"]
    ) -> Optional[Dict[str, Any]]:
        """소셜 미디어 감정 분석 (뉴스 기반 감정 분석으로 대체)

        Args:
            symbol: 주식 심볼
            platforms: 분석할 플랫폼 리스트 (현재는 뉴스 기반)

        Returns:
            소셜 감정 분석 결과
        """
        return await self._sentiment.get_social_sentiment(symbol, platforms)

    async def get_consumer_sentiment(
        self, timeframe: str = "1month"
    ) -> Optional[Dict[str, Any]]:
        """소비자 심리 지수 조회 (뉴스 감정 분석 기반)

        Args:
            timeframe: 분석 기간 (1day, 1week, 1month, 3month)

        Returns:
            소비자 심리 분석 결과
        """
        return await self._sentiment.get_consumer_sentiment(timeframe)

    # ==================== 분석가 메서드 위임 ====================

    async def get_analyst_recommendations(self, symbol: str) -> List[Dict[str, Any]]:
        """분석가 추천 의견 조회 (내부자 거래 정보 포함)

        Args:
            symbol: 주식 심볼

        Returns:
            분석가 추천 및 내부자 거래 리스트
        """
        return await self._analyst.get_analyst_recommendations(symbol)

    # ==================== 캐시 메서드 위임 (BaseMarketDataService 추상 메서드 구현) ====================

    async def _fetch_from_source(self, **kwargs) -> Any:
        """AlphaVantage에서 인텔리전스 데이터 가져오기

        BaseMarketDataService 추상 메서드 구현을 IntelligenceCacheManager로 위임합니다.

        Args:
            **kwargs: API 메서드 및 파라미터

        Returns:
            Alpha Vantage API 응답 데이터
        """
        return await self._cache._fetch_from_source(**kwargs)

    async def _save_to_cache(self, data: Any, **kwargs) -> bool:
        """인텔리전스 데이터를 캐시에 저장

        BaseMarketDataService 추상 메서드 구현을 IntelligenceCacheManager로 위임합니다.

        Args:
            data: 저장할 데이터
            **kwargs: 캐시 옵션

        Returns:
            저장 성공 여부
        """
        return await self._cache._save_to_cache(data, **kwargs)

    async def _get_from_cache(self, **kwargs) -> Optional[List[Any]]:
        """캐시에서 인텔리전스 데이터 조회

        BaseMarketDataService 추상 메서드 구현을 IntelligenceCacheManager로 위임합니다.

        Args:
            **kwargs: 조회 옵션

        Returns:
            캐시된 데이터 리스트 또는 None
        """
        return await self._cache._get_from_cache(**kwargs)

    async def refresh_data_from_source(self, **kwargs) -> List[Dict[str, Any]]:
        """베이스 클래스의 추상 메서드 구현 (deprecated)

        이 메서드는 더 이상 직접 사용되지 않으므로 빈 구현을 제공합니다.

        Returns:
            빈 리스트
        """
        logger.warning(
            "refresh_data_from_source is deprecated - use specific service methods"
        )
        return []
