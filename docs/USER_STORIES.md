# 📋 퀀트 백테스트 플랫폼 - 유저 스토리

## 🎯 **프로덕트 개요**

**목표 사용자**: 개인 투자자, 퀀트 트레이더, 금융 분석가
**핵심 가치**: 복잡한 백테스트를 간단한 UI로 실행하고 전문적인 분석 결과를 제공
**차별점**: 코딩 없이도 전문가 수준의 퀀트 전략 백테스트 가능

---

## 👤 **페르소나 정의**

### **Primary: 개인 투자자 (Alex)**
- **배경**: 5년차 개발자, 주식 투자 2년차
- **목표**: 체계적인 투자 전략 수립 및 백테스트
- **기술 수준**: 중급 (API 이해 가능, 프로그래밍 경험 있음)
- **페인 포인트**: 투자 전략의 과거 성과를 검증하고 싶지만 전문 도구는 비싸고 복잡함

### **Secondary: 퀀트 분석가 (Sam)**
- **배경**: 금융공학 석사, 헤지펀드 3년 경력
- **목표**: 빠른 전략 프로토타이핑 및 성과 검증
- **기술 수준**: 고급 (Python, R, 금융 모델링 전문)
- **페인 포인트**: 새로운 전략 아이디어를 빠르게 테스트하고 시각화할 도구 필요

---

## 🚀 **Epic 1: 대시보드 & 시작하기**

### **Epic Goal**: 사용자가 플랫폼을 처음 접했을 때 쉽게 시작할 수 있도록 안내

#### **Story 1.1: 대시보드 개요**
**As** 신규 사용자
**I want** 플랫폼의 핵심 기능을 한눈에 파악할 수 있는 대시보드
**So that** 어떤 기능부터 시작해야 할지 알 수 있다

**Acceptance Criteria:**
- [ ] 전체 백테스트 수, 성공률, 평균 수익률 등 KPI 표시
- [ ] 최근 실행한 백테스트 목록 (최대 5개)
- [ ] 빠른 시작 가이드 (4단계 이내)
- [ ] 시스템 상태 표시 (API 연결, 데이터 업데이트 상태)
- [ ] 인기 전략 추천 섹션

**API Endpoints:**
- `GET /api/v1/health`
- `GET /api/v1/backtests/?limit=5`
- `GET /api/v1/backtests/test-services`

---

#### **Story 1.2: 온보딩 플로우**
**As** 신규 사용자
**I want** 단계별 가이드를 통해 첫 백테스트를 실행
**So that** 플랫폼 사용법을 쉽게 익힐 수 있다

**Acceptance Criteria:**
- [ ] 4단계 온보딩: 워치리스트 → 전략 선택 → 백테스트 → 결과 분석
- [ ] 각 단계마다 툴팁 및 설명 제공
- [ ] 샘플 데이터로 테스트 실행 가능
- [ ] 건너뛰기 옵션 제공
- [ ] 진행률 표시

**API Endpoints:**
- `POST /api/v1/pipeline/setup-defaults`
- `POST /api/v1/backtests/integrated` (샘플 데이터)

---

## 📊 **Epic 2: 데이터 & 워치리스트 관리**

### **Epic Goal**: 사용자가 관심 있는 종목을 쉽게 관리하고 데이터 상태를 확인할 수 있도록 함

#### **Story 2.1: 워치리스트 생성 및 관리**
**As** 투자자
**I want** 관심 종목들을 그룹으로 관리
**So that** 포트폴리오별로 백테스트를 수행할 수 있다

**Acceptance Criteria:**
- [ ] 워치리스트 생성/수정/삭제
- [ ] 종목 검색 및 추가 (실시간 검색)
- [ ] 드래그 앤 드롭으로 종목 순서 변경
- [ ] 워치리스트별 색상 태그
- [ ] 기본 워치리스트 (Top 10 Tech, S&P 500 등) 제공

**API Endpoints:**
- `POST /api/v1/pipeline/watchlists`
- `GET /api/v1/pipeline/watchlists`
- `PUT /api/v1/pipeline/watchlists/{name}`
- `DELETE /api/v1/pipeline/watchlists/{name}`

---

#### **Story 2.2: 종목 정보 및 데이터 상태**
**As** 사용자
**I want** 각 종목의 기본 정보와 데이터 수집 상태를 확인
**So that** 백테스트에 사용할 수 있는 데이터인지 판단할 수 있다

