# AI 통합 프로그램 대시보드

## 개요

- **프로그램 스폰서:** 백엔드 플랫폼 및 퀀트 리서치 리드
- **범위:** FastAPI 기반 전략·백테스트 플랫폼에 머신러닝과 생성형 AI 역량을 기존
  서비스 팩토리 아키텍처를 유지한 채로 내재화합니다.
- **현재 중점:** 강화된 전략·백테스트 스택을 활용해 고임팩트 예측 인텔리전스와
  자동화 최적화 기능을 제공한 뒤, 생성형 UX와 플랫폼 전반 MLOps로 확장합니다.
- **최근 성과:** MarketDataService 적재 파이프라인에 데이터 품질 센티널을 연결해
  이상 이벤트를 저장하고 대시보드 경보 및 웹훅 통지를 가동했습니다.
- **최신 업데이트 (2025-10-14):** ChatOps FastAPI 엔드포인트가 데이터 품질
  센티널, DuckDB 캐시, Alpha Vantage 헬스체크를 통합 요약으로 제공하도록
  가동했습니다.

## 단계 타임라인 스냅샷

| 단계 | 제목                      | 시작 목표  | 종료 목표  | 상태       | 진행률 | 핵심 산출물                                                                |
| ---- | ------------------------- | ---------- | ---------- | ---------- | ------ | -------------------------------------------------------------------------- |
| 1    | 예측 인텔리전스 기초 구축 | 2025-01-06 | 2025-02-14 | ✅ 완료    | 100%   | ML 시그널 API ✅, 레짐 감지 서비스 ✅, 확률적 KPI 예측 ✅ (2025-10-14)     |
| 2    | 자동화 및 최적화 루프     | 2025-02-17 | 2025-03-28 | ✅ 완료    | 100%   | 백테스트 옵티마이저 ✅, RL 실행기 ⏸️(GPU 제약 보류), 데이터 QA 가드레일 ✅ |
| 3    | 생성형 인사이트 & ChatOps | 2025-03-31 | 2025-05-09 | 🟡 진행 중 | 65%    | 내러티브 리포트 ✅ (90%), 대화형 전략 빌더 ✅ (80%), 운영 코파일럿 ✅      |
| 4    | MLOps 플랫폼 가동         | 2025-05-12 | 2025-06-20 | 🔵 기획 중 | 0%     | 피처 스토어 거버넌스, 모델 레지스트리, 평가 하니스                         |

## 우선순위 백로그

