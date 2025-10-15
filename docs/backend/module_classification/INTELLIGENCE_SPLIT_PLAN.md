# Phase 2.1c: Intelligence.py 모듈 분할 계획

## 현황 분석

- **파일**: `backend/app/services/market_data/intelligence.py`
- **크기**: 1163 라인
- **클래스**: IntelligenceService (BaseMarketDataService 상속)
- **메서드**: 15개 (public 8개, private 7개)

## 분할 전략: 기능별 모듈화 (5 files)

### 1. `base.py` (50 라인)
**책임**: 공통 베이스 클래스 + 유틸리티

```python
class BaseIntelligenceService:
    """인텔리전스 서비스 기본 클래스"""
    
    @staticmethod
    def _safe_decimal(value) -> Optional[Decimal]:
        """API 응답값을 Decimal로 안전하게 변환"""
        # 기존 구현 그대로
```

**의존성**:
- `from .base_service import BaseMarketDataService`
- `decimal.Decimal`

---

### 2. `news.py` (~420 라인)
**책임**: 뉴스 데이터 수집 및 분석

**메서드**:
- `get_news()` - 캐시 우선 뉴스 조회 (78 라인)
- `_fetch_news_from_alpha_vantage()` - Alpha Vantage 뉴스 fetch (104 라인)
- `get_market_buzz()` - 시장 화제 종목 (상승/하락률) (87 라인)
- `analyze_news_impact()` - 뉴스 영향도 분석 (126 라인)

**클래스 구조**:
```python
class NewsService(BaseIntelligenceService):
    """뉴스 데이터 수집 및 분석 서비스"""
    
    async def get_news(
        self, symbol: Optional[str], topics: Optional[List[str]], 
        start_date: Optional[datetime], end_date: Optional[datetime], limit: int = 50
    ) -> List[Dict[str, Any]]:
        """뉴스 데이터 조회 (캐시 우선, Alpha Vantage fallback)"""
        
    async def _fetch_news_from_alpha_vantage(...) -> List:
        """Alpha Vantage 뉴스 fetch 및 NewsArticle 변환"""
        
    async def get_market_buzz(self, timeframe: str = "1day", limit: int = 10) -> List[Dict[str, Any]]:
        """시장 화제 종목 (TOP_GAINERS_LOSERS API)"""
        
    async def analyze_news_impact(self, symbol: str, news_url: str = "") -> Dict[str, Any]:
        """뉴스가 주가에 미친 영향 분석 (최근 3일 기반)"""
```

**의존성**:
- `app.models.market_data.intelligence.NewsArticle`
- `BaseIntelligenceService`
- `self.alpha_vantage.intelligence.news_sentiment()`
- `self.alpha_vantage.intelligence.top_gainers_losers()`

---

### 3. `sentiment.py` (~360 라인)
**책임**: 감정 분석 (뉴스 기반 감정 집계)

**메서드**:
- `get_sentiment_analysis()` - 감정 분석 (48 라인)
- `_fetch_sentiment_from_alpha_vantage()` - 감정 데이터 fetch (153 라인)
- `get_social_sentiment()` - 소셜 미디어 감정 (뉴스 기반) (86 라인)
- `get_consumer_sentiment()` - 소비자 심리 지수 (215 라인)

**클래스 구조**:
```python
class SentimentService(BaseIntelligenceService):
    """감정 분석 서비스 (뉴스 기반 감정 집계)"""
    
    async def get_sentiment_analysis(self, symbol: str, timeframe: str = "1day") -> Optional[Dict[str, Any]]:
        """감정 분석 데이터 조회 (캐시 우선)"""
        
    async def _fetch_sentiment_from_alpha_vantage(self, symbol: str, timeframe: str) -> List:
        """뉴스 감정 집계 후 SentimentAnalysis 모델 생성"""
        
    async def get_social_sentiment(
        self, symbol: str, platforms: List[str] = ["twitter", "reddit", "stocktwits"]
    ) -> Optional[Dict[str, Any]]:
        """소셜 미디어 감정 분석 (뉴스 기반 대체)"""
        
    async def get_consumer_sentiment(self, timeframe: str = "1month") -> Optional[Dict[str, Any]]:
        """소비자 심리 지수 (경제 키워드 뉴스 감정 분석)"""
```

**특징**:
- 모든 메서드가 뉴스 감정 점수를 집계하여 감정 지수 산출
- Bullish/Bearish/Neutral 라벨 결정 로직 공통화 가능
- 감정 점수 임계값 (0.15, 0.05, -0.05, -0.15) 상수화

**의존성**:
- `app.models.market_data.intelligence.SentimentAnalysis`
- `BaseIntelligenceService`
- `self.alpha_vantage.intelligence.news_sentiment()`

---

### 4. `analyst.py` (~60 라인)
**책임**: 분석가 추천 및 내부자 거래 정보

**메서드**:
- `get_analyst_recommendations()` - 내부자 거래 정보 조회 (47 라인)

**클래스 구조**:
```python
class AnalystService(BaseIntelligenceService):
    """분석가 추천 및 내부자 거래 서비스"""
    
    async def get_analyst_recommendations(self, symbol: str) -> List[Dict[str, Any]]:
        """분석가 추천 의견 조회 (내부자 거래 정보 포함)"""
```