**Acceptance Criteria:**
- [ ] 종목별 기본 정보 (회사명, 섹터, 시가총액 등)
- [ ] 데이터 커버리지 표시 (기간, 최신 업데이트 시간)
- [ ] 데이터 품질 지표 (결측치 비율, 이상값 등)
- [ ] 수동 데이터 업데이트 버튼
- [ ] 데이터 수집 진행률 실시간 표시

**API Endpoints:**
- `GET /api/v1/pipeline/company/{symbol}`
- `GET /api/v1/pipeline/coverage/{symbol}`
- `POST /api/v1/pipeline/collect-info/{symbol}`
- `POST /api/v1/pipeline/update`

---

## 🧠 **Epic 3: 전략 설정 및 관리**

### **Epic Goal**: 사용자가 다양한 퀀트 전략을 쉽게 설정하고 관리할 수 있도록 함

#### **Story 3.1: 전략 템플릿 선택**
**As** 초급 사용자
**I want** 검증된 전략 템플릿 중에서 선택
**So that** 복잡한 설정 없이도 전문적인 전략을 사용할 수 있다

**Acceptance Criteria:**
- [ ] 전략 카테고리별 분류 (트렌드 추종, 평균 회귀, 모멘텀 등)
- [ ] 각 전략의 설명, 장단점, 적합한 시장 조건 표시
- [ ] 전략별 과거 성과 통계 (백테스트 기반)
- [ ] 난이도 표시 (초급/중급/고급)
- [ ] 미리보기 기능 (샘플 결과)

**API Endpoints:**
- `GET /api/v1/strategies/templates`
- `GET /api/v1/strategies/templates/{template_id}`

---

#### **Story 3.2: 전략 파라미터 조정**
**As** 중급 사용자
**I want** 전략의 파라미터를 세부적으로 조정
**So that** 내 투자 스타일에 맞는 전략을 만들 수 있다

**Acceptance Criteria:**
- [ ] 파라미터별 설명 및 권장 범위 표시
- [ ] 슬라이더/입력 필드를 통한 직관적인 조정
- [ ] 파라미터 변경 시 실시간 영향도 시뮬레이션
- [ ] 파라미터 조합 저장 및 즐겨찾기
- [ ] A/B 테스트를 위한 다중 파라미터 설정

**API Endpoints:**
- `POST /api/v1/strategies`
- `PUT /api/v1/strategies/{strategy_id}`
- `GET /api/v1/strategies/{strategy_id}/validate`

---

#### **Story 3.3: 전략 성과 추적**
**As** 전략 개발자
**I want** 내가 만든 전략들의 성과를 추적
**So that** 어떤 전략이 효과적인지 비교 분석할 수 있다

**Acceptance Criteria:**
- [ ] 전략별 성과 대시보드
- [ ] 수익률, 샤프 비율, 최대 낙폭 등 핵심 지표 비교
- [ ] 시간별 성과 추이 차트
- [ ] 전략 간 상관관계 분석
- [ ] 성과 랭킹 및 베스트 전략 하이라이트

**API Endpoints:**
- `GET /api/v1/strategies`
- `GET /api/v1/strategies/{strategy_id}/performance`
- `GET /api/v1/strategies/compare?ids=1,2,3`

---

## 🎯 **Epic 4: 백테스트 실행 및 모니터링**

### **Epic Goal**: 사용자가 백테스트를 쉽게 실행하고 진행 상태를 실시간으로 확인할 수 있도록 함

#### **Story 4.1: 통합 백테스트 실행**
**As** 사용자
**I want** 원클릭으로 전체 백테스트를 실행
**So that** 복잡한 설정 과정 없이 빠르게 결과를 확인할 수 있다

**Acceptance Criteria:**
- [ ] 워치리스트, 전략, 기간을 선택하여 원클릭 실행
- [ ] 실행 전 예상 소요 시간 및 비용 표시
- [ ] 빠른 실행을 위한 프리셋 제공 (1개월, 1년, 5년)
- [ ] 백그라운드 실행 지원
- [ ] 실행 대기열 및 우선순위 관리

**API Endpoints:**
- `POST /api/v1/backtests/integrated`
- `GET /api/v1/backtests/{backtest_id}`

---

#### **Story 4.2: 실행 상태 모니터링**
**As** 사용자
**I want** 백테스트 진행 상황을 실시간으로 확인
**So that** 언제 완료될지 예상하고 다른 작업을 계획할 수 있다

**Acceptance Criteria:**
- [ ] 실시간 진행률 표시 (데이터 수집, 신호 생성, 시뮬레이션 단계별)
- [ ] 예상 완료 시간 및 남은 시간
- [ ] 중간 결과 미리보기 (처리된 데이터 포인트 수 등)
- [ ] 실행 중 취소 기능
- [ ] 오류 발생 시 상세한 에러 메시지

