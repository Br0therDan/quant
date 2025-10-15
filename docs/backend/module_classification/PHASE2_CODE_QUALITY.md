# Phase 2: 코드 품질 개선 및 레거시 정리

**시작 예정일**: Phase 1 완료 후  
**예상 소요**: 2-3주  
**목적**: 도메인 경계가 명확해진 코드베이스의 품질 향상  
**전제 조건**: Phase 1 완료 (✅ 2025-10-15)

---

## Phase 2 개요

### 배경

Phase 1에서 도메인별 디렉토리 구조화를 완료했습니다. 이제 **내부 코드 품질**을
개선할 차례입니다.

- ✅ Phase 1 완료: 도메인 경계 명확화 (Trading, ML Platform, Gen AI, User)
- 🎯 Phase 2 목표: 코드 품질, 테스트, 문서화 개선
- ⏸️ Phase 3-4 보류: MSA 전환은 전체 개발 완료 후

### Phase 2 vs Phase 3-4

| 구분          | Phase 2 (진행 예정)    | Phase 3-4 (전체 개발 완료 후) |
| ------------- | ---------------------- | ----------------------------- |
| **범위**      | 모노리스 내부 리팩토링 | 서비스 분리, 인프라 구축      |
| **API 변경**  | 없음 (내부 구조만)     | 큼 (Gateway, Event Bus)       |
| **배포 방식** | 기존 방식 유지         | Kubernetes, Service Mesh      |
| **진행 시점** | 개발 진행 중           | 전체 기능 완료 후             |
| **소요 시간** | 2-3주                  | 2-3개월                       |

---

## 현황 분석

### 1. 대형 파일 현황 (200+ lines)

```bash
# Phase 1 완료 후 확인
cd backend
find app/services -name "*.py" -exec wc -l {} \; | sort -rn | head -20
```

**예상 결과**:

- `market_data_service/stock.py`: 300+ lines
- `backtest_service.py`: 500+ lines (복잡한 실행 로직)
- `model_lifecycle_service.py`: 400+ lines (MLOps 로직)

**문제점**:

- 단일 책임 원칙(SRP) 위반
- 테스트 작성 어려움
- 코드 이해 및 유지보수 어려움

---

### 2. 중복 코드 현황

**예상 중복 패턴**:

1. **성과 계산 로직**

   - `backtest_service.py`
   - `portfolio_service.py`
   - `performance.py` (모델)
   - 중복도: 약 150 lines

2. **데이터 검증 로직**

   - 각 서비스에서 개별 구현
   - 일관성 부족
   - 중복도: 약 200 lines

3. **Signal 변환**
   - `strategy_service.py`
   - `ml_signal_service.py`
   - 중복도: 약 100 lines

**측정 방법**:

```bash
# CPD (Copy/Paste Detector)
pmd cpd --minimum-tokens 50 --files app/
```

---

### 3. 테스트 커버리지 현황

**현재 상태** (Phase 1 완료 후):

```bash
cd backend
uv run pytest --cov=app --cov-report=term-missing
```

**예상 커버리지**:

- 전체: 80%
- Trading 도메인: 85% (백테스트 중심)
- ML Platform: 70% (신규 기능)
- Gen AI: 60% (최근 추가)
- User: 75%

**문제점**:

- 통합 테스트 부족 (E2E 시나리오)
- Edge case 테스트 부족
- Mock 남용 (실제 동작 검증 부족)

---

### 4. 타입 안정성 현황

```bash
# mypy strict mode
uv run mypy app/ --strict
```

**예상 문제점**:

- 타입 힌트 누락: 약 30%
- Any 타입 남용
- Optional 처리 불완전

---

## Phase 2 작업 계획

### Step 1: 대형 파일 분할 (1주)

#### 1.1 `backtest_service.py` 분할

**현재** (500+ lines):

