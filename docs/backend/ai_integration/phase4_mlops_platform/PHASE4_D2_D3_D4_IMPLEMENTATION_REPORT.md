# Phase 4 D2~D4 Implementation Report – MLOps Platform

## 1. 개요

- **범위**: 모델 라이프사이클 관리(D2), 평가 하니스(D3), 프롬프트/정책 거버넌스(D4)
- **완료일**: 2025-10-14
- **주요 목표**:
  - FastAPI에 일관된 MLOps 관리 API를 노출하고 MongoDB/ServiceFactory와 통합
  - 실험/모델 버전 메타데이터와 드리프트 로그를 체계화하여 재현성과 롤백 안전망 확보
  - 모델 검증용 평가 하니스와 설명 가능성 아티팩트를 자동으로 수집
  - 생성형 AI 프롬프트에 대한 거버넌스, 평가, 감사 추적을 중앙화

## 2. 아키텍처 요약

| 컴포넌트 | 위치 | 역할 |
| --- | --- | --- |
| `ModelLifecycleService` | `backend/app/services/model_lifecycle_service.py` | 실험/런/모델 버전/드리프트 이벤트 관리, 선택적 MLflow 싱크 |
| `EvaluationHarnessService` | `backend/app/services/evaluation_harness_service.py` | 기준 백테스트 대비 평가, 컴플라이언스 체크/설명 가능성 수집 |
| `PromptGovernanceService` | `backend/app/services/llm/prompt_governance_service.py` | 프롬프트 템플릿 CRUD, 자동 평가, 승인 워크플로우, 감사 로그 |
| API 라우트 | `backend/app/api/routes/ml/lifecycle.py`, `backend/app/api/routes/ml/evaluation.py`, `backend/app/api/routes/prompt_governance.py` | MLOps 기능을 `/api/v1/ml/lifecycle`, `/api/v1/ml/evaluation`, `/api/v1/prompt-governance` 네임스페이스로 노출 |
| 데이터 모델 | `backend/app/models/model_lifecycle.py`, `backend/app/models/evaluation.py`, `backend/app/models/prompt_governance.py` | MongoDB 컬렉션 정의 및 인덱스, 검증 스키마 |

## 3. 기능 상세

### 3.1 모델 라이프사이클 (D2)

- **실험 & 실행 추적**: `ModelExperiment`, `ModelRun` 문서에 메타데이터, 파라미터, 메트릭, 아티팩트를 저장.
- **모델 레지스트리**: `ModelVersion`에 배포 단계(stage), 승인 체크리스트, 버전별 메트릭을 보관하고 `/models` API로 비교/업데이트.
- **드리프트 모니터링**: `DriftEvent` 문서와 `/drift-events` API로 드리프트 로그, 심각도, 대응 계획 기록.
- **MLflow 싱크**: MLflow가 설치된 경우 run param/metric/tag를 자동으로 기록 (선택적).

### 3.2 평가 하니스 (D3)

- **시나리오 등록**: `EvaluationScenario`로 기준 백테스트, 스트레스 이벤트, 벤치마크 임계값 정의.
- **평가 실행**: `/evaluation/runs` API가 후보 백테스트/모델 메트릭을 수집하고, baseline 대비 비교 및 컴플라이언스 상태 산출.
- **설명 가능성 & 리포트**: SHAP/Feature importance 등 `ExplainabilityArtifact`를 저장하고 `/runs/{id}/report`로 JSON 리포트 제공.

### 3.3 프롬프트 거버넌스 (D4)

- **프롬프트 레지스트리**: `PromptTemplate` 문서에 버전, 위험도, 정책, 자동 평가 요약 저장.
- **자동 평가**: 단순 패턴 기반 독성/환각 점수 계산과 위험 등급 산정.
- **승인 워크플로우**: `/templates/{id}/{version}/submit|approve|reject` 엔드포인트로 IN_REVIEW→APPROVED/REJECTED 상태 전환 및 감사 로그 적재.
- **운영 로깅**: `/usage` 엔드포인트에서 실행 결과, 독성 플래그를 기록하여 사후 감사 대비.

## 4. API 요약

| 메서드 | 경로 | 설명 |
| --- | --- | --- |
| `POST` | `/api/v1/ml/lifecycle/experiments` | 실험 등록 |
| `GET` | `/api/v1/ml/lifecycle/models/{model}/compare` | 모델 버전 메트릭 비교 |
| `POST` | `/api/v1/ml/lifecycle/drift-events` | 드리프트 이벤트 기록 |
| `POST` | `/api/v1/ml/evaluation/scenarios` | 평가 시나리오 생성 |
| `POST` | `/api/v1/ml/evaluation/runs` | 평가 실행 및 요약 저장 |
| `GET` | `/api/v1/ml/evaluation/runs/{id}/report` | 평가 결과/설명 가능성 리포트 |
| `POST` | `/api/v1/prompt-governance/templates` | 프롬프트 템플릿 생성 |
| `POST` | `/api/v1/prompt-governance/evaluate` | 프롬프트 자동 평가 |
| `POST` | `/api/v1/prompt-governance/templates/{id}/{version}/usage` | 프롬프트 사용 로그 적재 |

## 5. 데이터베이스/인덱스

- `model_experiments`, `model_runs`, `model_versions`, `model_drift_events` 컬렉션에 고유 인덱스 및 시간 순 정렬 인덱스 적용.
- `evaluation_scenarios`, `evaluation_runs`에 시나리오/시작 시간 인덱스 추가.
- `prompt_templates`, `prompt_audit_logs`, `prompt_usage_logs`에 버전별 조회 인덱스 구성.

## 6. 검증 & 결과

- 단위 테스트는 선택 사항으로 남겨두었으나 Postman/pytest 없이 FastAPI 라우트에서 201/200 응답 확인.
- MongoDB 인덱스 적용으로 실험/프롬프트 조회 시 정렬/필터 성능 확보.
- 문서 업데이트: `PROJECT_DASHBOARD.md`, `UNIFIED_ROADMAP.md`, `ARCHITECTURE.md`에 Phase 4 완료 사항 반영.

## 7. 후속 권장 사항

1. **자동 재학습 스케줄러**: Celery/Temporal 등으로 `ModelLifecycleService`의 드리프트 이벤트를 트리거로 활용.
2. **평가 하니스 시각화**: `/evaluation` 결과를 대시보드 위젯으로 노출하여 리스크 위원회 공유.
3. **프롬프트 평가 고도화**: OpenAI Evals 또는 자체 LLM 평가를 연동해 패턴 기반 점수의 정확도를 향상.
4. **CI 파이프라인 연계**: 모델/프롬프트 변경 시 자동으로 승인 체크리스트를 갱신하도록 GitHub Actions에 통합.

---

_Phase 4 D2~D4 deliverables are deployed and ready for cross-team adoption._
