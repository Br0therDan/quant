# Phase 1 Backend API 검증 가이드

**작성일**: 2025-01-16  
**작성자**: GitHub Copilot  
**목적**: Phase 1 Frontend가 사용하는 Backend API 동작 확인

---

## Executive Summary

Phase 1 Frontend에서 사용하는 **3개 AI API가 모두 구현 완료**되어 있습니다:

1. ✅ **ML 모델 관리 API** (`/api/v1/ml/*`)
2. ✅ **시장 국면 감지 API** (`/api/v1/market-data/regime/`)
3. ✅ **포트폴리오 예측 API** (`/api/v1/dashboard/portfolio/forecast`)

**다음 단계**: Backend 서버를 시작하고 각 API를 테스트하여 정상 동작 확인

---

## API 목록 및 매핑

### 1. ML 모델 관리 API

#### Frontend Hook: `useMLModel`

```typescript
// frontend/src/hooks/useMLModel.ts
const { modelList, modelDetail, compareModels, trainModel } = useMLModel();
```

#### Backend Endpoints

| Frontend 함수        | Backend API                                             | 구현 위치                                             | 상태 |
| -------------------- | ------------------------------------------------------- | ----------------------------------------------------- | ---- |
| `useModelList`       | GET `/api/v1/ml/models`                                 | `backend/app/api/routes/ml/train.py:get_models()`     | ✅   |
| `useModelDetail`     | GET `/api/v1/ml/models/{version}`                       | `backend/app/api/routes/ml/train.py:get_model_info()` | ✅   |
| `useModelComparison` | GET `/api/v1/ml/models/compare/{metric}?versions=v1,v2` | `backend/app/api/routes/ml/train.py:compare_models()` | ✅   |
| `useTrainModel`      | POST `/api/v1/ml/train`                                 | `backend/app/api/routes/ml/train.py:train_model()`    | ✅   |
| `useDeleteModel`     | DELETE `/api/v1/ml/models/{version}`                    | `backend/app/api/routes/ml/train.py:delete_model()`   | ✅   |

#### 테스트 시나리오

**1.1 모델 목록 조회**

```bash
curl -X GET "http://localhost:8500/api/v1/ml/models" \
  -H "Authorization: Bearer $TOKEN"

# 예상 응답
{
  "models": [
    {
      "version": "v20250116_120000",
      "model_type": "signal",
      "created_at": "2025-01-16T12:00:00",
      "metrics": { "accuracy": 0.85 },
      "feature_count": 42,
      "num_iterations": 100
    }
  ],
  "total": 1,
  "latest_version": "v20250116_120000"
}
```

**1.2 모델 학습**

```bash
curl -X POST "http://localhost:8500/api/v1/ml/train" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "symbols": ["AAPL", "MSFT"],
    "lookback_days": 500,
    "test_size": 0.2,
    "num_boost_round": 100,
    "threshold": 0.02
  }'

# 예상 응답
{
  "status": "started",
  "message": "모델 학습이 백그라운드에서 시작되었습니다",
  "task_id": "task_123"
}
```

---

### 2. 시장 국면 감지 API

#### Frontend Hook: `useRegimeDetection`

```typescript
// frontend/src/hooks/useRegimeDetection.ts
const { currentRegime, refreshRegime } = useRegimeDetection({ symbol: "AAPL" });
```

#### Backend Endpoints

| Frontend 함수      | Backend API                                                            | 구현 위치                                                          | 상태 |
| ------------------ | ---------------------------------------------------------------------- | ------------------------------------------------------------------ | ---- |
| `useCurrentRegime` | GET `/api/v1/market-data/regime/?symbol={symbol}&lookback_days={days}` | `backend/app/api/routes/market_data/regime.py:get_market_regime()` | ✅   |
| `useRefreshRegime` | GET `/api/v1/market-data/regime/?symbol={symbol}&refresh=true`         | 동일 (refresh 파라미터)                                            | ✅   |

#### 테스트 시나리오

**2.1 국면 감지 조회**

```bash
curl -X GET "http://localhost:8500/api/v1/market-data/regime/?symbol=AAPL&lookback_days=30" \
  -H "Authorization: Bearer $TOKEN"

# 예상 응답
{
  "success": true,
  "data": {
    "symbol": "AAPL",
    "regime": "bullish",
    "confidence": 0.85,
    "lookback_days": 30,
    "as_of": "2025-01-16T12:00:00Z",
    "metrics": {
      "avg_return_pct": 0.8,
      "volatility_pct": 12.5,
      "max_drawdown_pct": -3.2,
      "momentum_z_score": 1.2
    }
  },
  "metadata": { ... },
  "message": "Market regime snapshot retrieved"
}
```

**2.2 국면 강제 새로고침**

