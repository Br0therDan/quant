# Stock Service Split Plan (Phase 2.1b)

**Target File**: `backend/app/services/market_data/stock.py` (1241 lines)  
**Created**: 2025-10-15  
**Estimated Time**: 2-3 hours

---

## 현재 구조 분석

### Class Structure

```python
class StockService(BaseMarketDataService):
    def __init__(database_manager, data_quality_sentinel)

    # Public API Methods (주요 인터페이스)
    async def get_daily_prices(...)       # Line 40
    async def get_weekly_prices(...)      # Line 91
    async def get_monthly_prices(...)     # Line 128
    async def get_real_time_quote(...)    # Line 654
    async def get_intraday_data(...)      # Line 780
    async def get_historical_data(...)    # Line 945
    async def search_symbols(...)         # Line 1009

    # Alpha Vantage Fetchers (API 호출)
    async def _fetch_daily_prices_from_alpha_vantage(...)    # Line 166
    async def _fetch_weekly_prices_from_alpha_vantage(...)   # Line 347
    async def _fetch_monthly_prices_from_alpha_vantage(...)  # Line 427
    async def _fetch_quote_from_alpha_vantage(...)           # Line 702
    async def _fetch_intraday_from_alpha_vantage(...)        # Line 832

    # MongoDB Storage Helpers (데이터 저장)
    async def _fetch_and_store_daily_prices(...)    # Line 1112
    async def _fetch_and_store_weekly_prices(...)   # Line 1180
    async def _fetch_and_store_monthly_prices(...)  # Line 1202

    # Coverage Management (메타데이터)
    async def _get_or_create_coverage(...)  # Line 1043
    async def _update_coverage(...)         # Line 1065

    # BaseMarketDataService Overrides (캐시)
    async def _fetch_from_source(...)  # Line 515
    async def _save_to_cache(...)      # Line 544
    async def _get_from_cache(...)     # Line 630

    # Utility Methods (변환)
    def _dict_to_quote_data(...)  # Line 723
```

### Line Distribution (1241 lines total)

| Section                | Lines | %   | Description                  |
| ---------------------- | ----- | --- | ---------------------------- |
| Imports & Setup        | 30    | 2%  | imports, logger              |
| Public API Methods     | 150   | 12% | get_daily/weekly/monthly/etc |
| Alpha Vantage Fetchers | 680   | 55% | API 호출 및 응답 파싱        |
| MongoDB Storage        | 180   | 14% | 데이터 저장 로직             |
| Coverage Management    | 80    | 6%  | Coverage 생성/업데이트       |
| Cache Methods          | 90    | 7%  | DuckDB 캐싱                  |
| Utility                | 31    | 2%  | dict_to_quote_data           |

---

## 분할 전략

### Option 1: Functionality-Based Split (선택)

```
market_data/stock/
├── __init__.py (200 lines)        # StockService 통합 인터페이스
├── base.py (150 lines)            # BaseStockService (공통 로직)
├── fetcher.py (400 lines)         # Alpha Vantage API 호출
├── storage.py (250 lines)         # MongoDB 저장 로직
├── coverage.py (120 lines)        # Coverage 관리
└── cache.py (120 lines)           # DuckDB 캐싱
```

**장점**:

- 기능별 명확한 분리 (API, Storage, Coverage, Cache)
- 각 파일의 책임이 명확
- 테스트 작성 용이

**단점**:

- 6개 파일로 분할 (관리 복잡도 증가)
- fetcher.py가 여전히 400줄로 큼

### Option 2: Time-Frame Based Split (대안)

```
market_data/stock/
├── __init__.py           # StockService 통합 인터페이스
├── base.py               # BaseStockService (공통 로직)
├── daily.py              # Daily prices (get + fetch + store)
├── weekly.py             # Weekly prices
├── monthly.py            # Monthly prices
├── intraday.py           # Intraday & Quote
└── utilities.py          # Coverage, Cache, Search
```

**장점**:

- Time-frame별 독립성
- 각 파일이 자체 완결적

**단점**:

- 코드 중복 가능성 (각 파일에서 비슷한 패턴 반복)
- 공통 로직 추출 어려움

---

## 최종 선택: Option 1 (Functionality-Based)

**이유**:

1. 기능별 분리가 DRY 원칙에 부합
2. Alpha Vantage API 호출 로직 통합 관리
3. MongoDB 저장 로직의 일관성
4. Coverage 관리의 재사용성