```python
class BacktestService:
    async def run_backtest(self, ...):  # 150 lines
        # 검증
        # 데이터 로딩
        # 전략 실행
        # 성과 계산
        # 결과 저장
        ...
```

**개선 후**:

```
services/trading/
├── backtest_service.py          # 코어 로직 (100 lines)
├── backtest_validator.py        # 검증 (60 lines)
├── backtest_executor.py         # 실행 (80 lines)
└── backtest_calculator.py       # 성과 계산 (70 lines)
```

**작업 순서**:

1. 검증 로직 → `backtest_validator.py`
2. 계산 로직 → `backtest_calculator.py`
3. 실행 로직 → `backtest_executor.py`
4. `backtest_service.py`는 조율만 담당

---

#### 1.2 `model_lifecycle_service.py` 분할

**현재** (400+ lines):

```python
class ModelLifecycleService:
    async def create_experiment(self, ...):  # 100 lines
    async def log_run(self, ...):            # 80 lines
    async def deploy_model(self, ...):       # 120 lines
    async def monitor_drift(self, ...):      # 100 lines
```

**개선 후**:

```
services/ml_platform/
├── model_lifecycle_service.py   # 코어 로직 (100 lines)
├── experiment_manager.py        # 실험 관리 (80 lines)
├── deployment_manager.py        # 배포 관리 (120 lines)
└── drift_monitor.py             # 드리프트 모니터링 (100 lines)
```

---

#### 1.3 전략 파일 구조 개선

**현재**:

```
strategies/
├── base_strategy.py             # 200 lines
├── sma_crossover_strategy.py
├── rsi_mean_reversion_strategy.py
└── ...
```

**개선 후**:

```
strategies/
├── core/                        # 핵심 로직
│   ├── base_strategy.py         # 100 lines
│   ├── signal_generator.py      # 50 lines
│   └── position_manager.py      # 50 lines
├── indicators/                  # 기술 지표
│   ├── trend.py
│   └── momentum.py
└── implementations/             # 구현체
    ├── sma_crossover.py
    └── rsi_mean_reversion.py
```

---

### Step 2: 중복 코드 제거 (3-4일)

#### 2.1 공통 유틸리티 모듈 생성

```
backend/app/utils/
├── validators/
│   ├── __init__.py
│   ├── backtest.py              # 백테스트 검증
│   ├── strategy.py              # 전략 검증
│   └── market_data.py           # 데이터 검증
├── calculators/
│   ├── __init__.py
│   ├── performance.py           # 성과 지표 계산
│   ├── risk.py                  # 리스크 지표 계산
│   └── portfolio.py             # 포트폴리오 계산
└── transformers/
    ├── __init__.py
    ├── signal.py                # Signal 변환
    └── market_data.py           # 데이터 변환
```

---

#### 2.2 성과 계산 로직 통합

**Before** (중복):

```python
# backtest_service.py
def calculate_sharpe_ratio(returns):
    return np.mean(returns) / np.std(returns) * np.sqrt(252)

# portfolio_service.py
def get_sharpe_ratio(returns):
    return (returns.mean() / returns.std()) * np.sqrt(252)
```

**After** (통합):

```python
# utils/calculators/performance.py
class PerformanceCalculator:
    @staticmethod
    def sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
        """
        샤프 비율 계산

        Args:
            returns: 일별 수익률
            risk_free_rate: 무위험 수익률 (연율)

        Returns:
            샤프 비율
        """
        excess_returns = returns - risk_free_rate / 252
        return np.sqrt(252) * excess_returns.mean() / excess_returns.std()

    @staticmethod
    def sortino_ratio(returns: pd.Series, target_return: float = 0.0) -> float:
        """소르티노 비율 계산"""
        ...

    @staticmethod
    def max_drawdown(equity_curve: pd.Series) -> float:
        """최대 낙폭 계산"""
        ...
```

**사용**:

```python
# backtest_service.py
from app.utils.calculators.performance import PerformanceCalculator

sharpe = PerformanceCalculator.sharpe_ratio(returns)
```

---

#### 2.3 검증 로직 통합

**Before** (분산):

```python
# 각 서비스에서 개별 구현
if not symbol or len(symbol) > 10:
    raise ValueError("Invalid symbol")
```

**After** (통합):

```python
# utils/validators/market_data.py
from pydantic import BaseModel, field_validator

class MarketDataValidator:
    @staticmethod
    def validate_symbol(symbol: str) -> str:
        """심볼 검증"""
        if not symbol:
            raise ValueError("Symbol is required")
        if len(symbol) > 10:
            raise ValueError("Symbol too long")
        if not symbol.isalnum():
            raise ValueError("Symbol must be alphanumeric")
        return symbol.upper()

    @staticmethod
    def validate_date_range(start: str, end: str) -> tuple[str, str]:
        """날짜 범위 검증"""
        ...
```

---

### Step 3: 테스트 커버리지 개선 (3-4일)

#### 3.1 단위 테스트 추가

**우선순위**:

1. Phase 1에서 이동한 파일들
2. 복잡한 비즈니스 로직
3. Edge cases

**예시**: `backtest_calculator.py` 테스트

```python
# tests/services/trading/test_backtest_calculator.py
import pytest
from app.services.trading.backtest_calculator import BacktestCalculator

class TestBacktestCalculator:
    def test_calculate_performance_metrics_basic(self):
        """기본 성과 지표 계산 테스트"""
        trades = [...]
        metrics = BacktestCalculator.calculate_performance_metrics(trades)

        assert metrics.total_return > 0
        assert metrics.sharpe_ratio > 1.0
        assert 0 < metrics.win_rate < 1

    def test_calculate_performance_metrics_no_trades(self):
        """거래 없을 때 예외 처리"""
        with pytest.raises(ValueError):
            BacktestCalculator.calculate_performance_metrics([])

    def test_calculate_performance_metrics_all_losses(self):
        """모든 거래가 손실일 때"""
        trades = [Trade(pnl=-100), Trade(pnl=-50)]
        metrics = BacktestCalculator.calculate_performance_metrics(trades)

        assert metrics.total_return < 0
        assert metrics.win_rate == 0
```

---

#### 3.2 통합 테스트 강화

**E2E 백테스트 시나리오**:

```python
# tests/e2e/test_backtest_flow.py
@pytest.mark.e2e
async def test_full_backtest_flow():
    """전체 백테스트 플로우 테스트"""
    # 1. 전략 생성
    strategy = await create_strategy(...)

    # 2. 백테스트 실행
    backtest = await run_backtest(strategy_id=strategy.id)

    # 3. 결과 검증
    result = await get_backtest_result(backtest.id)
    assert result.status == "completed"
    assert result.metrics.total_return != 0

    # 4. 최적화 실행
    optimization = await optimize_strategy(strategy.id)
    assert len(optimization.trials) > 0

    # 5. 최적 파라미터로 재실행
    optimized_backtest = await run_backtest(
        strategy_id=strategy.id,
        params=optimization.best_params
    )
    assert optimized_backtest.metrics.sharpe_ratio > result.metrics.sharpe_ratio
```

---

#### 3.3 ML Pipeline 테스트

```python
# tests/e2e/test_ml_pipeline.py
@pytest.mark.e2e
async def test_ml_model_lifecycle():
    """ML 모델 생명주기 테스트"""
    # 1. 실험 생성
    experiment = await create_experiment(name="test_exp")

    # 2. 피처 추출
    features = await extract_features(symbols=["AAPL", "GOOGL"])

    # 3. 모델 학습
    run = await train_model(experiment_id=experiment.id, features=features)
    assert run.metrics["accuracy"] > 0.7

    # 4. 모델 평가
    eval_result = await evaluate_model(run.id)
    assert eval_result.test_score > 0.65

    # 5. 모델 배포
    deployment = await deploy_model(run.id, stage="production")
    assert deployment.status == "active"

    # 6. 예측 실행
    prediction = await predict(deployment.id, input_data={...})
    assert prediction.confidence > 0.5
```