**의존성**:
- `self.alpha_vantage.intelligence.insider_transactions()`

---

### 5. `cache.py` (~220 라인)
**책임**: DuckDB 캐시 레이어 (BaseMarketDataService 추상 메서드 구현)

**메서드**:
- `_fetch_from_source()` - Alpha Vantage API 라우팅 (19 라인)
- `_save_to_cache()` - NewsArticle 변환 후 DuckDB 저장 (84 라인)
- `_get_from_cache()` - DuckDB 캐시 조회 (26 라인)
- `_save_news_to_duckdb()` - DuckDB news_cache 테이블 저장 (87 라인)

**클래스 구조**:
```python
class IntelligenceCacheManager(BaseIntelligenceService):
    """인텔리전스 데이터 DuckDB 캐싱"""
    
    async def _fetch_from_source(self, **kwargs) -> Any:
        """Alpha Vantage 메서드 라우팅 (news_sentiment, insider_transactions, top_gainers_losers)"""
        
    async def _save_to_cache(self, data: Any, **kwargs) -> bool:
        """데이터를 NewsArticle 모델로 변환 후 _save_news_to_duckdb 호출"""
        
    async def _get_from_cache(self, **kwargs) -> Optional[List[Any]]:
        """DuckDB 캐시 조회 (_get_from_duckdb_cache 래핑)"""
        
    async def _save_news_to_duckdb(self, news_articles: List, cache_key: str) -> bool:
        """news_cache 테이블 INSERT OR REPLACE"""
```

**의존성**:
- `app.models.market_data.intelligence.NewsArticle`
- `self._db_manager.connection` (DuckDB)
- `datetime.UTC`

---

### 6. `__init__.py` (~150 라인 예상)
**책임**: 통합 IntelligenceService (Delegation 패턴)

**구조**:
```python
class IntelligenceService(BaseMarketDataService):
    """인텔리전스 데이터 통합 서비스"""
    
    def __init__(self, alpha_vantage, db_manager=None):
        super().__init__(alpha_vantage, db_manager)
        
        # 모듈 인스턴스 생성 (의존성 주입)
        self._news = NewsService(alpha_vantage, db_manager)
        self._sentiment = SentimentService(alpha_vantage, db_manager)
        self._analyst = AnalystService(alpha_vantage, db_manager)
        self._cache = IntelligenceCacheManager(alpha_vantage, db_manager)
    
    # 뉴스 메서드 위임
    async def get_news(self, symbol=None, topics=None, start_date=None, end_date=None, limit=50):
        return await self._news.get_news(symbol, topics, start_date, end_date, limit)
    
    async def get_market_buzz(self, timeframe="1day", limit=10):
        return await self._news.get_market_buzz(timeframe, limit)
    
    async def analyze_news_impact(self, symbol, news_url=""):
        return await self._news.analyze_news_impact(symbol, news_url)
    
    # 감정 분석 메서드 위임
    async def get_sentiment_analysis(self, symbol, timeframe="1day"):
        return await self._sentiment.get_sentiment_analysis(symbol, timeframe)
    
    async def get_social_sentiment(self, symbol, platforms=["twitter", "reddit", "stocktwits"]):
        return await self._sentiment.get_social_sentiment(symbol, platforms)
    
    async def get_consumer_sentiment(self, timeframe="1month"):
        return await self._sentiment.get_consumer_sentiment(timeframe)
    
    # 분석가 메서드 위임
    async def get_analyst_recommendations(self, symbol):
        return await self._analyst.get_analyst_recommendations(symbol)
    
    # 캐시 메서드 위임 (BaseMarketDataService 추상 메서드 구현)
    async def _fetch_from_source(self, **kwargs):
        return await self._cache._fetch_from_source(**kwargs)
    
    async def _save_to_cache(self, data, **kwargs):
        return await self._cache._save_to_cache(data, **kwargs)
    
    async def _get_from_cache(self, **kwargs):
        return await self._cache._get_from_cache(**kwargs)
    
    async def refresh_data_from_source(self, **kwargs):
        """Deprecated - 빈 구현"""
        return []
```

---

## 최종 파일 구조

```
backend/app/services/market_data/intelligence/
├── __init__.py           (150 lines) - IntelligenceService 통합
├── base.py               (50 lines)  - BaseIntelligenceService + 유틸리티
├── news.py               (420 lines) - NewsService
├── sentiment.py          (360 lines) - SentimentService
├── analyst.py            (60 lines)  - AnalystService
└── cache.py              (220 lines) - IntelligenceCacheManager
-----------------------------------------------------------
Total:                    1260 lines (vs. 원본 1163 lines, +8% for clarity)
```

---

## 장점 분석

### 1. 단일 책임 원칙 (SRP)
- **news.py**: 뉴스 수집 및 영향도 분석만 담당
- **sentiment.py**: 감정 집계 및 심리 지수 계산만 담당
- **analyst.py**: 내부자 거래 정보만 담당
- **cache.py**: DuckDB 캐싱 로직만 담당

