# Backtest Service

퀀트 백테스트 플랫폼의 백테스트 실행 마이크로서비스

## 기능

- 백테스트 CRUD 관리
- 백테스트 실행 및 시뮬레이션
- 성과 지표 계산 및 분석
- 거래 내역 추적
- RESTful API 제공

## API 엔드포인트

### 백테스트 관리
- `POST /api/v1/backtests/` - 백테스트 생성
- `GET /api/v1/backtests/` - 백테스트 목록 조회
- `GET /api/v1/backtests/{backtest_id}` - 백테스트 상세 조회
- `PUT /api/v1/backtests/{backtest_id}` - 백테스트 수정
- `DELETE /api/v1/backtests/{backtest_id}` - 백테스트 삭제

### 백테스트 실행
- `POST /api/v1/backtests/{backtest_id}/execute` - 백테스트 실행
- `GET /api/v1/backtests/{backtest_id}/executions` - 실행 내역 조회

### 결과 조회
- `GET /api/v1/backtests/results/` - 백테스트 결과 조회

### 시스템 상태
- `GET /api/v1/health/` - 기본 상태 확인
- `GET /api/v1/health/detailed` - 상세 상태 확인
- `GET /api/v1/health/readiness` - Kubernetes readiness probe
- `GET /api/v1/health/liveness` - Kubernetes liveness probe

## 백테스트 상태

- `PENDING` - 대기 중
- `RUNNING` - 실행 중
- `COMPLETED` - 완료
- `FAILED` - 실패
- `CANCELLED` - 취소

## 거래 타입

- `BUY` - 매수
- `SELL` - 매도

## 주문 타입

- `MARKET` - 시장가 주문
- `LIMIT` - 지정가 주문
- `STOP` - 스톱 주문
- `STOP_LIMIT` - 스톱 지정가 주문

## 성과 지표

- 총 수익률 (Total Return)
- 연환산 수익률 (Annualized Return)
- 변동성 (Volatility)
- 샤프 비율 (Sharpe Ratio)
- 최대 낙폭 (Max Drawdown)
- 승률 (Win Rate)
- 거래 통계

## 실행

```bash
# 개발 환경 실행
python main.py

# 또는 uvicorn으로 실행
uvicorn main:app --host 0.0.0.0 --port 8003 --reload
```

## 환경 설정

필요한 환경 변수:
- `MONGODB_URL` - MongoDB 연결 URL (기본값: mongodb://localhost:27017)
- `DATABASE_NAME` - 데이터베이스 이름 (기본값: quant_backtest)
- `DEBUG` - 디버그 모드 (기본값: false)

## 의존성

프로젝트의 의존성은 `pyproject.toml`에서 관리됩니다:
- FastAPI & Uvicorn (웹 프레임워크)
- Beanie & MongoDB (데이터베이스)
- Pandas & NumPy (데이터 처리)
- VectorBT (백테스트 엔진)
- mysingle-quant (공통 유틸리티)
