"""
Intelligence Service - Sentiment Analysis Module
감정 분석 서비스 (뉴스 기반 감정 집계)
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from .base import BaseIntelligenceService


logger = logging.getLogger(__name__)


class SentimentService(BaseIntelligenceService):
    """감정 분석 서비스

    뉴스 데이터를 기반으로 감정 점수를 집계하여
    종목별, 시장 전체, 소비자 심리 등을 분석합니다.
    """

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
        logger.info(f"Getting sentiment analysis for {symbol} ({timeframe})")

        try:
            from app.models.market_data.intelligence import SentimentAnalysis

            # 캐시 키 생성
            cache_key = f"sentiment_{symbol}_{timeframe}"

            # refresh_callback 함수 정의
            async def refresh_sentiment_data():
                return await self._fetch_sentiment_from_alpha_vantage(symbol, timeframe)

            # 캐시 우선 조회 패턴 적용 (통합 캐시 사용)
            data = await self.get_data_with_unified_cache(
                cache_key=cache_key,
                data_type="sentiment",
                model_class=SentimentAnalysis,
                refresh_callback=refresh_sentiment_data,
                symbol=symbol,
                ttl_hours=6,  # 감정 분석은 6시간 TTL
            )

            # 첫 번째 결과를 Dict 형태로 반환 (기존 API와 호환)
            if isinstance(data, list) and data:
                result = data[0]
                if hasattr(result, "model_dump"):
                    return result.model_dump()
                elif isinstance(result, dict):
                    return result

            return None

        except Exception as e:
            logger.error(f"Error getting sentiment analysis for {symbol}: {e}")
            return None

    async def _fetch_sentiment_from_alpha_vantage(
        self, symbol: str, timeframe: str = "1day"
    ) -> List:
        """Alpha Vantage에서 감정 분석 데이터를 가져와서 SentimentAnalysis 객체로 변환

        뉴스 감정 점수를 집계하여 SentimentAnalysis 모델을 생성합니다.

        Args:
            symbol: 주식 심볼
            timeframe: 분석 기간 (1day, 1week, 1month)

        Returns:
            SentimentAnalysis 객체 리스트 (단일 요소)
        """
        try:
            from app.models.market_data.intelligence import SentimentAnalysis

            # 시간 범위에 따른 기간 계산
            end_date = datetime.now()
            if timeframe == "1day":
                start_date = end_date - timedelta(days=1)
            elif timeframe == "1week":
                start_date = end_date - timedelta(days=7)
            elif timeframe == "1month":
                start_date = end_date - timedelta(days=30)
            else:
                start_date = end_date - timedelta(days=1)

            # Alpha Vantage NEWS_SENTIMENT API 호출
            response = await self.alpha_vantage.intelligence.news_sentiment(
                tickers=symbol,
                time_from=start_date.strftime("%Y%m%dT%H%M"),
                time_to=end_date.strftime("%Y%m%dT%H%M"),
                sort="LATEST",
                limit=200,  # 충분한 데이터로 감정 분석
            )

            if not isinstance(response, dict) or "feed" not in response:
                return []

            # 감정 점수 집계
            total_articles = len(response["feed"])
            if total_articles == 0:
                return []

            sentiment_scores = []
            positive_count = 0
            negative_count = 0
            neutral_count = 0

            for article in response["feed"]:
                sentiment_label = article.get("overall_sentiment_label", "Neutral")
                sentiment_score = article.get("overall_sentiment_score", 0)

                if sentiment_score:
                    sentiment_scores.append(float(sentiment_score))

                if (
                    sentiment_label == "Bullish"
                    or sentiment_label == "Somewhat-Bullish"
                ):
                    positive_count += 1
                elif (
                    sentiment_label == "Bearish"
                    or sentiment_label == "Somewhat-Bearish"
                ):
                    negative_count += 1
                else:
                    neutral_count += 1

            # 전체 감정 점수 계산
            overall_sentiment_score = (
                sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
            )

            # 감정 라벨 결정
            if overall_sentiment_score > 0.15:
                overall_sentiment_label = "Bullish"
            elif overall_sentiment_score > 0.05:
                overall_sentiment_label = "Somewhat-Bullish"
            elif overall_sentiment_score < -0.15:
                overall_sentiment_label = "Bearish"
            elif overall_sentiment_score < -0.05:
                overall_sentiment_label = "Somewhat-Bearish"
            else:
                overall_sentiment_label = "Neutral"

            # SentimentAnalysis 객체 생성
            sentiment_analysis = SentimentAnalysis(
                symbol=symbol,
                timeframe=timeframe,
                time_from=start_date.isoformat(),
                time_to=end_date.isoformat(),
                overall_sentiment_score=round(overall_sentiment_score, 4),
                overall_sentiment_label=overall_sentiment_label,
                article_count=total_articles,
                positive_count=positive_count,
                negative_count=negative_count,
                neutral_count=neutral_count,
                sentiment_score_definition="x <= -0.35: Bearish; -0.35 < x <= -0.15: Somewhat-Bearish; -0.15 < x < 0.15: Neutral; 0.15 <= x < 0.35: Somewhat-Bullish; x >= 0.35: Bullish",
                relevance_score_definition="0 < x <= 1, with a higher score indicating higher relevance.",
            )

            logger.info(
                f"Sentiment analysis completed for {symbol}: {overall_sentiment_label} ({overall_sentiment_score})"
            )
            return [sentiment_analysis]

        except Exception as e:
            logger.error(
                f"Failed to fetch sentiment from Alpha Vantage for {symbol}: {e}"
            )
            return []

    async def get_social_sentiment(
        self, symbol: str, platforms: List[str] = ["twitter", "reddit", "stocktwits"]
    ) -> Optional[Dict[str, Any]]:
        """소셜 미디어 감정 분석 (뉴스 기반 감정 분석으로 대체)

        Alpha Vantage에는 직접적인 소셜 미디어 API가 없으므로,
        뉴스 감정 분석으로 대체합니다.

        Args:
            symbol: 주식 심볼
            platforms: 분석할 플랫폼 리스트 (현재는 뉴스 기반)

        Returns:
            소셜 감정 분석 결과
        """
        logger.info(f"Getting social sentiment for {symbol} from news sources")

        try:
            # 최근 1일간의 뉴스 감정 분석으로 소셜 감정 대체
            end_date = datetime.now()
            start_date = end_date - timedelta(days=1)

            response = await self.alpha_vantage.intelligence.news_sentiment(
                tickers=symbol,
                time_from=start_date.strftime("%Y%m%dT%H%M"),
                time_to=end_date.strftime("%Y%m%dT%H%M"),
                sort="LATEST",
                limit=100,
            )

            if not isinstance(response, dict) or "feed" not in response:
                return None

            articles = response["feed"]
            if not articles:
                return None

            # 감정 분석 집계
            sentiment_scores = []
            mention_count = len(articles)
            positive_mentions = 0
            negative_mentions = 0
            neutral_mentions = 0

            for article in articles:
                sentiment_label = article.get("overall_sentiment_label", "Neutral")
                sentiment_score = article.get("overall_sentiment_score", 0)

                if sentiment_score:
                    sentiment_scores.append(float(sentiment_score))

                if sentiment_label in ["Bullish", "Somewhat-Bullish"]:
                    positive_mentions += 1
                elif sentiment_label in ["Bearish", "Somewhat-Bearish"]:
                    negative_mentions += 1
                else:
                    neutral_mentions += 1

            # 평균 감정 점수 계산
            avg_sentiment_score = (
                sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
            )

            # 감정 라벨 결정
            if avg_sentiment_score > 0.15:
                sentiment_label = "Bullish"
            elif avg_sentiment_score > 0.05:
                sentiment_label = "Somewhat-Bullish"
            elif avg_sentiment_score < -0.15:
                sentiment_label = "Bearish"
            elif avg_sentiment_score < -0.05:
                sentiment_label = "Somewhat-Bearish"
            else:
                sentiment_label = "Neutral"

            result = {
                "symbol": symbol,
                "date": datetime.now(),
                "platform": "news_aggregated",  # 뉴스 기반 감정 분석
                "sentiment_score": round(avg_sentiment_score, 4),
                "sentiment_label": sentiment_label,
                "mention_count": mention_count,
                "positive_mentions": positive_mentions,
                "negative_mentions": negative_mentions,
                "neutral_mentions": neutral_mentions,
                "engagement_score": min(
                    mention_count / 10, 10
                ),  # 언급량 기반 참여도 점수 (최대 10)
                "trend_direction": "stable",  # 기본값
                "confidence_level": min(mention_count / 50, 1.0),  # 신뢰도 (최대 1.0)
                "data_quality_score": 85.0,  # 뉴스 기반이므로 높은 품질
                "source": "alpha_vantage_news",
            }

            logger.info(
                f"Social sentiment analysis completed for {symbol}: {sentiment_label} ({avg_sentiment_score})"
            )
            return result

        except Exception as e:
            logger.error(f"Error getting social sentiment for {symbol}: {e}")
            return None

    async def get_consumer_sentiment(
        self, timeframe: str = "1month"
    ) -> Optional[Dict[str, Any]]:
        """소비자 심리 지수 조회 (뉴스 감정 분석 기반)

        Alpha Vantage에는 직접적인 소비자 심리 API가 없으므로,
        광범위한 시장 뉴스 감정 분석을 통해 소비자 심리를 추정합니다.

        Args:
            timeframe: 분석 기간 (1day, 1week, 1month, 3month)

        Returns:
            소비자 심리 분석 결과
        """
        logger.info(f"Getting consumer sentiment for timeframe: {timeframe}")

        try:
            # 시간 범위에 따른 기간 계산
            end_date = datetime.now()
            if timeframe == "1day":
                start_date = end_date - timedelta(days=1)
            elif timeframe == "1week":
                start_date = end_date - timedelta(days=7)
            elif timeframe == "1month":
                start_date = end_date - timedelta(days=30)
            elif timeframe == "3month":
                start_date = end_date - timedelta(days=90)
            else:
                start_date = end_date - timedelta(days=30)

            # 주요 경제/소비 관련 키워드로 뉴스 감정 분석
            consumer_keywords = [
                "consumer spending",
                "retail sales",
                "consumer confidence",
                "inflation",
                "employment",
                "housing market",
                "economic outlook",
            ]

            # 각 키워드별로 뉴스 감정 분석 실행
            all_sentiment_scores = []
            all_articles = []
            total_articles_count = 0

            for keyword in consumer_keywords:
                try:
                    response = await self.alpha_vantage.intelligence.news_sentiment(
                        topics=keyword,
                        time_from=start_date.strftime("%Y%m%dT%H%M"),
                        time_to=end_date.strftime("%Y%m%dT%H%M"),
                        sort="LATEST",
                        limit=20,  # 키워드당 20개씩
                    )

                    if isinstance(response, dict) and "feed" in response:
                        articles = response["feed"]
                        all_articles.extend(articles)
                        total_articles_count += len(articles)

                        for article in articles:
                            sentiment_score = article.get("overall_sentiment_score", 0)
                            relevance_score = article.get("relevance_score", 0)

                            if sentiment_score and relevance_score:
                                # 관련성으로 가중치 적용
                                weighted_score = float(sentiment_score) * float(
                                    relevance_score
                                )
                                all_sentiment_scores.append(weighted_score)

                except Exception as e:
                    logger.warning(
                        f"Error getting sentiment for keyword '{keyword}': {e}"
                    )
                    continue

            # 감정 분석이 불가능한 경우
            if not all_sentiment_scores:
                logger.warning(
                    "No sentiment data available for consumer sentiment analysis"
                )
                return None

            # 전체 소비자 심리 점수 계산
            avg_sentiment_score = sum(all_sentiment_scores) / len(all_sentiment_scores)

            # 감정 분포 계산
            positive_scores = [s for s in all_sentiment_scores if s > 0.05]
            negative_scores = [s for s in all_sentiment_scores if s < -0.05]
            neutral_scores = [s for s in all_sentiment_scores if -0.05 <= s <= 0.05]

            # 소비자 심리 레벨 결정
            if avg_sentiment_score > 0.15:
                sentiment_level = "Very Optimistic"
                sentiment_index = min(80 + (avg_sentiment_score * 100), 100)
            elif avg_sentiment_score > 0.05:
                sentiment_level = "Optimistic"
                sentiment_index = 60 + (avg_sentiment_score * 100)
            elif avg_sentiment_score > -0.05:
                sentiment_level = "Neutral"
                sentiment_index = 50 + (avg_sentiment_score * 100)
            elif avg_sentiment_score > -0.15:
                sentiment_level = "Pessimistic"
                sentiment_index = 40 + (avg_sentiment_score * 100)
            else:
                sentiment_level = "Very Pessimistic"
                sentiment_index = max(20 + (avg_sentiment_score * 100), 0)

            # 신뢰도 계산 (데이터 양 기반)
            confidence_score = min(total_articles_count / 50, 1.0)

            # 트렌드 방향 계산
            recent_articles = [
                a
                for a in all_articles
                if datetime.fromisoformat(
                    a.get("time_published", "").replace("Z", "+00:00")
                )
                > end_date - timedelta(days=3)
            ]

            if recent_articles:
                recent_scores = []
                for article in recent_articles:
                    score = article.get("overall_sentiment_score", 0)
                    relevance = article.get("relevance_score", 0)
                    if score and relevance:
                        recent_scores.append(float(score) * float(relevance))

                recent_avg = (
                    sum(recent_scores) / len(recent_scores) if recent_scores else 0
                )
                trend_direction = (
                    "improving" if recent_avg > avg_sentiment_score else "declining"
                )
            else:
                trend_direction = "stable"

            result = {
                "timeframe": timeframe,
                "analysis_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                },
                "consumer_sentiment": {
                    "sentiment_index": round(sentiment_index, 2),  # 0-100 스케일
                    "sentiment_level": sentiment_level,
                    "sentiment_score": round(avg_sentiment_score, 4),
                    "trend_direction": trend_direction,
                    "confidence_score": round(confidence_score, 2),
                },
                "sentiment_distribution": {
                    "positive_percentage": round(
                        (len(positive_scores) / len(all_sentiment_scores)) * 100, 1
                    ),
                    "negative_percentage": round(
                        (len(negative_scores) / len(all_sentiment_scores)) * 100, 1
                    ),
                    "neutral_percentage": round(
                        (len(neutral_scores) / len(all_sentiment_scores)) * 100, 1
                    ),
                },
                "data_metrics": {
                    "total_articles_analyzed": total_articles_count,
                    "sentiment_scores_count": len(all_sentiment_scores),
                    "keywords_analyzed": consumer_keywords,
                    "data_quality": (
                        "high"
                        if confidence_score > 0.7
                        else "medium" if confidence_score > 0.4 else "low"
                    ),
                },
                "interpretation": {
                    "market_outlook": (
                        "bullish"
                        if avg_sentiment_score > 0.1
                        else "bearish" if avg_sentiment_score < -0.1 else "neutral"
                    ),
                    "consumer_behavior": (
                        "spending_likely"
                        if sentiment_index > 65
                        else (
                            "cautious_spending"
                            if sentiment_index > 35
                            else "reduced_spending"
                        )
                    ),
                    "economic_indicator": (
                        "positive"
                        if sentiment_index > 55
                        else "negative" if sentiment_index < 45 else "mixed"
                    ),
                },
                "last_updated": end_date.isoformat(),
                "data_source": "alpha_vantage_news_sentiment_analysis",
            }

            logger.info(
                f"Consumer sentiment analysis completed: {sentiment_level} ({sentiment_index:.2f}/100)"
            )
            return result

        except Exception as e:
            logger.error(f"Error getting consumer sentiment: {e}")
            return None

    async def refresh_data_from_source(self, **kwargs) -> List[Dict[str, Any]]:
        """BaseMarketDataService 추상 메서드 구현 (deprecated)"""
        logger.warning("refresh_data_from_source is deprecated for SentimentService")
        return []