---

### Step 4: 문서화 및 타입 안정성 (2-3일)

#### 4.1 타입 힌트 완성

**Before**:

```python
def calculate_metrics(trades):
    total = sum(t.pnl for t in trades)
    return total
```

**After**:

```python
from typing import List
from app.models.trading.backtest import Trade

def calculate_metrics(trades: List[Trade]) -> float:
    """
    거래 리스트에서 총 수익 계산

    Args:
        trades: 거래 내역 리스트

    Returns:
        총 수익 (단위: USD)

    Raises:
        ValueError: 거래 리스트가 비어있을 때
    """
    if not trades:
        raise ValueError("Trade list is empty")

    total: float = sum(t.pnl for t in trades)
    return total
```

---

#### 4.2 Docstring 표준화 (Google Style)

```python
class BacktestService:
    """백테스트 실행 및 관리 서비스

    전략에 대한 백테스트를 실행하고 결과를 저장합니다.

    Attributes:
        db_manager: 데이터베이스 매니저
        market_data_service: 시장 데이터 서비스

    Example:
        >>> service = service_factory.get_backtest_service()
        >>> result = await service.run_backtest(
        ...     strategy_id="123",
        ...     start_date="2024-01-01",
        ...     end_date="2024-12-31"
        ... )
        >>> print(result.metrics.sharpe_ratio)
        1.85
    """

    async def run_backtest(
        self,
        strategy_id: str,
        start_date: str,
        end_date: str,
        initial_capital: float = 100000.0
    ) -> BacktestResult:
        """백테스트 실행

        지정된 전략으로 백테스트를 실행하고 결과를 반환합니다.

        Args:
            strategy_id: 전략 ID
            start_date: 시작일 (YYYY-MM-DD)
            end_date: 종료일 (YYYY-MM-DD)
            initial_capital: 초기 자본 (기본값: $100,000)

        Returns:
            백테스트 결과 (성과 지표 포함)

        Raises:
            ValueError: 전략을 찾을 수 없을 때
            ValidationError: 날짜 형식이 잘못되었을 때
            RuntimeError: 백테스트 실행 중 오류 발생

        Example:
            >>> result = await service.run_backtest(
            ...     strategy_id="sma-crossover-001",
            ...     start_date="2024-01-01",
            ...     end_date="2024-12-31"
            ... )
            >>> print(f"Sharpe Ratio: {result.metrics.sharpe_ratio:.2f}")
            Sharpe Ratio: 1.85
        """
        ...
```

---

#### 4.3 OpenAPI 스키마 개선

**Before**:

```python
@router.post("/backtests")
async def create_backtest(data: BacktestCreate):
    ...
```

**After**:

```python
@router.post(
    "/backtests",
    response_model=BacktestResponse,
    status_code=201,
    responses={
        201: {
            "description": "백테스트 생성 성공",
            "content": {
                "application/json": {
                    "example": {
                        "id": "bt_123abc",
                        "status": "queued",
                        "strategy_id": "st_456def",
                        "created_at": "2024-01-15T10:30:00Z"
                    }
                }
            }
        },
        400: {"description": "잘못된 요청 (검증 실패)"},
        404: {"description": "전략을 찾을 수 없음"},
        422: {"description": "처리할 수 없는 엔티티"},
    }
)
async def create_backtest(
    data: BacktestCreate = Body(
        ...,
        description="백테스트 생성 요청",
        example={
            "strategy_id": "st_456def",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "initial_capital": 100000.0,
            "config": {
                "commission": 0.001,
                "slippage": 0.0005
            }
        }
    )
) -> BacktestResponse:
    """
    백테스트 생성

    지정된 전략으로 새로운 백테스트를 생성합니다.
    백테스트는 비동기로 실행되며, 상태는 /backtests/{id} 엔드포인트로 확인할 수 있습니다.
    """
    ...
```

