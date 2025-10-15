# Frontend Hooks ↔ Backend Services 매핑 분석

**작성일**: 2025-10-15  
**목적**: 백엔드 서비스 리팩토링 이후 프론트엔드 훅 점검 및 동기화

---

## 매핑 테이블

| Backend Service (ServiceFactory) | Frontend Hook           | 상태        | 비고                              |
| -------------------------------- | ----------------------- | ----------- | --------------------------------- |
| **Market Data Domain**           |                         |             |                                   |
| `MarketDataService`              | `useMarketData`         | ✅ 존재     | Management/Info/Health 엔드포인트 |
| `StockService`                   | `useStocks`             | ✅ 존재     | Stock 모듈 API                    |
| `FundamentalService`             | `useFundamental`        | ❌ **누락** | 기업 재무 데이터                  |
| `EconomicIndicatorService`       | `useEconomic`           | ✅ 존재     | 경제 지표                         |
| `IntelligenceService`            | `useIntelligence`       | ✅ 존재     | 뉴스/감정 분석                    |
| `TechnicalIndicatorService`      | `useTechnicalIndicator` | ✅ 존재     | 기술적 지표                       |
| **Trading Domain**               |                         |             |                                   |
| `StrategyService`                | `useStrategy`           | ✅ 존재     | 전략 관리                         |
| `BacktestService`                | `useBacktests`          | ✅ 존재     | 백테스트 CRUD                     |
| `BacktestOrchestrator`           | `useBacktests` (통합)   | ✅ 존재     | 백테스트 실행 (execute 함수)      |
| `PortfolioService`               | ❌ **누락**             | ⚠️ **필요** | 포트폴리오 관리                   |
| `OptimizationService`            | `useOptimization`       | ✅ 존재     | Optuna 최적화 (Phase 2)           |
| **ML Platform Domain**           |                         |             |                                   |
| `MLSignalService`                | `useMLModel`            | ✅ 존재     | ML 모델 관리 (Phase 1)            |
| `RegimeDetectionService`         | `useRegimeDetection`    | ✅ 존재     | 시장 국면 감지 (Phase 1)          |
| `ProbabilisticKPIService`        | `usePortfolioForecast`  | ✅ 존재     | 포트폴리오 예측 (Phase 1)         |
| `AnomalyDetectionService`        | `useDataQuality` (통합) | ✅ 존재     | 이상 탐지 (Phase 2)               |
| `FeatureStoreService`            | `useFeatureStore`       | ✅ 존재     | Feature Store (Phase 4)           |
| `ModelLifecycleService`          | `useModelLifecycle`     | ✅ 존재     | 모델 라이프사이클 (Phase 4)       |
| `EvaluationHarnessService`       | `useEvaluationHarness`  | ✅ 존재     | 평가 하니스 (Phase 4)             |
| **GenAI Domain**                 |                         |             |                                   |
| `NarrativeReportService`         | `useNarrativeReport`    | ✅ 존재     | 내러티브 리포트 (Phase 3)         |
| `StrategyBuilderService`         | `useStrategyBuilder`    | ✅ 존재     | 전략 빌더 (Phase 3)               |
| `ChatOpsAgent`                   | ❌ **누락**             | ⚠️ **필요** | 기본 ChatOps (Phase 3)            |
| `ChatOpsAdvancedService`         | `useChatOps`            | ✅ 존재     | 고급 ChatOps (Phase 3)            |
| `PromptGovernanceService`        | `usePromptGovernance`   | ✅ 존재     | 프롬프트 거버넌스 (Phase 4)       |
| **User Domain**                  |                         |             |                                   |
| `WatchlistService`               | `useWatchList`          | ✅ 존재     | 관심종목                          |
| `DashboardService`               | `useDashboard`          | ✅ 존재     | 대시보드 (의존성 10개)            |
| **Infrastructure**               |                         |             |                                   |
| `DatabaseManager`                | (백엔드 전용)           | -           | DuckDB 캐시                       |
| `DataQualitySentinel`            | `useDataQuality`        | ✅ 존재     | 데이터 품질 모니터링 (Phase 2)    |

---

## 🚨 누락된 훅 (Action Required)

### 1. `useFundamental` ⚠️ 우선순위: 높음

**백엔드**: `FundamentalService`  
**프론트엔드**: `ussFundamental.ts` (오타 - `uss` → `use`)  
**상태**: 파일 존재하지만 **네이밍 오류**

**조치**:

- `ussFundamental.ts` → `useFundamental.ts` 파일명 수정
- 내용 검증 및 최신 API 반영

---

### 2. `usePortfolio` ⚠️ 우선순위: 중간

**백엔드**: `PortfolioService`  
**프론트엔드**: **없음**  
**상태**: **완전 누락**

**조치**:

- 새 훅 `usePortfolio.ts` 생성
- TanStack Query 패턴 적용
- API: 포트폴리오 CRUD, 성과 분석, 리밸런싱 등

