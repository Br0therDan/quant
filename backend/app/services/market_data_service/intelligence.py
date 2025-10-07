"""
Intelligence Service
뉴스, 감정 분석 등 인텔리전스 데이터를 처리하는 서비스
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from .base_service import BaseMarketDataService


logger = logging.getLogger(__name__)


class IntelligenceService(BaseMarketDataService):
    """인텔리전스 데이터 서비스

    뉴스, 감정 분석, 분석가 추천 등의 정성적 데이터를 처리합니다.
    """

    async def get_news(
        self,
        symbol: Optional[str] = None,
        topics: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """뉴스 데이터 조회

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

            news_items = []
            if isinstance(response, dict) and "feed" in response:
                for item in response["feed"][:limit]:
                    news_item = {
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "time_published": item.get("time_published", ""),
                        "source": item.get("source", ""),
                        "source_domain": item.get("source_domain", ""),
                        "summary": item.get("summary", ""),
                        "banner_image": item.get("banner_image"),
                        "overall_sentiment_score": item.get("overall_sentiment_score"),
                        "overall_sentiment_label": item.get("overall_sentiment_label"),
                        "ticker_sentiment": item.get("ticker_sentiment", []),
                        "topics": item.get("topics", []),
                        "relevance_score": item.get("relevance_score"),
                    }
                    news_items.append(news_item)

            logger.info(f"Retrieved {len(news_items)} news items for {symbol}")
            return news_items

        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
            return []

    async def get_sentiment_analysis(
        self, symbol: str, timeframe: str = "1day"
    ) -> Optional[Dict[str, Any]]:
        """감정 분석 데이터 조회

        Args:
            symbol: 주식 심볼
            timeframe: 분석 기간

        Returns:
            감정 분석 결과
        """
        logger.info(f"Getting sentiment analysis for {symbol} ({timeframe})")

        try:
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
                return None

            # 감정 점수 집계
            total_articles = len(response["feed"])
            if total_articles == 0:
                return None

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

            result = {
                "symbol": symbol,
                "timeframe": timeframe,
                "time_from": start_date.isoformat(),
                "time_to": end_date.isoformat(),
                "overall_sentiment_score": round(overall_sentiment_score, 4),
                "overall_sentiment_label": overall_sentiment_label,
                "article_count": total_articles,
                "positive_count": positive_count,
                "negative_count": negative_count,
                "neutral_count": neutral_count,
                "sentiment_score_definition": "x <= -0.35: Bearish; -0.35 < x <= -0.15: Somewhat-Bearish; -0.15 < x < 0.15: Neutral; 0.15 <= x < 0.35: Somewhat-Bullish; x >= 0.35: Bullish",
                "relevance_score_definition": "0 < x <= 1, with a higher score indicating higher relevance.",
            }

            logger.info(
                f"Sentiment analysis completed for {symbol}: {overall_sentiment_label} ({overall_sentiment_score})"
            )
            return result

        except Exception as e:
            logger.error(f"Error getting sentiment analysis for {symbol}: {e}")
            return None

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
                    "confidence_level": min(total_articles / 20, 1.0),  # 신뢰도 (뉴스 개수 기반)
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
                        else "medium"
                        if confidence_score > 0.4
                        else "low"
                    ),
                },
                "interpretation": {
                    "market_outlook": (
                        "bullish"
                        if avg_sentiment_score > 0.1
                        else "bearish"
                        if avg_sentiment_score < -0.1
                        else "neutral"
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
                        else "negative"
                        if sentiment_index < 45
                        else "mixed"
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

    # BaseMarketDataService 추상 메서드 구현
    async def _fetch_from_source(self, **kwargs) -> Any:
        """AlphaVantage에서 인텔리전스 데이터 가져오기"""
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
        """인텔리전스 데이터를 캐시에 저장 (향후 구현 예정)"""
        try:
            cache_key = kwargs.get("cache_key", "intelligence_data")
            # TODO: DuckDB 캐시 테이블 구현 후 실제 저장 로직 추가
            logger.info(f"Intelligence data cached for key: {cache_key}")
            return True
        except Exception as e:
            logger.error(f"Error saving intelligence data to cache: {e}")
            return False

    async def _get_from_cache(self, **kwargs) -> Optional[List[Any]]:
        """캐시에서 인텔리전스 데이터 조회 (향후 구현 예정)"""
        try:
            cache_key = kwargs.get("cache_key", "intelligence_data")
            # TODO: DuckDB 캐시 테이블 구현 후 실제 조회 로직 추가
            logger.debug(f"Cache lookup for key: {cache_key} (not implemented yet)")
            return None
        except Exception as e:
            logger.error(f"Error getting intelligence data from cache: {e}")
            return None

    async def refresh_data_from_source(self, **kwargs) -> List[Dict[str, Any]]:
        """베이스 클래스의 추상 메서드 구현"""
        # 이 메서드는 더 이상 직접 사용되지 않으므로 빈 구현
        return []
