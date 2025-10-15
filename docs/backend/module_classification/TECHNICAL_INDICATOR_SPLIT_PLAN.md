# Technical Indicator 파일 분할 계획

**파일**: `backend/app/services/market_data_service/technical_indicator.py`  
**현재 크기**: 1465 lines  
**분석일**: 2025-10-15

---

## 현재 구조 분석

### 클래스 구성

**TechnicalIndicatorService** (1465 lines):

- `__init__`, 프로퍼티 (alpha_vantage, db_manager): ~60 lines
- 캐시 관련 메서드 (`_generate_cache_key`, `_check_cache`, `_save_cache`): ~200
  lines
- **Trend 지표** (SMA, EMA, WMA, DEMA, TEMA): ~600 lines
  - `get_sma`: ~110 lines
  - `get_ema`: ~98 lines
  - `get_wma`: ~103 lines
  - `get_dema`: ~102 lines
  - `get_tema`: ~102 lines
- **Momentum 지표** (RSI, MACD, STOCH): ~550 lines
  - `get_rsi`: ~98 lines
  - `get_macd`: ~112 lines
  - `get_stoch`: ~118 lines
- **Volatility 지표** (BBANDS, ATR, ADX): ~300 lines
  - `get_bbands`: ~114 lines
  - `get_atr`: ~98 lines
  - `get_adx`: ~98 lines
- **Utility**: ~100 lines
  - `get_indicator_list`: ~20 lines

---

## 문제점

1. **단일 책임 원칙 위반**: 12개 지표가 한 클래스에 집중
2. **테스트 어려움**: 각 지표별 독립 테스트 불가
3. **확장성 제한**: 새 지표 추가 시 파일 계속 증가
4. **코드 중복**: 각 지표마다 동일한 캐싱 로직 반복

---

## 분할 전략

### Option 1: 카테고리별 분할 (권장 ✅)

```
market_data_service/indicators/
├── __init__.py                  # 통합 export
├── base.py                      # 공통 기능 (캐싱, 파싱) (~200 lines)
├── trend.py                     # SMA, EMA, WMA, DEMA, TEMA (~350 lines)
├── momentum.py                  # RSI, MACD, STOCH (~350 lines)
└── volatility.py                # BBANDS, ATR, ADX (~250 lines)
```

**장점**:

- ✅ 논리적 그룹핑 (금융 도메인 표준)
- ✅ 파일 크기 적절 (200-350 lines)
- ✅ 확장 용이 (카테고리별 추가)
- ✅ 기존 API 호환성 유지 쉬움

**단점**:

- 카테고리 분류가 애매한 지표 존재 가능

---

### Option 2: 개별 지표별 분할 (과도한 분할)

```
market_data_service/indicators/
├── __init__.py
├── base.py
├── sma.py (~110 lines)
├── ema.py (~98 lines)
├── rsi.py (~98 lines)
└── ... (12개 파일)
```

**장점**:

- ✅ 최소 파일 크기
- ✅ 개별 지표 독립성 극대화

**단점**:

- ❌ 파일 개수 과다 (12+ 파일)
- ❌ Import 복잡도 증가
- ❌ 관리 오버헤드

---

## 권장 방안: Option 1 구현

### Step 1: Base 클래스 생성

**`indicators/base.py`** (~200 lines):

```python
class BaseIndicatorService:
    """기술 지표 서비스 기본 클래스

    캐싱, 파싱, 공통 로직 제공
    """

    def __init__(self, database_manager: Optional[DatabaseManager] = None):
        self._alpha_vantage_client: Optional[AlphaVantageClient] = None
        self._db_manager = database_manager
        self.cache_ttl_hours = 24

    @property
    def alpha_vantage(self) -> AlphaVantageClient:
        """AlphaVantage 클라이언트 lazy loading"""
        ...

    @property
    def db_manager(self) -> DatabaseManager:
        """데이터베이스 매니저 lazy loading"""
        ...

    def _generate_cache_key(self, symbol, indicator_type, interval, parameters) -> str:
        """캐시 키 생성"""
        ...

    async def _check_cache(self, cache_key: str) -> Optional[List[IndicatorDataPoint]]:
        """DuckDB 캐시 확인"""
        ...

    async def _save_cache(self, cache_key: str, data: List[IndicatorDataPoint]):
        """DuckDB에 캐시 저장"""
        ...

    def _parse_indicator_response(self, response, indicator_type) -> List[IndicatorDataPoint]:
        """Alpha Vantage 응답 파싱"""
        ...
```

---

### Step 2: Trend 지표 클래스

**`indicators/trend.py`** (~350 lines):

```python
from .base import BaseIndicatorService

class TrendIndicatorService(BaseIndicatorService):
    """트렌드 지표 서비스 (SMA, EMA, WMA, DEMA, TEMA)"""

    async def get_sma(self, symbol, interval, time_period, series_type) -> TechnicalIndicatorData:
        """Simple Moving Average"""
        ...

    async def get_ema(self, symbol, interval, time_period, series_type) -> TechnicalIndicatorData:
        """Exponential Moving Average"""
        ...

    async def get_wma(self, symbol, interval, time_period, series_type) -> TechnicalIndicatorData:
        """Weighted Moving Average"""
        ...

    async def get_dema(self, symbol, interval, time_period, series_type) -> TechnicalIndicatorData:
        """Double Exponential Moving Average"""
        ...

    async def get_tema(self, symbol, interval, time_period, series_type) -> TechnicalIndicatorData:
        """Triple Exponential Moving Average"""
        ...
```

---

### Step 3: Momentum 지표 클래스