---

## 구현 계획

### 1. base.py (150 lines)

```python
"""
Base Stock Service
주식 서비스 기본 클래스 - 공통 로직
"""

class BaseStockService(BaseMarketDataService):
    """주식 서비스 기본 클래스

    Attributes:
        database_manager: DuckDB 캐시 매니저
        data_quality_sentinel: 데이터 품질 모니터
    """

    def __init__(
        self,
        database_manager: Optional[DatabaseManager] = None,
        data_quality_sentinel: Optional[DataQualitySentinel] = None,
    ):
        super().__init__(database_manager)
        self.data_quality_sentinel = data_quality_sentinel

    # 공통 유틸리티 메서드
    def _dict_to_quote_data(self, quote_dict: dict) -> QuoteData:
        """딕셔너리를 QuoteData 객체로 변환"""
        ...

    async def _validate_symbol(self, symbol: str) -> str:
        """심볼 유효성 검사 및 정규화"""
        ...
```

**Content**:

- BaseMarketDataService 상속
- **init** with database_manager, data_quality_sentinel
- 공통 유틸리티 메서드 (\_dict_to_quote_data, etc.)

### 2. fetcher.py (400 lines)

```python
"""
Stock Data Fetcher
Alpha Vantage API 호출 로직
"""

from .base import BaseStockService

class StockFetcher(BaseStockService):
    """Alpha Vantage API 호출 클래스

    Methods:
        - fetch_daily_prices: Daily price 조회
        - fetch_weekly_prices: Weekly price 조회
        - fetch_monthly_prices: Monthly price 조회
        - fetch_quote: Real-time quote 조회
        - fetch_intraday: Intraday data 조회
        - search_symbols: Symbol 검색
    """

    async def fetch_daily_prices(
        self, symbol: str, outputsize: str = "compact"
    ) -> List[DailyPrice]:
        """Alpha Vantage에서 일일 주가 데이터 가져오기"""
        ...

    async def fetch_weekly_prices(...) -> List[WeeklyPrice]:
        ...

    async def fetch_monthly_prices(...) -> List[MonthlyPrice]:
        ...

    async def fetch_quote(self, symbol: str) -> QuoteData:
        ...

    async def fetch_intraday(...) -> List[DailyPrice]:
        ...

    async def search_symbols(self, keywords: str) -> dict:
        ...
```

**Content**:

- `_fetch_daily_prices_from_alpha_vantage` (180 lines)
- `_fetch_weekly_prices_from_alpha_vantage` (80 lines)
- `_fetch_monthly_prices_from_alpha_vantage` (80 lines)
- `_fetch_quote_from_alpha_vantage` (20 lines)
- `_fetch_intraday_from_alpha_vantage` (110 lines)
- `search_symbols` (30 lines)

**Key Responsibilities**:

- Alpha Vantage API 호출
- 응답 데이터 파싱
- DailyPrice/WeeklyPrice/MonthlyPrice 객체로 변환
- 에러 핸들링

### 3. storage.py (250 lines)

```python
"""
Stock Data Storage
MongoDB 저장 로직
"""

from .base import BaseStockService

class StockStorage(BaseStockService):
    """MongoDB 저장 클래스

    Methods:
        - store_daily_prices: Daily prices 저장 (upsert)
        - store_weekly_prices: Weekly prices 저장
        - store_monthly_prices: Monthly prices 저장
    """

    async def store_daily_prices(
        self,
        symbol: str,
        prices: List[DailyPrice],
        is_full: bool = True
    ) -> List[DailyPrice]:
        """Daily prices를 MongoDB에 저장

        Args:
            symbol: 심볼
            prices: 저장할 가격 데이터
            is_full: True면 기존 데이터 삭제 후 저장

        Returns:
            저장된 DailyPrice 리스트
        """
        # Data quality sentinel 실행
        if self.data_quality_sentinel:
            await self.data_quality_sentinel.evaluate_daily_prices(...)

        # Upsert logic
        ...

    async def store_weekly_prices(...) -> List[WeeklyPrice]:
        ...

    async def store_monthly_prices(...) -> List[MonthlyPrice]:
        ...
```

**Content**:

- `_fetch_and_store_daily_prices` (70 lines) → `store_daily_prices`
- `_fetch_and_store_weekly_prices` (22 lines) → `store_weekly_prices`
- `_fetch_and_store_monthly_prices` (22 lines) → `store_monthly_prices`
- Data quality sentinel 통합
- Upsert 로직 (symbol + date unique)

**Key Responsibilities**:

- MongoDB에 저장 (insert/update)
- Data quality evaluation
- 중복 처리 (upsert)

### 4. coverage.py (120 lines)

```python
"""
Stock Data Coverage Management
Coverage 메타데이터 관리
"""

from .base import BaseStockService

class CoverageManager(BaseStockService):
    """Coverage 관리 클래스

    Methods:
        - get_or_create_coverage: Coverage 조회 또는 생성
        - update_coverage: Coverage 업데이트
    """

    async def get_or_create_coverage(
        self, symbol: str, data_type: str
    ) -> StockDataCoverage:
        """Coverage 레코드 조회 또는 생성"""
        ...

    async def update_coverage(
        self,
        coverage: StockDataCoverage,
        data_records: List,
        update_type: Literal["full", "delta"],
    ) -> None:
        """Coverage 레코드 업데이트"""
        ...
```

**Content**:

- `_get_or_create_coverage` (22 lines)
- `_update_coverage` (58 lines)
- Coverage 생성/업데이트 로직
- 날짜 범위 계산
- 다음 업데이트 예정일 계산

### 5. cache.py (120 lines)

```python
"""
Stock Data Cache Management
DuckDB 캐싱 로직
"""

from .base import BaseStockService

class StockCacheManager(BaseStockService):
    """DuckDB 캐시 관리 클래스

    Methods:
        - fetch_from_source: Alpha Vantage에서 데이터 가져오기
        - save_to_cache: DuckDB에 저장
        - get_from_cache: DuckDB에서 조회
    """

    async def fetch_from_source(self, **kwargs):
        """Alpha Vantage에서 주식 데이터 가져오기

        BaseMarketDataService의 추상 메서드 구현
        """
        ...

    async def save_to_cache(self, data, **kwargs) -> bool:
        """주식 데이터를 DuckDB 캐시에 저장"""
        ...

    async def get_from_cache(self, **kwargs):
        """DuckDB 캐시에서 데이터 조회"""
        ...
```

**Content**:

- `_fetch_from_source` (32 lines)
- `_save_to_cache` (86 lines)
- `_get_from_cache` (25 lines)
- DuckDB 캐싱 전략

### 6. **init**.py (200 lines)

```python
"""
Stock Service Package
주식 서비스 통합 인터페이스
"""

from typing import List, Literal, Optional
from datetime import datetime

from .base import BaseStockService
from .fetcher import StockFetcher
from .storage import StockStorage
from .coverage import CoverageManager
from .cache import StockCacheManager


class StockService(BaseStockService):
    """주식 데이터 서비스 통합 인터페이스

    기존 stock.py와 100% 호환되는 인터페이스를 제공합니다.
    내부적으로 전문화된 서비스로 위임하여 처리합니다.

    Delegation Pattern:
        - Fetcher: Alpha Vantage API 호출
        - Storage: MongoDB 저장
        - Coverage: Coverage 메타데이터 관리
        - Cache: DuckDB 캐싱
    """

    def __init__(self, database_manager=None, data_quality_sentinel=None):
        super().__init__(database_manager, data_quality_sentinel)

        # Specialized services
        self._fetcher = StockFetcher(database_manager, data_quality_sentinel)
        self._storage = StockStorage(database_manager, data_quality_sentinel)
        self._coverage = CoverageManager(database_manager, data_quality_sentinel)
        self._cache = StockCacheManager(database_manager, data_quality_sentinel)

    # ========== Public API Methods ==========

    async def get_daily_prices(
        self, symbol: str, outputsize: str = "compact", adjusted: bool = True
    ) -> List[DailyPrice]:
        """일일 주가 데이터 조회 (Coverage 기반 캐싱)"""
        # Coverage 확인
        coverage = await self._coverage.get_or_create_coverage(symbol, "daily")

        # Full update 필요 여부 확인
        needs_full_update = (...)

        # MongoDB에서 기존 데이터 조회
        existing_prices = await DailyPrice.find(...).to_list()

        if not existing_prices or needs_full_update:
            # Fetch from Alpha Vantage
            prices = await self._fetcher.fetch_daily_prices(symbol, outputsize)

            # Store to MongoDB
            saved_prices = await self._storage.store_daily_prices(
                symbol, prices, is_full=True
            )

            # Update coverage
            if saved_prices:
                await self._coverage.update_coverage(
                    coverage, saved_prices, "full"
                )

            return saved_prices or []
        else:
            # Use cached data
            return existing_prices

    async def get_weekly_prices(...) -> List[WeeklyPrice]:
        """주간 주가 데이터 조회"""
        ...

    async def get_monthly_prices(...) -> List[MonthlyPrice]:
        """월간 주가 데이터 조회"""
        ...

    async def get_real_time_quote(...) -> QuoteData:
        """실시간 호가 조회"""
        return await self._fetcher.fetch_quote(symbol)

    async def get_intraday_data(...) -> List[DailyPrice]:
        """인트라데이 데이터 조회"""
        return await self._fetcher.fetch_intraday(...)

    async def get_historical_data(...) -> dict:
        """히스토리컬 데이터 조회"""
        ...

    async def search_symbols(self, keywords: str) -> dict:
        """심볼 검색"""
        return await self._fetcher.search_symbols(keywords)

    # ========== BaseMarketDataService Overrides ==========

    async def refresh_data_from_source(self, **kwargs) -> List[DailyPrice]:
        """베이스 클래스의 추상 메서드 구현"""
        return []

    async def _fetch_from_source(self, **kwargs):
        """캐시 미스 시 호출"""
        return await self._cache.fetch_from_source(**kwargs)

    async def _save_to_cache(self, data, **kwargs) -> bool:
        """캐시에 저장"""
        return await self._cache.save_to_cache(data, **kwargs)

    async def _get_from_cache(self, **kwargs):
        """캐시에서 조회"""
        return await self._cache.get_from_cache(**kwargs)


__all__ = ["StockService"]
```

