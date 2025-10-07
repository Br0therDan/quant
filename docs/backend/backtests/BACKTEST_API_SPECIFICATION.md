# 🔌 백테스트 API 설계 상세 명세서

## 📋 개요

백테스트 서비스 고도화를 위한 REST API 및 WebSocket API의 상세 설계
명세서입니다. 프론트엔드 요구사항과 백테스트 시스템의 실시간 모니터링 기능을
지원하는 완전한 API를 정의합니다.

---

## 🌐 REST API 설계

### 기본 정보

- **Base URL**: `/api/v1/backtests`
- **Authentication**: Bearer Token (JWT)
- **Content-Type**: `application/json`
- **API Version**: v1

### 1. 백테스트 관리 API

#### 1.1 백테스트 생성

```http
POST /api/v1/backtests
```

**Request Body**:

```json
{
  "name": "Tech Stock Momentum Strategy",
  "description": "장기 모멘텀 전략을 활용한 기술주 투자",
  "strategy_type": "momentum",
  "strategy_config": {
    "lookback_period": 30,
    "momentum_threshold": 0.05,
    "rebalance_frequency": "weekly"
  },
  "symbols": ["AAPL", "GOOGL", "MSFT", "AMZN"],
  "start_date": "2023-01-01",
  "end_date": "2024-01-01",
  "initial_capital": 100000,
  "risk_management": {
    "max_position_size": 0.25,
    "stop_loss": 0.1,
    "max_drawdown_limit": 0.2
  },
  "execution_config": {
    "auto_start": true,
    "priority": "normal",
    "notification_settings": {
      "email": true,
      "webhook": "https://api.example.com/webhooks/backtest"
    }
  }
}
```

**Response**:

```json
{
  "backtest_id": "bt_7a8b9c0d1e2f3g4h",
  "status": "queued",
  "estimated_duration": 180,
  "queue_position": 3,
  "created_at": "2024-01-15T10:30:00Z",
  "websocket_url": "wss://api.example.com/ws/backtest/bt_7a8b9c0d1e2f3g4h"
}
```

#### 1.2 백테스트 목록 조회

```http
GET /api/v1/backtests?status=completed&strategy_type=momentum&limit=10&offset=0
```

**Query Parameters**:

- `status`: completed, running, failed, cancelled, queued
- `strategy_type`: momentum, mean_reversion, sma_crossover 등
- `start_date`: 생성일 필터 시작
- `end_date`: 생성일 필터 종료
- `symbols`: 심볼 필터 (쉼표 구분)
- `user_id`: 사용자 ID 필터
- `tags`: 태그 필터
- `sort_by`: created_at, total_return, name
- `sort_order`: asc, desc
- `limit`: 페이지 크기 (기본 20, 최대 100)
- `offset`: 오프셋

**Response**:

```json
{
  "backtests": [
    {
      "id": "bt_7a8b9c0d1e2f3g4h",
      "name": "Tech Stock Momentum Strategy",
      "status": "completed",
      "strategy_type": "momentum",
      "symbols": ["AAPL", "GOOGL", "MSFT", "AMZN"],
      "start_date": "2023-01-01",
      "end_date": "2024-01-01",
      "created_at": "2024-01-15T10:30:00Z",
      "completed_at": "2024-01-15T10:33:45Z",
      "execution_time": 225,
      "summary": {
        "total_return": 0.127,
        "sharpe_ratio": 1.45,
        "max_drawdown": -0.08,
        "total_trades": 47
      },
      "tags": ["momentum", "tech", "long-term"]
    }
  ],
  "pagination": {
    "total": 156,
    "limit": 10,
    "offset": 0,
    "has_next": true,
    "has_prev": false
  }
}
```

#### 1.3 백테스트 상세 조회

```http
GET /api/v1/backtests/{backtest_id}
```

**Response**:

