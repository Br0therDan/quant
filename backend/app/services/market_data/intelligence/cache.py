"""
Intelligence Service - Cache Module
DuckDB 캐시 레이어 (BaseMarketDataService 추상 메서드 구현)
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, UTC
import logging

from .base import BaseIntelligenceService


logger = logging.getLogger(__name__)


class IntelligenceCacheManager(BaseIntelligenceService):
    """인텔리전스 데이터 DuckDB 캐싱

    BaseMarketDataService의 추상 메서드를 구현하여
    뉴스 및 감정 분석 데이터를 DuckDB에 캐싱합니다.
    """

    async def _fetch_from_source(self, **kwargs) -> Any:
        """AlphaVantage에서 인텔리전스 데이터 가져오기

        Args:
            **kwargs: API 메서드 및 파라미터
                - method: 'news_sentiment', 'insider_transactions', 'top_gainers_losers'
                - symbol: 주식 심볼 (insider_transactions에 필요)
                - 기타 API 파라미터

        Returns:
            Alpha Vantage API 응답 데이터
        """
        method = kwargs.get("method", "news_sentiment")
        symbol = kwargs.get("symbol")

        if method == "news_sentiment":
            return await self.alpha_vantage.intelligence.news_sentiment(
                tickers=symbol,
                **{k: v for k, v in kwargs.items() if k not in ["method", "symbol"]},
            )
        elif method == "insider_transactions" and symbol:
            return await self.alpha_vantage.intelligence.insider_transactions(
                symbol=str(symbol)
            )
        elif method == "top_gainers_losers":
            return await self.alpha_vantage.intelligence.top_gainers_losers()
        else:
            raise ValueError(f"Unknown intelligence method: {method}")

    async def _save_to_cache(self, data: Any, **kwargs) -> bool:
        """인텔리전스 데이터를 캐시에 저장

        데이터를 NewsArticle 모델로 변환한 후
        DuckDB news_cache 테이블에 저장합니다.

        Args:
            data: 저장할 데이터 (Dict 또는 List)
            **kwargs: 캐시 옵션
                - cache_key: 캐시 키
                - symbol: 주식 심볼

        Returns:
            저장 성공 여부
        """
        try:
            cache_key = kwargs.get("cache_key", "intelligence_data")

            # 데이터를 NewsArticle 모델로 변환
            if isinstance(data, dict):
                data = [data]  # 단일 데이터를 리스트로 변환

            if isinstance(data, list) and data:
                # 데이터를 NewsArticle 객체로 변환
                news_articles = []
                for item in data:
                    if isinstance(item, dict):
                        # NewsArticle 모델에 맞는 필드로 매핑
                        article_data = {
                            "symbol": item.get(
                                "symbol", kwargs.get("symbol", "UNKNOWN")
                            ),
                            "title": item.get(
                                "title", item.get("overall_sentiment_label", "News")
                            ),
                            "url": item.get("url", item.get("link", "")),
                            "time_published": datetime.now(
                                UTC
                            ),  # NewsArticle 모델 필드명에 맞춤
                            "news_source": item.get(
                                "source", "Alpha Vantage Intelligence"
                            ),
                            "source_domain": item.get("source_domain", ""),
                            "summary": item.get(
                                "summary", str(item)[:500]
                            ),  # 요약 또는 전체 데이터 일부
                            "banner_image": item.get("banner_image"),
                            "overall_sentiment_score": item.get(
                                "overall_sentiment_score", 0.0
                            ),
                            "overall_sentiment_label": item.get(
                                "overall_sentiment_label", "Neutral"
                            ),
                            "relevance_score": item.get("relevance_score", 0.0),
                            # topics를 문자열 배열로 변환
                            "topics": [
                                (
                                    topic.get("topic", str(topic))
                                    if isinstance(topic, dict)
                                    else str(topic)
                                )
                                for topic in item.get("topics", [])
                            ],
                        }
                        try:
                            from app.models.market_data.intelligence import NewsArticle

                            article = NewsArticle(**article_data)
                            news_articles.append(article)
                        except Exception as model_error:
                            logger.warning(
                                f"Failed to create NewsArticle model: {model_error}"
                            )
                            continue

                if news_articles:
                    # DuckDB 뉴스 캐시에 직접 저장
                    try:
                        success = await self._save_news_to_duckdb(
                            news_articles, cache_key
                        )
                        if success:
                            logger.info(
                                f"Intelligence data cached successfully: {cache_key} ({len(news_articles)} items)"
                            )
                        return success
                    except Exception as save_error:
                        logger.error(f"Failed to save news to DuckDB: {save_error}")
                        return False

            logger.info(f"No valid intelligence data to cache for: {cache_key}")
            return True

        except Exception as e:
            logger.error(f"Error saving intelligence data to cache: {e}")
            return False

    async def _get_from_cache(self, **kwargs) -> Optional[List[Any]]:
        """캐시에서 인텔리전스 데이터 조회

        DuckDB news_cache 테이블에서 데이터를 조회합니다.

        Args:
            **kwargs: 조회 옵션
                - cache_key: 캐시 키
                - start_date: 시작 날짜
                - end_date: 종료 날짜
                - ignore_ttl: TTL 무시 여부

        Returns:
            캐시된 데이터 리스트 또는 None
        """
        try:
            cache_key = kwargs.get("cache_key", "intelligence_data")

            # DuckDB 캐시에서 데이터 조회
            cached_data = await self._get_from_duckdb_cache(
                cache_key=cache_key,
                start_date=kwargs.get("start_date"),
                end_date=kwargs.get("end_date"),
                ignore_ttl=kwargs.get("ignore_ttl", False),
            )

            if cached_data:
                logger.info(
                    f"Intelligence cache hit: {cache_key} ({len(cached_data)} items)"
                )
                return cached_data
            else:
                logger.debug(f"Intelligence cache miss: {cache_key}")
                return None

        except Exception as e:
            logger.error(f"Error getting intelligence data from cache: {e}")
            return None

    async def _save_news_to_duckdb(self, news_articles: List, cache_key: str) -> bool:
        """뉴스 데이터를 DuckDB news_cache 테이블에 저장

        Args:
            news_articles: NewsArticle 객체 리스트
            cache_key: 캐시 키

        Returns:
            저장 성공 여부
        """
        try:
            if not self._db_manager or not news_articles:
                logger.warning("No database manager or no news articles to save")
                return True

            # DuckDB 연결
            self._db_manager.connect()
            conn = self._db_manager.connection

            if not conn:
                logger.error("DuckDB connection failed")
                return False

            logger.info(
                f"Attempting to save {len(news_articles)} news articles to DuckDB"
            )

            # 뉴스 데이터 저장
            saved_count = 0
            for article in news_articles:
                try:
                    # NewsArticle 모델에서 필드 추출
                    if hasattr(article, "model_dump"):
                        data = article.model_dump()
                    elif hasattr(article, "dict"):
                        data = article.dict()
                    else:
                        logger.warning(
                            f"Article has no model_dump or dict method: {type(article)}"
                        )
                        continue

                    logger.debug(
                        f"Saving article: {data.get('title', 'Unknown')[:50]}..."
                    )

                    conn.execute(
                        """
                        INSERT OR REPLACE INTO news_cache (
                            symbol, title, url, time_published, authors, summary,
                            banner_image, source, category_within_source, source_domain,
                            topics, overall_sentiment_score, overall_sentiment_label,
                            ticker_sentiment, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        [
                            data.get("symbol", "UNKNOWN"),
                            data.get("title", ""),
                            data.get("url", ""),
                            data.get("time_published", ""),
                            data.get("authors", []),
                            data.get("summary", ""),
                            data.get("banner_image", ""),
                            data.get("news_source", data.get("source", "")),
                            data.get("category_within_source", ""),
                            data.get("source_domain", ""),
                            data.get("topics", []),
                            float(data.get("overall_sentiment_score", 0.0)),
                            data.get("overall_sentiment_label", "Neutral"),
                            str(data.get("ticker_sentiment", {})),
                            datetime.now(UTC).isoformat(),
                        ],
                    )
                    saved_count += 1
                except Exception as insert_error:
                    logger.error(f"Failed to insert news article: {insert_error}")
                    logger.error(
                        f"Article data: {data if 'data' in locals() else 'No data'}"
                    )
                    continue

            if saved_count > 0:
                logger.info(
                    f"Successfully saved {saved_count}/{len(news_articles)} news articles to DuckDB cache"
                )
            else:
                logger.warning("No articles were saved to DuckDB cache")

            return saved_count > 0

        except Exception as e:
            logger.error(f"Error saving news to DuckDB: {e}")
            logger.error(f"Exception details: {type(e).__name__}: {str(e)}")
            return False

    async def refresh_data_from_source(self, **kwargs) -> List[Dict[str, Any]]:
        """BaseMarketDataService 추상 메서드 구현 (deprecated)"""
        logger.warning(
            "refresh_data_from_source is deprecated for IntelligenceCacheManager"
        )
        return []