```bash
curl -X GET "http://localhost:8500/api/v1/market-data/regime/?symbol=AAPL&refresh=true" \
  -H "Authorization: Bearer $TOKEN"

# 예상 응답: 동일 (새로 계산된 결과)
```

---

### 3. 포트폴리오 예측 API

#### Frontend Hook: `usePortfolioForecast`

```typescript
// frontend/src/hooks/usePortfolioForecast.ts
const { forecastData, scenarios } = usePortfolioForecast({ horizonDays: 30 });
```

#### Backend Endpoints

| Frontend 함수               | Backend API                                                    | 구현 위치                                                      | 상태 |
| --------------------------- | -------------------------------------------------------------- | -------------------------------------------------------------- | ---- |
| `usePortfolioForecastQuery` | GET `/api/v1/dashboard/portfolio/forecast?horizon_days={days}` | `backend/app/api/routes/dashboard.py:get_portfolio_forecast()` | ✅   |

#### 테스트 시나리오

**3.1 포트폴리오 예측 조회**

```bash
curl -X GET "http://localhost:8500/api/v1/dashboard/portfolio/forecast?horizon_days=30" \
  -H "Authorization: Bearer $TOKEN"

# 예상 응답
{
  "success": true,
  "data": {
    "as_of": "2025-01-16T12:00:00Z",
    "horizon_days": 30,
    "last_portfolio_value": 100000.0,
    "expected_return_pct": 5.2,
    "expected_volatility_pct": 12.8,
    "percentile_bands": [
      { "percentile": 5, "projected_value": 95000.0 },
      { "percentile": 50, "projected_value": 105200.0 },
      { "percentile": 95, "projected_value": 115000.0 }
    ],
    "methodology": "Gaussian projection from historical returns"
  },
  "metadata": { ... },
  "message": "30일 포트폴리오 예측 생성 완료"
}
```

---

## Backend 서버 시작 가이드

### 1. 환경 준비

```bash
cd /Users/donghakim/quant

# .env 파일 확인 (필수 환경 변수)
cat .env
# ALPHA_VANTAGE_API_KEY=your_api_key
# MONGODB_SERVER=localhost:27019
# DUCKDB_PATH=./app/data/quant.duckdb
```

### 2. MongoDB 시작 (Docker)

```bash
# MongoDB 컨테이너 시작
docker-compose up -d mongodb

# 상태 확인
docker ps | grep mongo
```

### 3. Backend 서버 시작

```bash
cd backend

# 방법 1: uv (개발 모드)
uv run fastapi dev app/main.py --port 8500

# 방법 2: Docker
cd ..
pnpm docker:backend
```

### 4. API 문서 확인

브라우저에서 열기:

- **Swagger UI**: http://localhost:8500/docs
- **ReDoc**: http://localhost:8500/redoc
- **OpenAPI JSON**: http://localhost:8500/openapi.json

---

## 통합 테스트 시나리오

### Phase 1 Full Flow Test

**목표**: 3개 API를 순차적으로 호출하여 Phase 1 Frontend 흐름 재현

#### Step 1: 인증 (토큰 발급)

```bash
# OAuth2 로그인 (실제 토큰 필요)
# 또는 테스트 토큰 사용
export TOKEN="your_access_token"
```

#### Step 2: ML 모델 학습

```bash
# 2.1 모델 학습 시작
curl -X POST "http://localhost:8500/api/v1/ml/train" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "symbols": ["AAPL"],
    "lookback_days": 500,
    "num_boost_round": 50
  }'

# 2.2 모델 목록 조회 (30초 후)
sleep 30
curl -X GET "http://localhost:8500/api/v1/ml/models" \
  -H "Authorization: Bearer $TOKEN"

# 2.3 최신 모델 상세 조회
VERSION=$(curl -s -X GET "http://localhost:8500/api/v1/ml/models" \
  -H "Authorization: Bearer $TOKEN" | jq -r '.latest_version')

curl -X GET "http://localhost:8500/api/v1/ml/models/$VERSION" \
  -H "Authorization: Bearer $TOKEN"
```

#### Step 3: 시장 국면 감지

```bash
# 3.1 AAPL 국면 감지
curl -X GET "http://localhost:8500/api/v1/market-data/regime/?symbol=AAPL&lookback_days=30" \
  -H "Authorization: Bearer $TOKEN" | jq

# 3.2 여러 심볼 국면 비교
for symbol in AAPL MSFT GOOGL; do
  echo "=== $symbol ==="
  curl -s -X GET "http://localhost:8500/api/v1/market-data/regime/?symbol=$symbol" \
    -H "Authorization: Bearer $TOKEN" | jq '.data | {symbol, regime, confidence}'
done
```

#### Step 4: 포트폴리오 예측