**예상 API**:

- `GET /api/portfolios/`
- `POST /api/portfolios/`
- `GET /api/portfolios/{id}`
- `GET /api/portfolios/{id}/performance`
- `POST /api/portfolios/{id}/rebalance`

---

### 3. `useChatOpsBasic` ⚠️ 우선순위: 낮음

**백엔드**: `ChatOpsAgent`  
**프론트엔드**: `useChatOps` (ChatOpsAdvancedService 매핑)  
**상태**: **고급 서비스만 존재**, 기본 서비스 누락

**조치**:

- 현재 `useChatOps`가 `ChatOpsAdvancedService`를 사용 중
- `ChatOpsAgent`는 별도 훅 생성 필요 여부 검토
- 또는 `useChatOps` 내부에서 두 서비스 모두 호출하도록 확장

**판단 기준**:

- `ChatOpsAgent`와 `ChatOpsAdvancedService`의 기능 중복 확인
- 프론트엔드에서 기본 기능만 사용하는 경우가 있는지 검토

---

## ✅ 기존 훅 검증 필요 (Refactoring Required)

### 1. `useBacktests` - BacktestOrchestrator 통합 검증

**현재 상태**: `BacktestService` + `BacktestOrchestrator` 모두 사용  
**검증 사항**:

- `execute` 함수가 `BacktestOrchestrator`를 올바르게 호출하는가?
- CRUD는 `BacktestService`, 실행은 `Orchestrator` 분리 확인

---

### 2. `useMLModel` - MLSignalService 네이밍 검증

**현재 상태**: `MLSignalService` → `useMLModel` 매핑  
**검증 사항**:

- 백엔드 서비스명과 프론트엔드 훅명이 불일치 (의도적인가?)
- 훅명을 `useMLSignal`로 변경할지 검토

---

### 3. `useDataQuality` - 통합 서비스 검증

**현재 상태**: `DataQualitySentinel` + `AnomalyDetectionService` 통합  
**검증 사항**:

- 두 서비스의 API가 모두 훅에 반영되어 있는가?
- 백엔드 리팩토링 이후 API 변경사항 반영 확인

---

## 🔄 OpenAPI 클라이언트 재생성 필요

**배경**: 백엔드 서비스 리팩토링 이후 스키마 변경 가능성

**조치**:

```bash
cd /Users/donghakim/quant
pnpm gen:client
```

**확인사항**:

- `frontend/src/openapi.json` 업데이트
- `frontend/src/client/` 타입 재생성
- TypeScript 에러 발생 시 훅 코드 수정

---

## 📋 다음 단계 (Action Items)

### 즉시 실행 (P0)

1. ✅ `ussFundamental.ts` → `useFundamental.ts` 파일명 수정
2. ✅ `pnpm gen:client` 실행 (OpenAPI 클라이언트 재생성)
3. ✅ TypeScript 빌드 에러 확인 (`pnpm build`)

### 단기 실행 (P1 - 1-2일)

4. ⚠️ `usePortfolio` 훅 생성 (PortfolioService API 연동)
5. ⚠️ `useBacktests` BacktestOrchestrator 통합 검증
6. ⚠️ `useDataQuality` 백엔드 API 변경사항 반영

### 중기 실행 (P2 - 3-5일)

7. ⚠️ `ChatOpsAgent` vs `ChatOpsAdvancedService` 중복 검토
8. ⚠️ 전체 훅 TanStack Query 패턴 일관성 검증
9. ⚠️ 훅별 성능 최적화 (staleTime, gcTime 재검토)

### 장기 실행 (P3 - 1주+)

10. ⏸️ E2E 테스트 작성 (Playwright)
11. ⏸️ Storybook 문서화
12. ⏸️ Phase 5 통합 테스트 및 배포 준비

---

## 📊 완성도 분석

| 카테고리              | 완성도        | 비고                         |
| --------------------- | ------------- | ---------------------------- |
| **Market Data Hooks** | 5/6 (83%)     | `useFundamental` 네이밍 오류 |
| **Trading Hooks**     | 4/5 (80%)     | `usePortfolio` 누락          |
| **ML Platform Hooks** | 6/6 (100%)    | ✅ 완료                      |
| **GenAI Hooks**       | 4/5 (80%)     | `ChatOpsAgent` 훅 검토 필요  |
| **User Hooks**        | 2/2 (100%)    | ✅ 완료                      |
| **전체**              | 21/24 (87.5%) | 3개 Action Items             |

---

## 🎯 결론

**상태**: Phase 1-4 훅 구현은 87.5% 완료  
**주요 이슈**:

1. `useFundamental` 네이밍 오류 (긴급)
2. `usePortfolio` 누락 (중요)
3. `ChatOpsAgent` 중복 검토 (검토 필요)

**다음 작업**: OpenAPI 클라이언트 재생성 → 파일명 수정 → TypeScript 에러 해결
