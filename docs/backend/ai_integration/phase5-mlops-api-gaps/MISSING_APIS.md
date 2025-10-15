# Phase 5 MLOps - 백엔드 API 부족 사항

## 문서 정보

- **작성일**: 2025-10-15
- **작성자**: AI Agent
- **목적**: Phase 4 MLOps 플랫폼 구현 중 발견된 백엔드 API 부족 사항 문서화
- **영향**: Frontend hooks에서 TODO 주석이 남아있는 기능들

---

## 1. Model Lifecycle - Deployment 관련 API 부재

### 1.1 Missing Endpoints

#### `GET /api/v1/ml/lifecycle/deployments`

**Status**: ❌ 없음

**목적**: 모델 배포 목록 조회

**Frontend 요구사항** (`useModelLifecycle.ts` line 170-180):

```typescript
const deploymentsQuery = useQuery({
  queryKey: modelLifecycleQueryKeys.deploymentsList(),
  queryFn: async (): Promise<Deployment[]> => {
    // TODO: Replace with actual API call
    // const response = await ModelLifecycleService.getDeployments();
    // return response.data;
  },
});
```

**필요한 Response Schema**:

```typescript
interface Deployment {
  id: string;
  model_id: string;
  model_name: string;
  model_version: string;
  status:
    | "pending"
    | "validating"
    | "deploying"
    | "active"
    | "failed"
    | "rollback";
  environment: "development" | "staging" | "production";
  endpoint: string;
  created_by: string;
  deployed_at?: string;
  created_at: string;
}
```

---

#### `POST /api/v1/ml/lifecycle/deployments`

**Status**: ❌ 없음

**목적**: 모델 배포 실행

**Frontend 요구사항** (`useModelLifecycle.ts` line 242-265):

```typescript
const deployModelMutation = useMutation({
  mutationFn: async (data: ModelDeploy): Promise<Deployment> => {
    // TODO: Replace with actual API call
    // const response = await ModelLifecycleService.deployModel({ body: data });
    // return response.data;
  },
});
```

**필요한 Request Schema**:

```typescript
interface ModelDeploy {
  model_id: string;
  environment: "development" | "staging" | "production";
  endpoint_config?: {
    instances: number;
    instance_type: string;
    auto_scaling?: boolean;
  };
}
```

---

#### `GET /api/v1/ml/lifecycle/deployments/{deployment_id}`

**Status**: ❌ 없음

**목적**: 배포 상세 정보 및 모니터링 지표 조회

**Frontend 요구사항** (`useModelLifecycle.ts` line 450-485):

```typescript
const deploymentDetailQuery = useQuery({
  queryKey: modelLifecycleQueryKeys.deploymentDetail(deploymentId),
  queryFn: async (): Promise<DeploymentDetail> => {
    // TODO: Replace with actual API call
  },
});
```

**필요한 Response Schema**:

```typescript
interface DeploymentDetail extends Deployment {
  logs: string[];
  health_status: "healthy" | "degraded" | "unhealthy";
  request_count: number;
  error_rate: number;
  avg_latency_ms: number;
}
```

---

### 1.2 현재 대안책

**Stage 변경으로 일부 대체 가능**:

```python
# 현재 존재하는 API
PATCH /api/v1/ml/lifecycle/models/{model_name}/{version}
Body: ChecklistUpdateRequest {
    stage?: "experimental" | "staging" | "production" | "archived"
}
```

**한계점**:

- Stage 변경 ≠ 실제 배포 (deployment)
- 배포 이력 추적 불가
- 배포 환경별 엔드포인트 관리 불가
- 배포 상태 모니터링 불가 (health, latency, error rate)

---

### 1.3 권장 구현 방안

**Backend 작업** (예상 4-6시간):

1. **Model 추가** (`backend/app/models/ml/deployment.py`):

```python
from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Optional, Literal

class Deployment(Document):
    model_name: str
    model_version: str
    environment: Literal["development", "staging", "production"]
    status: Literal["pending", "active", "failed", "rollback"]
    endpoint: str
    created_by: str
    deployed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Monitoring fields
    health_status: Literal["healthy", "degraded", "unhealthy"] = "healthy"
    request_count: int = 0
    error_rate: float = 0.0
    avg_latency_ms: float = 0.0

    class Settings:
        name = "ml_deployments"
```

2. **Schema 추가** (`backend/app/schemas/ml/deployment.py`):

```python
class DeploymentCreate(BaseModel):
    model_name: str
    model_version: str
    environment: Literal["development", "staging", "production"]

class DeploymentResponse(BaseModel):
    id: str
    model_name: str
    model_version: str
    environment: str
    status: str
    endpoint: str
    created_by: str
    deployed_at: Optional[datetime] = None
    created_at: datetime
```

3. **Service 추가** (`backend/app/services/deployment_service/`):

```python
class DeploymentService:
    async def create_deployment(self, data: DeploymentCreate, user: str) -> Deployment
    async def list_deployments(self, environment: Optional[str] = None) -> List[Deployment]
    async def get_deployment(self, deployment_id: str) -> Deployment
    async def update_deployment_status(self, deployment_id: str, status: str) -> Deployment
    async def rollback_deployment(self, deployment_id: str) -> Deployment
```

