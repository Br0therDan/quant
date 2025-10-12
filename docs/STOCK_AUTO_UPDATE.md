# 주식 데이터 자동 업데이트 시스템

## 개요

주식 데이터의 자동 증분 업데이트를 지원하는 시스템입니다. `StockDataCoverage`
모델을 기반으로 데이터 커버리지를 추적하고, 만료된 데이터를 자동으로
업데이트합니다.

## 아키텍처

### 1. Coverage 기반 캐싱

- **StockDataCoverage 모델**: 각 심볼의 데이터 범위와 업데이트 이력을 추적
- **자동 만료 감지**: `next_update_due` 필드로 업데이트 필요 여부 판단
- **Full vs Delta 업데이트**:
  - **Full Update**: 최초 또는 오래된 데이터 (7일/30일/60일 경과)
  - **Delta Update**: 최근 데이터만 보충 (compact 모드)

### 2. 업데이트 주기

| 데이터 타입 | Full Update 주기 | Delta Update 주기 | Alpha Vantage API            |
| ----------- | ---------------- | ----------------- | ---------------------------- |
| Daily       | 7일              | 1일               | TIME_SERIES_DAILY_ADJUSTED   |
| Weekly      | 30일             | 7일               | TIME_SERIES_WEEKLY_ADJUSTED  |
| Monthly     | 60일             | 30일              | TIME_SERIES_MONTHLY_ADJUSTED |

### 3. 데이터 흐름

```
API 요청
  ↓
StockService.get_daily_prices()
  ↓
Coverage 확인 (next_update_due)
  ↓
  ├─ 만료됨 → Alpha Vantage API 호출 → MongoDB 저장 → Coverage 업데이트
  └─ 유효함 → MongoDB 조회 (캐시)
```

## 사용 방법

### 1. 수동 실행 (스크립트)

#### 만료된 데이터만 증분 업데이트

```bash
# 프로젝트 루트에서 실행
python scripts/run_stock_update.py
```

**동작:**

- StockDataCoverage에서 `next_update_due`가 현재 시간보다 이전인 레코드 찾기
- Daily: compact (최근 100개)
- Weekly/Monthly: full (전체 데이터)

#### 모든 활성 심볼 강제 Full Update

```bash
# ⚠️ 주의: 많은 API 호출 발생!
python scripts/run_stock_update.py --force-all
```

**동작:**

- 모든 활성 StockDataCoverage 레코드 대상
- 모든 데이터 타입을 full 모드로 업데이트
- Alpha Vantage API 한도(500 calls/day) 고려 필요

### 2. API 엔드포인트

#### 증분 업데이트 실행

```bash
POST /api/v1/tasks/stock-update/delta
```

**응답:**

```json
{
  "status": "completed",
  "message": "Delta update completed: 5 success, 0 failed",
  "total": 5,
  "success": 5,
  "failed": 0,
  "errors": []
}
```

#### 강제 Full Update 실행

```bash
POST /api/v1/tasks/stock-update/force-all
```

#### 업데이트 상태 조회

```bash
GET /api/v1/tasks/stock-update/status
```

**응답:**

```json
{
  "status": "ok",
  "total_active_coverages": 10,
  "expired_coverages": 3,
  "update_needed": true,
  "timestamp": "2025-01-12T10:30:00"
}
```

### 3. 프로그래밍 방식

```python
from app.tasks.stock_update import update_stock_data_coverage

# 증분 업데이트 실행
result = await update_stock_data_coverage()

print(f"Success: {result['success']}, Failed: {result['failed']}")
```

## Cron Job 설정 (권장)

### Linux/Mac (crontab)

```bash
# 매일 오전 9시에 증분 업데이트 실행
0 9 * * * cd /path/to/quant && python scripts/run_stock_update.py

# 매주 일요일 오전 3시에 전체 업데이트 실행
0 3 * * 0 cd /path/to/quant && python scripts/run_stock_update.py --force-all
```

### systemd Timer (Linux)

```ini
# /etc/systemd/system/stock-update.timer
[Unit]
Description=Stock Data Update Timer

[Timer]
OnCalendar=daily
OnCalendar=09:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

```ini
# /etc/systemd/system/stock-update.service
[Unit]
Description=Stock Data Update Task