**`indicators/momentum.py`** (~350 lines):

```python
from .base import BaseIndicatorService

class MomentumIndicatorService(BaseIndicatorService):
    """모멘텀 지표 서비스 (RSI, MACD, STOCH)"""

    async def get_rsi(self, symbol, interval, time_period, series_type) -> TechnicalIndicatorData:
        """Relative Strength Index"""
        ...

    async def get_macd(self, symbol, interval, series_type, ...) -> TechnicalIndicatorData:
        """Moving Average Convergence Divergence"""
        ...

    async def get_stoch(self, symbol, interval, ...) -> TechnicalIndicatorData:
        """Stochastic Oscillator"""
        ...
```

---

### Step 4: Volatility 지표 클래스

**`indicators/volatility.py`** (~250 lines):

```python
from .base import BaseIndicatorService

class VolatilityIndicatorService(BaseIndicatorService):
    """변동성 지표 서비스 (BBANDS, ATR, ADX)"""

    async def get_bbands(self, symbol, interval, time_period, series_type, ...) -> TechnicalIndicatorData:
        """Bollinger Bands"""
        ...

    async def get_atr(self, symbol, interval, time_period) -> TechnicalIndicatorData:
        """Average True Range"""
        ...

    async def get_adx(self, symbol, interval, time_period) -> TechnicalIndicatorData:
        """Average Directional Index"""
        ...
```

---

### Step 5: 통합 서비스 (호환성 유지)

**`indicators/__init__.py`**:

```python
"""Technical Indicators Package"""

from .base import BaseIndicatorService
from .trend import TrendIndicatorService
from .momentum import MomentumIndicatorService
from .volatility import VolatilityIndicatorService

class TechnicalIndicatorService:
    """통합 기술 지표 서비스 (하위 호환성 유지)

    기존 코드와의 호환성을 위해 모든 지표 메서드를 제공합니다.
    """

    def __init__(self, database_manager=None):
        self.trend = TrendIndicatorService(database_manager)
        self.momentum = MomentumIndicatorService(database_manager)
        self.volatility = VolatilityIndicatorService(database_manager)

    # Delegation 패턴으로 기존 API 유지
    async def get_sma(self, *args, **kwargs):
        return await self.trend.get_sma(*args, **kwargs)

    async def get_ema(self, *args, **kwargs):
        return await self.trend.get_ema(*args, **kwargs)

    async def get_rsi(self, *args, **kwargs):
        return await self.momentum.get_rsi(*args, **kwargs)

    # ... (모든 지표 메서드 delegation)

    async def get_indicator_list(self) -> Dict[str, List[str]]:
        """사용 가능한 지표 목록 반환"""
        return {
            "trend": ["SMA", "EMA", "WMA", "DEMA", "TEMA"],
            "momentum": ["RSI", "MACD", "STOCH"],
            "volatility": ["BBANDS", "ATR", "ADX"],
        }

__all__ = [
    "TechnicalIndicatorService",
    "BaseIndicatorService",
    "TrendIndicatorService",
    "MomentumIndicatorService",
    "VolatilityIndicatorService",
]
```

---

## 마이그레이션 전략

### 기존 코드 호환성

**Before** (기존 코드 그대로 작동):

```python
from app.services.market_data_service.technical_indicator import TechnicalIndicatorService

service = TechnicalIndicatorService(db_manager)
data = await service.get_sma("AAPL", "daily", 20, "close")
```

**After** (새로운 방식도 가능):

```python
# 방법 1: 기존 방식 (호환성 유지)
from app.services.market_data_service.indicators import TechnicalIndicatorService
service = TechnicalIndicatorService(db_manager)
data = await service.get_sma("AAPL", "daily", 20, "close")

# 방법 2: 새로운 방식 (직접 접근)
from app.services.market_data_service.indicators import TrendIndicatorService
trend_service = TrendIndicatorService(db_manager)
data = await trend_service.get_sma("AAPL", "daily", 20, "close")
```

---

## 실행 계획

1. ✅ **분할 계획 수립** (현재 단계)
2. **Base 클래스 생성** (1시간)
   - `indicators/base.py` 생성
   - 캐싱 로직 이동
3. **Trend 지표 분리** (1시간)
   - `indicators/trend.py` 생성
   - SMA, EMA, WMA, DEMA, TEMA 이동
4. **Momentum 지표 분리** (1시간)
   - `indicators/momentum.py` 생성
   - RSI, MACD, STOCH 이동
5. **Volatility 지표 분리** (1시간)
   - `indicators/volatility.py` 생성
   - BBANDS, ATR, ADX 이동
6. **통합 서비스 생성** (30분)
   - `indicators/__init__.py` 작성
   - Delegation 패턴 구현
7. **Import 경로 수정** (30분)
   - 기존 import 유지 (호환성)
   - 새 경로 추가
8. **테스트 및 검증** (1시간)
   - pytest 실행
   - OpenAPI 재생성

**총 예상 시간**: 6시간

---

## 검증 체크리스트

- [ ] `indicators/base.py` 생성 완료
- [ ] `indicators/trend.py` 생성 완료
- [ ] `indicators/momentum.py` 생성 완료
- [ ] `indicators/volatility.py` 생성 완료
- [ ] `indicators/__init__.py` 통합 완료
- [ ] 기존 import 경로 작동 확인
- [ ] pytest 전체 통과
- [ ] pnpm gen:client 성공
- [ ] 기존 코드 100% 호환성 확인

---

**승인 요청**: 이 계획대로 진행하시겠습니까?

**작성자**: Backend Team  
**상태**: ⏸️ 승인 대기