4. **Routes 추가** (`backend/app/api/routes/ml/deployments.py`):

```python
@router.post("/deployments", response_model=DeploymentResponse)
@router.get("/deployments", response_model=List[DeploymentResponse])
@router.get("/deployments/{deployment_id}", response_model=DeploymentResponse)
@router.patch("/deployments/{deployment_id}/status")
@router.post("/deployments/{deployment_id}/rollback")
```

---

## 2. Model Lifecycle - Detail 조회 API 부재

### 2.1 Missing Endpoints

#### `GET /api/v1/ml/lifecycle/experiments/{experiment_name}`

**Status**: ❌ 없음 (List만 존재)

**목적**: 실험 상세 정보 조회

**Frontend 요구사항** (`useModelLifecycle.ts` line 314-355):

```typescript
const experimentDetailQuery = useQuery({
  queryKey: modelLifecycleQueryKeys.experimentDetail(experimentId),
  queryFn: async (): Promise<ExperimentDetail> => {
    // TODO: Replace with actual API call
    // const response = await ModelLifecycleService.getExperiment({
    //   path: { experiment_id: experimentId! }
    // });
  },
});
```

**필요한 Response Schema**:

```typescript
interface ExperimentDetail extends ExperimentResponse {
  completed_at?: string;
  duration_seconds?: number;
  logs: string[];
  artifacts: Array<{
    name: string;
    path: string;
    size_bytes: number;
  }>;
}
```

---

#### `GET /api/v1/ml/lifecycle/models/{model_name}/{version}`

**Status**: ❌ 없음 (List만 존재, PATCH는 있음)

**목적**: 모델 버전 상세 정보 조회

**Frontend 요구사항** (`useModelLifecycle.ts` line 397-440):

```typescript
const modelDetailQuery = useQuery({
  queryKey: modelLifecycleQueryKeys.modelDetail(modelId),
  queryFn: async (): Promise<ModelDetail> => {
    // TODO: Replace with actual API call
  },
});
```

**필요한 Response Schema**:

```typescript
interface ModelDetail extends ModelVersionResponse {
  framework?: string;
  hyperparameters?: Record<string, any>;
  size_mb?: number;
  artifact_path?: string;
  deployment_count?: number;
}
```

---

### 2.2 현재 대안책

**List API로 필터링**:

```typescript
// Experiment detail 대체
const experiments = await ModelLifecycleService.listExperiments({
  query: { owner: "user" },
});
const experiment = experiments.data?.find((e) => e.name === experimentName);

// Model detail 대체
const models = await ModelLifecycleService.listModelVersions({
  query: { stage: "production" },
});
const model = models.data?.find((m) => m.model_name === modelName);
```

**한계점**:

- 불필요한 데이터 전송 (전체 목록 조회)
- 상세 정보 부족 (logs, artifacts, deployment_count 등)
- 성능 저하 (client-side filtering)

---

### 2.3 권장 구현 방안

**Backend 작업** (예상 2-3시간):

1. **Experiment Detail Endpoint**:

```python
# backend/app/api/routes/ml/lifecycle.py
@router.get("/experiments/{name}", response_model=ExperimentResponse)
async def get_experiment(
    name: str,
    lifecycle_service: ModelLifecycleService = Depends(get_lifecycle_service)
) -> ExperimentResponse:
    """Get experiment by name with full details"""
    experiment = await lifecycle_service.get_experiment(name)
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return experiment
```

2. **Model Detail Endpoint**:

```python
@router.get("/models/{model_name}/{version}", response_model=ModelVersionResponse)
async def get_model_version(
    model_name: str,
    version: str,
    lifecycle_service: ModelLifecycleService = Depends(get_lifecycle_service)
) -> ModelVersionResponse:
    """Get model version by name and version"""
    model = await lifecycle_service.get_model_version(model_name, version)
    if not model:
        raise HTTPException(status_code=404, detail="Model version not found")
    return model
```

3. **Service 메서드 추가**:

```python
# backend/app/services/model_lifecycle_service/lifecycle_service.py
async def get_experiment(self, name: str) -> Optional[Experiment]:
    return await Experiment.find_one(Experiment.name == name)

async def get_model_version(
    self,
    model_name: str,
    version: str
) -> Optional[ModelVersion]:
    return await ModelVersion.find_one(
        ModelVersion.model_name == model_name,
        ModelVersion.version == version
    )
```

---

## 3. Feature Store - Dataset 관련 API 부재

### 3.1 Missing Endpoints

#### `GET /api/v1/features/datasets`

**Status**: ❌ 없음

**목적**: 데이터셋 목록 조회

**Frontend 요구사항** (`useFeatureStore.ts` line 141-148):

```typescript
const datasetsQuery = useQuery({
  queryKey: featureStoreQueryKeys.datasets(),
  queryFn: async (): Promise<Dataset[]> => {
    // TODO: Replace with actual API call
    // const response = await FeatureStoreService.getDatasets();
  },
});
```

