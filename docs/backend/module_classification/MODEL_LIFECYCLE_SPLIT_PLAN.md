# Phase 2.2a: model_lifecycle_service.py 모듈 분할 계획

## 현재 상태 분석

**파일**: `backend/app/services/ml_platform/services/model_lifecycle_service.py`
**라인 수**: 476 lines (1 class: ModelLifecycleService)

### 메서드 분류 (25개 메서드 + 1 유틸리티 함수)

#### 1. Experiment Management (4 메서드, ~100 lines)

- `create_experiment()` - 실험 생성
- `update_experiment()` - 실험 업데이트
- `list_experiments()` - 실험 목록 조회 (owner, status 필터)
- `get_experiment()` - 실험 조회 (name)

#### 2. Run Tracking (5 메서드, ~120 lines)

- `log_run()` - Run 기록 (MLflow 동기화 포함)
- `update_run()` - Run 업데이트
- `list_runs()` - Run 목록 조회 (experiment_name, statuses 필터)
- `get_run()` - Run 조회 (run_id)
- `_sync_run_to_mlflow()` - MLflow 동기화 (private, ~40 lines)

#### 3. Model Registry (6 메서드, ~120 lines)

- `register_model_version()` - 모델 버전 등록
- `update_model_version()` - 모델 버전 업데이트
- `compare_model_versions()` - 모델 버전 비교 (메트릭)
- `list_model_versions()` - 모델 버전 목록 조회
- `get_model_version()` - 모델 버전 조회
- `set_stage()` - 모델 스테이지 설정 (Staging, Production, etc.)

#### 4. Approval & Checklist (3 메서드, ~60 lines)

- `append_checklist_item()` - 체크리스트 항목 추가
- `mark_checklist_status()` - 체크리스트 상태 업데이트
- `build_checklist()` - 유틸리티 함수 (체크리스트 생성)

#### 5. Drift Monitoring (2 메서드, ~50 lines)

- `record_drift_event()` - 드리프트 이벤트 기록
- `list_drift_events()` - 드리프트 이벤트 목록 조회

#### 6. Deployment Management (Phase 4 D4, 5 메서드, ~120 lines)

- `list_deployments()` - 배포 목록 조회
- `create_deployment()` - 배포 생성
- `get_deployment()` - 배포 조회
- `update_deployment()` - 배포 업데이트
- (Phase 4 기능, 프로덕션 배포 관리)

---

## 분할 전략

### 원칙

1. **Domain 분리**: Experiment, Run, Registry, Approval, Drift, Deployment
2. **단일 책임**: 각 모듈은 하나의 생명주기 단계만 담당
3. **MLflow 통합 유지**: Run 모듈에서 MLflow 동기화 처리
4. **타입 안전성**: 모든 메서드 타입 힌트 유지

### 모듈 구조 (6개 파일)

```
backend/app/services/ml_platform/services/model_lifecycle_service/
├── __init__.py              # ModelLifecycleService 통합 (200 lines)
├── experiment.py            # ExperimentManager (105 lines)
├── run.py                   # RunTracker (130 lines, MLflow 포함)
├── registry.py              # ModelRegistry (135 lines)
├── approval.py              # ApprovalManager (75 lines, checklist)
├── drift.py                 # DriftMonitor (60 lines)
└── deployment.py            # DeploymentManager (130 lines, Phase 4)
```

**Total**: 835 lines (+75% for clarity, MLflow 통합, Phase 4 기능 포함)

---

## 모듈별 상세 설계

### 1. experiment.py (105 lines)

**책임**: Experiment CRUD 작업

```python
"""Model Experiment Management"""

class ExperimentManager:
    def __init__(self):
        pass

    async def create_experiment(self, payload: dict[str, Any]) -> ModelExperiment:
        """실험 생성"""

    async def update_experiment(
        self, name: str, updates: dict[str, Any]
    ) -> ModelExperiment | None:
        """실험 업데이트"""

    async def list_experiments(
        self, *, owner: str | None = None, status: ExperimentStatus | None = None
    ) -> list[ModelExperiment]:
        """실험 목록 조회 (owner, status 필터)"""

    async def get_experiment(self, name: str) -> ModelExperiment | None:
        """실험 조회 (name)"""
```