---

## Phase 2 성공 지표

### 정량적 지표

| 지표                      | Phase 1 완료 | Phase 2 목표 | 측정 방법       |
| ------------------------- | ------------ | ------------ | --------------- |
| **200+ lines 파일**       | 0개          | 0개 (유지)   | `wc -l`         |
| **100+ lines 함수**       | 5+           | 0개          | `radon cc`      |
| **중복 코드 (CPD)**       | 15%          | 5% 이하      | `pmd cpd`       |
| **테스트 커버리지**       | 80%          | 85%+         | `pytest --cov`  |
| **타입 힌트 커버리지**    | 70%          | 95%+         | `mypy --strict` |
| **Cyclomatic Complexity** | 평균 15      | 평균 10 이하 | `radon cc`      |
| **Docstring 커버리지**    | 60%          | 90%+         | `pydocstyle`    |

---

### 정성적 지표

- [ ] 모든 public API에 예제 포함
- [ ] OpenAPI 문서에 모든 에러 코드 설명
- [ ] 통합 테스트로 주요 유저 플로우 커버
- [ ] mypy strict mode 통과
- [ ] 신규 개발자가 README만으로 시작 가능

---

## 실행 가이드

### 사전 준비

```bash
# 1. 현재 상태 측정
cd backend

# 파일 크기 분포
find app -name "*.py" -exec wc -l {} \; | sort -rn > file_sizes.txt

# 테스트 커버리지
uv run pytest --cov=app --cov-report=html
open htmlcov/index.html

# 중복 코드 (pmd 설치 필요)
pmd cpd --minimum-tokens 50 --files app/ > cpd_report.txt

# Cyclomatic Complexity
uv run radon cc app/ -a -s > complexity_report.txt

# 타입 체크
uv run mypy app/ --strict 2>&1 | tee mypy_baseline.txt
```

---

### Step별 진행

#### Step 1: 대형 파일 분할

```bash
# 1. 분할 대상 식별
grep "def " app/services/trading/backtest_service.py | wc -l

# 2. 새 파일 생성
touch app/services/trading/backtest_validator.py
touch app/services/trading/backtest_executor.py
touch app/services/trading/backtest_calculator.py

# 3. 로직 이동
# (수동 작업 - IDE 리팩토링 도구 사용 권장)

# 4. 테스트 실행
uv run pytest tests/services/trading/

# 5. 커밋
git add app/services/trading/
git commit -m "refactor: split backtest_service into smaller modules"
```

---

#### Step 2: 중복 코드 제거

```bash
# 1. 유틸리티 디렉토리 생성
mkdir -p app/utils/{validators,calculators,transformers}

# 2. 공통 로직 추출
# (수동 작업)

# 3. 중복 코드 재확인
pmd cpd --minimum-tokens 50 --files app/

# 4. 테스트 실행
uv run pytest

# 5. 커밋
git add app/utils/
git commit -m "refactor: extract common utilities to reduce duplication"
```

---

#### Step 3: 테스트 커버리지 개선

```bash
# 1. 커버리지 측정
uv run pytest --cov=app --cov-report=term-missing

# 2. 누락된 영역 테스트 추가
# (tests/ 디렉토리에 추가)

# 3. E2E 테스트 작성
touch tests/e2e/test_backtest_flow.py
touch tests/e2e/test_ml_pipeline.py

# 4. 테스트 실행
uv run pytest tests/e2e/ -v

# 5. 커버리지 재확인
uv run pytest --cov=app --cov-report=html

# 6. 커밋
git add tests/
git commit -m "test: improve test coverage to 85%"
```

---

#### Step 4: 문서화 및 타입 안정성

