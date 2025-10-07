# Alpha Vantage MCP Server 설정 가이드

## 개요

이 프로젝트에서는 Alpha Vantage API를 MCP (Model Context Protocol) 서버를 통해
VS Code GitHub Copilot과 OpenAI Codex에서 직접 사용할 수 있도록 설정했습니다.

## 🔐 보안 고려사항

**중요**: API 키는 환경변수를 통해 관리되며, 설정 파일에 하드코딩하지 않습니다.

- `.env` 파일에 `ALPHA_VANTAGE_API_KEY=M9TJCCBXW5PJZ3HF` 설정
- `.vscode/` 디렉토리는 `.gitignore`에 포함되어 있음
- 모든 MCP 설정은 환경변수 참조 방식 사용

## 설정 파일들

### 1. 환경변수 설정 - `.env`

```bash
# Alpha Vantage API 키 (필수)
ALPHA_VANTAGE_API_KEY=M9TJCCBXW5PJZ3HF
```

### 2. 로컬 서버 설정 (권장) - `.vscode/mcp.json`

```json
{
  "servers": {
    "alphavantage": {
      "type": "stdio",
      "command": "uvx",
      "args": ["av-mcp"],
      "env": {
        "ALPHA_VANTAGE_API_KEY": "${ALPHA_VANTAGE_API_KEY}"
      }
    }
  }
}
```

### 3. 원격 서버 설정 (대안) - `.vscode/mcp-remote.json`

```json
{
  "servers": {
    "alphavantage": {
      "type": "http",
      "url": "https://mcp.alphavantage.co/mcp?apikey=${ALPHA_VANTAGE_API_KEY}"
    }
  }
}
```

### 4. 범용 설정 - `mcp_config.json` (선택사항)

```json
{
  "mcpServers": {
    "alphavantage": {
      "command": "uvx",
      "args": ["av-mcp"],
      "env": {
        "ALPHA_VANTAGE_API_KEY": "${ALPHA_VANTAGE_API_KEY}"
      }
    }
  }
}
```

## 사용 방법

### VS Code GitHub Copilot에서 사용

1. **Chat 뷰 열기**: VS Code에서 GitHub Copilot Chat 패널 열기
2. **Agent 모드 선택**: Chat 뷰에서 Agent 모드 활성화
3. **MCP 명령어 사용**:

```
@workspace /mcp-alphavantage AAPL의 최근 주가 정보를 가져와주세요
```

```
@workspace /mcp-alphavantage TSLA의 재무제표를 조회해주세요
```

```
@workspace /mcp-alphavantage 미국 GDP 데이터를 가져와주세요
```

### 사용 가능한 Alpha Vantage 기능들

#### 1. 주식 데이터 (Core Stock APIs)

- `TIME_SERIES_INTRADAY` - 일중 시계열 데이터
- `TIME_SERIES_DAILY` - 일간 시계열 데이터
- `TIME_SERIES_WEEKLY` - 주간 시계열 데이터
- `TIME_SERIES_MONTHLY` - 월간 시계열 데이터
- `GLOBAL_QUOTE` - 실시간 주가
- `SYMBOL_SEARCH` - 심볼 검색

#### 2. 펀더멘털 데이터 (Fundamental Data)

- `COMPANY_OVERVIEW` - 회사 개요
- `INCOME_STATEMENT` - 손익계산서
- `BALANCE_SHEET` - 대차대조표
- `CASH_FLOW` - 현금흐름표
- `EARNINGS` - 실적 정보

#### 3. 경제 지표 (Economic Indicators)

- `REAL_GDP` - 실질 GDP
- `FEDERAL_FUNDS_RATE` - 연방기금금리
- `INFLATION` - 인플레이션율
- `UNEMPLOYMENT` - 실업률
- `CPI` - 소비자물가지수

#### 4. 인텔리전스 데이터 (Alpha Intelligence)

- `NEWS_SENTIMENT` - 뉴스 감정 분석
- `TOP_GAINERS_LOSERS` - 상위 상승/하락 종목
- `INSIDER_TRANSACTIONS` - 내부자 거래
- `EARNINGS_CALL_TRANSCRIPT` - 실적 발표 대본

#### 5. 기술적 지표 (Technical Indicators)

- `SMA`, `EMA`, `RSI`, `MACD` 등 모든 기술적 지표
- `BBANDS` - 볼린저 밴드
- `STOCH` - 스토캐스틱

## 테스트 및 문제 해결

### MCP 서버 연결 테스트

```bash
# MCP 서버 기본 테스트
python scripts/test_mcp_setup.py

# 수동 테스트
uvx av-mcp --list-categories
uvx av-mcp M9TJCCBXW5PJZ3HF
```

### 일반적인 문제들

1. **uv가 설치되지 않은 경우**:

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **VS Code에서 MCP 서버가 인식되지 않는 경우**:

   - VS Code 재시작
   - GitHub Copilot 확장 프로그램 재로드
   - `.vscode/mcp.json` 파일 경로 확인

3. **원격 서버 사용 시 느린 응답**:
   - 로컬 서버 설정 (`.vscode/mcp.json`) 사용 권장
   - 네트워크 연결 상태 확인

## API 사용량 관리

- **일일 한도**: 25회 무료 (프리미엄은 더 많음)
- **분당 한도**: 5회
- **API 키**: M9TJCCBXW5PJZ3HF

## 프로젝트 통합

이 MCP 설정은 다음과 함께 작동합니다:

1. **Backend Services**: `app/services/market_data_service/` 의 모든 Alpha
   Vantage 통합
2. **DuckDB 캐싱**: 고성능 데이터 캐시 레이어
3. **FastAPI 엔드포인트**: RESTful API 인터페이스
4. **Next.js Frontend**: 웹 인터페이스

## 추가 리소스

- [Alpha Vantage MCP 공식 문서](https://mcp.alphavantage.co/)
- [Alpha Vantage API 문서](https://www.alphavantage.co/documentation/)
- [VS Code MCP 확장 문서](https://code.visualstudio.com/docs/copilot/mcp)
- [Model Context Protocol 사양](https://modelcontextprotocol.io/)

## 예제 사용법

### GitHub Copilot Chat에서 실제 사용 예제

```
사용자: @workspace /mcp-alphavantage Apple 주식의 최근 1개월 일간 데이터를 가져와서 RSI 지표를 계산해주세요

Copilot: Alpha Vantage MCP를 통해 AAPL의 데이터를 가져오겠습니다...
[MCP 호출: TIME_SERIES_DAILY, RSI 계산]
```

```
사용자: @workspace /mcp-alphavantage 미국의 최근 GDP 성장률과 인플레이션 데이터를 비교 분석해주세요

Copilot: 경제 지표 데이터를 조회하겠습니다...
[MCP 호출: REAL_GDP, INFLATION]
```

이제 VS Code에서 GitHub Copilot을 통해 실시간 Alpha Vantage 데이터에 접근할 수
있습니다! 🚀
