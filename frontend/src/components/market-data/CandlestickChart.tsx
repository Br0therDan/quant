"use client";

import { Box, useTheme } from "@mui/material";
import {
  CandlestickSeries,
  createChart,
  CrosshairMode,
  HistogramSeries,
  type IChartApi,
  LineStyle,
} from "lightweight-charts";
import { useEffect, useRef } from "react";

interface CandlestickData {
  time: string; // "YYYY-MM-DD" format
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number;
}

interface CandlestickChartProps {
  data: CandlestickData[];
  symbol: string;
  height?: number;
  showVolume?: boolean;
}

export default function CandlestickChart({
  data,
  height = 400,
  showVolume = true,
}: CandlestickChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candlestickSeriesRef = useRef<any>(null);
  const volumeSeriesRef = useRef<any>(null);
  const theme = useTheme();

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // 차트 생성
    const chart = createChart(chartContainerRef.current, {
      layout: {
        // background: {
        // 	type: ColorType.Solid,
        // 	color: theme.palette.background.paper,
        // },
        textColor: theme.palette.text.primary,
      },
      grid: {
        vertLines: {
          color: theme.palette.divider,
          style: LineStyle.Dotted,
        },
        horzLines: {
          color: theme.palette.divider,
          style: LineStyle.Dotted,
        },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
      },
      rightPriceScale: {
        borderColor: theme.palette.divider,
      },
      timeScale: {
        borderColor: theme.palette.divider,
        timeVisible: true,
        secondsVisible: false,
      },
      height,
    });

    chartRef.current = chart;

    // 캔들스틱 시리즈 추가
    const candlestickSeries = chart.addSeries(CandlestickSeries, {
      upColor: theme.palette.success.main,
      downColor: theme.palette.error.main,
      borderDownColor: theme.palette.error.main,
      borderUpColor: theme.palette.success.main,
      wickDownColor: theme.palette.error.main,
      wickUpColor: theme.palette.success.main,
    });

    candlestickSeriesRef.current = candlestickSeries;

    // 볼륨 시리즈 추가 (별도 패널에)
    if (showVolume) {
      const volumeSeries = chart.addSeries(
        HistogramSeries,
        {
          color: theme.palette.primary.main,
          priceFormat: {
            type: "volume",
          },
          priceScaleId: "volume", // 별도 스케일 사용
        },
        1
      ); // 1번째 패널(새로운 패널)에 추가
      volumeSeriesRef.current = volumeSeries;
    }

    // 창 크기 조정 핸들러
    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chart.remove();
    };
  }, [theme, height, showVolume]);

  // 데이터 업데이트
  useEffect(() => {
    console.log("🎨 CandlestickChart - Data Update:", {
      hasChart: !!candlestickSeriesRef.current,
      dataLength: data.length,
      firstData: data[0],
      lastData: data[data.length - 1],
    });

    if (!candlestickSeriesRef.current || !data.length) {
      console.log("⚠️ CandlestickChart - Skipping update:", {
        hasChart: !!candlestickSeriesRef.current,
        dataLength: data.length,
      });
      return;
    }

    // 캔들스틱 데이터 설정
    const candlestickData = data.map((item) => ({
      time: item.time,
      open: item.open,
      high: item.high,
      low: item.low,
      close: item.close,
    }));

    console.log("✅ CandlestickChart - Setting data:", {
      candlestickDataLength: candlestickData.length,
      firstCandle: candlestickData[0],
      lastCandle: candlestickData[candlestickData.length - 1],
    });

    candlestickSeriesRef.current.setData(candlestickData);

    // 볼륨 데이터 설정
    if (volumeSeriesRef.current && showVolume) {
      const volumeData = data
        .filter((item) => item.volume !== undefined)
        .map((item) => ({
          time: item.time,
          value: item.volume !== undefined ? item.volume : 0,
          color:
            item.close >= item.open
              ? theme.palette.success.main + "80" // 80은 알파값 (투명도)
              : theme.palette.error.main + "80",
        }));

      volumeSeriesRef.current.setData(volumeData);
    }

    // 자동 스케일 조정
    chartRef.current?.timeScale().fitContent();
  }, [data, showVolume, theme]);

  return (
    <Box
      sx={{
        width: "100%",
        height,
        position: "relative",
        "& > div": {
          borderRadius: 1,
          width: "100%",
          height: "100%",
        },
      }}
    >
      <div ref={chartContainerRef} />
    </Box>
  );
}
