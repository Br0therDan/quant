# CHANGELOG - Strategy & Backtest 리팩토링

## Phase 1 완료 (2025-10-13)

### ✅ 의존성 주입 개선

**변경사항:**

- `BacktestService` 생성자를 필수 파라미터로 변경
- `set_dependencies()` 메서드 제거
- 초기화 시점에 `IntegratedBacktestExecutor` 자동 생성

**영향:**

- 서비스 생성 즉시 사용 가능
- 런타임 에러 가능성 감소
- 테스트 용이성 향상

### ✅ 거래 로직 통합

**변경사항:**

- `TradeEngine` 클래스 신규 생성 (Portfolio, TradeCosts 포함)
- `TradingSimulator` 클래스 완전히 제거
- `IntegratedBacktestExecutor`에서 TradeEngine 사용
- 중복 거래 로직 제거

**영향:**

- 코드 중복 제거 (100+ 라인 감소)
- 수수료/슬리피지 계산 일관성 확보
- 거래 실행 로직 단일화

**신규 API:**

```python
from app.services.backtest.trade_engine import TradeEngine, Portfolio

config = BacktestConfig(...)
engine = TradeEngine(config)
trade = engine.execute_order(...)
```

### ✅ 전략 파라미터 타입 안전성

**변경사항:**

- 전략별 Config 클래스 정의: `SMACrossoverConfig`, `RSIMeanReversionConfig`,
  `MomentumConfig`, `BuyAndHoldConfig`
- `Strategy` 모델: `parameters: dict[str, Any]` → `config: StrategyConfigUnion`
- `StrategyTemplate` 모델: `default_parameters` → `default_config`
- API 스키마 업데이트: 모든 요청/응답에서 `config` 필드 사용

**영향:**

- 컴파일 타임 타입 검증
- IDE 자동완성 지원
- 잘못된 파라미터 설정 방지
- Pydantic 검증 (범위, 타입, 관계)

**마이그레이션 필요:**

```python
# ❌ 기존 방식
strategy = Strategy(
    name="My SMA",
    strategy_type=StrategyType.SMA_CROSSOVER,
    parameters={"short_window": 10, "long_window": 30}
)

# ✅ 새 방식
from app.strategies.configs import SMACrossoverConfig

config = SMACrossoverConfig(short_window=10, long_window=30)
strategy = Strategy(
    name="My SMA",
    strategy_type=StrategyType.SMA_CROSSOVER,
    config=config
)
```

### 🧪 테스트 커버리지

**신규 테스트:**

- `test_service_factory.py`: 의존성 주입 검증 (3 tests)
- `test_trade_engine.py`: 거래 엔진 검증 (6 tests)
- `test_strategy_config.py`: Config 검증 (3 tests)

**결과:** 12/12 tests passed ✅

### 📊 성능 영향

- 백테스트 서비스 초기화: **즉시 가능** (기존: set_dependencies 호출 필요)
- 거래 실행 일관성: **100%** (기존: 로직 중복으로 불일치 가능)
- 타입 안전성: **컴파일 타임** (기존: 런타임)

### 🚫 Breaking Changes

**1. Strategy 모델**

- `parameters` 필드 제거 → `config` 필드로 대체
- 기존 데이터베이스의 Strategy 문서는 마이그레이션 필요

**2. StrategyTemplate 모델**

- `default_parameters`, `parameter_schema` 필드 제거 → `default_config` 필드로
  대체
- `category` 필드 필수로 변경

**3. API 스키마**

- `StrategyCreate`, `StrategyUpdate` 요청에서 `parameters` → `config`
- `TemplateCreate`, `TemplateUpdate` 요청에서 `default_parameters` →
  `default_config`

**4. StrategyService**

- `get_strategy_instance(strategy_type, parameters)` →
  `get_strategy_instance(strategy_type, config)`

### 📝 TODO (Phase 1 미완료)

- [ ] 데이터베이스 마이그레이션 스크립트 작성
- [ ] API 문서 자동 업데이트 확인
- [ ] 프로덕션 배포 가이드 작성

---

## 다음 단계: Phase 2

Phase 2에서는 다음 작업을 진행할 예정:

- 레이어드 아키텍처 도입
- 성능 최적화 (DuckDB 활용 강화)
- 고급 백테스트 기능 (포트폴리오 최적화, 리스크 관리)

자세한 내용은 `docs/backend/strategy_backtest/NEW_ARCHITECTURE.md` 참조.
