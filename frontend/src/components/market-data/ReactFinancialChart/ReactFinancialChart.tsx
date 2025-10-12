"use client";

import { Box, useTheme } from "@mui/material";
import { timeFormat } from "d3-time-format";
import { memo, useEffect, useMemo, useRef, useState } from "react";
import {
  atr,
  BarSeries,
  bollingerBand,
  BollingerSeries,
  CandlestickSeries,
  Chart,
  ChartCanvas,
  CrossHairCursor,
  CurrentCoordinate,
  discontinuousTimeScaleProviderBuilder,
  EdgeIndicator,
  elderImpulse,
  elderRay,
  ElderRaySeries,
  ema,
  forceIndex,
  heikinAshi,
  kagi,
  KagiSeries,
  LineSeries,
  macd,
  MACDSeries,
  MACDTooltip,
  MouseCoordinateX,
  MouseCoordinateY,
  OHLCTooltip,
  pointAndFigure,
  PointAndFigureSeries,
  renko,
  RenkoSeries,
  rsi,
  RSISeries,
  RSITooltip,
  sar,
  SARSeries,
  ScatterSeries,
  SingleValueTooltip,
  sma,
  stochasticOscillator,
  StochasticSeries,
  StochasticTooltip,
  tma,
  wma,
  XAxis,
  YAxis,
  ZoomButtons,
} from "react-financial-charts";

interface CandlestickData {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number;
}

interface ProcessedData {
  date: Date;
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number;
  [key: string]: any;
}

export interface ChartType {
  type:
    | "candlestick"
    | "ohlc"
    | "line"
    | "area"
    | "scatter"
    | "heikinAshi"
    | "renko"
    | "kagi"
    | "pointAndFigure";
}

export interface IndicatorConfig {
  // Moving Averages
  ema?: number[];
  sma?: number[];
  wma?: number[];
  tma?: number[];

  // Volatility
  bollingerBand?: boolean;
  atr?: boolean;

  // Trend
  sar?: boolean;
  macd?: boolean;

  // Momentum
  rsi?: boolean;
  stochastic?: "fast" | "slow" | "full" | null;
  forceIndex?: boolean;

  // Volume
  elderRay?: boolean;
  elderImpulse?: boolean;
}

interface ReactFinancialChartProps {
  data: CandlestickData[];
  symbol: string;
  height?: number;
  chartType?: ChartType["type"];
  indicators?: IndicatorConfig;
  ratio?: number;
}

