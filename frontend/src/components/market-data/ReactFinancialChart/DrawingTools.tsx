"use client";

import {
  FibonacciRetracement,
  TrendLine,
} from "@react-financial-charts/interactive";
import { useState } from "react";

export interface DrawingToolsConfig {
  enabled: boolean;
  mode: "trendline" | "fibonacci" | "none";
}

interface DrawingToolsProps {
  config: DrawingToolsConfig;
  onComplete?: () => void;
}

export default function DrawingTools({
  config,
  onComplete,
}: DrawingToolsProps) {
  const [trendLines, setTrendLines] = useState<any[]>([]);
  const [fibonaccis, setFibonaccis] = useState<any[]>([]);

  if (!config.enabled || config.mode === "none") {
    return null;
  }

  const handleTrendLineComplete = (trendLine: any) => {
    setTrendLines([...trendLines, trendLine]);
    onComplete?.();
  };

  const handleFibonacciComplete = (fibonacci: any) => {
    setFibonaccis([...fibonaccis, fibonacci]);
    onComplete?.();
  };

  return (
    <>
      {/* Trend Lines */}
      {config.mode === "trendline" && (
        <TrendLine
          snap={false}
          enabled={true}
          snapTo={(d: any) => [d.high, d.low]}
          onComplete={handleTrendLineComplete}
          trends={trendLines}
          appearance={{
            strokeStyle: "#1E88E5",
            strokeWidth: 2,
            strokeDasharray: "Solid",
            edgeStroke: "#1E88E5",
            edgeFill: "#FFFFFF",
            edgeStrokeWidth: 2,
          }}
        />
      )}

      {/* Fibonacci Retracement */}
      {config.mode === "fibonacci" && (
        <FibonacciRetracement
          enabled={true}
          retracements={fibonaccis}
          onComplete={handleFibonacciComplete}
          appearance={{
            strokeStyle: "#E91E63",
            strokeWidth: 1,
            fontFamily: "Arial",
            fontSize: 11,
            fontFill: "#E91E63",
            edgeStroke: "#E91E63",
            edgeFill: "#FFFFFF",
            nsEdgeFill: "#FFFFFF",
            edgeStrokeWidth: 2,
            r: 5,
          }}
        />
      )}
    </>
  );
}