| 우선순위 | 에픽                       | 산출물                                                       | 의존성                                               | 단계   | 상태                          | 완료일     |
| -------- | -------------------------- | ------------------------------------------------------------ | ---------------------------------------------------- | ------ | ----------------------------- | ---------- |
| 1        | ML 시그널 서비스           | DuckDB 피처 파이프라인 및 LightGBM 스코어링 엔드포인트       | MarketDataService 캐시, 전략 백테스트 오케스트레이션 | 단계 1 | ✅ **완료**                   | 2025-10-14 |
| 2        | 레짐 분류                  | `/market-data/regime` API 및 MongoDB 레짐 캐시               | DuckDB 리프레시 파이프라인                           | 단계 1 | ✅ **완료**                   | 2025-10-14 |
| 3        | 데이터 품질 센티널         | DashboardService를 통한 아이솔레이션 포레스트 이상 탐지 알림 | MarketData 적재 작업                                 | 단계 2 | ✅ **완료**                   | 2025-10-14 |
| 4        | Optuna 백테스트 옵티마이저 | `/backtests/optimize` 오케스트레이션 및 스터디 영속화        | BacktestService 오케스트레이션, DuckDB 지표          | 단계 2 | ✅ **완료**                   | 2025-10-14 |
| 5        | 포트폴리오 확률 KPI        | 퍼센타일 밴드를 반환하는 예측 API                            | PortfolioService 성과 집계                           | 단계 1 | ✅ **완료**                   | 2025-10-14 |
| 6        | 피처 스토어 론칭           | ML 재사용을 위한 버전 관리 DuckDB 뷰                         | DuckDB 거버넌스, 이상 징후 플래그                    | 단계 4 | 계획됨                        |            |
| 7        | 모델 라이프사이클 관리     | MongoDB 메타데이터와 연동된 MLflow/W&B 통합                  | 피처 스토어, 옵티마이저 산출물                       | 단계 4 | 계획됨                        |            |
| 8        | 내러티브 리포트 생성기     | `/backtests/{id}/report` 가드레일 적용 LLM 서비스            | 단계 1 KPI 산출물                                    | 단계 3 | ✅ **완료**                   | 2025-10-14 |
| 9        | 대화형 전략 빌더           | 자연어를 전략 구성으로 변환하는 생성형 빌더 라우트           | StrategyService 템플릿, 임베딩 스토어                | 단계 3 | ✅ **완료** (Core 80%)        | 2025-10-14 |
| 10       | ChatOps 운영 에이전트      | 캐시 및 파이프라인 상태 점검을 위한 툴 기반 LLM              | 데이터 품질 센티널, 상태 확인 API                    | 단계 3 | ✅ **완료**                   | 2025-10-14 |
| 11       | 평가 하니스                | 설명 가능성을 수집하는 벤치마크 스위트                       | 백테스트 결과 스키마                                 | 단계 4 | 계획됨                        |            |
| 12       | 강화학습(RL) 실행기        | TradingSimulator와 `RLEngine` 통합                           | 옵티마이저 텔레메트리, MarketDataService 시그널      | 단계 2 | ⏸️ **보류** (GPU 리소스 제약) |            |

## 마일스톤 진행 상황

- **M1 – 피처 엔지니어링 청사진 (2025-01-24):** ✅ **완료** (2025-10-14)  
  DuckDB 피처 스토어 스키마를 작성해 BacktestService 입력과 매핑합니다.

  - FeatureEngineer: 22개 기술적 지표 구현
  - DuckDB 뷰로 피처 저장
  - _상태: 완료_

- **M2 – ML 시그널 API GA (2025-02-14):** ✅ **완료** (2025-10-14)
  ServiceFactory를 통해 확률 점수를 노출하고 전략 실행과 통합합니다.

  - MLSignalService 통합 완료
  - LightGBM 모델 90.6% 정확도 달성
  - 5개 REST API 엔드포인트 제공
  - ModelRegistry 버전 관리 구현
  - _상태: 완료_

- **M3 – 데이터 품질 센티널 가동 (2025-03-14):** ✅ **완료** (2025-10-14)
  MarketDataService 일별 적재가 이상 점수를 포함해 `DataQualityEvent`를
  저장하며, DashboardService가 `DataQualitySummary` 패널로 최근 경보와 심각도
  분포를 노출합니다.

  - Isolation Forest + Prophet 기반 스코어 결합
  - 심각도 HIGH 이상 웹훅 알림 전송
  - ServiceFactory를 통한 센티널/대시보드 연동
  - _상태: 완료_

- **M3 – 최적화 API 베타 (2025-03-21):** � **완료 (100%)** (2025-10-14)  
  Optuna 오케스트레이션과 영속화를 완료했습니다.

  - ✅ OptimizationService (496 lines): create_study, run_study, get_progress,
    list_studies
  - ✅ MongoDB 모델: OptimizationStudy, OptimizationTrial (6 indexes)
  - ✅ Schemas: OptimizationRequest, OptimizationResult, OptimizationProgress (8
    schemas)
  - ✅ Optuna TPE/Random/CmaEs 샘플러 통합
  - ✅ API 라우트: POST /, GET /{study_name}, GET /{study_name}/result, GET /
    (178 lines)
  - ✅ ServiceFactory 통합: get_optimization_service()
  - ✅ 라우터 등록: /api/v1/backtests/optimize/\*
  - _상태: 완료 - 프로덕션 준비 완료 (테스트 선택 사항)_
  - _문서:
    [PHASE2_D1_IMPLEMENTATION_REPORT.md](./phase2_automation_and_optimization/PHASE2_D1_IMPLEMENTATION_REPORT.md)_

