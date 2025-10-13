# Strategy & Backtest 개선 프로젝트 문서

> **목적**: 백테스트 시스템의 아키텍처 개선 및 확장성 강화  
> **작성일**: 2025년 10월 13일

## 📚 문서 구성

### 1. [아키텍처 검토](./ARCHITECTURE_REVIEW.md)

**현재 시스템 분석 및 문제점 파악**

- 현재 아키텍처 구조 분석
- 12가지 주요 문제점 식별
  - 아키텍처 레벨 (SRP 위반, DRY 위반, DI 불완전)
  - 전략 시스템 (결합도 높음, 검증 부재, 중복 계산)
  - 백테스트 실행 (하드코딩, 추상화 부재, 로직 분산)
  - 데이터 처리 (비효율, 메모리 문제, 검증 부재)
- 개선 제안 사항 (12가지 솔루션)
- 4단계 구현 우선순위 로드맵

**주요 내용**:

- 문제 진단 및 영향도 분석
- 해결 방안 제시
- 리팩토링 일정 (12주 로드맵)

### 2. [Phase 1 리팩토링 가이드](./REFACTORING_PHASE1.md)

**긴급 개선 사항 구현 가이드 (1-2주)**

**P1.1 의존성 주입 개선**:

- `BacktestService` 생성자 리팩토링
- `ServiceFactory` 업데이트
- `set_dependencies()` 메서드 제거
- 완전한 객체 생성 보장

**P1.2 중복 거래 로직 통합**:

- `TradeEngine` 클래스 신규 구현
- `Portfolio` 클래스 구현
- `TradingSimulator` 제거
- 수수료/슬리피지 계산 통일

**P1.3 전략 파라미터 타입 안전성**:

- 전략별 Config 클래스 (Pydantic)
- `Strategy.parameters` → `Strategy.config` 변경
- 런타임 타입 검증
- 마이그레이션 스크립트

**포함 내용**:

- 단계별 구현 코드
- 테스트 전략 (단위/통합/성능)
- 배포 체크리스트
- 롤백 계획

### 3. [새로운 아키텍처 설계](./NEW_ARCHITECTURE.md)

**Phase 2-4 구현을 위한 상세 설계 (3-12주)**

**레이어드 아키텍처**:

```
API Layer → Application Layer → Domain Layer → Infrastructure Layer
```

**핵심 컴포넌트**:

- `BacktestOrchestrator`: 워크플로우 조율
- `StrategyExecutor`: 전략 실행 전담
- `TradeEngine`: 거래 엔진
- `PerformanceAnalyzer`: 통합 성과 분석
- `DataProcessor`: DuckDB 기반 고속 처리

**확장 포인트**:

- 전략 플러그인 시스템
- 커스텀 주문 타입
- 벤치마크 비교
- 병렬 백테스트

**성능 최적화**:

- DuckDB SQL 기반 지표 계산
- 스트리밍 백테스트
- 지표 계산 캐싱
- 멀티프로세싱

## 🎯 핵심 개선 목표

### 즉시 해결 (Phase 1) ✅ 완료

- ✅ **의존성 주입**: 서비스 생성 시점 완전 초기화
- ✅ **중복 제거**: 거래 로직 단일 엔진으로 통합
- ✅ **타입 안전성**: Pydantic 기반 파라미터 검증

**완료일**: 2025-10-13  
**테스트**: 12/12 passed  
**상세**: [CHANGELOG.md](./CHANGELOG.md) 참조

### 단기 개선 (Phase 2) ⏳ 예정

- 📊 **책임 분리**: 오케스트레이터 패턴 도입
- 📈 **성과 분석**: 8가지 이상 지표 지원
- 🔧 **지표 라이브러리**: 중복 계산 제거, 캐싱

### 중기 개선 (Phase 3)

- 🚀 **DuckDB 활용**: SQL 기반 10배 성능 향상
- 💾 **스트리밍**: 메모리 효율 80% 개선
- 🔌 **플러그인**: 동적 전략 등록

### 장기 개선 (Phase 4)

- 📝 **주문 타입**: 4가지 주문 타입 지원
- ✔️ **데이터 검증**: 자동화 파이프라인
- ⚡ **병렬 처리**: 5배 속도 향상

## 📊 성공 지표

### 코드 품질

- [ ] `BacktestService` 라인 수 50% 감소 (707 → ~350줄)
- [ ] 중복 코드 50% 이상 제거
- [ ] 테스트 커버리지 80% 이상

### 성능

- [ ] DuckDB 쿼리 성능 10배 향상
- [ ] 메모리 사용량 80% 감소
- [ ] 백테스트 처리 속도 5배 향상

### 확장성

- [ ] 전략 추가 시간 30분 이내
- [ ] 커스텀 전략 플러그인 지원
- [ ] 100만 행 이상 데이터 처리

