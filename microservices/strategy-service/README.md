# Strategy Service

퀀트 백테스트 플랫폼의 전략 관리 마이크로서비스

## 기능

- 투자 전략 CRUD 관리
- 전략 템플릿 시스템
- 전략 실행 및 백테스팅
- 성과 측정 및 분석
- RESTful API 제공

## API 엔드포인트

### 전략 관리
- `POST /api/v1/strategies/` - 전략 생성
- `GET /api/v1/strategies/` - 전략 목록 조회
- `GET /api/v1/strategies/{strategy_id}` - 전략 상세 조회
- `PUT /api/v1/strategies/{strategy_id}` - 전략 수정
- `DELETE /api/v1/strategies/{strategy_id}` - 전략 삭제

### 전략 실행
- `POST /api/v1/strategies/{strategy_id}/execute` - 전략 실행
- `GET /api/v1/strategies/{strategy_id}/executions` - 실행 내역 조회
- `GET /api/v1/strategies/{strategy_id}/performance` - 성과 조회

### 템플릿 관리
- `POST /api/v1/templates/` - 템플릿 생성
- `GET /api/v1/templates/` - 템플릿 목록 조회
- `POST /api/v1/templates/{template_id}/create-strategy` - 템플릿으로 전략 생성

### 시스템 상태
- `GET /api/v1/health/` - 기본 상태 확인
- `GET /api/v1/health/detailed` - 상세 상태 확인
- `GET /api/v1/health/readiness` - Kubernetes readiness probe
- `GET /api/v1/health/liveness` - Kubernetes liveness probe

## 전략 타입

- `BUY_AND_HOLD` - 매수 후 보유 전략
- `MOMENTUM` - 모멘텀 전략
- `RSI_MEAN_REVERSION` - RSI 평균 회귀 전략
- `SMA_CROSSOVER` - 단순이동평균선 교차 전략

## 실행

```bash
# 개발 환경 실행
python main.py

# 또는 uvicorn으로 실행
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

## 환경 설정

필요한 환경 변수:
- `MONGODB_URL` - MongoDB 연결 URL (기본값: mongodb://localhost:27017)
- `DATABASE_NAME` - 데이터베이스 이름 (기본값: quant_strategy)
- `DEBUG` - 디버그 모드 (기본값: false)

## 의존성

프로젝트의 의존성은 `pyproject.toml`에서 관리됩니다:
- FastAPI & Uvicorn (웹 프레임워크)
- Beanie & MongoDB (데이터베이스)
- Pandas & NumPy (데이터 처리)
- TA-Lib (기술적 지표)
- mysingle-quant (공통 유틸리티)