[Service]
Type=oneshot
WorkingDirectory=/path/to/quant
ExecStart=/usr/bin/python3 scripts/run_stock_update.py
User=quant
```

```bash
# 활성화
sudo systemctl enable stock-update.timer
sudo systemctl start stock-update.timer

# 상태 확인
sudo systemctl status stock-update.timer
```

## 모니터링

### Coverage 상태 확인

```python
from app.models.market_data.stock import StockDataCoverage

# 만료된 Coverage 조회
expired = await StockDataCoverage.find({
    "is_active": True,
    "next_update_due": {"$lte": datetime.utcnow()}
}).to_list()

for cov in expired:
    print(f"{cov.symbol} {cov.data_type}: last_update={cov.last_full_update}")
```

### 로그 확인

```bash
# 백엔드 로그
tail -f backend/logs/app.log | grep "stock.*update"

# 에러 로그
tail -f backend/logs/error.log
```

## 제거된 모델

### Dividend, Split 모델 제거

**이유:**

- 독립적으로 사용되지 않음
- `DailyPrice`, `WeeklyPrice`, `MonthlyPrice` 모델에 이미 `dividend_amount`,
  `split_coefficient` 필드 포함
- MongoDB collections만 차지하고 실제 기능 없음

**제거 내용:**

- `backend/app/models/market_data/stock.py`: `Dividend`, `Split` 클래스 삭제
- `backend/app/models/__init__.py`: collections에서 제거
- `backend/app/models/market_data/__init__.py`: **all**에서 제거

## 향후 개선 사항

### 1. APScheduler 통합 (선택사항)

```python
# backend/app/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.tasks.stock_update import update_stock_data_coverage

scheduler = AsyncIOScheduler()

# 매일 오전 9시에 자동 실행
scheduler.add_job(
    update_stock_data_coverage,
    'cron',
    hour=9,
    id='stock_delta_update'
)

scheduler.start()
```

### 2. Celery 통합 (대규모 환경)

```python
# backend/app/celery_app.py
from celery import Celery

celery_app = Celery('quant', broker='redis://localhost:6379/0')

@celery_app.task
def run_stock_update():
    asyncio.run(update_stock_data_coverage())
```

### 3. 우선순위 기반 업데이트

```python
# 거래량이 많은 심볼 우선 업데이트
high_priority_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
```

## API 한도 관리

### Alpha Vantage 무료 플랜

- **일일 한도**: 500 calls
- **분당 한도**: 5 calls

### 권장 사항

1. **증분 업데이트 사용**: Full update는 주 1회로 제한
2. **Batch 크기 제한**: 한 번에 100개 심볼 이하 업데이트
3. **Rate Limiting**: `mysingle-quant` 패키지가 자동 처리
4. **모니터링**: API 호출 수 추적

```python
# API 호출 수 계산
symbols_count = 10
data_types = 3  # daily, weekly, monthly
total_calls = symbols_count * data_types  # 30 calls
```

## 문제 해결

### Coverage가 생성되지 않음

**원인**: 최초 API 호출 시 자동 생성됨

**해결**:

```bash
# 임의의 심볼로 API 호출하여 Coverage 생성
curl http://localhost:8500/api/v1/market-data/stock/daily/AAPL?outputsize=full
```

### 업데이트가 실행되지 않음

**확인 사항**:

1. MongoDB 연결 상태
2. Alpha Vantage API 키 유효성
3. `next_update_due` 날짜가 현재보다 이전인지 확인

```python
# 강제로 next_update_due 업데이트
coverage.next_update_due = datetime.utcnow() - timedelta(days=1)
await coverage.save()
```

### API 한도 초과

**해결**:

1. Premium 플랜 사용 고려
2. 업데이트 주기를 늘림
3. 필요한 심볼만 활성화 (`is_active=False` 설정)

```python
# 불필요한 심볼 비활성화
coverage = await StockDataCoverage.find_one({"symbol": "RARE_STOCK"})
coverage.is_active = False
await coverage.save()
```

## 참고 자료

- [Alpha Vantage API 문서](https://www.alphavantage.co/documentation/)
- [StockDataCoverage 모델 정의](../app/models/market_data/stock.py)
- [Stock Service 구현](../app/services/market_data_service/stock.py)
