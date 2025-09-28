# 📁 Pipeline API Routes - Modular Structure

## 🎯 **개요**

Pipeline API가 기능별로 모듈화되어 유지보수성과 가독성이 크게 향상되었습니다.

## 📂 **파일 구조**

```
backend/app/api/routes/
├── pipeline.py          # 🔗 메인 라우터 (sub-routers 통합)
├── status.py           # 📊 파이프라인 상태 및 모니터링
├── companies.py        # 🏢 회사 데이터 수집 및 조회
└── watchlists.py       # 📝 워치리스트 관리 (CRUD)
```

## 🔧 **각 모듈별 기능**

### **1. status.py - Pipeline Status & Monitoring**
- `GET /pipeline/status` - 전체 시스템 상태 확인
- `POST /pipeline/setup-defaults` - 기본 설정 초기화
- `POST /pipeline/update` - 백그라운드 데이터 업데이트

### **2. companies.py - Company Data Management**
- `POST /pipeline/collect-info/{symbol}` - 개별 종목 정보 수집
- `POST /pipeline/collect-data/{symbol}` - 개별 종목 가격 데이터 수집
- `GET /pipeline/coverage/{symbol}` - 데이터 커버리지 확인
- `GET /pipeline/company/{symbol}` - 저장된 회사 정보 조회
- `GET /pipeline/companies` - 모든 회사 목록 조회

### **3. watchlists.py - Watchlist Management**
- `POST /pipeline/watchlist` - 유연한 생성/업데이트
- `POST /pipeline/watchlists` - 명시적 신규 생성
- `GET /pipeline/watchlists` - 전체 목록 조회
- `GET /pipeline/watchlists/{name}` - 특정 워치리스트 조회
- `PUT /pipeline/watchlists/{name}` - 기존 워치리스트 수정
- `DELETE /pipeline/watchlists/{name}` - 워치리스트 삭제

## ✅ **장점**

### **1. 유지보수성 향상**
- 각 기능별로 독립적인 파일 관리
- 버그 수정 시 해당 모듈만 집중 가능
- 코드 리뷰 시 변경 범위 명확

### **2. 개발 효율성 증대**
- 팀 개발 시 충돌 최소화
- 새로운 기능 추가 시 적절한 모듈 선택 용이
- 테스트 코드 작성 시 모듈별 격리 가능

### **3. 코드 가독성 개선**
- 각 파일이 200-300 라인으로 적절한 크기 유지
- 관련 기능끼리 그룹화되어 이해 용이
- 상세한 docstring으로 API 사용법 명확

### **4. 확장성 보장**
- 새로운 기능 모듈 추가 용이
- 기존 코드 수정 없이 새 라우터 추가 가능
- 마이크로서비스 전환 시 모듈별 분리 용이

## 🚀 **사용법**

### **메인 라우터 임포트**
```python
from app.api.routes.pipeline import router as pipeline_router
app.include_router(pipeline_router, prefix="/api/v1")
```

### **개별 모듈 사용**
```python
# 특정 기능만 필요한 경우
from app.api.routes.watchlists import router as watchlist_router
app.include_router(watchlist_router, prefix="/api/v1")
```

## 📊 **API 테스트 예시**

```bash
# 1. 시스템 상태 확인
curl -X GET "http://localhost:8000/api/v1/pipeline/status"

# 2. 워치리스트 생성
curl -X POST "http://localhost:8000/api/v1/pipeline/watchlist" \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["AAPL", "MSFT"], "name": "my_stocks"}'

# 3. 회사 정보 수집
curl -X POST "http://localhost:8000/api/v1/pipeline/collect-info/AAPL"

# 4. 전체 워치리스트 조회
curl -X GET "http://localhost:8000/api/v1/pipeline/watchlists"
```

이제 프론트엔드 개발 시 각 기능별로 명확하게 구분된 API를 활용할 수 있습니다! 🎯
