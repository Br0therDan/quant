# Strategy & Backtest 마이그레이션 계획

> **목적**: 기존 코드를 새 아키텍처로 안전하게 이전  
> **대상**: Phase 1-4 전체 기간 (12주)

## 📋 목차

1. [마이그레이션 원칙](#1-마이그레이션-원칙)
2. [Phase 1 마이그레이션](#2-phase-1-마이그레이션)
3. [Phase 2 마이그레이션](#3-phase-2-마이그레이션)
4. [Phase 3-4 마이그레이션](#4-phase-3-4-마이그레이션)
5. [데이터 마이그레이션](#5-데이터-마이그레이션)
6. [API 호환성 관리](#6-api-호환성-관리)
7. [롤백 전략](#7-롤백-전략)

---

## 1. 마이그레이션 원칙

### 1.1 무중단 배포

**전략**: Blue-Green Deployment

```
기존 코드 (Blue)  →  새 코드 (Green)
     ↓                    ↓
   동시 실행 (병렬 지원 기간)
     ↓                    ↓
  점진적 트래픽 이전
     ↓                    ↓
   완전 이전 → 기존 코드 제거
```

**기간**: 각 Phase 완료 후 2주 병렬 지원

### 1.2 하위 호환성 유지

**Deprecation 프로세스**:

1. **경고 단계** (2주): 기존 API 사용 시 경고 로그
2. **병렬 단계** (2주): 새/구 API 동시 지원
3. **마이그레이션 단계** (1주): 자동 변환 스크립트 제공
4. **제거 단계**: 기존 API 완전 제거

### 1.3 롤백 가능성 보장

**체크포인트**:

- 각 Phase 시작 전 DB 백업
- Git 태그로 버전 관리
- 환경 변수로 기능 토글

```python
# 기능 플래그 예시
USE_NEW_TRADE_ENGINE = os.getenv("USE_NEW_TRADE_ENGINE", "false") == "true"

if USE_NEW_TRADE_ENGINE:
    trade_engine = TradeEngine(config)
else:
    trade_engine = TradingSimulator(config)  # 레거시
```

---

## 2. Phase 1 마이그레이션

### 2.1 의존성 주입 개선 마이그레이션

#### Step 1: ServiceFactory 업데이트 (호환성 유지)

```python
# backend/app/services/service_factory.py

class ServiceFactory:
    # ... 기존 코드 ...

    def get_backtest_service(self, use_new_di: bool = True) -> BacktestService:
        """백테스트 서비스 반환

        Args:
            use_new_di: True면 새 DI 방식, False면 레거시 방식
        """
        if self._backtest_service is None:
            if use_new_di:
                # ✅ 새 방식: 생성자 주입
                market_data = self.get_market_data_service()
                strategy = self.get_strategy_service()
                db_manager = self.get_database_manager()

                self._backtest_service = BacktestService(
                    market_data_service=market_data,
                    strategy_service=strategy,
                    database_manager=db_manager,
                )
            else:
                # ❌ 레거시 방식: 후속 주입
                self._backtest_service = BacktestService()
                self._backtest_service.set_dependencies(
                    market_data_service=self.get_market_data_service(),
                    strategy_service=self.get_strategy_service(),
                )

        return self._backtest_service
```

#### Step 2: BacktestService 하위 호환 생성자

```python
# backend/app/services/backtest_service.py

class BacktestService:
    def __init__(
        self,
        market_data_service: Optional["MarketDataService"] = None,
        strategy_service: Optional["StrategyService"] = None,
        database_manager: Optional["DatabaseManager"] = None,
    ):
        """백테스트 서비스 초기화

        Args:
            market_data_service: 시장 데이터 서비스 (None이면 레거시 모드)
            strategy_service: 전략 서비스
            database_manager: DB 매니저
        """
        self.market_data_service = market_data_service
        self.strategy_service = strategy_service
        self.database_manager = database_manager

        # 새 방식: 즉시 초기화
        if all([market_data_service, strategy_service, database_manager]):
            self._initialize_dependencies()
            logger.info("BacktestService initialized (new DI)")
        else:
            # 레거시 방식: 지연 초기화
            logger.warning("BacktestService initialized (legacy mode)")

    def _initialize_dependencies(self):
        """의존성 초기화"""
        self.integrated_executor = IntegratedBacktestExecutor(
            market_data_service=self.market_data_service,
            strategy_service=self.strategy_service,
        )
        self.performance_calculator = PerformanceCalculator()

    def set_dependencies(self, market_data_service, strategy_service):
        """[DEPRECATED] 레거시 의존성 주입

        Warning:
            이 메서드는 Phase 1 완료 후 제거됩니다.
            대신 생성자 주입을 사용하세요.
        """
        import warnings
        warnings.warn(
            "set_dependencies() is deprecated. Use constructor injection.",
            DeprecationWarning,
            stacklevel=2,
        )

        self.market_data_service = market_data_service
        self.strategy_service = strategy_service
        self._initialize_dependencies()
```

#### Step 3: 환경 변수 토글

```bash
# .env
USE_NEW_DI=true  # Phase 1 완료 후
```

```python
# main.py
from app.core.config import get_settings

settings = get_settings()
use_new_di = settings.use_new_di  # 환경 변수에서 읽기

# ServiceFactory 호출 시
backtest_service = service_factory.get_backtest_service(use_new_di=use_new_di)
```

### 2.2 TradeEngine 마이그레이션

#### Step 1: TradeEngine 구현 및 테스트

```bash
# 1. TradeEngine 구현
# backend/app/services/backtest/trade_engine.py

# 2. 단위 테스트 작성
# backend/tests/test_trade_engine.py

# 3. 테스트 실행
cd backend && uv run pytest tests/test_trade_engine.py -v

# 4. 커버리지 확인
uv run pytest tests/test_trade_engine.py --cov=app.services.backtest.trade_engine --cov-report=html
```

#### Step 2: BacktestService에서 선택적 사용

```python
# backend/app/services/backtest_service.py

class BacktestService:
    def __init__(self, ..., use_new_trade_engine: bool = False):
        self.use_new_trade_engine = use_new_trade_engine

        if use_new_trade_engine:
            from app.services.backtest.trade_engine import TradeEngine
            self.trade_engine_class = TradeEngine
        else:
            self.trade_engine_class = TradingSimulator

    async def execute_backtest(self, ...):
        # 플래그에 따라 엔진 선택
        trade_engine = self.trade_engine_class(config=backtest.config)

        # 동일한 인터페이스
        portfolio_values, trades = trade_engine.simulate(signals)

        # ...
```

#### Step 3: A/B 테스트

```python
# tests/integration/test_trade_engine_migration.py

import pytest

@pytest.mark.parametrize("use_new_engine", [True, False])
async def test_trade_engine_results_match(use_new_engine):
    """새/구 엔진 결과 일치 검증"""

    # Given
    backtest_service = BacktestService(use_new_trade_engine=use_new_engine)

    # When
    result = await backtest_service.execute_backtest(...)

    # Then
    # 결과가 동일해야 함
    assert result.performance.total_return is not None

    # 결과 비교 (새/구 엔진 결과 허용 오차 1% 이내)
    if use_new_engine:
        save_result_for_comparison(result)
    else:
        compare_with_new_engine(result, tolerance=0.01)
```

### 2.3 전략 파라미터 마이그레이션

#### Step 1: 마이그레이션 스크립트

```python
# backend/scripts/migrate_strategy_params.py

"""
전략 파라미터 마이그레이션 스크립트

기존: Strategy.parameters (dict[str, Any])
신규: Strategy.config (Pydantic Config 객체)
"""

import asyncio
import logging
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.models.strategy import Strategy, StrategyType
from app.strategies.configs import (
    SMACrossoverConfig,
    RSIMeanReversionConfig,
    MomentumConfig,
    BuyAndHoldConfig,
)
from app.core.config import get_settings

logger = logging.getLogger(__name__)


CONFIG_MAP = {
    StrategyType.SMA_CROSSOVER: SMACrossoverConfig,
    StrategyType.RSI_MEAN_REVERSION: RSIMeanReversionConfig,
    StrategyType.MOMENTUM: MomentumConfig,
    StrategyType.BUY_AND_HOLD: BuyAndHoldConfig,
}


async def migrate():
    """마이그레이션 실행"""

    # 1. DB 연결
    settings = get_settings()
    client = AsyncIOMotorClient(settings.mongodb_url)
    await init_beanie(database=client.quant, document_models=[Strategy])

    logger.info("Starting strategy parameter migration...")

    # 2. 백업
    backup_file = f"backup_strategies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    await backup_strategies(backup_file)
    logger.info(f"Backup saved: {backup_file}")

    # 3. 마이그레이션
    strategies = await Strategy.find_all().to_list()

    migrated = 0
    failed = 0
    skipped = 0

    for strategy in strategies:
        try:
            # config 필드가 이미 있으면 스킵
            if hasattr(strategy, 'config') and strategy.config:
                logger.info(f"Skipped (already migrated): {strategy.name}")
                skipped += 1
                continue

            # parameters 필드가 없으면 스킵
            if not hasattr(strategy, 'parameters') or not strategy.parameters:
                logger.warning(f"Skipped (no parameters): {strategy.name}")
                skipped += 1
                continue

            # 변환
            config_class = CONFIG_MAP.get(strategy.strategy_type)
            if not config_class:
                logger.error(f"Unknown strategy type: {strategy.strategy_type}")
                failed += 1
                continue

            # Pydantic 검증
            try:
                config = config_class(**strategy.parameters)
            except Exception as e:
                logger.error(
                    f"Invalid parameters for {strategy.name}: {e}\n"
                    f"Parameters: {strategy.parameters}"
                )
                failed += 1
                continue

            # 업데이트
            strategy.config = config

            # parameters 필드 제거 (명시적)
            if hasattr(strategy, 'parameters'):
                delattr(strategy, 'parameters')

            await strategy.save()

            logger.info(f"Migrated: {strategy.name}")
            migrated += 1

        except Exception as e:
            logger.error(f"Migration failed for {strategy.name}: {e}")
            failed += 1

    # 4. 결과 보고
    logger.info(f"\nMigration completed:")
    logger.info(f"  Migrated: {migrated}")
    logger.info(f"  Skipped: {skipped}")
    logger.info(f"  Failed: {failed}")
    logger.info(f"  Total: {len(strategies)}")

    if failed > 0:
        logger.warning(f"\n⚠️  {failed} strategies failed. Check logs above.")
        logger.warning(f"Restore from backup if needed: {backup_file}")
    else:
        logger.info(f"\n✅ All strategies migrated successfully!")


async def backup_strategies(filename: str):
    """전략 백업"""
    import json

    strategies = await Strategy.find_all().to_list()

    backup_data = [
        {
            'id': str(strategy.id),
            'name': strategy.name,
            'strategy_type': strategy.strategy_type,
            'parameters': getattr(strategy, 'parameters', None),
            'config': getattr(strategy, 'config', None),
        }
        for strategy in strategies
    ]

    with open(filename, 'w') as f:
        json.dump(backup_data, f, indent=2, default=str)


async def restore_from_backup(filename: str):
    """백업 복원"""
    import json

    with open(filename, 'r') as f:
        backup_data = json.load(f)

    for item in backup_data:
        strategy = await Strategy.get(item['id'])
        if strategy:
            if 'parameters' in item and item['parameters']:
                strategy.parameters = item['parameters']

            if hasattr(strategy, 'config'):
                delattr(strategy, 'config')

            await strategy.save()
            logger.info(f"Restored: {item['name']}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(migrate())
```

#### Step 2: 검증 스크립트

```python
# backend/scripts/validate_migration.py

"""마이그레이션 검증 스크립트"""

import asyncio
from app.models.strategy import Strategy
from app.strategies.configs import CONFIG_MAP

async def validate():
    """마이그레이션 검증"""

    strategies = await Strategy.find_all().to_list()

    all_valid = True

    for strategy in strategies:
        # 1. config 필드 존재 확인
        if not hasattr(strategy, 'config'):
            print(f"❌ {strategy.name}: config field missing")
            all_valid = False
            continue

        # 2. config 타입 확인
        expected_type = CONFIG_MAP.get(strategy.strategy_type)
        if expected_type and not isinstance(strategy.config, expected_type):
            print(
                f"❌ {strategy.name}: "
                f"expected {expected_type.__name__}, "
                f"got {type(strategy.config).__name__}"
            )
            all_valid = False
            continue

        # 3. parameters 필드 존재 확인 (있으면 안됨)
        if hasattr(strategy, 'parameters'):
            print(f"⚠️  {strategy.name}: parameters field still exists")
            all_valid = False
            continue

        print(f"✅ {strategy.name}: valid")

    if all_valid:
        print("\n✅ All strategies validated successfully!")
    else:
        print("\n❌ Validation failed. Check errors above.")

    return all_valid

if __name__ == "__main__":
    asyncio.run(validate())
```

#### Step 3: 마이그레이션 실행

```bash
# 1. 백엔드 서버 중지
pnpm stop:backend

# 2. DB 백업
mongodump --uri="mongodb://localhost:27019/quant" --out=backup_$(date +%Y%m%d)

# 3. 마이그레이션 실행
cd backend
uv run python scripts/migrate_strategy_params.py

# 출력 예시:
# Starting strategy parameter migration...
# Backup saved: backup_strategies_20251013_143022.json
# Migrated: My SMA Strategy
# Migrated: RSI Strategy
# Skipped (already migrated): Test Strategy
#
# Migration completed:
#   Migrated: 8
#   Skipped: 2
#   Failed: 0
#   Total: 10

# 4. 검증
uv run python scripts/validate_migration.py

# 5. 서버 재시작
pnpm dev:backend

# 6. 통합 테스트
uv run pytest tests/integration/test_strategy_service.py -v
```

---

## 3. Phase 2 마이그레이션

### 3.1 BacktestOrchestrator 도입

#### 기존 코드 유지 + 새 코드 병렬

```python
# backend/app/services/backtest_service.py

class BacktestService:
    async def execute_backtest(
        self,
        backtest_id: str,
        strategy_id: str,
        use_orchestrator: bool = False,  # 플래그
    ) -> BacktestResult | None:
        """백테스트 실행

        Args:
            use_orchestrator: True면 새 Orchestrator 사용
        """

        if use_orchestrator:
            # ✅ 새 방식
            from app.services.backtest.orchestrator import BacktestOrchestrator

            orchestrator = BacktestOrchestrator(
                market_data_service=self.market_data_service,
                strategy_executor=...,
                trade_engine=...,
                performance_analyzer=...,
                data_processor=...,
            )

            return await orchestrator.execute(backtest_id, strategy_id)

        else:
            # ❌ 레거시 방식
            return await self._execute_backtest_legacy(backtest_id, strategy_id)

    async def _execute_backtest_legacy(self, backtest_id, strategy_id):
        """[DEPRECATED] 레거시 백테스트 실행"""
        # 기존 코드 그대로 유지
        ...
```

#### API 엔드포인트 업데이트

```python
# backend/app/api/routes/backtests.py

@router.post("/{backtest_id}/execute", response_model=BacktestExecutionResponse)
async def execute_backtest(
    backtest_id: str,
    request: BacktestExecutionRequest,
    use_new_executor: bool = Query(False, description="새 실행기 사용 여부"),
    service: BacktestService = Depends(get_backtest_service),
):
    """백테스트 실행

    Query Parameters:
        use_new_executor: true면 새 Orchestrator 사용 (Phase 2+)
    """

    result = await service.execute_backtest(
        backtest_id=backtest_id,
        strategy_id=request.strategy_id,
        use_orchestrator=use_new_executor,  # 사용자 선택
    )

    # ...
```

### 3.2 점진적 트래픽 이전

#### Week 1: 10% 트래픽

```python
# 무작위 10%만 새 실행기 사용
import random

use_orchestrator = random.random() < 0.10  # 10%
result = await service.execute_backtest(..., use_orchestrator=use_orchestrator)
```

#### Week 2: 50% 트래픽

```python
use_orchestrator = random.random() < 0.50  # 50%
```

#### Week 3: 100% 트래픽

```python
use_orchestrator = True  # 모두 새 실행기
```

#### Week 4: 레거시 코드 제거

```python
# _execute_backtest_legacy 메서드 삭제
# TradingSimulator 클래스 삭제
```

---

## 4. Phase 3-4 마이그레이션

### 4.1 DuckDB 활용 강화

#### 기존 MongoDB 데이터 → DuckDB 마이그레이션

```python
# scripts/migrate_to_duckdb.py

import asyncio
from app.models.backtest import BacktestResult
from app.services.database_manager import DatabaseManager

async def migrate_results_to_duckdb():
    """백테스트 결과를 DuckDB로 마이그레이션"""

    db_manager = DatabaseManager()
    conn = db_manager.duckdb_conn

    # 1. DuckDB 테이블 생성
    conn.execute("""
        CREATE TABLE IF NOT EXISTS backtest_results (
            result_id VARCHAR PRIMARY KEY,
            backtest_id VARCHAR,
            execution_id VARCHAR,
            total_return DOUBLE,
            sharpe_ratio DOUBLE,
            max_drawdown DOUBLE,
            created_at TIMESTAMP
        )
    """)

    # 2. MongoDB에서 데이터 읽기
    results = await BacktestResult.find_all().to_list()

    # 3. DuckDB로 삽입
    for result in results:
        conn.execute("""
            INSERT INTO backtest_results VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [
            str(result.id),
            result.backtest_id,
            result.execution_id,
            result.performance.total_return,
            result.performance.sharpe_ratio,
            result.performance.max_drawdown,
            result.created_at,
        ])

    logger.info(f"Migrated {len(results)} results to DuckDB")

if __name__ == "__main__":
    asyncio.run(migrate_results_to_duckdb())
```

---

## 5. 데이터 마이그레이션

### 5.1 MongoDB 스키마 변경

#### Strategy 컬렉션

**Before**:

```json
{
  "_id": "...",
  "name": "My SMA Strategy",
  "strategy_type": "sma_crossover",
  "parameters": {
    "short_window": 10,
    "long_window": 30
  }
}
```

**After**:

```json
{
  "_id": "...",
  "name": "My SMA Strategy",
  "strategy_type": "sma_crossover",
  "config": {
    "short_window": 10,
    "long_window": 30,
    "min_crossover_strength": 0.01,
    "lookback_period": 252,
    "max_position_size": 1.0
  }
}
```

#### 마이그레이션 명령

```javascript
// MongoDB shell
use quant;

// 1. 백업
db.strategies.aggregate([
  { $out: "strategies_backup_20251013" }
]);

// 2. 필드 이름 변경
db.strategies.updateMany(
  { parameters: { $exists: true } },
  { $rename: { "parameters": "config" } }
);

// 3. 기본값 추가
db.strategies.updateMany(
  { "config.lookback_period": { $exists: false } },
  { $set: { "config.lookback_period": 252 } }
);
```

### 5.2 DuckDB 스키마

```sql
-- 백테스트 결과 (고속 쿼리용)
CREATE TABLE backtest_results (
    result_id VARCHAR PRIMARY KEY,
    backtest_id VARCHAR,
    execution_id VARCHAR,
    strategy_id VARCHAR,
    strategy_type VARCHAR,

    -- 성과 지표
    total_return DOUBLE,
    annualized_return DOUBLE,
    volatility DOUBLE,
    sharpe_ratio DOUBLE,
    sortino_ratio DOUBLE,
    max_drawdown DOUBLE,

    -- 거래 통계
    total_trades INTEGER,
    win_rate DOUBLE,
    profit_factor DOUBLE,

    -- 메타데이터
    created_at TIMESTAMP,
    duration_seconds DOUBLE,

    INDEX idx_backtest_id (backtest_id),
    INDEX idx_strategy_id (strategy_id),
    INDEX idx_created_at (created_at)
);

-- 거래 기록 (분석용)
CREATE TABLE trades (
    trade_id VARCHAR PRIMARY KEY,
    execution_id VARCHAR,
    symbol VARCHAR,
    trade_type VARCHAR,  -- BUY, SELL
    quantity DOUBLE,
    price DOUBLE,
    timestamp TIMESTAMP,
    commission DOUBLE,
    slippage DOUBLE,

    INDEX idx_execution_id (execution_id),
    INDEX idx_symbol (symbol),
    INDEX idx_timestamp (timestamp)
);

-- 포트폴리오 이력 (차트용)
CREATE TABLE portfolio_history (
    id VARCHAR PRIMARY KEY,
    execution_id VARCHAR,
    timestamp TIMESTAMP,
    total_value DOUBLE,
    cash DOUBLE,
    positions_value DOUBLE,

    INDEX idx_execution_id (execution_id),
    INDEX idx_timestamp (timestamp)
);
```

---

## 6. API 호환성 관리

### 6.1 API 버전 관리

#### Option 1: Query Parameter

```python
# v1 (레거시)
GET /api/v1/backtests/{id}/execute

# v2 (새 아키텍처)
GET /api/v1/backtests/{id}/execute?version=2
```

#### Option 2: URL Path 버전

```python
# v1 (레거시)
GET /api/v1/backtests/{id}/execute

# v2 (새 아키텍처)
GET /api/v2/backtests/{id}/execute
```

**권장**: Query Parameter (유연성)

### 6.2 Deprecation 헤더

```python
# backend/app/api/routes/backtests.py

@router.post("/{backtest_id}/execute")
async def execute_backtest(
    backtest_id: str,
    response: Response,  # FastAPI Response 주입
    use_new_executor: bool = Query(False),
    ...
):
    if not use_new_executor:
        # Deprecation 경고
        response.headers["X-API-Deprecation"] = (
            "Legacy executor will be removed in v2.0. "
            "Use ?use_new_executor=true"
        )
        response.headers["X-API-Sunset"] = "2025-11-15"  # 제거 예정일

    # ...
```

### 6.3 프론트엔드 업데이트

```typescript
// frontend/src/hooks/useBacktest.ts

const executeBacktestMutation = useMutation({
  mutationFn: async (data: BacktestExecutionRequest) => {
    // 환경 변수로 제어
    const useNewExecutor = process.env.NEXT_PUBLIC_USE_NEW_EXECUTOR === "true";

    return await BacktestService.executeBacktest({
      body: data,
      query: {
        use_new_executor: useNewExecutor, // 쿼리 파라미터 추가
      },
    });
  },
  // ...
});
```

---

## 7. 롤백 전략

### 7.1 Phase별 롤백 절차

#### Phase 1 롤백

```bash
# 1. Git 리버트
git revert <phase-1-commit-hash>

# 2. 데이터 복원
mongorestore --uri="mongodb://localhost:27019" backup_20251013/

# 3. 환경 변수 원복
# .env
USE_NEW_DI=false
USE_NEW_TRADE_ENGINE=false

# 4. 서비스 재시작
pnpm dev:backend

# 5. 검증
curl http://localhost:8500/health
uv run pytest tests/integration/ -v
```

#### Phase 2 롤백

```bash
# 1. 기능 플래그 비활성화 (즉시)
# .env
USE_ORCHESTRATOR=false

# 2. 서비스 재시작 (다운타임 최소화)
docker-compose restart backend

# 3. Git 리버트 (필요 시)
git revert <phase-2-commit-hash>

# 4. 코드 배포
docker-compose up -d backend
```

### 7.2 롤백 트리거 조건

**자동 롤백**:

- 에러율 5% 초과
- 응답 시간 2배 증가
- 메모리 사용량 150% 초과

**수동 롤백**:

- 치명적 버그 발견
- 데이터 손실 위험
- 사용자 불만 급증

### 7.3 롤백 테스트

```python
# tests/rollback/test_rollback_procedures.py

import pytest

async def test_rollback_to_legacy_di():
    """DI 롤백 테스트"""

    # Given - 새 방식으로 서비스 생성
    service = service_factory.get_backtest_service(use_new_di=True)

    # When - 레거시 방식으로 롤백
    service_factory.reset()  # 캐시 클리어
    legacy_service = service_factory.get_backtest_service(use_new_di=False)

    # Then - 정상 작동 확인
    backtest = await legacy_service.create_backtest(...)
    assert backtest is not None

async def test_rollback_data_migration():
    """데이터 마이그레이션 롤백 테스트"""

    # Given - 백업 파일
    backup_file = "backup_strategies_20251013.json"

    # When - 복원
    await restore_from_backup(backup_file)

    # Then - 데이터 일치 확인
    strategies = await Strategy.find_all().to_list()
    for strategy in strategies:
        assert hasattr(strategy, 'parameters')  # 레거시 필드
        assert not hasattr(strategy, 'config')  # 새 필드 없음
```

---

## 8. 체크리스트

### Phase 1 마이그레이션 체크리스트

**준비 단계**:

- [ ] 백업 자동화 스크립트 작성
- [ ] 마이그레이션 스크립트 작성
- [ ] 검증 스크립트 작성
- [ ] 롤백 절차 문서화

**실행 단계**:

- [ ] DB 백업 (MongoDB + DuckDB)
- [ ] 마이그레이션 실행 (스테이징)
- [ ] 검증 스크립트 실행
- [ ] 통합 테스트 (스테이징)
- [ ] 프로덕션 배포
- [ ] 모니터링 (24시간)

**완료 확인**:

- [ ] 에러율 < 1%
- [ ] 응답 시간 증가 < 10%
- [ ] 메모리 사용량 정상
- [ ] 기능 테스트 100% 통과

**정리 단계**:

- [ ] 레거시 코드 제거 (2주 후)
- [ ] Deprecation 경고 제거
- [ ] 문서 업데이트
- [ ] CHANGELOG 작성

---

**참고 문서**:

- [아키텍처 검토](./ARCHITECTURE_REVIEW.md)
- [Phase 1 가이드](./REFACTORING_PHASE1.md)
- [새 아키텍처](./NEW_ARCHITECTURE.md)