**API Endpoints:**
- `GET /api/v1/backtests/{backtest_id}/executions`
- `GET /api/v1/backtests/{backtest_id}/status`

---

#### **Story 4.3: 백테스트 히스토리 관리**
**As** 파워 유저
**I want** 과거 실행한 모든 백테스트를 체계적으로 관리
**So that** 이전 실험을 참조하고 재실행할 수 있다

**Acceptance Criteria:**
- [ ] 백테스트 목록 필터링 (날짜, 전략, 성과 등)
- [ ] 즐겨찾기 및 태그 기능
- [ ] 백테스트 복제 및 수정 실행
- [ ] 실행 설정 및 결과 비교 뷰
- [ ] 백테스트 삭제 및 아카이브

**API Endpoints:**
- `GET /api/v1/backtests/?status=COMPLETED&limit=50`
- `DELETE /api/v1/backtests/{backtest_id}`
- `POST /api/v1/backtests/{backtest_id}/clone`

---

## 📈 **Epic 5: 결과 분석 및 시각화**

### **Epic Goal**: 백테스트 결과를 직관적으로 이해하고 심층 분석할 수 있는 도구 제공

#### **Story 5.1: 성과 대시보드**
**As** 투자자
**I want** 백테스트 결과의 핵심 지표를 한눈에 확인
**So that** 전략의 효과를 빠르게 판단할 수 있다

**Acceptance Criteria:**
- [ ] 핵심 KPI 카드 (총 수익률, 연환산 수익률, 샤프 비율, 최대 낙폭)
- [ ] 수익률 곡선 차트 (벤치마크 대비)
- [ ] 월별/연도별 수익률 히트맵
- [ ] 승률 및 평균 수익/손실 표시
- [ ] 위험 지표 게이지 (VaR, 변동성 등)

**API Endpoints:**
- `GET /api/v1/backtests/results/?backtest_id={id}`
- `GET /api/v1/backtests/{backtest_id}/performance`

---

#### **Story 5.2: 상세 분석 차트**
**As** 분석가
**I want** 다양한 각도에서 성과를 분석할 수 있는 차트
**So that** 전략의 강점과 약점을 정확히 파악할 수 있다

**Acceptance Criteria:**
- [ ] 포트폴리오 가치 추이 (누적 수익률)
- [ ] 드로우다운 차트 (수중 기간 시각화)
- [ ] 월별 수익률 분포 히스토그램
- [ ] 롤링 샤프 비율 추이
- [ ] 거래 빈도 및 홀딩 기간 분석

**API Endpoints:**
- `GET /api/v1/backtests/{backtest_id}/executions`
- `GET /api/v1/backtests/{backtest_id}/trades`

---

#### **Story 5.3: 거래 내역 분석**
**As** 트레이더
**I want** 개별 거래의 상세 정보를 확인
**So that** 전략의 매매 패턴과 수익 구조를 이해할 수 있다

**Acceptance Criteria:**
- [ ] 거래 내역 테이블 (날짜, 종목, 매수/매도, 수량, 가격, 수익률)
- [ ] 거래별 수익/손실 분포
- [ ] 홀딩 기간별 성과 분석
- [ ] 최고/최악의 거래 하이라이트
- [ ] 거래 타이밍 차트 (가격 차트 위에 매매 신호 표시)

**API Endpoints:**
- `GET /api/v1/backtests/{backtest_id}/executions`
- `GET /api/v1/market-data/data/{symbol}?start_date=X&end_date=Y`

---

## 🔧 **Epic 6: 고급 기능 및 설정**

### **Epic Goal**: 파워 유저를 위한 고급 분석 도구 및 시스템 관리 기능 제공

#### **Story 6.1: 멀티 전략 포트폴리오**
**As** 포트폴리오 매니저
**I want** 여러 전략을 조합한 포트폴리오 백테스트
**So that** 분산 투자 효과를 검증할 수 있다

**Acceptance Criteria:**
- [ ] 전략별 가중치 설정 UI
- [ ] 리밸런싱 주기 및 방법 선택
- [ ] 전략 간 상관관계 매트릭스
- [ ] 포트폴리오 효율적 경계선 차트
- [ ] 개별 전략 vs 포트폴리오 성과 비교

**API Endpoints:**
- `POST /api/v1/backtests/portfolio`
- `GET /api/v1/strategies/correlation-matrix`

---