```bash
# 1. 타입 힌트 추가
# (수동 작업 - IDE 도구 활용)

# 2. mypy 검사
uv run mypy app/ --strict

# 3. Docstring 추가
# (Google Style)

# 4. pydocstyle 검사
uv run pydocstyle app/

# 5. OpenAPI 예제 추가
# (routes 파일 수정)

# 6. 문서 생성
cd docs && make html

# 7. 커밋
git add app/
git commit -m "docs: add comprehensive docstrings and type hints"
```

---

### 검증 체크리스트

**Step 1 완료 후**:

- [ ] 모든 파일 200 lines 이하
- [ ] pytest 전체 통과
- [ ] pnpm gen:client 성공
- [ ] Frontend 빌드 성공

**Step 2 완료 후**:

- [ ] CPD 중복도 5% 이하
- [ ] 새 유틸리티 모듈 테스트 100%
- [ ] pytest 전체 통과

**Step 3 완료 후**:

- [ ] 테스트 커버리지 85%+
- [ ] E2E 테스트 30+ 개
- [ ] pytest 전체 통과

**Step 4 완료 후**:

- [ ] mypy --strict 통과
- [ ] pydocstyle 에러 0개
- [ ] OpenAPI 문서 완성도 90%+

---

## 위험 관리

### 주요 위험

1. **리팩토링 중 버그 유입**

   - **확률**: 중간
   - **영향**: 높음
   - **대응**: 각 단계마다 전체 테스트 실행, PR 리뷰 강화

2. **테스트 작성 시간 초과**

   - **확률**: 높음
   - **영향**: 중간
   - **대응**: 핵심 로직 우선, 80% 달성 후 평가

3. **타입 힌트 적용 어려움**

   - **확률**: 중간
   - **영향**: 낮음
   - **대응**: strict mode 점진적 적용, Any 타입 허용 범위 설정

4. **팀원 코드 리뷰 부담**
   - **확률**: 낮음
   - **영향**: 중간
   - **대응**: PR 단위 작게 분할, 리뷰 가이드 작성

---

### 대응 전략

#### 점진적 적용

```bash
# mypy strict mode를 점진적으로 적용
# 1. 새 코드부터 strict
# 2. 기존 코드는 disallow_untyped_defs만
uv run mypy app/utils/ --strict
uv run mypy app/services/ --disallow-untyped-defs
```

#### 롤백 계획

```bash
# 각 Step마다 태그 생성
git tag phase2-step1-complete
git tag phase2-step2-complete

# 문제 발생 시 롤백
git reset --hard phase2-step1-complete
```

---

## Phase 2 완료 후

### 기대 효과

1. **개발 속도 향상**

   - 공통 유틸리티로 코드 재사용
   - 명확한 구조로 기능 추가 용이

2. **버그 감소**

   - 높은 테스트 커버리지
   - 타입 안정성 향상

3. **협업 효율 개선**

   - 완벽한 문서화
   - 일관된 코드 스타일

4. **유지보수 비용 절감**
   - 작은 모듈 단위
   - 명확한 책임 분리

---

### Phase 3-4 준비 상태

Phase 2 완료 후:

- ✅ 깨끗한 코드베이스
- ✅ 높은 테스트 커버리지
- ✅ 명확한 도메인 경계
- ⏸️ MSA 전환 대기 (전체 개발 완료 후)

---

## 참고 자료

### 코드 품질 도구

- [Radon](https://radon.readthedocs.io/): Complexity 측정
- [PMD CPD](https://pmd.github.io/): 중복 코드 검출
- [mypy](https://mypy.readthedocs.io/): 정적 타입 체크
- [pydocstyle](http://www.pydocstyle.org/): Docstring 검증

### 베스트 프랙티스

- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Clean Code in Python](https://github.com/zedr/clean-code-python)
- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)

---

**작성일**: 2025-10-15  
**작성자**: Backend Team  
**상태**: 📋 계획 중