```json
{
  "id": "bt_7a8b9c0d1e2f3g4h",
  "name": "Tech Stock Momentum Strategy",
  "description": "장기 모멘텀 전략을 활용한 기술주 투자",
  "status": "completed",
  "strategy_type": "momentum",
  "strategy_config": {
    "lookback_period": 30,
    "momentum_threshold": 0.05,
    "rebalance_frequency": "weekly"
  },
  "symbols": ["AAPL", "GOOGL", "MSFT", "AMZN"],
  "start_date": "2023-01-01",
  "end_date": "2024-01-01",
  "initial_capital": 100000,
  "created_at": "2024-01-15T10:30:00Z",
  "started_at": "2024-01-15T10:30:15Z",
  "completed_at": "2024-01-15T10:33:45Z",
  "execution_time": 225,
  "performance_metrics": {
    "total_return": 0.127,
    "annualized_return": 0.134,
    "sharpe_ratio": 1.45,
    "sortino_ratio": 1.78,
    "max_drawdown": -0.08,
    "volatility": 0.095,
    "beta": 0.87,
    "alpha": 0.034
  },
  "trade_summary": {
    "total_trades": 47,
    "winning_trades": 29,
    "losing_trades": 18,
    "win_rate": 0.617,
    "avg_win": 0.035,
    "avg_loss": -0.021,
    "profit_factor": 1.56
  },
  "risk_metrics": {
    "var_95": -0.024,
    "cvar_95": -0.031,
    "calmar_ratio": 1.68,
    "max_consecutive_losses": 5
  }
}
```

#### 1.4 백테스트 삭제

```http
DELETE /api/v1/backtests/{backtest_id}
```

**Response**:

```json
{
  "message": "백테스트가 성공적으로 삭제되었습니다",
  "deleted_at": "2024-01-15T15:45:30Z"
}
```

### 2. 백테스트 실행 제어 API

#### 2.1 백테스트 시작

```http
POST /api/v1/backtests/{backtest_id}/start
```

**Request Body**:

```json
{
  "priority": "high",
  "force_restart": false
}
```

**Response**:

```json
{
  "task_id": "task_abc123def456",
  "status": "queued",
  "estimated_start_time": "2024-01-15T10:35:00Z",
  "queue_position": 1
}
```

#### 2.2 백테스트 중단

```http
POST /api/v1/backtests/{backtest_id}/stop
```

**Response**:

```json
{
  "message": "백테스트 중단 요청이 처리되었습니다",
  "status": "stopping",
  "stopped_at": "2024-01-15T10:32:15Z"
}
```

#### 2.3 실행 상태 조회

```http
GET /api/v1/backtests/{backtest_id}/status
```

**Response**:

```json
{
  "backtest_id": "bt_7a8b9c0d1e2f3g4h",
  "status": "running",
  "progress": {
    "percentage": 65.5,
    "current_step": "calculating_indicators",
    "processed_days": 131,
    "total_days": 200,
    "estimated_completion": "2024-01-15T10:34:30Z"
  },
  "execution_info": {
    "task_id": "task_abc123def456",
    "worker_id": "worker_node_2",
    "started_at": "2024-01-15T10:30:15Z",
    "elapsed_time": 145
  },
  "intermediate_metrics": {
    "processed_trades": 28,
    "current_portfolio_value": 108500,
    "unrealized_pnl": 8500
  }
}
```

### 3. 백테스트 결과 API

#### 3.1 결과 데이터 조회

```http
GET /api/v1/backtests/{backtest_id}/results
```

**Query Parameters**:

- `include`: performance, trades, positions, logs (쉼표 구분)
- `format`: json, csv, excel
- `date_range`: 특정 기간 필터링

**Response**:

```json
{
  "backtest_id": "bt_7a8b9c0d1e2f3g4h",
  "performance": {
    "equity_curve": [
      {
        "date": "2023-01-01",
        "portfolio_value": 100000,
        "benchmark_value": 100000
      },
      {
        "date": "2023-01-02",
        "portfolio_value": 100250,
        "benchmark_value": 100180
      }
    ],
    "monthly_returns": [
      { "month": "2023-01", "return": 0.025, "benchmark_return": 0.018 },
      { "month": "2023-02", "return": -0.015, "benchmark_return": -0.008 }
    ],
    "drawdown_periods": [
      {
        "start_date": "2023-03-15",
        "end_date": "2023-04-10",
        "max_drawdown": -0.08,
        "duration_days": 26
      }
    ]
  },
  "trades": [
    {
      "trade_id": "trade_001",
      "symbol": "AAPL",
      "side": "buy",
      "quantity": 100,
      "entry_date": "2023-01-15",
      "entry_price": 150.25,
      "exit_date": "2023-02-10",
      "exit_price": 158.5,
      "pnl": 825.0,
      "return": 0.055
    }
  ],
  "positions": [
    {
      "date": "2023-01-15",
      "symbol": "AAPL",
      "quantity": 100,
      "market_value": 15025,
      "weight": 0.25,
      "unrealized_pnl": 0
    }
  ]
}
```

