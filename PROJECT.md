# PROJECT.md
## 프로젝트 개요
- **목표**: Alpha Vantage API 기반의 단일 사용자용 퀀트 백테스트 앱 개발
- **MVP 범위**: 실시간 트레이딩 제외, 전략 수립 및 백테스트 중심
- **아키텍처**: 마이크로서비스 기반 모노레포 구조

---

## 🏗️ 프로젝트 구조

```
quant/
├── services/
│   ├── data-service/          # 데이터 수집 및 관리
│   ├── strategy-service/      # 전략 개발 및 관리
│   ├── backtest-service/      # 백테스트 실행 엔진
│   └── analytics-service/     # 성과 분석 및 리포트
├── frontend/                  # 웹 대시보드 (향후)
├── shared/                    # 공통 라이브러리
│   ├── models/               # 데이터 모델
│   ├── utils/                # 유틸리티 함수
│   └── config/               # 설정 관리
├── tests/                    # 통합 테스트
└── scripts/                  # 개발 스크립트
```

---

## 📋 Phase 1: Core Infrastructure (2주)

### Sprint 1.1: 프로젝트 기반 구축
- [ ] **UV 환경 구성**: `pyproject.toml` 설정 및 의존성 관리
- [ ] **공통 모듈 구성**: `shared/` 디렉토리 구조 및 기본 모델
- [ ] **개발 환경**: black, ruff, mypy, pytest 설정
- [ ] **CI/CD**: GitHub Actions 워크플로우
- [ ] **환경 변수**: `.env` 관리 및 설정 클래스 구현

### Sprint 1.2: Data Service 구현
- [ ] **Alpha Vantage API 클라이언트**:
  - 시계열 데이터 수집 (Daily, Intraday)
  - Rate limiting 및 에러 핸들링
  - 재시도 로직 구현
- [ ] **DuckDB 스키마**:
  - 시계열 데이터 테이블 설계
  - 인덱스 및 파티셔닝 전략
- [ ] **데이터 파이프라인**:
  - 캐싱 메커니즘 (TTL 기반)
  - 결측치 보간 (forward fill)
  - 스플릿/배당 조정

---

## 🚀 Phase 2: Strategy & Backtest Engine (4주)

### Sprint 2.1: Strategy Service
- [ ] **전략 프레임워크**:
  - vectorbt 기반 백테스트 엔진 선택
  - 전략 베이스 클래스 및 인터페이스 정의
- [ ] **기본 전략 구현**:
  - Simple Moving Average Crossover
  - RSI Mean Reversion
  - Momentum Strategy
  - Buy & Hold 벤치마크
- [ ] **전략 설정 관리**:
  - Pydantic 기반 파라미터 스키마
  - 전략별 설정 JSON 템플릿

### Sprint 2.2: Backtest Service
- [ ] **백테스트 엔진**:
  - 거래 시뮬레이션 로직
  - 수수료 및 슬리피지 모델링
  - 포지션 사이징 알고리즘
- [ ] **성과 지표 계산**:
  - 수익률 지표 (CAGR, Total Return)
  - 리스크 지표 (Sharpe, Sortino, Calmar)
  - 드로다운 분석 (Max DD, Average DD)
- [ ] **결과 저장**:
  - 백테스트 결과 DuckDB 저장
  - 거래 로그 및 포트폴리오 히스토리

### Sprint 2.3: Analytics Service
- [ ] **성과 분석**:
  - 기간별 수익률 분석
  - 벤치마크 대비 성과
  - 위험 조정 수익률
- [ ] **시각화**:
  - matplotlib 기반 차트 생성
  - Equity Curve, Drawdown Chart
  - 월별/연도별 수익률 히트맵

---

## 🎯 Phase 3: User Experience (3주)

### Sprint 3.1: CLI 인터페이스
- [ ] **Typer 기반 CLI**:
  ```bash
  quant data fetch --symbol AAPL --interval daily --period 2y
  quant strategy create --template sma_cross --symbol AAPL
  quant backtest run --strategy my_sma --start 2022-01-01 --end 2023-12-31
  quant report show --backtest-id bt_20240913_001
  ```
- [ ] **Rich 기반 시각화**:
  - 진행률 표시
  - 테이블 형태 결과 출력
  - 컬러풀한 로그 메시지

### Sprint 3.2: 설정 관리 및 템플릿
- [ ] **전략 템플릿 시스템**:
  - 사전 정의된 전략 템플릿
  - 사용자 정의 전략 추가 기능
- [ ] **백테스트 프리셋**:
  - 일반적인 백테스트 설정 저장
  - 빠른 재실행을 위한 설정 템플릿

---

## 🔮 Phase 4: Advanced Features (지속적)

### Sprint 4.1: 전략 최적화
- [ ] **파라미터 최적화**:
  - Grid Search
  - Random Search
  - Bayesian Optimization (optuna)
- [ ] **Walk-Forward Analysis**:
  - 시기별 성과 검증
  - 오버피팅 방지

### Sprint 4.2: 포트폴리오 백테스트
- [ ] **다중 자산 백테스트**:
  - 포트폴리오 리밸런싱
  - 상관관계 분석
- [ ] **리스크 관리**:
  - 포지션 사이징 최적화
  - VaR 계산

### Sprint 4.3: 웹 대시보드 (선택사항)
- [ ] **FastAPI 백엔드**:
  - RESTful API 설계
  - 백테스트 결과 API 엔드포인트
- [ ] **React/Next.js 프론트엔드**:
  - 인터랙티브 차트 (plotly.js)
  - 전략 설정 UI

---

## 🛠️ 기술 스택 상세

### 백엔드 서비스
- **Python 3.12+**: 타입힌트 및 최신 기능 활용
- **UV**: 고속 패키지 관리 및 가상환경
- **vectorbt**: 고성능 백테스트 엔진
- **DuckDB**: 로컬 시계열 데이터베이스
- **Alpha Vantage API**: 시장 데이터 소스

### 개발 도구
- **black + ruff**: 코드 포맷팅 및 린팅
- **mypy**: 정적 타입 검사
- **pytest**: 테스트 프레임워크
- **GitHub Actions**: CI/CD 파이프라인

### CLI & 시각화
- **Typer**: 모던 CLI 프레임워크
- **Rich**: 콘솔 출력 강화
- **matplotlib/plotly**: 차트 생성

---

## 📊 마일스톤 및 일정

| Phase | 기간 | 주요 목표 | 완료 기준 |
|-------|------|-----------|-----------|
| Phase 1 | 2주 | 데이터 수집 및 기반 구축 | Alpha Vantage 데이터 수집 및 DuckDB 저장 완료 |
| Phase 2 | 4주 | 백테스트 엔진 및 전략 구현 | 기본 전략 3개 백테스트 실행 가능 |
| Phase 3 | 3주 | CLI 및 사용자 경험 개선 | 완전한 CLI 기반 워크플로우 완성 |
| Phase 4 | 지속적 | 고급 기능 및 최적화 | 전략 최적화 및 포트폴리오 백테스트 |

---

## 🎯 성공 지표 (KPI)

- [ ] **기능적 목표**:
  - 3개 이상의 검증된 전략 구현
  - 1년 이상 기간의 백테스트 실행 가능
  - 주요 성과 지표 10개 이상 계산

- [ ] **기술적 목표**:
  - 테스트 커버리지 80% 이상
  - 타입 검사 통과율 100%
  - 코드 품질 스코어 A 등급 (ruff 기준)

- [ ] **사용성 목표**:
  - 새 전략 추가 30분 이내
  - 백테스트 실행 5분 이내
  - 직관적인 CLI 명령어 체계
