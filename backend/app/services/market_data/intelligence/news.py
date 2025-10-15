"""
Intelligence Service - News Module
뉴스 데이터 수집 및 분석
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, UTC
import logging

from .base import BaseIntelligenceService


logger = logging.getLogger(__name__)


class NewsService(BaseIntelligenceService):
    """뉴스 데이터 수집 및 분석 서비스

    Alpha Vantage NEWS_SENTIMENT API를 사용하여 뉴스 데이터를 수집하고,
    뉴스가 주가에 미치는 영향을 분석합니다.
    """

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
        logger.info(f"Getting news for symbol={symbol}, topics={topics}")

        try:
            from app.models.market_data.intelligence import NewsArticle

            # 캐시 키 생성
            cache_key = (
                f"news_{symbol or 'market'}_{','.join(topics) if topics else 'all'}"
            )

            # refresh_callback 함수 정의
            async def refresh_news_data(
                symbol=symbol,
                topics=topics,
                start_date=start_date,
                end_date=end_date,
                limit=limit,
            ):
                news_data = await self._fetch_news_from_alpha_vantage(
                    symbol=symbol,
                    topics=topics,
                    start_date=start_date,
                    end_date=end_date,
                    limit=limit,
                )
                return news_data if isinstance(news_data, list) else []

            # 캐시 우선 조회 패턴 적용 (통합 캐시 사용)
            data = await self.get_data_with_unified_cache(
                cache_key=cache_key,
                data_type="news",
                model_class=NewsArticle,
                refresh_callback=refresh_news_data,
                symbol=symbol,
                ttl_hours=4,  # 뉴스는 4시간 TTL
                topics=topics,
                start_date=start_date,
                end_date=end_date,
                limit=limit,
            )

            # 데이터를 Dict 형태로 변환하여 반환 (기존 API와 호환)
            if isinstance(data, list):
                result = []
                for item in data[:limit]:
                    if hasattr(item, "model_dump"):
                        result.append(item.model_dump())
                    elif isinstance(item, dict):
                        result.append(item)
                return result
            else:
                logger.warning(f"Unexpected data type for {symbol}")
                return []

        except Exception as e:
            logger.error(f"Error getting news for {symbol}: {e}")
            return []

    async def _fetch_news_from_alpha_vantage(
        self,
        symbol: Optional[str] = None,
        topics: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50,
    ) -> List:
        """Alpha Vantage에서 뉴스 데이터를 가져와서 NewsArticle 객체 리스트로 변환

        Args:
            symbol: 주식 심볼
            topics: 토픽 리스트
            start_date: 시작 날짜
            end_date: 종료 날짜
            limit: 최대 결과 수

        Returns:
            NewsArticle 객체 리스트
        """
        try:
            from app.models.market_data.intelligence import NewsArticle

            # Alpha Vantage NEWS_SENTIMENT API 호출
            tickers = symbol if symbol else None
            topics_str = ",".join(topics) if topics else None
            time_from = start_date.strftime("%Y%m%dT%H%M") if start_date else None
            time_to = end_date.strftime("%Y%m%dT%H%M") if end_date else None

            response = await self.alpha_vantage.intelligence.news_sentiment(
                tickers=tickers,
                topics=topics_str,
                time_from=time_from,
                time_to=time_to,
                sort="LATEST",
                limit=min(limit, 1000),  # Alpha Vantage 최대값 적용
            )

            news_articles = []
            if isinstance(response, dict) and "feed" in response:
                for item in response["feed"][:limit]:
                    try:
                        # topics 필드 변환 (객체 배열을 문자열 배열로)
                        topics_list = []
                        if item.get("topics"):
                            for topic_item in item["topics"]:
                                if (
                                    isinstance(topic_item, dict)
                                    and "topic" in topic_item
                                ):
                                    topics_list.append(topic_item["topic"])
                                elif isinstance(topic_item, str):
                                    topics_list.append(topic_item)

                        # time_published 파싱
                        time_published_str = item.get("time_published", "")
                        if time_published_str:
                            try:
                                # Alpha Vantage 시간 형식: "20231208T120000"
                                time_published = datetime.strptime(
                                    time_published_str, "%Y%m%dT%H%M%S"
                                )
                                time_published = time_published.replace(tzinfo=UTC)
                            except ValueError:
                                logger.warning(
                                    f"Invalid time format: {time_published_str}"
                                )
                                time_published = datetime.now(UTC)
                        else:
                            time_published = datetime.now(UTC)

                        # NewsArticle 객체 생성 (data_quality_score 자동 계산됨)
                        news_article = NewsArticle(
                            symbol=symbol or "MARKET",
                            title=item.get("title", ""),
                            url=item.get("url", ""),
                            time_published=time_published,
                            news_source=item.get("source", ""),
                            source_domain=item.get("source_domain", ""),
                            authors=item.get("authors", []),
                            summary=item.get("summary", ""),
                            banner_image=item.get("banner_image"),
                            overall_sentiment_score=self._safe_decimal(
                                item.get("overall_sentiment_score")
                            ),
                            overall_sentiment_label=item.get("overall_sentiment_label"),
                            relevance_score=self._safe_decimal(
                                item.get("relevance_score")
                            ),
                            topics=topics_list,
                            category_within_source=item.get("category_within_source"),
                            data_quality_score=85.0,  # Default value for data quality score
                        )

                        news_articles.append(news_article)

                    except Exception as item_error:
                        logger.warning(
                            f"Failed to create NewsArticle from item: {item_error}"
                        )
                        logger.warning(f"Item data: {item}")
                        import traceback

                        logger.warning(f"Full traceback: {traceback.format_exc()}")
                        continue

            logger.info(
                f"Retrieved {len(news_articles)} news articles from Alpha Vantage for {symbol}"
            )
            return news_articles

        except Exception as e:
            logger.error(f"Failed to fetch news from Alpha Vantage for {symbol}: {e}")
            return []

    async def get_market_buzz(
        self, timeframe: str = "1day", limit: int = 10
    ) -> List[Dict[str, Any]]:
        """시장 화제 종목 조회 (상승/하락률 기반)

        Alpha Vantage TOP_GAINERS_LOSERS API를 사용하여
        상위 상승/하락 종목을 조회합니다.

        Args:
            timeframe: 분석 기간
            limit: 최대 결과 수

        Returns:
            화제 종목 리스트
        """
        logger.info(f"Getting market buzz for {timeframe}")

        try:
            # Alpha Vantage TOP_GAINERS_LOSERS API 호출
            response = await self.alpha_vantage.intelligence.top_gainers_losers()

            if not isinstance(response, dict):
                return []

            buzz_stocks = []

            # 상위 상승 종목 (버즈 점수 높음)
            top_gainers = response.get("top_gainers", [])[: limit // 2]
            for stock in top_gainers:
                buzz_item = {
                    "symbol": stock.get("ticker", ""),
                    "company_name": stock.get("ticker", ""),  # API에서 회사명 미제공
                    "buzz_type": "top_gainer",
                    "price": float(stock.get("price", 0)),
                    "change_amount": float(stock.get("change_amount", 0)),
                    "change_percentage": float(
                        stock.get("change_percentage", "0%").replace("%", "")
                    ),
                    "volume": int(stock.get("volume", 0)),
                    "buzz_score": min(
                        abs(
                            float(stock.get("change_percentage", "0%").replace("%", ""))
                        )
                        * 10,
                        100,
                    ),
                    "buzz_reason": f"Major price increase: {stock.get('change_percentage', '0%')}",
                    "sentiment": "bullish",
                    "last_updated": datetime.now().isoformat(),
                }
                buzz_stocks.append(buzz_item)

            # 상위 하락 종목 (버즈 점수 높음)
            top_losers = response.get("top_losers", [])[: limit // 2]
            for stock in top_losers:
                buzz_item = {
                    "symbol": stock.get("ticker", ""),
                    "company_name": stock.get("ticker", ""),
                    "buzz_type": "top_loser",
                    "price": float(stock.get("price", 0)),
                    "change_amount": float(stock.get("change_amount", 0)),
                    "change_percentage": float(
                        stock.get("change_percentage", "0%").replace("%", "")
                    ),
                    "volume": int(stock.get("volume", 0)),
                    "buzz_score": min(
                        abs(
                            float(stock.get("change_percentage", "0%").replace("%", ""))
                        )
                        * 10,
                        100,
                    ),
                    "buzz_reason": f"Major price decline: {stock.get('change_percentage', '0%')}",
                    "sentiment": "bearish",
                    "last_updated": datetime.now().isoformat(),
                }
                buzz_stocks.append(buzz_item)

            # 버즈 점수로 정렬
            buzz_stocks.sort(key=lambda x: x["buzz_score"], reverse=True)

            logger.info(
                f"Retrieved {len(buzz_stocks)} buzz stocks for timeframe {timeframe}"
            )
            return buzz_stocks[:limit]

        except Exception as e:
            logger.error(f"Error getting market buzz: {e}")
            return []

    async def analyze_news_impact(
        self, symbol: str, news_url: str = ""
    ) -> Dict[str, Any]:
        """뉴스가 주가에 미친 영향 분석 (최근 뉴스 기반)

        최근 3일간의 뉴스를 분석하여 영향도를 계산합니다.

        Args:
            symbol: 주식 심볼
            news_url: 뉴스 URL (선택사항)

        Returns:
            영향 분석 결과
        """
        logger.info(f"Analyzing news impact for {symbol}")

        try:
            # 최근 3일간의 뉴스를 분석하여 영향도 계산
            end_date = datetime.now()
            start_date = end_date - timedelta(days=3)

            response = await self.alpha_vantage.intelligence.news_sentiment(
                tickers=symbol,
                time_from=start_date.strftime("%Y%m%dT%H%M"),
                time_to=end_date.strftime("%Y%m%dT%H%M"),
                sort="LATEST",
                limit=50,
            )

            if not isinstance(response, dict) or "feed" not in response:
                return {}

            articles = response["feed"]
            if not articles:
                return {}

            # 뉴스 영향도 분석
            total_articles = len(articles)
            high_impact_count = 0
            sentiment_scores = []
            relevance_scores = []

            for article in articles:
                sentiment_score = article.get("overall_sentiment_score", 0)
                relevance_score = article.get("relevance_score", 0)

                if sentiment_score:
                    sentiment_scores.append(abs(float(sentiment_score)))
                if relevance_score:
                    relevance_scores.append(float(relevance_score))

                # 높은 영향도 뉴스 판정 (높은 감정 점수 + 높은 관련성)
                if (
                    abs(float(sentiment_score or 0)) > 0.2
                    and float(relevance_score or 0) > 0.5
                ):
                    high_impact_count += 1

            # 평균 점수 계산
            avg_sentiment_impact = (
                sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
            )
            avg_relevance = (
                sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0
            )

            # 전체 영향도 점수 계산 (0-100)
            impact_score = min(
                (avg_sentiment_impact * avg_relevance * total_articles) * 100, 100
            )

            # 영향도 레벨 결정
            if impact_score > 70:
                impact_level = "High"
            elif impact_score > 40:
                impact_level = "Medium"
            elif impact_score > 15:
                impact_level = "Low"
            else:
                impact_level = "Minimal"

            result = {
                "symbol": symbol,
                "analysis_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                },
                "news_metrics": {
                    "total_articles": total_articles,
                    "high_impact_articles": high_impact_count,
                    "avg_sentiment_impact": round(avg_sentiment_impact, 4),
                    "avg_relevance_score": round(avg_relevance, 4),
                },
                "impact_analysis": {
                    "overall_impact_score": round(impact_score, 2),
                    "impact_level": impact_level,
                    "sentiment_direction": (
                        "positive"
                        if sum(
                            [
                                float(a.get("overall_sentiment_score", 0))
                                for a in articles
                            ]
                        )
                        > 0
                        else "negative"
                    ),
                    "confidence_level": min(
                        total_articles / 20, 1.0
                    ),  # 신뢰도 (뉴스 개수 기반)
                },
                "recommendations": {
                    "monitor_closely": impact_level in ["High", "Medium"],
                    "sentiment_trend": (
                        "bullish" if avg_sentiment_impact > 0 else "bearish"
                    ),
                    "news_coverage": "high" if total_articles > 10 else "low",
                },
                "last_updated": datetime.now().isoformat(),
            }

            logger.info(
                f"News impact analysis completed for {symbol}: {impact_level} impact ({impact_score:.2f})"
            )
            return result

        except Exception as e:
            logger.error(f"Error analyzing news impact for {symbol}: {e}")
            return {}

    async def refresh_data_from_source(self, **kwargs) -> List[Dict[str, Any]]:
        """BaseMarketDataService 추상 메서드 구현 (deprecated)"""
        logger.warning("refresh_data_from_source is deprecated for NewsService")
        return []