#### 3.2 성과 차트 데이터

```http
GET /api/v1/backtests/{backtest_id}/charts/equity-curve
```

**Response**:

```json
{
  "chart_type": "equity_curve",
  "data": [
    {
      "timestamp": "2023-01-01T00:00:00Z",
      "portfolio": 100000,
      "benchmark": 100000
    },
    {
      "timestamp": "2023-01-02T00:00:00Z",
      "portfolio": 100250,
      "benchmark": 100180
    }
  ],
  "metadata": {
    "total_points": 365,
    "start_date": "2023-01-01",
    "end_date": "2024-01-01",
    "benchmark": "SPY"
  }
}
```

### 4. 백테스트 분석 API

#### 4.1 백테스트 비교

```http
POST /api/v1/backtests/compare
```

**Request Body**:

```json
{
  "backtest_ids": [
    "bt_7a8b9c0d1e2f3g4h",
    "bt_8b9c0d1e2f3g4h5",
    "bt_9c0d1e2f3g4h5i6"
  ],
  "metrics": ["total_return", "sharpe_ratio", "max_drawdown", "volatility"],
  "chart_types": ["equity_curve", "drawdown", "monthly_returns"]
}
```

**Response**:

```json
{
  "comparison_id": "comp_abc123def456",
  "backtests": [
    {
      "id": "bt_7a8b9c0d1e2f3g4h",
      "name": "Momentum Strategy",
      "metrics": {
        "total_return": 0.127,
        "sharpe_ratio": 1.45,
        "max_drawdown": -0.08,
        "volatility": 0.095
      }
    }
  ],
  "correlation_matrix": [
    [1.0, 0.75, 0.68],
    [0.75, 1.0, 0.82],
    [0.68, 0.82, 1.0]
  ],
  "chart_data": {
    "equity_curve": {
      "dates": ["2023-01-01", "2023-01-02"],
      "series": [
        { "name": "Momentum Strategy", "data": [100000, 100250] },
        { "name": "Mean Reversion", "data": [100000, 100180] }
      ]
    }
  }
}
```

#### 4.2 성과 통계 분석

```http
GET /api/v1/backtests/analytics/performance-stats
```

**Query Parameters**:

- `period`: 1M, 3M, 6M, 1Y, 2Y, 5Y, ALL
- `strategy_type`: 전략 유형 필터
- `min_return`: 최소 수익률 필터
- `max_drawdown`: 최대 드로우다운 필터

**Response**:

```json
{
  "period": "1Y",
  "analysis_date": "2024-01-15T00:00:00Z",
  "total_backtests": 1247,
  "filtered_backtests": 89,
  "performance_stats": {
    "avg_return": 0.085,
    "median_return": 0.072,
    "std_return": 0.123,
    "min_return": -0.234,
    "max_return": 0.456,
    "success_rate": 0.674
  },
  "top_performers": [
    {
      "backtest_id": "bt_top001",
      "name": "High Alpha Strategy",
      "total_return": 0.456,
      "sharpe_ratio": 2.34
    }
  ],
  "distribution": {
    "return_buckets": [
      { "range": "-50% to -25%", "count": 5 },
      { "range": "-25% to 0%", "count": 24 },
      { "range": "0% to 25%", "count": 45 },
      { "range": "25% to 50%", "count": 12 },
      { "range": "50%+", "count": 3 }
    ]
  }
}
```

### 5. 실행 로그 및 모니터링 API

#### 5.1 실행 로그 조회

```http
GET /api/v1/backtests/{backtest_id}/logs
```

**Query Parameters**:

- `level`: info, warning, error
- `start_time`: 시작 시간 필터
- `end_time`: 종료 시간 필터
- `limit`: 로그 개수 제한
- `offset`: 페이지네이션 오프셋