#### **Story 6.2: 위험 관리 설정**
**As** 리스크 매니저
**I want** 상세한 위험 관리 규칙을 설정
**So that** 극단적 손실을 방지할 수 있다

**Acceptance Criteria:**
- [ ] 최대 손실 한도 설정 (일간, 월간, 전체)
- [ ] 포지션 크기 제한 규칙
- [ ] 스톱로스 및 익절 규칙 설정
- [ ] 섹터/종목별 집중도 제한
- [ ] 시나리오 분석 (스트레스 테스트)

**API Endpoints:**
- `POST /api/v1/backtests` (risk management config)
- `GET /api/v1/backtests/{id}/risk-analysis`

---

#### **Story 6.3: 시스템 설정 및 모니터링**
**As** 시스템 관리자
**I want** 플랫폼의 상태와 성능을 모니터링
**So that** 안정적인 서비스를 제공할 수 있다

**Acceptance Criteria:**
- [ ] API 응답 시간 및 성공률 모니터링
- [ ] 데이터 수집 상태 및 오류 로그
- [ ] 사용자 활동 대시보드
- [ ] 시스템 리소스 사용량 (CPU, 메모리, 스토리지)
- [ ] 알림 설정 (오류, 성능 이슈 등)

**API Endpoints:**
- `GET /api/v1/health`
- `GET /api/v1/backtests/test-services`
- `GET /api/v1/pipeline/status`

---

## 📱 **UI/UX 요구사항**

### **디자인 원칙**
- **직관성**: 금융 비전문가도 쉽게 사용할 수 있는 인터페이스
- **전문성**: 복잡한 분석 결과를 명확하게 표현
- **효율성**: 빠른 데이터 로딩과 반응형 차트
- **접근성**: 다양한 화면 크기와 장애인 접근성 고려

### **핵심 컴포넌트**
- **차트 라이브러리**: D3.js 또는 Chart.js 기반 금융 차트
- **데이터 테이블**: 가상화된 대용량 데이터 테이블
- **실시간 업데이트**: WebSocket 기반 진행률 표시
- **반응형 레이아웃**: 모바일, 태블릿, 데스크톱 대응

### **성능 요구사항**
- **초기 로딩**: 3초 이내 대시보드 표시
- **차트 렌더링**: 1만 포인트 데이터를 1초 이내 렌더링
- **API 응답**: 평균 500ms 이내 응답
- **실시간 업데이트**: 100ms 이내 UI 반영

---

## 🎨 **와이어프레임 & 플로우**

### **메인 플로우**
```
1. 로그인/대시보드 →
2. 워치리스트 설정 →
3. 전략 선택/설정 →
4. 백테스트 실행 →
5. 결과 분석 →
6. 보고서 생성/공유
```

### **화면 구성 (5개 메인 페이지)**
1. **대시보드**: KPI 요약, 최근 활동, 빠른 시작
2. **데이터 관리**: 워치리스트, 종목 정보, 데이터 상태
3. **전략 센터**: 전략 템플릿, 파라미터 설정, 성과 비교
4. **백테스트**: 실행 설정, 진행 모니터링, 히스토리
5. **분석 결과**: 성과 차트, 거래 내역, 상세 분석

---

## ✅ **개발 우선순위**

### **Phase 1 (MVP - 4주)**
- [ ] Story 1.1: 기본 대시보드
- [ ] Story 2.1: 워치리스트 관리
- [ ] Story 3.1: 전략 템플릿 선택
- [ ] Story 4.1: 통합 백테스트 실행
- [ ] Story 5.1: 기본 성과 대시보드

### **Phase 2 (Enhanced - 3주)**
- [ ] Story 1.2: 온보딩 플로우
- [ ] Story 2.2: 종목 정보 및 상태
- [ ] Story 4.2: 실행 상태 모니터링
- [ ] Story 5.2: 상세 분석 차트

### **Phase 3 (Advanced - 3주)**
- [ ] Story 3.2: 전략 파라미터 조정
- [ ] Story 4.3: 백테스트 히스토리
- [ ] Story 5.3: 거래 내역 분석
- [ ] Story 6.3: 시스템 모니터링

### **Phase 4 (Pro - 4주)**
- [ ] Story 3.3: 전략 성과 추적
- [ ] Story 6.1: 멀티 전략 포트폴리오
- [ ] Story 6.2: 위험 관리 설정

**총 개발 기간: 14주 (약 3.5개월)**

---

*이 문서는 프론트엔드 개발팀과 제품 기획자가 함께 참조하여 사용자 중심의 인터페이스를 구축하는 데 활용됩니다.*
