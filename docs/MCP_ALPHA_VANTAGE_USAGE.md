# Alpha Vantage MCP Server 사용 예제

## VS Code에서 사용하기

VS Code에서 GitHub Copilot Chat을 통해 Alpha Vantage 데이터에 접근할 수
있습니다:

```
@workspace /mcp-alpha-vantage AAPL의 최근 주가 정보를 가져와주세요
```

```
@workspace /mcp-alpha-vantage TSLA의 재무제표 정보를 조회해주세요
```

```
@workspace /mcp-alpha-vantage 최근 GDP 데이터를 가져와주세요
```

## 사용 가능한 주요 기능들

### 1. 주식 데이터 (Core Stock APIs)

- 일중/일간/주간/월간 시계열 데이터
- 실시간 주가 정보
- 심볼 검색
- 시장 상태 확인

### 2. 펀더멘털 데이터 (Fundamental Data)

- 회사 개요 정보
- 손익계산서, 대차대조표, 현금흐름표
- 실적 정보
- 상장/폐지 정보

### 3. 경제 지표 (Economic Indicators)

- 실질 GDP
- 연방기금금리
- 소비자물가지수 (CPI)
- 인플레이션율
- 실업률

### 4. 알파 인텔리전스 (Alpha Intelligence)

- 뉴스 감정 분석
- 실적 발표 대본
- 상위 상승/하락 종목
- 내부자 거래 정보

### 5. 기술적 지표 (Technical Indicators)

- 이동평균 (SMA, EMA, WMA 등)
- RSI, MACD, 스토캐스틱
- 볼린저 밴드
- 기타 기술적 지표들

## 환경 설정

MCP 서버는 다음 환경변수를 사용합니다:

- ALPHA_VANTAGE_API_KEY: M9TJCCBXW5PJZ3HF

## 테스트 명령어

```bash
# 카테고리 목록 확인
uvx av-mcp --list-categories

# 기본 실행
uvx av-mcp M9TJCCBXW5PJZ3HF

# 특정 카테고리만 사용
uvx av-mcp M9TJCCBXW5PJZ3HF --categories fundamental_data,economic_indicators
```