**Response**:

```json
{
  "logs": [
    {
      "timestamp": "2024-01-15T10:30:15Z",
      "level": "info",
      "message": "백테스트 실행 시작",
      "details": {
        "step": "initialization",
        "symbols": ["AAPL", "GOOGL"],
        "data_points": 365
      }
    },
    {
      "timestamp": "2024-01-15T10:31:20Z",
      "level": "info",
      "message": "데이터 수집 완료",
      "details": {
        "step": "data_collection",
        "collected_symbols": 4,
        "missing_data_days": 2
      }
    },
    {
      "timestamp": "2024-01-15T10:32:45Z",
      "level": "warning",
      "message": "일부 데이터 누락 감지",
      "details": {
        "step": "data_validation",
        "missing_dates": ["2023-07-04", "2023-12-25"],
        "symbols_affected": ["AAPL"]
      }
    }
  ],
  "pagination": {
    "total": 156,
    "limit": 50,
    "offset": 0,
    "has_next": true
  }
}
```

#### 5.2 시스템 상태 조회

```http
GET /api/v1/backtests/system/status
```

**Response**:

```json
{
  "system_status": "healthy",
  "queue_info": {
    "total_queued": 5,
    "currently_running": 3,
    "max_concurrent": 10,
    "estimated_wait_time": 180
  },
  "worker_status": [
    {
      "worker_id": "worker_node_1",
      "status": "busy",
      "current_task": "bt_7a8b9c0d1e2f3g4h",
      "cpu_usage": 85.5,
      "memory_usage": 72.3
    },
    {
      "worker_id": "worker_node_2",
      "status": "idle",
      "cpu_usage": 12.1,
      "memory_usage": 45.8
    }
  ],
  "performance_metrics": {
    "avg_execution_time": 245,
    "success_rate": 0.967,
    "error_rate": 0.033,
    "uptime": 99.95
  }
}
```

---

## 🔌 WebSocket API 설계

### 연결 정보

**Endpoint**: `wss://api.example.com/ws/backtest/{backtest_id}`
**Authentication**: Query parameter로 JWT 토큰 전달 **Connection URL**:
`wss://api.example.com/ws/backtest/bt_7a8b9c0d1e2f3g4h?token=jwt_token_here`

### 메시지 형식

모든 WebSocket 메시지는 다음 형식을 따릅니다:

```json
{
  "type": "message_type",
  "timestamp": "2024-01-15T10:30:15Z",
  "backtest_id": "bt_7a8b9c0d1e2f3g4h",
  "data": {
    // 메시지별 데이터
  }
}
```

### 1. 상태 업데이트 메시지

#### 1.1 진행률 업데이트

```json
{
  "type": "progress_update",
  "timestamp": "2024-01-15T10:31:30Z",
  "backtest_id": "bt_7a8b9c0d1e2f3g4h",
  "data": {
    "progress": 35.5,
    "current_step": "calculating_indicators",
    "processed_days": 71,
    "total_days": 200,
    "estimated_completion": "2024-01-15T10:34:15Z",
    "elapsed_time": 75
  }
}
```

#### 1.2 상태 변경

```json
{
  "type": "status_change",
  "timestamp": "2024-01-15T10:30:15Z",
  "backtest_id": "bt_7a8b9c0d1e2f3g4h",
  "data": {
    "old_status": "queued",
    "new_status": "running",
    "message": "백테스트 실행이 시작되었습니다"
  }
}
```

### 2. 실행 로그 메시지

#### 2.1 일반 로그

```json
{
  "type": "log",
  "timestamp": "2024-01-15T10:31:45Z",
  "backtest_id": "bt_7a8b9c0d1e2f3g4h",
  "data": {
    "level": "info",
    "message": "매수 신호 발생",
    "details": {
      "symbol": "AAPL",
      "signal_strength": 0.85,
      "price": 150.25,
      "quantity": 100
    }
  }
}
```

#### 2.2 오류 로그

