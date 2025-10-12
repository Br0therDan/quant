# React Financial Charts 컴포넌트

## 현재 상태

react-financial-charts 패키지가 추가되었으나, 복잡한 API와 TypeScript 타입
이슈로 인해 현재는 **기존 LightWeightChart.tsx 사용을 권장**합니다.

## 기존 컴포넌트

### LightWeightChart.tsx ✅

안정적으로 작동하는 캔들스틱 차트 컴포넌트입니다.

**기능:**

- 캔들스틱 차트
- 볼륨 차트
- 타임스케일 자동 조정
- 크로스헤어 커서
- 반응형 크기 조정

**사용 예시:**

```tsx
import LightWeightChart from "./LightWeightChart";

<LightWeightChart
  data={candlestickData}
  symbol="AAPL"
  height={400}
  showVolume={true}
/>;
```

### LightWeightChartControls.tsx ✅

차트 컨트롤 패널 컴포넌트입니다.

**기능:**

- 기간 선택 (1D ~ 전체)
- 커스텀 날짜 범위
- 인터벌 선택 (분봉/일봉/주봉/월봉)
- Adjusted Price 토글

**사용 예시:**

```tsx
import ChartControls from "./LightWeightChartControls";

<ChartControls
  startDate={startDate}
  endDate={endDate}
  onStartDateChange={setStartDate}
  onEndDateChange={setEndDate}
  interval={interval}
  onIntervalChange={setInterval}
  isLoading={isLoading}
  adjusted={adjusted}
  onAdjustedChange={setAdjusted}
/>;
```

## 향후 계획

react-financial-charts를 사용한 고급 기능 구현을 위해서는:

1. **옵션 1: TradingView Lightweight Charts 확장**

   - 현재 사용 중인 lightweight-charts v5 기반
   - 커스텀 플러그인/인디케이터 추가
   - 상대적으로 간단한 API
   - ✅ 권장 방법

2. **옵션 2: react-financial-charts 마이그레이션**

   - 더 많은 내장 지표
   - 복잡한 타입 정의
   - 학습 곡선이 높음
   - ⚠️ 추가 연구 필요

3. **옵션 3: 하이브리드 접근**
   - 기본 차트: LightWeightChart
   - 지표 계산: 별도 라이브러리 (technicalindicators 등)
   - 지표를 오버레이로 표시
   - ✅ 가장 유연한 방법

## 기술 지표 구현 로드맵

### Phase 1: 기본 이동평균선 (우선순위 높음)

- [ ] SMA (Simple Moving Average)
- [ ] EMA (Exponential Moving Average)
- [ ] WMA (Weighted Moving Average)

### Phase 2: 변동성 지표

- [ ] Bollinger Bands
- [ ] ATR (Average True Range)

### Phase 3: 모멘텀 지표

- [ ] RSI (Relative Strength Index)
- [ ] MACD
- [ ] Stochastic

### Phase 4: Interactive Tools

- [ ] Trendline Drawing
- [ ] Fibonacci Retracement
- [ ] Support/Resistance Lines

## 개발 가이드

### 이동평균선 추가 예시 (권장)

```tsx
// 1. lightweight-charts의 LineSeries 사용
import { createChart } from "lightweight-charts";

const chart = createChart(container, options);
const candlestickSeries = chart.addCandlestickSeries();
const smaSeries = chart.addLineSeries({
  color: "blue",
  lineWidth: 2,
});

// 2. SMA 계산
function calculateSMA(data: number[], period: number) {
  // 구현...
}

// 3. 데이터 설정
const smaData = calculateSMA(closes, 20);
smaSeries.setData(smaData);
```

## 패키지 정보

- lightweight-charts: v5.0.8
- react-financial-charts: 최신 버전 (사용 보류)
- @mui/material: v6.x
- @mui/x-date-pickers: v7.x

## 참고 자료

- [TradingView Lightweight Charts Docs](https://tradingview.github.io/lightweight-charts/)
- [react-financial-charts Examples](https://github.com/react-financial/react-financial-charts)
- [Technical Indicators Library](https://www.npmjs.com/package/technicalindicators)