### 안정성

- [ ] 타입 에러 0건
- [ ] 데이터 검증 자동화 100%
- [ ] 롤백 가능한 마이그레이션

## 🚀 시작하기

### 1. 현재 상태 파악

```bash
# 아키텍처 검토 문서 읽기
cat docs/backend/strategy_backtest/ARCHITECTURE_REVIEW.md
```

### 2. Phase 1 구현

```bash
# 리팩토링 가이드 참조
cat docs/backend/strategy_backtest/REFACTORING_PHASE1.md

# 의존성 주입 개선
# 1. BacktestService 수정
# 2. ServiceFactory 업데이트
# 3. 테스트 실행
cd backend && uv run pytest tests/test_service_factory.py -v
```

### 3. 새 아키텍처 구현 (Phase 2+)

```bash
# 상세 설계 참조
cat docs/backend/strategy_backtest/NEW_ARCHITECTURE.md

# 레이어별 구현
# 1. Domain Layer (모델)
# 2. Infrastructure Layer (DB)
# 3. Application Layer (서비스)
# 4. API Layer (라우트)
```

## 📈 진행 상황 추적

### Week 1-2 (Phase 1) 🔴 긴급

- [ ] P1.1: 의존성 주입 개선
- [ ] P1.2: 거래 로직 통합
- [ ] P1.3: 파라미터 타입 안전성
- [ ] 테스트 작성 및 검증
- [ ] 스테이징 배포

### Week 3-4 (Phase 2) 🟡 중요

- [ ] P2.1: BacktestOrchestrator 구현
- [ ] P2.2: PerformanceAnalyzer 통합
- [ ] P2.3: 기술적 지표 라이브러리
- [ ] 통합 테스트
- [ ] 프로덕션 배포

### Week 5-8 (Phase 3) 🟢 개선

- [ ] P3.1: DuckDB 활용 강화
- [ ] P3.2: 스트리밍 백테스트
- [ ] P3.3: 전략 팩토리 패턴
- [ ] 성능 벤치마킹

### Week 9-12 (Phase 4) 🔵 최적화

- [ ] P4.1: 다중 주문 타입
- [ ] P4.2: 데이터 검증 파이프라인
- [ ] P4.3: 병렬 백테스트
- [ ] 최종 문서화

## 🔗 관련 문서

### 프로젝트 문서

- [AGENTS.md](../../../AGENTS.md) - 프로젝트 전체 가이드
- [Backend AGENTS.md](../../AGENTS.md) - 백엔드 개발 가이드
- [Frontend AGENTS.md](../../../frontend/AGENTS.md) - 프론트엔드 가이드

### 백엔드 문서

- [Backend README](../../README.md) - 백엔드 개요
- [Dashboard](../DASHBOARD.md) - 대시보드 설계
- [Market Data](../market_data/) - 시장 데이터 문서

### API 문서

- [OpenAPI Docs](http://localhost:8500/docs) - 라이브 API 문서
- [ReDoc](http://localhost:8500/redoc) - API 레퍼런스

## 💡 개발 팁

### 코드 품질 유지

```bash
# 포맷팅
cd backend && uv run ruff format

# 린팅
cd backend && uv run ruff check --fix

# 타입 체크
cd backend && uv run mypy app/

# 테스트
cd backend && uv run pytest -v
```

### 성능 프로파일링

```bash
# 백테스트 성능 측정
cd backend && uv run python -m cProfile -o backtest.prof scripts/benchmark_backtest.py

# 프로파일 분석
uv run python -m pstats backtest.prof
```

### 데이터베이스

```bash
# DuckDB 쿼리 실행
cd backend && uv run python
>>> import duckdb
>>> conn = duckdb.connect('app/data/quant.duckdb')
>>> conn.execute("SELECT * FROM market_data LIMIT 10").df()

# MongoDB 조회
mongosh mongodb://localhost:27019
> use quant
> db.strategies.find()
```

## 🤝 기여 가이드

### Pull Request 프로세스

1. 이슈 생성 (개선 제안)
2. 브랜치 생성 (`feature/strategy-refactor-p1`)
3. 코드 작성 (TDD 권장)
4. 테스트 추가
5. PR 생성 (리뷰 요청)
6. 코드 리뷰 반영
7. 머지 후 배포

### 코딩 컨벤션

- **타입 힌트 필수**: 모든 함수/메서드
- **Docstring 필수**: Google 스타일
- **테스트 커버리지**: 80% 이상
- **린트 통과**: Ruff 경고 0건

## 📞 문의

- **아키텍처 관련**: GitHub Issues
- **버그 리포트**: GitHub Issues (bug label)
- **기능 제안**: GitHub Discussions

---

**마지막 업데이트**: 2025년 10월 13일  
**다음 리뷰**: Phase 1 완료 후 (2주 후)