```json
{
  "type": "error",
  "timestamp": "2024-01-15T10:32:10Z",
  "backtest_id": "bt_7a8b9c0d1e2f3g4h",
  "data": {
    "level": "error",
    "message": "데이터 수집 실패",
    "error_code": "DATA_FETCH_ERROR",
    "details": {
      "symbol": "GOOGL",
      "date": "2023-07-04",
      "reason": "Market holiday - no data available"
    }
  }
}
```

### 3. 중간 결과 메시지

#### 3.1 거래 실행 알림

```json
{
  "type": "trade_executed",
  "timestamp": "2024-01-15T10:31:55Z",
  "backtest_id": "bt_7a8b9c0d1e2f3g4h",
  "data": {
    "trade_id": "trade_001",
    "symbol": "AAPL",
    "side": "buy",
    "quantity": 100,
    "price": 150.25,
    "value": 15025,
    "commission": 1.5,
    "portfolio_value": 108500
  }
}
```

#### 3.2 포트폴리오 업데이트

```json
{
  "type": "portfolio_update",
  "timestamp": "2024-01-15T10:32:00Z",
  "backtest_id": "bt_7a8b9c0d1e2f3g4h",
  "data": {
    "portfolio_value": 108500,
    "cash": 45750,
    "total_return": 0.085,
    "unrealized_pnl": 2750,
    "positions": [
      {
        "symbol": "AAPL",
        "quantity": 100,
        "market_value": 15050,
        "unrealized_pnl": 25,
        "weight": 0.139
      }
    ]
  }
}
```

### 4. 완료 및 결과 메시지

#### 4.1 백테스트 완료

```json
{
  "type": "backtest_completed",
  "timestamp": "2024-01-15T10:33:45Z",
  "backtest_id": "bt_7a8b9c0d1e2f3g4h",
  "data": {
    "status": "completed",
    "execution_time": 225,
    "final_metrics": {
      "total_return": 0.127,
      "sharpe_ratio": 1.45,
      "max_drawdown": -0.08,
      "total_trades": 47
    },
    "results_url": "/api/v1/backtests/bt_7a8b9c0d1e2f3g4h/results"
  }
}
```

#### 4.2 백테스트 실패

```json
{
  "type": "backtest_failed",
  "timestamp": "2024-01-15T10:32:30Z",
  "backtest_id": "bt_7a8b9c0d1e2f3g4h",
  "data": {
    "status": "failed",
    "error_message": "Insufficient data for analysis",
    "error_code": "INSUFFICIENT_DATA",
    "execution_time": 145,
    "retry_suggested": true,
    "retry_config": {
      "start_date": "2023-01-15",
      "reason": "Extend start date to ensure sufficient data"
    }
  }
}
```

### 5. 클라이언트 명령 메시지

클라이언트는 다음 명령을 서버로 전송할 수 있습니다:

#### 5.1 백테스트 중단 요청

```json
{
  "type": "stop_request",
  "timestamp": "2024-01-15T10:32:15Z",
  "backtest_id": "bt_7a8b9c0d1e2f3g4h",
  "data": {
    "reason": "user_requested"
  }
}
```

#### 5.2 진행률 조회 요청

```json
{
  "type": "status_request",
  "timestamp": "2024-01-15T10:32:20Z",
  "backtest_id": "bt_7a8b9c0d1e2f3g4h"
}
```

---

## 🔒 보안 및 인증

### JWT 토큰 구조

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "user_id": "user_12345",
    "email": "user@example.com",
    "role": "premium",
    "permissions": ["backtest:create", "backtest:read", "backtest:delete"],
    "backtest_quota": {
      "max_concurrent": 5,
      "max_daily": 50,
      "max_symbols": 20
    },
    "exp": 1705315200,
    "iat": 1705311600
  }
}
```

### API 권한 체계

| 엔드포인트                   | 필요 권한          | 설명          |
| ---------------------------- | ------------------ | ------------- |
| `POST /backtests`            | `backtest:create`  | 백테스트 생성 |
| `GET /backtests`             | `backtest:read`    | 목록 조회     |
| `GET /backtests/{id}`        | `backtest:read`    | 상세 조회     |
| `DELETE /backtests/{id}`     | `backtest:delete`  | 삭제          |
| `POST /backtests/{id}/start` | `backtest:execute` | 실행          |
| `POST /backtests/{id}/stop`  | `backtest:execute` | 중단          |
| `GET /backtests/analytics/*` | `analytics:read`   | 분석 데이터   |

### Rate Limiting

```yaml
rate_limits:
  by_user:
    backtest_creation: "10/hour"
    backtest_execution: "5/hour"
    api_calls: "1000/hour"

  by_ip:
    api_calls: "100/minute"

  by_endpoint:
    "/backtests": "50/minute"
    "/backtests/*/results": "20/minute"
    "/backtests/analytics/*": "10/minute"