### 2. 테스트 용이성
```python
# 뉴스 메서드만 단위 테스트
from app.services.market_data.intelligence.news import NewsService
news_service = NewsService(mock_alpha_vantage, mock_db_manager)
result = await news_service.get_market_buzz("1day", 10)
assert len(result) <= 10
```

### 3. 확장성
- 새로운 감정 분석 소스 추가 시 `sentiment.py`만 수정
- 뉴스 분석 알고리즘 개선 시 `news.py`만 수정
- 캐싱 전략 변경 시 `cache.py`만 수정

### 4. 기존 API 호환성 유지
```python
# ✅ 기존 코드 그대로 작동
from app.services.service_factory import service_factory
intelligence = service_factory.get_intelligence_service()
news = await intelligence.get_news("AAPL", ["earnings"], limit=10)
sentiment = await intelligence.get_sentiment_analysis("AAPL", "1day")
```

---

## 구현 순서 (Phase 2.1c)

1. **Step 1**: `base.py` 생성 (BaseIntelligenceService + _safe_decimal)
2. **Step 2**: `news.py` 생성 (4개 뉴스 메서드)
3. **Step 3**: `sentiment.py` 생성 (4개 감정 분석 메서드)
4. **Step 4**: `analyst.py` 생성 (1개 메서드)
5. **Step 5**: `cache.py` 생성 (4개 캐시 메서드)
6. **Step 6**: `__init__.py` 생성 (전체 위임 로직)
7. **Step 7**: `intelligence.py` → `intelligence_legacy.py` 백업
8. **Step 8**: Import 검증 (get_errors)
9. **Step 9**: OpenAPI 클라이언트 재생성 (`pnpm gen:client`)
10. **Step 10**: Git commit (Phase 2.1c 완료)

---

## 잠재적 이슈 및 해결책

### Issue 1: 순환 의존성 (Circular Import)
**문제**: BaseIntelligenceService가 BaseMarketDataService를 상속받는데, 모든 서브 모듈도 상속받으면 복잡해짐

**해결책**:
```python
# base.py
from .base_service import BaseMarketDataService

class BaseIntelligenceService(BaseMarketDataService):
    """공통 베이스 클래스"""
    pass

# news.py, sentiment.py, analyst.py, cache.py
from .base import BaseIntelligenceService

class NewsService(BaseIntelligenceService):
    """BaseIntelligenceService만 상속"""
```

### Issue 2: alpha_vantage 및 db_manager 전달
**문제**: 각 서브 모듈에 의존성 전달 필요

**해결책** (Delegation 패턴):
```python
# __init__.py
class IntelligenceService(BaseMarketDataService):
    def __init__(self, alpha_vantage, db_manager=None):
        super().__init__(alpha_vantage, db_manager)
        
        # 모든 서브 모듈에 동일 의존성 주입
        self._news = NewsService(alpha_vantage, db_manager)
        self._sentiment = SentimentService(alpha_vantage, db_manager)
        self._analyst = AnalystService(alpha_vantage, db_manager)
        self._cache = IntelligenceCacheManager(alpha_vantage, db_manager)
```

### Issue 3: get_data_with_unified_cache 호출
**문제**: BaseMarketDataService의 통합 캐시 메서드 호출이 서브 모듈에서 가능해야 함

**해결책**:
```python
# BaseIntelligenceService가 BaseMarketDataService 상속받으므로 자동 해결
# news.py
class NewsService(BaseIntelligenceService):
    async def get_news(self, ...):
        data = await self.get_data_with_unified_cache(  # ✅ 상속받은 메서드 사용
            cache_key=cache_key,
            data_type="news",
            model_class=NewsArticle,
            ...
        )
```

---

## 예상 리스크 및 대응

| 리스크 | 확률 | 영향 | 대응 방안 |
|--------|------|------|----------|
| 타입 에러 (abstract method) | 높음 | 중 | Phase 2.1b와 동일하게 `refresh_data_from_source()` 빈 구현 추가 |
| 순환 의존성 | 낮음 | 중 | base.py를 최상위로 두고 계층 구조 명확화 |
| API 응답 파싱 실패 | 중 | 낮음 | 기존 try-except 로직 유지, 에러 로깅 강화 |
| DuckDB 연결 실패 | 낮음 | 중 | _db_manager 체크 로직 유지 |

---

## 성공 기준

- ✅ 1163 라인 → 6개 파일 (평균 210 라인 이하)
- ✅ 각 파일이 단일 책임 원칙 준수
- ✅ 기존 API 엔드포인트 호환성 유지
- ✅ 타입 에러 0개 (mypy 검증)
- ✅ OpenAPI 클라이언트 생성 성공
- ✅ Git commit 성공

---

## 참고 문서

- Phase 2.1a 완료: `docs/backend/module_classification/PHASE2.1A_COMPLETION.md`
- Phase 2.1b 완료: `docs/backend/module_classification/PHASE2.1B_COMPLETION.md`
- Stock 모듈 패턴: `backend/app/services/market_data/stock/__init__.py`
- Technical Indicator 모듈 패턴: `backend/app/services/market_data/technical_indicator/__init__.py`