**필요한 Response Schema**:

```typescript
interface Dataset {
  id: string;
  name: string;
  description: string;
  features: string[]; // Feature names in this dataset
  row_count: number;
  created_at: string;
  updated_at: string;
}
```

---

#### `GET /api/v1/features/datasets/{dataset_id}`

**Status**: ❌ 없음

**목적**: 데이터셋 상세 정보 및 샘플 데이터 조회

**Frontend 요구사항** (`useFeatureStore.ts` line 340-365):

```typescript
const datasetDetailQuery = useQuery({
  queryKey: featureStoreQueryKeys.datasetDetail(datasetId),
  queryFn: async (): Promise<Dataset> => {
    // TODO: Replace with actual API call
  },
});
```

**필요한 Response Schema**:

```typescript
interface DatasetDetail extends Dataset {
  sample_data?: Record<string, unknown>[]; // First N rows
  correlation_matrix?: {
    feature1: string;
    feature2: string;
    correlation: number;
  }[];
}
```

---

### 3.2 현재 대안책

**없음**: Dataset 관련 기능은 현재 완전히 mock 상태

**한계점**:

- 데이터셋 탐색 불가
- Feature-Dataset 관계 추적 불가
- 데이터 품질 검증 불가

---

### 3.3 권장 구현 방안

**Backend 작업** (예상 3-4시간):

1. **Model 추가** (`backend/app/models/ml/dataset.py`):

```python
from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import List, Dict, Any, Optional

class Dataset(Document):
    name: str
    description: str
    features: List[str]  # Feature names
    row_count: int
    schema: Dict[str, str]  # column_name -> data_type
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Sample data (first 100 rows, DuckDB에서 조회)
    # Correlation matrix (DuckDB에서 계산)

    class Settings:
        name = "ml_datasets"
```

2. **Service 추가** (`backend/app/services/dataset_service.py`):

```python
class DatasetService:
    async def list_datasets(self) -> List[Dataset]
    async def get_dataset(self, dataset_id: str) -> Dataset
    async def get_sample_data(self, dataset_id: str, limit: int = 100) -> List[Dict[str, Any]]
    async def get_correlation_matrix(self, dataset_id: str) -> List[Dict[str, Any]]
```

3. **Routes 추가** (`backend/app/api/routes/ml/datasets.py`):

```python
@router.get("/datasets", response_model=List[DatasetResponse])
@router.get("/datasets/{dataset_id}", response_model=DatasetDetailResponse)
@router.get("/datasets/{dataset_id}/sample", response_model=List[Dict[str, Any]])
@router.get("/datasets/{dataset_id}/correlation", response_model=CorrelationMatrixResponse)
```

---

## 4. 우선순위 및 일정 추천

### 3.1 높은 우선순위 (Phase 5 Day 7-8 AI Integration 전 완료 권장)

1. **Experiment Detail API** (2시간)

   - 난이도: 낮음
   - 영향: 높음 (실험 추적 핵심 기능)
   - 의존성: 없음

2. **Model Detail API** (2시간)
   - 난이도: 낮음
   - 영향: 높음 (모델 관리 핵심 기능)
   - 의존성: 없음

### 3.2 중간 우선순위 (Phase 5 완료 후)

3. **Deployment CRUD APIs** (6시간)

   - 난이도: 중간
   - 영향: 높음 (프로덕션 필수)
   - 의존성: Model 시스템 안정화 필요

4. **Deployment Monitoring APIs** (4시간)
   - 난이도: 중간
   - 영향: 중간 (운영 편의성)
   - 의존성: Deployment CRUD 완료

### 3.3 낮은 우선순위 (추후 고려)

5. **Deployment Rollback** (3시간)
   - 난이도: 중간
   - 영향: 중간 (안전성 향상)
   - 의존성: Deployment 시스템 전체

---

## 4. Frontend 조치 사항

### 4.1 현재 상태

- `useModelLifecycle.ts`: 5개 TODO 주석 유지
- Mock 데이터로 UI 테스트 가능
- 백엔드 API 완성 시 즉시 연결 가능

### 4.2 다음 단계

1. ✅ **useFeatureStore.ts** TODO 제거 (백엔드 API 완비)
2. ✅ **useEvaluationHarness.ts** TODO 제거 (백엔드 API 완비)
3. ⏸️ **useModelLifecycle.ts** TODO 제거 (백엔드 API 추가 후)

---

## 5. 참고 자료

### 5.1 관련 파일

- Frontend Hook: `frontend/src/hooks/useModelLifecycle.ts`
- Backend Service: `backend/app/services/model_lifecycle_service/`
- Backend Routes: `backend/app/api/routes/ml/lifecycle.py`
- Backend Models: `backend/app/models/ml/`

### 5.2 관련 문서

- `docs/backend/ai_integration/MODEL_LIFECYCLE.md`
- `docs/frontend/enhanced_implementation/model-lifecycle.md`
- `AGENTS.md` - ServiceFactory pattern

---

## 변경 이력

- 2025-10-15: 초안 작성 (Phase 4 완료 시점)
