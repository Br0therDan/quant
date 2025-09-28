# 통합 퀀트 백테스트 플랫폼

Alpha Vantage 기반의 통합 퀀트 백테스트 플랫폼입니다. 데이터 수집, 전략 실행, 백테스트 분석이 하나의 백엔드 서비스에 통합되어 있습니다.

## 🏗️ **프로젝트 구조**

```
quant/
├── backend/                    # 통합 백엔드 서비스
│   ├── app/
│   │   ├── api/               # FastAPI 라우터
│   │   │   └── routes/        # API 엔드포인트
│   │   ├── models/            # 데이터 모델 (Beanie ODM)
│   │   ├── services/          # 비즈니스 로직
│   │   ├── strategies/        # 전략 구현체
│   │   └── utils/             # 유틸리티
│   ├── tests/                 # 테스트 코드
│   └── pyproject.toml         # 백엔드 의존성
├── frontend/                  # 프론트엔드 (향후 구현)
├── docs/                      # 문서
├── scripts/                   # 개발 스크립트
├── run_server.py             # 서버 실행 스크립트
└── pyproject.toml            # 프로젝트 설정
```

## 📊 **주요 기능**

### **통합 서비스 아키텍처**
- **Data Service**: Alpha Vantage API를 통한 실시간 시장 데이터 수집
- **Strategy Service**: 다양한 퀀트 전략 구현 및 관리
- **Backtest Service**: 통합 백테스트 실행 및 성과 분석

### **지원 전략**
- **Buy & Hold**: 매수 후 보유 전략
- **SMA Crossover**: 단순이동평균선 교차 전략
- **RSI Mean Reversion**: RSI 기반 평균 회귀 전략
- **Momentum**: 모멘텀 기반 전략

### **백테스트 기능**
- 실시간 데이터 수집 및 검증
- 전략 신호 생성 및 검증
- 거래 시뮬레이션 (수수료 포함)
- 성과 지표 계산 (수익률, 샤프비율, 최대낙폭 등)

## 🚀 **빠른 시작**

### 1. 환경 설정
```bash
# 저장소 클론
git clone <repository-url>
cd quant

# UV를 사용한 의존성 설치
uv sync

# 환경 변수 설정
cp .env.example .env
# .env 파일에서 ALPHA_VANTAGE_API_KEY 설정
```

### 2. 서버 실행
```bash
# 간단한 실행
python run_server.py

# 또는 직접 실행
cd backend
uvicorn app.main:app --reload --port 8501
```

### 3. API 접속
- **서버 주소**: http://localhost:8501
- **API 문서**: http://localhost:8501/docs
- **서비스 테스트**: http://localhost:8501/api/v1/integrated/test-services

## 🔧 **API 사용법**

### **통합 백테스트 실행**
```bash
POST /api/v1/integrated/backtest
Content-Type: application/json

{
  "name": "AAPL SMA Crossover Test",
  "symbols": ["AAPL"],
  "start_date": "2023-01-01T00:00:00",
  "end_date": "2023-12-31T23:59:59",
  "strategy_type": "SMA_CROSSOVER",
  "strategy_params": {
    "short_window": 20,
    "long_window": 50
  },
  "initial_capital": 100000
}
```

### **서비스 상태 확인**
```bash
GET /api/v1/integrated/test-services
```

### **시장 데이터 조회**
```bash
GET /api/v1/market-data/data/AAPL?start_date=2023-01-01&end_date=2023-12-31
```

## 🛠️ **개발 환경**

### **기술 스택**
- **Backend**: Python 3.12+, FastAPI, Beanie ODM
- **Database**: MongoDB
- **Data Source**: Alpha Vantage API
- **Analysis**: pandas, numpy, vectorbt
- **Package Manager**: UV

### **개발 도구**
```bash
# 코드 포맷팅
uv run ruff format

# 린팅
uv run ruff check

# 테스트 실행
uv run pytest

# 타입 체크
uv run mypy backend/app
```

## 📈 **성과 지표**

백테스트 결과로 제공되는 주요 성과 지표:
- **총 수익률** (Total Return)
- **연환산 수익률** (Annualized Return)
- **변동성** (Volatility)
- **샤프 비율** (Sharpe Ratio)
- **최대 낙폭** (Maximum Drawdown)
- **승률** (Win Rate)
- **수익 인수** (Profit Factor)

## 🔐 **보안 설정**

### **환경 변수**
```bash
# .env 파일 설정
ALPHA_VANTAGE_API_KEY=your_api_key_here
MONGODB_URL=mongodb://localhost:27017
SERVICE_NAME=backend
LOG_LEVEL=INFO
```

### **API 키 관리**
- Alpha Vantage API 키는 `.env` 파일에만 저장
- 프로덕션 환경에서는 환경 변수로 주입
- Rate limiting 준수 (5 calls/min, 500 calls/day)

## 📝 **라이센스**

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.


---

## 📝 라이선스

MIT License
