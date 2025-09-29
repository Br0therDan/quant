# AGENTS.md
## Purpose
이 문서는 단일 사용자용 퀀트 백테스트 앱의 **코딩 가이드라인**을 정의한다.
목표는 유지보수·확장성·재현성 높은 백엔드 및 분석 환경을 구현하는 것이다## 8. ## 7. Security & Secrets
### **환경 변수 관리**
- API 키 및 민감정보는 `.env` → `.env.example`를 제공
- Docker 환경에서는 `.env` 파일 또는 환경 변수로 주입
- GitHub Actions에서는 Repository Secrets 사용

### **데이터베이스 보안**
- MongoDB 인증 활성화 (`--auth` 플래그)
- DuckDB 파일 권한 관리 (600)
- Docker 네트워크 격리 (internal/public 분리)

### **API 보안**
- FastAPI CORS 설정으로 허용 도메인 제한
- Rate limiting으로 API 남용 방지
- 백테스트 결과 민감정보 마스킹

### **컨테이너 보안**
- 비루트 사용자로 컨테이너 실행
- 최소 권한 원칙 적용
- 정기적인 베이스 이미지 업데이트g Strategy
### **Backend Testing (Python)**
- **단위 테스트**: pytest 기반 각 서비스별 핵심 로직
- **통합 테스트**: FastAPI TestClient로 API 엔드포인트 테스트
- **성능 테스트**: 대용량 백테스트 실행 시간 검증
- **데이터 테스트**: 알려진 결과와 백테스트 결과 비교
- **Mock 사용**: httpx-mock으로 Alpha Vantage API 외부 의존성 제거

### **Frontend Testing (TypeScript)**
- **컴포넌트 테스트**: React Testing Library 기반
- **E2E 테스트**: Playwright로 브라우저 자동화 테스트
- **타입 안전성**: TypeScript 컴파일 시 정적 분석
- **API 통합**: MSW(Mock Service Worker)로 API 모킹

### **통합 테스트**
- **Docker Compose**: 전체 스택 통합 테스트 환경
- **데이터베이스**: 테스트용 MongoDB 인스턴스 격리
- **CI/CD**: GitHub Actions에서 자동화된 테스트 파이프라인

## 1. Code Structure
- **마이크로서비스 기반 모노레포**
    ```
    quant/
    ├── services/
    │   ├── data-service/          # Alpha Vantage API, DuckDB
    │   ├── strategy-service/      # 전략 로직 및 파라미터 관리
    │   ├── backtest-service/      # vectorbt 백테스트 실행
    │   └── analytics-service/     # 성과 분석 및 리포트
    ├── shared/
    │   ├── models/               # Pydantic 데이터 모델
    │   ├── utils/                # 공통 유틸리티
    │   └── config/               # 설정 관리
    ├── tests/                    # 서비스별 통합 테스트
    └── scripts/                  # 개발/배포 스크립트
    ```

- **서비스별 독립성**: 각 서비스는 독립적인 책임을 가지며 명확한 인터페이스로 통신
- **공통 모듈 활용**: `shared/` 디렉토리를 통한 코드 재사용성 극대화

---

## 2. Language & Framework
- **Python 3.12+** (타입힌트 필수)
- **UV**: 고속 패키지 관리 및 가상환경 관리
- **vectorbt** 또는 **backtrader**: 백테스트 및 지표 계산
- **DuckDB**: 로컬 시계열 DB
- **Typer / Rich**: CLI 및 콘솔 시각화

---

## 3. Style Guide
- [PEP 8](https://peps.python.org/pep-0008/) 준수
- 모든 public 함수/클래스는 **docstring** 필수
- 타입힌트 필수 (`mypy` 통과)
- `black` + `ruff`로 포맷팅 & 린트 자동화
- 테스트는 `pytest` 기반, 최소 80% 커버리지 유지

---

## 4. Data Handling
- **Alpha Vantage API**:
  - `.env` 파일에 `ALPHAVANTAGE_API_KEY` 저장
  - Rate limiting: 5 calls/min, 500 calls/day 준수
  - 중복 호출 방지를 위한 DuckDB 캐싱 (TTL 24시간)
  - 에러 핸들링: 재시도 로직 (exponential backoff)
- **데이터 정합성**:
  - 결측치 보간 (forward fill)
  - 스플릿/배당 조정 자동 처리
  - 데이터 검증: OHLC 일관성 체크
- **DuckDB 최적화**:
  - 시계열 데이터용 파티셔닝 (월별)
  - 적절한 인덱스 설계 (symbol, date)
  - 압축 설정으로 디스크 사용량 최적화

---

## 5. Service Architecture
- **data-service**:
  - Alpha Vantage API 래퍼
  - DuckDB 스키마 관리
  - 데이터 검증 및 정제
- **strategy-service**:
  - 전략 클래스 베이스 및 팩토리 패턴
  - Pydantic 기반 파라미터 스키마
  - 전략 템플릿 관리
- **backtest-service**:
  - vectorbt 엔진 래핑
  - 거래 시뮬레이션 로직
  - 성과 지표 계산
- **analytics-service**:
  - 결과 분석 및 시각화
  - 리포트 생성 (PDF, HTML)
  - 벤치마크 비교

---

## 5. Git & CI/CD
- `main` 브랜치 보호 → PR 머지 필수
- PR 템플릿 사용 (feature / hotfix / doc)
- GitHub Actions:
  - lint & type-check (ruff, mypy)
  - pytest (최소 80% 커버리지)
  - 보안 검사 (bandit, safety)
  - 의존성 취약점 스캔
- **브랜치 전략**:
  - `main`: 프로덕션 준비 코드
  - `develop`: 개발 통합 브랜치
  - `feature/*`: 기능 개발 브랜치
  - `hotfix/*`: 긴급 수정 브랜치

---

## 6. Security & Secrets
- API 키 및 민감정보는 `.env` → `.env.example`를 제공
- GitHub Secret으로만 배포 파이프라인에 주입
- 로컬 개발 시 `.env` 파일 암호화 검토
- DuckDB 파일 권한 관리 (600)
- 백테스트 결과 민감정보 마스킹

---

## 7. Testing Strategy
- **단위 테스트**: 각 서비스별 핵심 로직
- **통합 테스트**: API 엔드포인트 및 데이터 파이프라인
- **성능 테스트**: 대용량 백테스트 실행 시간 검증
- **데이터 테스트**: 알려진 결과와 백테스트 결과 비교
- **Mock 사용**: Alpha Vantage API 호출 시 외부 의존성 제거

---

## 8. Performance & Monitoring
- **로깅**: 구조화된 로그 (JSON 형태)
- **메트릭**: 백테스트 실행 시간, API 호출 횟수
- **프로파일링**: cProfile로 병목 지점 식별
- **메모리 관리**: 대용량 데이터셋 처리 시 청크 단위 처리
- **캐시 최적화**: 자주 사용되는 데이터 우선 캐싱

---

## 9. Future Proof
- 향후 실거래 API 연계 (Alpaca, Interactive Brokers) 대비
- 포트폴리오 최적화(PyPortfolioOpt) 연동 고려
- 다중 사용자 지원을 위한 확장 가능한 아키텍처
- 클라우드 배포 옵션 (Docker, Kubernetes)
- 실시간 데이터 스트리밍 준비 (WebSocket)