**특징**:

- Beanie ODM 기반 CRUD
- ExperimentStatus 필터링 지원
- 중복 실험명 검증

---

### 2. run.py (130 lines)

**책임**: Run 추적 및 MLflow 동기화

```python
"""Model Run Tracking with MLflow Integration"""

class RunTracker:
    def __init__(self, tracking_uri: str | None = None):
        self._tracking_uri = tracking_uri or os.getenv("MLFLOW_TRACKING_URI")
        self._mlflow_available = self._check_mlflow_availability()

    def _check_mlflow_availability(self) -> bool:
        """MLflow 사용 가능 여부 확인"""

    async def log_run(self, payload: dict[str, Any]) -> ModelRun:
        """Run 기록 (MLflow 자동 동기화)"""

    async def update_run(self, run_id: str, payload: dict[str, Any]) -> ModelRun | None:
        """Run 업데이트 (상태, 메트릭)"""

    async def list_runs(
        self, *, experiment_name: str | None = None, statuses: Iterable[RunStatus] | None = None
    ) -> list[ModelRun]:
        """Run 목록 조회"""

    async def get_run(self, run_id: str) -> ModelRun | None:
        """Run 조회"""

    async def _sync_run_to_mlflow(
        self, run: ModelRun, update_only: bool = False
    ) -> None:
        """MLflow 동기화 (parameters, metrics, artifacts, tags)"""
```

**특징**:

- MLflow 선택적 통합 (fallback to document-only tracking)
- RunStatus 필터링 (RUNNING, COMPLETED, FAILED)
- Parameters, Metrics, Artifacts 자동 동기화

---

### 3. registry.py (135 lines)

**책임**: 모델 버전 관리 및 비교

```python
"""Model Registry and Version Management"""

class ModelRegistry:
    def __init__(self):
        pass

    async def register_model_version(self, payload: dict[str, Any]) -> ModelVersion:
        """모델 버전 등록"""

    async def update_model_version(
        self, model_name: str, version: str, payload: dict[str, Any]
    ) -> ModelVersion | None:
        """모델 버전 업데이트"""

    async def compare_model_versions(
        self, model_name: str, versions: list[str]
    ) -> dict[str, dict[str, float]]:
        """모델 버전 메트릭 비교 (성능 평가)"""

    async def list_model_versions(
        self, *, model_name: str | None = None, stage: ModelStage | None = None
    ) -> list[ModelVersion]:
        """모델 버전 목록 조회"""

    async def get_model_version(
        self, model_name: str, version: str
    ) -> ModelVersion | None:
        """모델 버전 조회"""

    async def set_stage(
        self, model_name: str, version: str, stage: ModelStage
    ) -> ModelVersion | None:
        """스테이지 설정 (None, Staging, Production, Archived)"""
```

**특징**:

- 중복 버전 검증
- 메트릭 비교 (여러 버전의 성능 평가)
- ModelStage 관리 (Staging → Production 전환)

---

### 4. approval.py (75 lines)

**책임**: 배포 승인 및 체크리스트 관리

```python
"""Deployment Approval and Checklist Management"""

class ApprovalManager:
    def __init__(self):
        pass

    async def append_checklist_item(
        self, model_name: str, version: str, item: DeploymentChecklistItem
    ) -> ModelVersion | None:
        """체크리스트 항목 추가"""

    async def mark_checklist_status(
        self,
        model_name: str,
        version: str,
        *,
        checklist: list[DeploymentChecklistItem] | None = None,
        approved_by: str | None = None,
        approval_notes: str | None = None,
    ) -> ModelVersion | None:
        """체크리스트 상태 업데이트 및 승인 처리"""


def build_checklist(
    items: Iterable[str],
    *,
    default_status: str = "pending",
) -> list[DeploymentChecklistItem]:
    """체크리스트 생성 유틸리티"""
```

**특징**:

- DeploymentChecklistItem 관리 (PENDING, APPROVED, REJECTED)
- 승인자 및 승인 시간 기록
- 유틸리티 함수 (체크리스트 초기화)

---

### 5. drift.py (60 lines)

**책임**: 모델 드리프트 감지 및 모니터링

```python
"""Model Drift Monitoring"""

class DriftMonitor:
    def __init__(self):
        pass

    async def record_drift_event(self, payload: dict[str, Any]) -> DriftEvent:
        """드리프트 이벤트 기록 (경고 로그)"""

    async def list_drift_events(
        self, *, model_name: str | None = None, severity: DriftSeverity | None = None
    ) -> list[DriftEvent]:
        """드리프트 이벤트 목록 조회 (심각도 필터)"""
```

**특징**:

- DriftSeverity (LOW, MEDIUM, HIGH, CRITICAL)
- 메트릭별 드리프트 감지 (accuracy, precision, recall)
- 경고 로그 자동 생성

---

### 6. deployment.py (130 lines)

**책임**: 프로덕션 배포 관리 (Phase 4 D4)

```python
"""Model Deployment Management (Phase 4 D4)"""

class DeploymentManager:
    def __init__(self):
        pass

    async def list_deployments(
        self,
        model_name: str | None = None,
        environment: DeploymentEnvironment | None = None,
        status: DeploymentStatus | None = None,
    ) -> list[Deployment]:
        """배포 목록 조회"""

    async def create_deployment(self, payload: dict[str, Any]) -> Deployment:
        """배포 생성 (모델 버전 검증)"""

    async def get_deployment(self, deployment_id: str) -> Deployment | None:
        """배포 조회"""

    async def update_deployment(
        self, deployment_id: str, payload: dict[str, Any]
    ) -> Deployment | None:
        """배포 상태 업데이트 (PENDING → ACTIVE → TERMINATED)"""
```

**특징**:

- DeploymentEnvironment (DEV, STAGING, PRODUCTION)
- DeploymentStatus (PENDING, ACTIVE, FAILED, TERMINATED)
- 엔드포인트 설정 및 헬스 체크
- 롤백 지원 (rollback_from 추적)

---

### 7. **init**.py (200 lines)

**책임**: Delegation 패턴으로 통합

```python
"""Model Lifecycle Service - Main Integration"""

class ModelLifecycleService:
    """ML 모델 전체 생명주기 관리 (Delegation 패턴)"""

    def __init__(self, tracking_uri: str | None = None):
        # Delegate modules
        self._experiment_manager = ExperimentManager()
        self._run_tracker = RunTracker(tracking_uri)
        self._model_registry = ModelRegistry()
        self._approval_manager = ApprovalManager()
        self._drift_monitor = DriftMonitor()
        self._deployment_manager = DeploymentManager()

    # Experiment 위임 (4 메서드)
    async def create_experiment(self, payload: dict[str, Any]) -> ModelExperiment:
        return await self._experiment_manager.create_experiment(payload)

    async def update_experiment(...) -> ModelExperiment | None:
        return await self._experiment_manager.update_experiment(...)

    async def list_experiments(...) -> list[ModelExperiment]:
        return await self._experiment_manager.list_experiments(...)

    async def get_experiment(self, name: str) -> ModelExperiment | None:
        return await self._experiment_manager.get_experiment(name)

    # Run 위임 (5 메서드)
    async def log_run(self, payload: dict[str, Any]) -> ModelRun:
        return await self._run_tracker.log_run(payload)

    async def update_run(...) -> ModelRun | None:
        return await self._run_tracker.update_run(...)

    async def list_runs(...) -> list[ModelRun]:
        return await self._run_tracker.list_runs(...)

    async def get_run(self, run_id: str) -> ModelRun | None:
        return await self._run_tracker.get_run(run_id)

    # Registry 위임 (6 메서드)
    async def register_model_version(...) -> ModelVersion:
        return await self._model_registry.register_model_version(...)

    async def update_model_version(...) -> ModelVersion | None:
        return await self._model_registry.update_model_version(...)

    async def compare_model_versions(...) -> dict[str, dict[str, float]]:
        return await self._model_registry.compare_model_versions(...)

    async def list_model_versions(...) -> list[ModelVersion]:
        return await self._model_registry.list_model_versions(...)

    async def get_model_version(...) -> ModelVersion | None:
        return await self._model_registry.get_model_version(...)

    async def set_stage(...) -> ModelVersion | None:
        return await self._model_registry.set_stage(...)

    # Approval 위임 (3 메서드)
    async def append_checklist_item(...) -> ModelVersion | None:
        return await self._approval_manager.append_checklist_item(...)

    async def mark_checklist_status(...) -> ModelVersion | None:
        return await self._approval_manager.mark_checklist_status(...)

    # Drift 위임 (2 메서드)
    async def record_drift_event(...) -> DriftEvent:
        return await self._drift_monitor.record_drift_event(...)

    async def list_drift_events(...) -> list[DriftEvent]:
        return await self._drift_monitor.list_drift_events(...)

    # Deployment 위임 (5 메서드)
    async def list_deployments(...) -> list[Deployment]:
        return await self._deployment_manager.list_deployments(...)

    async def create_deployment(...) -> Deployment:
        return await self._deployment_manager.create_deployment(...)

    async def get_deployment(...) -> Deployment | None:
        return await self._deployment_manager.get_deployment(...)

    async def update_deployment(...) -> Deployment | None:
        return await self._deployment_manager.update_deployment(...)


# Re-export build_checklist utility
from .approval import build_checklist

__all__ = ["ModelLifecycleService", "build_checklist"]
```