```bash
# 4.1 30일 예측
curl -X GET "http://localhost:8500/api/v1/dashboard/portfolio/forecast?horizon_days=30" \
  -H "Authorization: Bearer $TOKEN" | jq

# 4.2 여러 기간 예측 비교
for days in 7 14 30 60 90; do
  echo "=== ${days}일 예측 ==="
  curl -s -X GET "http://localhost:8500/api/v1/dashboard/portfolio/forecast?horizon_days=$days" \
    -H "Authorization: Bearer $TOKEN" | jq '.data | {horizon_days, expected_return_pct}'
done
```

---

## 성능 목표 검증

### Phase 1 KPI

| API             | 목표 응답 시간 | 측정 방법       |
| --------------- | -------------- | --------------- |
| ML 모델 목록    | < 1초          | `time curl ...` |
| 시장 국면 감지  | < 2초          | `time curl ...` |
| 포트폴리오 예측 | < 3초          | `time curl ...` |

### 성능 측정 스크립트

```bash
#!/bin/bash
# perf_test.sh

echo "=== Phase 1 API 성능 테스트 ==="

# 1. ML 모델 목록
echo -n "1. ML 모델 목록: "
time curl -s -X GET "http://localhost:8500/api/v1/ml/models" \
  -H "Authorization: Bearer $TOKEN" > /dev/null
echo ""

# 2. 시장 국면 감지
echo -n "2. 시장 국면 감지: "
time curl -s -X GET "http://localhost:8500/api/v1/market-data/regime/?symbol=AAPL" \
  -H "Authorization: Bearer $TOKEN" > /dev/null
echo ""

# 3. 포트폴리오 예측
echo -n "3. 포트폴리오 예측: "
time curl -s -X GET "http://localhost:8500/api/v1/dashboard/portfolio/forecast" \
  -H "Authorization: Bearer $TOKEN" > /dev/null
echo ""

echo "=== 테스트 완료 ==="
```

---

## 알려진 이슈 및 주의사항

### 1. 인증 필요

- 모든 API는 OAuth2 인증 필요 (`Authorization: Bearer $TOKEN`)
- 테스트 시 먼저 로그인하여 토큰 발급

### 2. 데이터 의존성

- **ML 모델 API**: DuckDB에 market_data 필요
- **시장 국면 API**: DuckDB에 symbol 데이터 필요
- **포트폴리오 예측 API**: 사용자 포트폴리오 히스토리 필요 (최소 6개월)

### 3. 백그라운드 작업

- ML 모델 학습은 백그라운드에서 실행 (30초~5분 소요)
- `task_id`로 진행 상황 추적 가능 (향후 구현)

### 4. 캐싱

- 시장 국면 API는 결과를 캐싱 (refresh=true로 강제 갱신)
- 포트폴리오 예측 API도 캐싱 (5분 TTL)

---

## 다음 단계

### 1. Backend 서버 시작 및 API 테스트 (우선순위: 최상)

```bash
# 1. MongoDB 시작
pnpm docker:backend

# 2. Backend 서버 시작
cd backend && uv run fastapi dev app/main.py --port 8500

# 3. API 문서 확인
open http://localhost:8500/docs

# 4. 통합 테스트 실행
bash perf_test.sh
```

### 2. Frontend-Backend 연동 검증

```bash
# 1. Frontend 서버 시작
cd frontend && pnpm dev

# 2. 브라우저에서 테스트
open http://localhost:3000

# 3. ML 모델 관리 페이지 테스트
open http://localhost:3000/ml-models

# 4. 대시보드 페이지 테스트 (국면, 예측)
open http://localhost:3000/dashboard
```

### 3. E2E 테스트 작성

```bash
# Playwright E2E 테스트
cd frontend
pnpm test:e2e
```

### 4. 기존 훅 통합 (Phase 1.7)

[PHASE1_INTEGRATION_PLAN.md](./PHASE1_INTEGRATION_PLAN.md) 참고

---

## 결론

Phase 1 Frontend가 사용하는 **모든 Backend API가 이미 구현 완료**되어 있습니다!

**현재 상태**:

- ✅ ML 모델 관리 API (5개 엔드포인트)
- ✅ 시장 국면 감지 API (1개 엔드포인트)
- ✅ 포트폴리오 예측 API (1개 엔드포인트)

**다음 작업**:

1. **Backend 서버 시작** (MongoDB + FastAPI)
2. **API 동작 검증** (통합 테스트)
3. **Frontend 연동 테스트** (브라우저)
4. **성능 측정** (< 1초/2초/3초 목표)

Phase 1이 거의 완료되었습니다! Backend 서버만 시작하면 전체 시스템이 동작합니다!
🎉

---

**작성자**: GitHub Copilot  
**작성일**: 2025-01-16  
**버전**: 1.0
