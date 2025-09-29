"use client";

import { Box, Paper, Tab, Tabs, Typography, useTheme } from "@mui/material";
import {
  CandlestickSeries,
  ColorType,
  createChart,
  CrosshairMode,
  HistogramSeries,
  IChartApi,
  LineSeries,
  LineStyle,
} from "lightweight-charts";
import React, { useEffect, useRef } from "react";

interface CandlestickData {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number;
}

interface TechnicalIndicatorsProps {
  data: CandlestickData[];
  symbol: string;
  height?: number;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`technical-tabpanel-${index}`}
      aria-labelledby={`technical-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

// RSI 계산 함수
function calculateRSI(data: CandlestickData[], period: number = 14) {
  if (data.length < period + 1) return [];

  const gains: number[] = [];
  const losses: number[] = [];

  // 첫 번째 gain/loss 계산
  for (let i = 1; i < data.length; i++) {
    const change = data[i].close - data[i - 1].close;
    gains.push(Math.max(change, 0));
    losses.push(Math.max(-change, 0));
  }

  const rsiData: { time: string; value: number }[] = [];

  // 첫 번째 RSI 계산 (SMA 사용)
  if (gains.length >= period) {
    const avgGain = gains.slice(0, period).reduce((a, b) => a + b) / period;
    const avgLoss = losses.slice(0, period).reduce((a, b) => a + b) / period;
    const rs = avgGain / (avgLoss || 0.0001);
    const rsi = 100 - 100 / (1 + rs);

    rsiData.push({
      time: data[period].time,
      value: rsi,
    });

    // 나머지 RSI 계산 (EMA 사용)
    let currentAvgGain = avgGain;
    let currentAvgLoss = avgLoss;

    for (let i = period; i < gains.length; i++) {
      currentAvgGain = (currentAvgGain * (period - 1) + gains[i]) / period;
      currentAvgLoss = (currentAvgLoss * (period - 1) + losses[i]) / period;
      const currentRs = currentAvgGain / (currentAvgLoss || 0.0001);
      const currentRsi = 100 - 100 / (1 + currentRs);

      rsiData.push({
        time: data[i + 1].time,
        value: currentRsi,
      });
    }
  }

  return rsiData;
}

// MACD 계산 함수
function calculateMACD(
  data: CandlestickData[],
  fastPeriod: number = 12,
  slowPeriod: number = 26,
  signalPeriod: number = 9
) {
  if (data.length < slowPeriod) return { macd: [], signal: [], histogram: [] };

  // EMA 계산 함수
  const calculateEMA = (values: number[], period: number) => {
    const ema: number[] = [];
    const multiplier = 2 / (period + 1);

    ema[0] = values[0];
    for (let i = 1; i < values.length; i++) {
      ema[i] = values[i] * multiplier + ema[i - 1] * (1 - multiplier);
    }
    return ema;
  };

  const closePrices = data.map((d) => d.close);
  const fastEMA = calculateEMA(closePrices, fastPeriod);
  const slowEMA = calculateEMA(closePrices, slowPeriod);

  const macdLine: { time: string; value: number }[] = [];
  const macdValues: number[] = [];

  for (let i = slowPeriod - 1; i < data.length; i++) {
    const macdValue = fastEMA[i] - slowEMA[i];
    macdValues.push(macdValue);
    macdLine.push({
      time: data[i].time,
      value: macdValue,
    });
  }

  const signalEMA = calculateEMA(macdValues, signalPeriod);
  const signalLine: { time: string; value: number }[] = [];
  const histogramData: { time: string; value: number }[] = [];

  for (let i = signalPeriod - 1; i < macdValues.length; i++) {
    const dataIndex = i + slowPeriod - 1;
    signalLine.push({
      time: data[dataIndex].time,
      value: signalEMA[i],
    });
    histogramData.push({
      time: data[dataIndex].time,
      value: macdValues[i] - signalEMA[i],
    });
  }

  return {
    macd: macdLine,
    signal: signalLine,
    histogram: histogramData,
  };
}

// 볼린저 밴드 계산 함수
function calculateBollingerBands(
  data: CandlestickData[],
  period: number = 20,
  multiplier: number = 2
) {
  if (data.length < period) return { upper: [], middle: [], lower: [] };

  const upper: { time: string; value: number }[] = [];
  const middle: { time: string; value: number }[] = [];
  const lower: { time: string; value: number }[] = [];

  for (let i = period - 1; i < data.length; i++) {
    const slice = data.slice(i - period + 1, i + 1);
    const sma = slice.reduce((sum, item) => sum + item.close, 0) / period;
    const variance =
      slice.reduce((sum, item) => sum + Math.pow(item.close - sma, 2), 0) /
      period;
    const stdDev = Math.sqrt(variance);

    const time = data[i].time;
    upper.push({ time, value: sma + multiplier * stdDev });
    middle.push({ time, value: sma });
    lower.push({ time, value: sma - multiplier * stdDev });
  }

  return { upper, middle, lower };
}

export default function TechnicalIndicators({
  data,
  symbol,
  height = 300,
}: TechnicalIndicatorsProps) {
  const [tabValue, setTabValue] = React.useState(0);
  const rsiChartRef = useRef<HTMLDivElement>(null);
  const macdChartRef = useRef<HTMLDivElement>(null);
  const bbChartRef = useRef<HTMLDivElement>(null);
  const rsiChartApiRef = useRef<IChartApi | null>(null);
  const macdChartApiRef = useRef<IChartApi | null>(null);
  const bbChartApiRef = useRef<IChartApi | null>(null);
  const theme = useTheme();

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  // RSI 차트 생성 및 업데이트
  useEffect(() => {
    if (tabValue === 0 && rsiChartRef.current && data.length > 0) {
      // 기존 차트 정리
      if (rsiChartApiRef.current) {
        try {
          rsiChartApiRef.current.remove();
        } catch (error) {
          console.warn("RSI chart already disposed:", error);
        }
        rsiChartApiRef.current = null;
      }

      const chart = createChart(rsiChartRef.current, {
        layout: {
          background: {
            type: ColorType.Solid,
            color: theme.palette.background.paper,
          },
          textColor: theme.palette.text.primary,
        },
        grid: {
          vertLines: { color: theme.palette.divider, style: LineStyle.Dotted },
          horzLines: { color: theme.palette.divider, style: LineStyle.Dotted },
        },
        crosshair: { mode: CrosshairMode.Normal },
        rightPriceScale: { borderColor: theme.palette.divider },
        timeScale: { borderColor: theme.palette.divider },
        height,
      });

      rsiChartApiRef.current = chart;

      const rsiSeries = chart.addSeries(LineSeries, {
        color: theme.palette.primary.main,
        lineWidth: 2,
      });

      // 과매수/과매도 라인 추가
      const overboughtLine = chart.addSeries(LineSeries, {
        color: theme.palette.error.main,
        lineWidth: 1,
        lineStyle: LineStyle.Dashed,
      });

      const oversoldLine = chart.addSeries(LineSeries, {
        color: theme.palette.success.main,
        lineWidth: 1,
        lineStyle: LineStyle.Dashed,
      });

      const rsiData = calculateRSI(data);
      rsiSeries.setData(rsiData);

      // 70과 30 라인 추가
      if (rsiData.length > 0) {
        const overboughtData = rsiData.map((d) => ({
          time: d.time,
          value: 70,
        }));
        const oversoldData = rsiData.map((d) => ({ time: d.time, value: 30 }));
        overboughtLine.setData(overboughtData);
        oversoldLine.setData(oversoldData);
      }

      chart.timeScale().fitContent();
    }
  }, [tabValue, data, theme, height]);

  // MACD 차트 생성 및 업데이트
  useEffect(() => {
    if (tabValue === 1 && macdChartRef.current && data.length > 0) {
      // 기존 차트 정리
      if (macdChartApiRef.current) {
        try {
          macdChartApiRef.current.remove();
        } catch (error) {
          console.warn("MACD chart already disposed:", error);
        }
        macdChartApiRef.current = null;
      }

      const chart = createChart(macdChartRef.current, {
        layout: {
          background: {
            type: ColorType.Solid,
            color: theme.palette.background.paper,
          },
          textColor: theme.palette.text.primary,
        },
        grid: {
          vertLines: { color: theme.palette.divider, style: LineStyle.Dotted },
          horzLines: { color: theme.palette.divider, style: LineStyle.Dotted },
        },
        crosshair: { mode: CrosshairMode.Normal },
        rightPriceScale: { borderColor: theme.palette.divider },
        timeScale: { borderColor: theme.palette.divider },
        height,
      });

      macdChartApiRef.current = chart;

      const macdSeries = chart.addSeries(LineSeries, {
        color: theme.palette.primary.main,
        lineWidth: 2,
      });

      const signalSeries = chart.addSeries(LineSeries, {
        color: theme.palette.secondary.main,
        lineWidth: 2,
      });

      const histogramSeries = chart.addSeries(HistogramSeries, {
        color: theme.palette.info.main,
      });

      const macdData = calculateMACD(data);
      macdSeries.setData(macdData.macd);
      signalSeries.setData(macdData.signal);
      histogramSeries.setData(macdData.histogram);

      chart.timeScale().fitContent();
    }
  }, [tabValue, data, theme, height]);

  // 볼린저 밴드 차트 생성 및 업데이트
  useEffect(() => {
    if (tabValue === 2 && bbChartRef.current && data.length > 0) {
      // 기존 차트 정리
      if (bbChartApiRef.current) {
        try {
          bbChartApiRef.current.remove();
        } catch (error) {
          console.warn("BB chart already disposed:", error);
        }
        bbChartApiRef.current = null;
      }

      const chart = createChart(bbChartRef.current, {
        layout: {
          background: {
            type: ColorType.Solid,
            color: theme.palette.background.paper,
          },
          textColor: theme.palette.text.primary,
        },
        grid: {
          vertLines: { color: theme.palette.divider, style: LineStyle.Dotted },
          horzLines: { color: theme.palette.divider, style: LineStyle.Dotted },
        },
        crosshair: { mode: CrosshairMode.Normal },
        rightPriceScale: { borderColor: theme.palette.divider },
        timeScale: { borderColor: theme.palette.divider },
        height,
      });

      bbChartApiRef.current = chart;

      // 가격 캔들스틱 시리즈
      const candlestickSeries = chart.addSeries(CandlestickSeries, {
        upColor: theme.palette.success.main,
        downColor: theme.palette.error.main,
        borderDownColor: theme.palette.error.main,
        borderUpColor: theme.palette.success.main,
        wickDownColor: theme.palette.error.main,
        wickUpColor: theme.palette.success.main,
      });

      const bbData = calculateBollingerBands(data);

      // 볼린저 밴드 라인들
      const upperBandSeries = chart.addSeries(LineSeries, {
        color: theme.palette.warning.main,
        lineWidth: 1,
      });

      const middleBandSeries = chart.addSeries(LineSeries, {
        color: theme.palette.primary.main,
        lineWidth: 2,
      });

      const lowerBandSeries = chart.addSeries(LineSeries, {
        color: theme.palette.warning.main,
        lineWidth: 1,
      });

      // 데이터 설정
      candlestickSeries.setData(data);
      upperBandSeries.setData(bbData.upper);
      middleBandSeries.setData(bbData.middle);
      lowerBandSeries.setData(bbData.lower);

      chart.timeScale().fitContent();
    }
  }, [tabValue, data, theme, height]);

  // 컴포넌트 언마운트 시 차트 정리
  useEffect(() => {
    return () => {
      if (rsiChartApiRef.current) {
        try {
          rsiChartApiRef.current.remove();
        } catch (error) {
          console.warn("RSI chart cleanup error:", error);
        }
        rsiChartApiRef.current = null;
      }
      if (macdChartApiRef.current) {
        try {
          macdChartApiRef.current.remove();
        } catch (error) {
          console.warn("MACD chart cleanup error:", error);
        }
        macdChartApiRef.current = null;
      }
      if (bbChartApiRef.current) {
        try {
          bbChartApiRef.current.remove();
        } catch (error) {
          console.warn("BB chart cleanup error:", error);
        }
        bbChartApiRef.current = null;
      }
    };
  }, []);

  return (
    <Paper sx={{ width: "100%" }}>
      <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="RSI (상대강도지수)" />
          <Tab label="MACD" />
          <Tab label="볼린저 밴드" />
        </Tabs>
      </Box>

      <TabPanel value={tabValue} index={0}>
        <Typography variant="h6" gutterBottom>
          RSI (Relative Strength Index) - {symbol}
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          과매수(70 이상) 및 과매도(30 이하) 신호를 제공하는 모멘텀 지표
        </Typography>
        <Box ref={rsiChartRef} sx={{ width: "100%", height }} />
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <Typography variant="h6" gutterBottom>
          MACD (Moving Average Convergence Divergence) - {symbol}
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          추세 방향과 모멘텀 변화를 분석하는 지표 (MACD선, 시그널선, 히스토그램)
        </Typography>
        <Box ref={macdChartRef} sx={{ width: "100%", height }} />
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        <Typography variant="h6" gutterBottom>
          볼린저 밴드 (Bollinger Bands) - {symbol}
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          변동성과 상대적 가격 수준을 분석하는 지표 (상단밴드, 중간선, 하단밴드)
        </Typography>
        <Box ref={bbChartRef} sx={{ width: "100%", height }} />
      </TabPanel>
    </Paper>
  );
}