---

## 구현 순서

1. **experiment.py 생성** (105 lines)

   - ExperimentManager 클래스 (4 메서드)

2. **run.py 생성** (130 lines)

   - RunTracker 클래스 (5 메서드 + MLflow 통합)

3. **registry.py 생성** (135 lines)

   - ModelRegistry 클래스 (6 메서드)

4. **approval.py 생성** (75 lines)

   - ApprovalManager 클래스 (2 메서드)
   - build_checklist 유틸리티 함수

5. **drift.py 생성** (60 lines)

   - DriftMonitor 클래스 (2 메서드)

6. **deployment.py 생성** (130 lines)

   - DeploymentManager 클래스 (5 메서드, Phase 4 기능)

7. \***\*init**.py 완성\*\* (200 lines)

   - ModelLifecycleService 통합 클래스
   - 25개 메서드 위임

8. **검증**

   - get_errors로 타입 에러 확인
   - Import 순환 의존성 검사

9. **레거시 백업**

   - model_lifecycle_service.py → model_lifecycle_service_legacy.py

10. **Git commit**
    - Phase 2.2a 완료

---

## 기존 API 호환성

```python
# ✅ 기존 코드 그대로 작동
from app.services.ml_platform.services.model_lifecycle_service import ModelLifecycleService

service = ModelLifecycleService(tracking_uri="http://mlflow:5000")

# All 25 methods work exactly the same
experiment = await service.create_experiment(...)
run = await service.log_run(...)
version = await service.register_model_version(...)
checklist = build_checklist(["Test", "Approve"])
deployment = await service.create_deployment(...)
```

---

## 타입 안전성 강화

- **ModelExperiment, ModelRun, ModelVersion**: Beanie ODM 모델
- **ExperimentStatus, RunStatus, ModelStage**: Enum 타입
- **DriftSeverity, DeploymentStatus, DeploymentEnvironment**: Enum 타입
- **모든 메서드**: 반환 타입 명시 (ModelVersion | None, list[...])

---

## Phase 2.2a 완료 후 상태

**Progress**: Phase 2.2 - 25% Complete (1/4 major files)

- 🔄 Phase 2.2a: model_lifecycle_service.py (476 → 7 files, 835 lines)
- ⏸️ Phase 2.2b: feature_engineer.py (256 lines)
- ⏸️ Phase 2.2c: anomaly_detector.py (273 lines)
- ⏸️ Phase 2.2d: trainer.py (322 lines)

**다음 단계**: Phase 2.2b (feature_engineer.py 모듈화)