```

---

## 📊 모니터링 및 로깅

### API 메트릭

모든 API 호출에 대해 다음 메트릭을 수집합니다:

```python
# Prometheus 메트릭 예시
api_requests_total = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status_code', 'user_id']
)

api_request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration',
    ['method', 'endpoint']
)

active_backtests = Gauge(
    'active_backtests_total',
    'Number of active backtests',
    ['user_id', 'strategy_type']
)

websocket_connections = Gauge(
    'websocket_connections_total',
    'Number of active WebSocket connections',
    ['backtest_id']
)
```

### 구조화된 로깅

```json
{
  "timestamp": "2024-01-15T10:30:15Z",
  "level": "INFO",
  "service": "backtest-api",
  "endpoint": "POST /api/v1/backtests",
  "user_id": "user_12345",
  "request_id": "req_abc123def456",
  "backtest_id": "bt_7a8b9c0d1e2f3g4h",
  "execution_time": 0.245,
  "status_code": 201,
  "message": "Backtest created successfully",
  "metadata": {
    "strategy_type": "momentum",
    "symbols_count": 4,
    "date_range_days": 365
  }
}
```

---

## 🧪 API 테스트 및 검증

### 테스트 시나리오

#### 1. 백테스트 생명주기 테스트

```python
import pytest
import httpx
import asyncio

class TestBacktestLifecycle:

    @pytest.mark.asyncio
    async def test_complete_backtest_flow(self):
        """백테스트 전체 플로우 테스트"""

        # 1. 백테스트 생성
        create_response = await self.client.post(
            "/api/v1/backtests",
            json={
                "name": "Test Strategy",
                "strategy_type": "sma_crossover",
                "symbols": ["AAPL"],
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "initial_capital": 100000
            }
        )
        assert create_response.status_code == 201
        backtest_id = create_response.json()["backtest_id"]

        # 2. 실행 시작
        start_response = await self.client.post(
            f"/api/v1/backtests/{backtest_id}/start"
        )
        assert start_response.status_code == 200

        # 3. 상태 모니터링
        await self._monitor_backtest_completion(backtest_id)

        # 4. 결과 조회
        results_response = await self.client.get(
            f"/api/v1/backtests/{backtest_id}/results"
        )
        assert results_response.status_code == 200

        # 5. 백테스트 삭제
        delete_response = await self.client.delete(
            f"/api/v1/backtests/{backtest_id}"
        )
        assert delete_response.status_code == 200

    async def _monitor_backtest_completion(self, backtest_id: str):
        """백테스트 완료까지 모니터링"""
        timeout = 300  # 5분 타임아웃
        start_time = time.time()

        while time.time() - start_time < timeout:
            status_response = await self.client.get(
                f"/api/v1/backtests/{backtest_id}/status"
            )
            status = status_response.json()["status"]

            if status in ["completed", "failed"]:
                break

            await asyncio.sleep(2)

        assert status == "completed"
```

#### 2. WebSocket 연결 테스트

```python
import websockets
import json

class TestWebSocketAPI:

    @pytest.mark.asyncio
    async def test_websocket_backtest_monitoring(self):
        """WebSocket 실시간 모니터링 테스트"""

        backtest_id = await self._create_test_backtest()

        uri = f"wss://localhost:8000/ws/backtest/{backtest_id}?token={self.jwt_token}"

        async with websockets.connect(uri) as websocket:
            # 초기 상태 메시지 수신
            initial_message = await websocket.recv()
            data = json.loads(initial_message)
            assert data["type"] == "initial_status"

            # 백테스트 시작
            await self._start_backtest(backtest_id)

            # 진행률 업데이트 수신
            progress_updates = []
            completion_received = False

            while not completion_received:
                message = await websocket.recv()
                data = json.loads(message)

                if data["type"] == "progress_update":
                    progress_updates.append(data["data"]["progress"])
                elif data["type"] == "backtest_completed":
                    completion_received = True

            # 진행률이 증가하는지 확인
            assert all(
                progress_updates[i] <= progress_updates[i+1]
                for i in range(len(progress_updates)-1)
            )