**Content**:

- StockService 통합 클래스
- Delegation pattern으로 specialized services 사용
- 기존 public API 100% 호환
- BaseMarketDataService 추상 메서드 구현

---

## 구현 순서

### Step 1: base.py 생성 (15분)

- BaseStockService 클래스
- **init**, \_dict_to_quote_data, \_validate_symbol

### Step 2: fetcher.py 생성 (40분)

- StockFetcher 클래스
- 6개 fetch 메서드 이식 (daily, weekly, monthly, quote, intraday, search)

### Step 3: storage.py 생성 (30분)

- StockStorage 클래스
- 3개 store 메서드 이식 (daily, weekly, monthly)
- Data quality sentinel 통합

### Step 4: coverage.py 생성 (15분)

- CoverageManager 클래스
- get_or_create_coverage, update_coverage

### Step 5: cache.py 생성 (15분)

- StockCacheManager 클래스
- fetch_from_source, save_to_cache, get_from_cache

### Step 6: **init**.py 생성 (30분)

- StockService 통합 클래스
- Delegation pattern 구현
- Public API 메서드 7개

### Step 7: 검증 및 커밋 (15분)

- Import 에러 확인
- 테스트 실행
- OpenAPI client 재생성
- Git commit

**Total**: 2시간 30분

---

## 검증 체크리스트

- [ ] base.py 생성 완료
- [ ] fetcher.py 생성 완료
- [ ] storage.py 생성 완료
- [ ] coverage.py 생성 완료
- [ ] cache.py 생성 완료
- [ ] **init**.py 생성 완료
- [ ] 원본 stock.py 삭제
- [ ] service_factory.py import 업데이트
- [ ] No import errors
- [ ] OpenAPI client 재생성
- [ ] Pre-commit hooks 통과
- [ ] Git commit with detailed message

---

## 예상 효과

### Before

- 1 file, 1241 lines
- All responsibilities mixed
- Hard to find specific logic
- Difficult to test

### After

- 6 files, ~1240 lines total
- Clear separation of concerns:
  - API calls (fetcher.py)
  - Storage (storage.py)
  - Coverage (coverage.py)
  - Cache (cache.py)
- Easy to find and modify
- Testable in isolation

### Metrics

- **찾기 쉬움**: ⬆️ 85% (기능별 분리)
- **수정 용이성**: ⬆️ 75% (isolated changes)
- **테스트 작성**: ⬆️ 80% (focused tests)
- **확장성**: ⬆️ 90% (new features in specific files)