function ReactFinancialChart({
  data,
  symbol,
  height = 600,
  chartType = "candlestick",
  indicators = {},
  ratio = 1,
}: ReactFinancialChartProps) {
  const theme = useTheme();
  const chartRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 0, height });

  // 윈도우 리사이즈 처리
  useEffect(() => {
    const updateDimensions = () => {
      if (chartRef.current) {
        setDimensions({
          width: chartRef.current.clientWidth,
          height,
        });
      }
    };

    updateDimensions();
    window.addEventListener("resize", updateDimensions);
    return () => window.removeEventListener("resize", updateDimensions);
  }, [height]);

  // 데이터 처리 및 지표 계산
  const processedData = useMemo(() => {
    if (!data || data.length === 0) return [];

    // 기본 데이터 변환
    let processed: ProcessedData[] = data
      .map((d) => ({
        date: new Date(d.time),
        open: d.open,
        high: d.high,
        low: d.low,
        close: d.close,
        volume: d.volume || 0,
      }))
      .sort((a, b) => a.date.getTime() - b.date.getTime());

    // 차트 타입별 데이터 변환
    if (chartType === "heikinAshi") {
      const heikinAshiCalculator = heikinAshi();
      processed = heikinAshiCalculator(processed);
    } else if (chartType === "renko") {
      const renkoCalculator = renko();
      processed = renkoCalculator(processed);
    } else if (chartType === "kagi") {
      const kagiCalculator = kagi();
      processed = kagiCalculator(processed);
    } else if (chartType === "pointAndFigure") {
      const pnfCalculator = pointAndFigure();
      processed = pnfCalculator(processed);
    }

    // EMA 지표
    indicators.ema?.forEach((period) => {
      const emaCalculator = ema()
        .options({ windowSize: period })
        .merge((d: any, c: any) => {
          d[`ema${period}`] = c;
        })
        .accessor((d: any) => d[`ema${period}`]);
      processed = emaCalculator(processed);
    });

    // SMA 지표
    indicators.sma?.forEach((period) => {
      const smaCalculator = sma()
        .options({ windowSize: period })
        .merge((d: any, c: any) => {
          d[`sma${period}`] = c;
        })
        .accessor((d: any) => d[`sma${period}`]);
      processed = smaCalculator(processed);
    });

    // WMA 지표
    indicators.wma?.forEach((period) => {
      const wmaCalculator = wma()
        .options({ windowSize: period })
        .merge((d: any, c: any) => {
          d[`wma${period}`] = c;
        })
        .accessor((d: any) => d[`wma${period}`]);
      processed = wmaCalculator(processed);
    });

    // TMA 지표
    indicators.tma?.forEach((period) => {
      const tmaCalculator = tma()
        .options({ windowSize: period })
        .merge((d: any, c: any) => {
          d[`tma${period}`] = c;
        })
        .accessor((d: any) => d[`tma${period}`]);
      processed = tmaCalculator(processed);
    });

    // Bollinger Bands
    if (indicators.bollingerBand) {
      const bb = bollingerBand()
        .merge((d: any, c: any) => {
          d.bb = c;
        })
        .accessor((d: any) => d.bb);
      processed = bb(processed);
    }

    // SAR
    if (indicators.sar) {
      const sarCalculator = sar()
        .merge((d: any, c: any) => {
          d.sar = c;
        })
        .accessor((d: any) => d.sar);
      processed = sarCalculator(processed);
    }

    // MACD
    if (indicators.macd) {
      const macdCalculator = macd();
      processed = macdCalculator(processed);
    }

    // RSI
    if (indicators.rsi) {
      const rsiCalculator = rsi()
        .options({ windowSize: 14 })
        .merge((d: any, c: any) => {
          d.rsi = c;
        })
        .accessor((d: any) => d.rsi);
      processed = rsiCalculator(processed);
    }

    // ATR
    if (indicators.atr) {
      const atrCalculator = atr()
        .options({ windowSize: 14 })
        .merge((d: any, c: any) => {
          d.atr = c;
        })
        .accessor((d: any) => d.atr);
      processed = atrCalculator(processed);
    }

    // Stochastic
    if (indicators.stochastic) {
      const stochasticCalculator = stochasticOscillator()
        .options({
          windowSize: 14,
          kWindowSize: indicators.stochastic === "slow" ? 3 : 1,
          dWindowSize: 3,
        })
        .merge((d: any, c: any) => {
          d.stochastic = c;
        })
        .accessor((d: any) => d.stochastic);
      processed = stochasticCalculator(processed);
    }

    // Force Index
    if (indicators.forceIndex) {
      const forceIndexCalculator = forceIndex()
        .merge((d: any, c: any) => {
          d.forceIndex = c;
        })
        .accessor((d: any) => d.forceIndex);
      processed = forceIndexCalculator(processed);
    }

    // Elder Ray
    if (indicators.elderRay) {
      const elderRayCalculator = elderRay();
      processed = elderRayCalculator(processed);
    }

    // Elder Impulse
    if (indicators.elderImpulse) {
      const elderImpulseCalculator = elderImpulse();
      processed = elderImpulseCalculator(processed);
    }

    return processed;
  }, [data, chartType, indicators]);

  const {
    data: chartData,
    xScale,
    xAccessor,
    displayXAccessor,
  } = useMemo(() => {
    const ScaleProvider =
      discontinuousTimeScaleProviderBuilder().inputDateAccessor(
        (d: ProcessedData) => d.date
      );
    return ScaleProvider(processedData);
  }, [processedData]);

  if (!chartData || chartData.length === 0 || dimensions.width === 0) {
    return (
      <Box ref={chartRef} sx={{ width: "100%", height }}>
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            height: "100%",
          }}
        >
          Loading chart...
        </Box>
      </Box>
    );
  }

  // 차트 높이 계산
  const mainChartHeight =
    indicators.macd || indicators.rsi || indicators.stochastic
      ? height * 0.6
      : height * 0.85;

  const volumeHeight = height * 0.15;
  const indicatorHeight = height * 0.25;

  let currentYOffset = 0;
  const charts: any[] = [];

  // 메인 차트
  charts.push({
    id: 1,
    yExtents: (d: ProcessedData) => [d.high, d.low],
    height: mainChartHeight,
    origin: [0, currentYOffset],
  });
  currentYOffset += mainChartHeight;

  // 볼륨 차트
  if (chartData.some((d: any) => d.volume)) {
    charts.push({
      id: 2,
      yExtents: (d: ProcessedData) => d.volume || 0,
      height: volumeHeight,
      origin: [0, currentYOffset],
    });
    currentYOffset += volumeHeight;
  }

  // MACD 차트
  if (indicators.macd) {
    charts.push({
      id: 3,
      yExtents: (d: any) =>
        d.macd ? [d.macd.divergence, d.macd.macd, d.macd.signal] : [0],
      height: indicatorHeight,
      origin: [0, currentYOffset],
    });
    currentYOffset += indicatorHeight;
  }

  // RSI 차트
  if (indicators.rsi) {
    charts.push({
      id: 4,
      yExtents: [0, 100],
      height: indicatorHeight,
      origin: [0, currentYOffset],
    });
    currentYOffset += indicatorHeight;
  }

  // Stochastic 차트
  if (indicators.stochastic) {
    charts.push({
      id: 5,
      yExtents: [0, 100],
      height: indicatorHeight,
      origin: [0, currentYOffset],
    });
    currentYOffset += indicatorHeight;
  }

  const margin = { left: 0, right: 60, top: 10, bottom: 30 };
  const gridHeight = currentYOffset;

  return (
    <Box
      ref={chartRef}
      sx={{
        width: "100%",
        height: gridHeight,
        position: "relative",
        backgroundColor: "transparent",
      }}
    >
      <ChartCanvas
        height={gridHeight}
        width={dimensions.width}
        ratio={ratio}
        margin={margin}
        data={chartData}
        displayXAccessor={displayXAccessor}
        seriesName={symbol}
        xScale={xScale}
        xAccessor={xAccessor}
        xExtents={[
          xAccessor(chartData[0]),
          xAccessor(chartData[chartData.length - 1]),
        ]}
      >
        {/* 메인 차트 */}
        <Chart
          id={1}
          yExtents={charts[0].yExtents}
          height={charts[0].height}
          origin={charts[0].origin}
        >
          <XAxis />
          <YAxis />

          {/* 차트 타입별 렌더링 */}
          {chartType === "candlestick" && (
            <CandlestickSeries
              fill={(d: ProcessedData) =>
                d.close > d.open
                  ? theme.palette.success.main
                  : theme.palette.error.main
              }
              wickStroke={(d: ProcessedData) =>
                d.close > d.open
                  ? theme.palette.success.main
                  : theme.palette.error.main
              }
            />
          )}

          {chartType === "ohlc" && (
            <CandlestickSeries
              wickStroke={(d: ProcessedData) =>
                d.close > d.open
                  ? theme.palette.success.main
                  : theme.palette.error.main
              }
            />
          )}

          {chartType === "line" && (
            <LineSeries
              yAccessor={(d: ProcessedData) => d.close}
              strokeStyle={theme.palette.primary.main}
            />
          )}

          {chartType === "area" && (
            <LineSeries
              yAccessor={(d: ProcessedData) => d.close}
              strokeStyle={theme.palette.primary.main}
            />
          )}

          {chartType === "scatter" && (
            <ScatterSeries
              yAccessor={(d: ProcessedData) => d.close}
              marker={(props: any) => {
                const { datum } = props;
                const fill =
                  datum.close > datum.open
                    ? theme.palette.success.main
                    : theme.palette.error.main;
                return <circle {...props} fill={fill} r={3} />;
              }}
            />
          )}

          {chartType === "heikinAshi" && (
            <CandlestickSeries
              fill={(d: any) =>
                d.close > d.open
                  ? theme.palette.success.main
                  : theme.palette.error.main
              }
            />
          )}

          {chartType === "renko" && <RenkoSeries />}

          {chartType === "kagi" && <KagiSeries />}

          {chartType === "pointAndFigure" && <PointAndFigureSeries />}

          {/* 이동평균선 */}
          {indicators.ema?.map((period) => (
            <LineSeries
              key={`ema-${period}`}
              yAccessor={(d: any) => d[`ema${period}`]}
              strokeStyle={`hsl(${period * 30}, 70%, 50%)`}
              strokeWidth={2}
            />
          ))}

          {indicators.sma?.map((period) => (
            <LineSeries
              key={`sma-${period}`}
              yAccessor={(d: any) => d[`sma${period}`]}
              strokeStyle={`hsl(${period * 30 + 60}, 70%, 50%)`}
              strokeWidth={2}
            />
          ))}

          {indicators.wma?.map((period) => (
            <LineSeries
              key={`wma-${period}`}
              yAccessor={(d: any) => d[`wma${period}`]}
              strokeStyle={`hsl(${period * 30 + 120}, 70%, 50%)`}
              strokeWidth={2}
            />
          ))}

          {indicators.tma?.map((period) => (
            <LineSeries
              key={`tma-${period}`}
              yAccessor={(d: any) => d[`tma${period}`]}
              strokeStyle={`hsl(${period * 30 + 180}, 70%, 50%)`}
              strokeWidth={2}
            />
          ))}

          {/* Bollinger Bands */}
          {indicators.bollingerBand && (
            <BollingerSeries yAccessor={(d: any) => d.bb} />
          )}

          {/* SAR */}
          {indicators.sar && <SARSeries yAccessor={(d: any) => d.sar} />}

          {/* Elder Ray */}
          {indicators.elderRay && (
            <ElderRaySeries yAccessor={(d: any) => d.elderRay} />
          )}

          {/* Edge Indicators */}
          <CurrentCoordinate
            yAccessor={(d: ProcessedData) => d.close}
            fillStyle={theme.palette.primary.main}
          />
          <EdgeIndicator
            itemType="last"
            rectWidth={60}
            fill={theme.palette.primary.main}
            lineStroke={theme.palette.primary.main}
            displayFormat={(value: number) => value.toFixed(2)}
            yAccessor={(d: ProcessedData) => d.close}
          />

          {/* Tooltips */}
          <OHLCTooltip origin={[8, 16]} />

          {indicators.bollingerBand && (
            <SingleValueTooltip
              yAccessor={(d: any) => d.bb}
              yLabel="BB"
              origin={[8, 40]}
            />
          )}

          {/* MouseCoordinate for crosshair */}
          <MouseCoordinateX displayFormat={timeFormat("%Y-%m-%d %H:%M")} />
          <MouseCoordinateY
            rectWidth={margin.right}
            displayFormat={(d: number) => d.toFixed(2)}
          />
        </Chart>

        {/* 볼륨 차트 */}
        {charts.length > 1 && chartData.some((d: any) => d.volume) && (
          <Chart
            id={2}
            yExtents={charts[1].yExtents}
            height={charts[1].height}
            origin={charts[1].origin}
          >
            <YAxis ticks={3} />
            <BarSeries
              yAccessor={(d: ProcessedData) => d.volume || 0}
              fillStyle={(d: ProcessedData) =>
                d.close > d.open
                  ? theme.palette.success.main + "80"
                  : theme.palette.error.main + "80"
              }
            />
          </Chart>
        )}

        {/* MACD 차트 */}
        {indicators.macd &&
          (() => {
            const macdChart = charts.find((c) => c.id === 3);
            if (!macdChart) return null;
            return (
              <Chart
                id={3}
                yExtents={macdChart.yExtents}
                height={macdChart.height}
                origin={macdChart.origin}
              >
                <XAxis />
                <YAxis ticks={2} />
                <MACDSeries yAccessor={(d: any) => d.macd} />
                <MACDTooltip
                  origin={[8, 16]}
                  yAccessor={(d: any) => d.macd}
                  options={{
                    fast: 12,
                    slow: 26,
                    signal: 9,
                  }}
                  appearance={{
                    strokeStyle: {
                      macd: "#2196f3",
                      signal: "#f44336",
                    },
                    fillStyle: {
                      divergence: "#4CAF50",
                    },
                  }}
                />
              </Chart>
            );
          })()}

        {/* RSI 차트 */}
        {indicators.rsi &&
          (() => {
            const rsiChart = charts.find((c) => c.id === 4);
            if (!rsiChart) return null;
            return (
              <Chart
                id={4}
                yExtents={[0, 100]}
                height={rsiChart.height}
                origin={rsiChart.origin}
              >
                <XAxis />
                <YAxis ticks={2} tickValues={[30, 70]} />
                <RSISeries yAccessor={(d: any) => d.rsi} />
                <RSITooltip
                  origin={[8, 16]}
                  yAccessor={(d: any) => d.rsi}
                  options={{ windowSize: 14 }}
                />
              </Chart>
            );
          })()}

        {/* Stochastic 차트 */}
        {indicators.stochastic &&
          (() => {
            const stochasticChart = charts.find((c) => c.id === 5);
            if (!stochasticChart) return null;
            return (
              <Chart
                id={5}
                yExtents={[0, 100]}
                height={stochasticChart.height}
                origin={stochasticChart.origin}
              >
                <XAxis />
                <YAxis ticks={2} tickValues={[20, 80]} />
                <StochasticSeries yAccessor={(d: any) => d.stochastic} />
                <StochasticTooltip
                  origin={[8, 16]}
                  yAccessor={(d: any) => d.stochastic}
                  options={{
                    windowSize: 14,
                    kWindowSize: indicators.stochastic === "slow" ? 3 : 1,
                    dWindowSize: 3,
                  }}
                  appearance={{
                    stroke: {
                      kLine: "#2196f3",
                      dLine: "#f44336",
                    },
                  }}
                />
              </Chart>
            );
          })()}

        {/* CrossHair Cursor */}
        <CrossHairCursor />
        <ZoomButtons />
      </ChartCanvas>
    </Box>
  );
}

// Performance optimization: Memoize component to prevent unnecessary re-renders
export default memo(ReactFinancialChart, (prevProps, nextProps) => {
  // Custom comparison function for memo
  return (
    prevProps.symbol === nextProps.symbol &&
    prevProps.height === nextProps.height &&
    prevProps.chartType === nextProps.chartType &&
    prevProps.ratio === nextProps.ratio &&
    prevProps.data.length === nextProps.data.length &&
    JSON.stringify(prevProps.indicators) ===
      JSON.stringify(nextProps.indicators)
  );
});