```

### 성능 테스트

#### 부하 테스트 시나리오

```python
import locust
from locust import HttpUser, task, between

class BacktestAPIUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """테스트 시작 시 인증"""
        response = self.client.post("/auth/login", json={
            "username": "test_user",
            "password": "test_password"
        })
        self.jwt_token = response.json()["access_token"]
        self.client.headers.update({
            "Authorization": f"Bearer {self.jwt_token}"
        })

    @task(3)
    def list_backtests(self):
        """백테스트 목록 조회"""
        self.client.get("/api/v1/backtests?limit=20")

    @task(2)
    def view_backtest_details(self):
        """백테스트 상세 조회"""
        # 실제 환경에서는 존재하는 백테스트 ID 사용
        self.client.get("/api/v1/backtests/bt_sample_id")

    @task(1)
    def create_backtest(self):
        """백테스트 생성"""
        self.client.post("/api/v1/backtests", json={
            "name": f"Load Test {self.user_id}",
            "strategy_type": "sma_crossover",
            "symbols": ["AAPL", "GOOGL"],
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "initial_capital": 100000
        })

    @task(1)
    def get_analytics(self):
        """분석 데이터 조회"""
        self.client.get("/api/v1/backtests/analytics/performance-stats")
```

---

## 📚 API 문서화 및 버전 관리

### OpenAPI 스키마

```yaml
openapi: 3.0.3
info:
  title: Quant Backtest API
  description: 퀀트 백테스트 플랫폼 API
  version: 1.0.0

servers:
  - url: https://api.quant.example.com/v1
    description: Production server
  - url: https://staging-api.quant.example.com/v1
    description: Staging server

paths:
  /backtests:
    post:
      summary: 백테스트 생성
      tags: [Backtest Management]
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/BacktestCreateRequest"
      responses:
        201:
          description: 백테스트 생성 성공
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/BacktestCreateResponse"
        400:
          description: 잘못된 요청
        401:
          description: 인증 실패
        429:
          description: Rate limit 초과

components:
  schemas:
    BacktestCreateRequest:
      type: object
      required:
        - name
        - strategy_type
        - symbols
        - start_date
        - end_date
        - initial_capital
      properties:
        name:
          type: string
          example: "Tech Stock Momentum Strategy"
        strategy_type:
          type: string
          enum: [momentum, mean_reversion, sma_crossover]
        symbols:
          type: array
          items:
            type: string
          example: ["AAPL", "GOOGL", "MSFT"]
```

### 버전 관리 전략

1. **Major Version (v1 → v2)**

   - Breaking changes
   - 응답 구조 변경
   - 필수 필드 추가/제거

2. **Minor Version (v1.0 → v1.1)**

   - 새로운 엔드포인트 추가
   - 선택적 필드 추가
   - 하위 호환성 유지

3. **Patch Version (v1.0.0 → v1.0.1)**
   - 버그 수정
   - 성능 개선
   - 문서 업데이트

### SDK 및 클라이언트 라이브러리

```python
# Python SDK 예시
from quant_api import BacktestClient

client = BacktestClient(api_key="your_api_key")

# 백테스트 생성
backtest = client.backtests.create(
    name="My Strategy",
    strategy_type="momentum",
    symbols=["AAPL", "GOOGL"],
    start_date="2023-01-01",
    end_date="2023-12-31",
    initial_capital=100000
)

# 실시간 모니터링
async for update in client.backtests.monitor(backtest.id):
    print(f"Progress: {update.progress}%")
    if update.type == "backtest_completed":
        break

# 결과 조회
results = client.backtests.get_results(backtest.id)
print(f"Total Return: {results.performance.total_return:.2%}")
```

---

_이 API 명세서는 백테스트 서비스 고도화 전략에 맞춰 설계되었으며, 실제 구현
과정에서 세부사항이 조정될 수 있습니다._