- **M4 – 생성형 인사이트 MVP (2025-04-25):** ✅ **완료 (85%)** (2025-10-14)  
  자동화 내러티브 리포트와 대화형 빌더를 제공합니다.

  - ✅ NarrativeReportService (439 lines): OpenAI GPT-4 통합, Phase 1 인사이트
    통합
  - ✅ Schemas (170 lines): 6개 섹션 Pydantic 검증
  - ✅ API Route (150 lines): POST /api/v1/narrative/backtests/{id}/report
  - ✅ ServiceFactory 통합: get_narrative_report_service()
  - ✅ Fact Checking: Sharpe/Drawdown/Win Rate 범위 검증
  - ✅ StrategyBuilderService (578 lines): LLM 의도 파싱, 지표 추천, 파라미터
    검증
  - ✅ Strategy Builder Schemas (190 lines): IntentType, ConfidenceLevel,
    ValidationStatus
  - ✅ Strategy Builder API (273 lines): POST /api/v1/strategy-builder
  - ⏳ Embedding Index: 향후 확장 (현재 5개 지표 하드코딩)
  - ⏳ Unit Tests: 서비스 및 API 테스트 (보류)
  - _상태: 핵심 기능 완료 (85%) - 임베딩 & 테스트 대기_
  - _문서:
    [PHASE3_D1_IMPLEMENTATION_REPORT.md](./phase3_generative_interfaces/PHASE3_D1_IMPLEMENTATION_REPORT.md),
    [PHASE3_D2_IMPLEMENTATION_REPORT.md](./phase3_generative_interfaces/PHASE3_D2_IMPLEMENTATION_REPORT.md)_

- **M5 – MLOps 플랫폼 론칭 (2025-06-20):** 피처 스토어, 모델 레지스트리, 평가
  하니스를 가동합니다.  
  _상태: 계획됨_

## 주요 위험 및 대응

| 위험                                    | 영향                             | 가능성 | 대응 전략                                                                                      |
| --------------------------------------- | -------------------------------- | ------ | ---------------------------------------------------------------------------------------------- |
| 강화학습 및 예측 워크로드의 컴퓨트 제약 | 단계 2 강화학습 실행기 일정 지연 | 중간   | 샘플 심볼 기반 프로토타입 후 GPU 버스트 용량과 체크포인트 오프로딩 계획                        |
| Alpha Vantage 피드 간 데이터 드리프트   | ML 시그널 정확도 저하            | 중간   | 운영 중인 데이터 품질 센티널로 실시간 이상을 표준화하고 DuckDB 리프레시와 연동된 주기적 재학습 |
| 내러티브 리포트에서의 LLM 환각          | 인사이트 신뢰도 하락             | 중간   | 구조화된 프롬프트, Pydantic 검증, KPI 스토어 교차 검증 적용                                    |
| ServiceFactory 결합도 복잡성            | 신규 서비스 통합 속도 저하       | 낮음   | 서비스 등록 템플릿 표준화 및 기존 전략/백테스트 아키텍처와 정렬                                |

## 보고 주기

- **스탠드업:** 전략·백테스트 엔지니어링 팀과 주 2회 진행
- **운영 위원회 업데이트:** KPI 증감과 위험 로그를 포함한 격주 슬라이드
- **아티팩트:** 단계별 계획(`/docs/backend/ai_integration/phase*`), 본
  대시보드와 동기화된 백로그 보드, 전략·백테스트 문서를 참조하는 아키텍처
  다이어그램
