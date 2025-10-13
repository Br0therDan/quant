"use client";

import { Box } from "@mui/material";
import { HoverTooltip } from "@react-financial-charts/tooltip";
import { format } from "d3-format";
import { timeFormat } from "d3-time-format";
import * as React from "react";
import { useMemo } from "react";
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
	lastVisibleItemBasedZoomAnchor,
	LineSeries,
	macd,
	MouseCoordinateX,
	MouseCoordinateY,
	MovingAverageTooltip,
	OHLCTooltip,
	pointAndFigure,
	renko,
	rsi,
	sar,
	SARSeries,
	SingleValueTooltip,
	sma,
	stochasticOscillator,
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
	width: number;
}

function ReactFinancialChart({
	data,
	symbol,
	height = 800,
	chartType = "candlestick",
	indicators = {},
	ratio = 1,
	width,
}: ReactFinancialChartProps) {
	// Display format utilities
	const pricesDisplayFormat = format(".2f");
	const dateTimeFormat = "%d %b %H:%M";
	const timeDisplayFormat = timeFormat(dateTimeFormat); // xScale Provider (StockChart 패턴)
	const xScaleProvider = useMemo(
		() =>
			discontinuousTimeScaleProviderBuilder().inputDateAccessor(
				(d: ProcessedData) => d.date,
			),
		[],
	);

	// 데이터 처리 및 지표 계산
	const calculatedData = useMemo(() => {
		if (!data || data.length === 0) return [];

		// 기본 데이터 변환 (UTC → 로컬 시간대)
		let processed: ProcessedData[] = data
			.map((d) => {
				// Alpha Vantage API는 UTC 시간을 반환하므로 로컬 시간대로 변환
				// JavaScript Date 객체는 내부적으로 UTC를 저장하고
				// 표시할 때 자동으로 로컬 시간대로 변환됨
				const date = new Date(d.time);
				return {
					date,
					open: d.open,
					high: d.high,
					low: d.low,
					close: d.close,
					volume: d.volume || 0,
				};
			})
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

		// EMA 지표 (StockChart 패턴 적용)
		indicators.ema?.forEach((period) => {
			const emaCalculator = ema()
				.id(period)
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

	// xScale Provider로 데이터 변환 (StockChart 패턴)
	const {
		data: chartData,
		xScale,
		xAccessor,
		displayXAccessor,
	} = useMemo(() => {
		return xScaleProvider(calculatedData);
	}, [calculatedData, xScaleProvider]);

	// xExtents 계산 (StockChart 패턴: 마지막 100개 + 5 여유)
	const xExtents = useMemo(() => {
		if (!chartData || chartData.length === 0) return [0, 0];
		const max = xAccessor(chartData[chartData.length - 1]);
		const min = xAccessor(chartData[Math.max(0, chartData.length - 100)]);
		return [min, max + 5];
	}, [chartData, xAccessor]);

	if (!chartData || chartData.length === 0 || width === 0) {
		return (
			<Box sx={{ width: "100%", height }}>
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

	// Margin 설정 (StockChart 패턴)
	const margin = { left: 0, right: 80, top: 0, bottom: 30 };
	const gridHeight = height - margin.top - margin.bottom;

	// 차트별 높이 계산 (StockChart 패턴 개선)
	const indicatorHeight = gridHeight * 0.2;

	// Volume은 메인 차트 하단에 작게 오버레이
	const volumeHeight = gridHeight * 0.25;
	const mainPriceHeight = gridHeight;

	// Elder Ray가 있으면 별도 영역
	const elderRayHeight = indicators.elderRay ? 120 : 0;

	// 메인 차트 높이 계산
	let adjustedMainHeight = mainPriceHeight;
	if (indicators.macd) adjustedMainHeight -= indicatorHeight;
	if (indicators.rsi) adjustedMainHeight -= indicatorHeight;
	if (indicators.stochastic) adjustedMainHeight -= indicatorHeight;
	if (indicators.elderRay) adjustedMainHeight -= elderRayHeight;

	// Origin 계산 함수 (StockChart 패턴)
	const volumeOrigin = (_: number, h: number) => [
		0,
		h - volumeHeight - elderRayHeight,
	];
	const elderRayOrigin = (_: number, h: number) => [0, h - elderRayHeight];

	// Helper functions
	const barChartExtents = (d: ProcessedData) => d.volume || 0;
	const candleChartExtents = (d: ProcessedData) => [d.high, d.low];
	const yEdgeIndicator = (d: ProcessedData) => d.close;
	const volumeColor = (d: ProcessedData) =>
		d.close > d.open ? "rgba(38, 166, 154, 0.3)" : "rgba(239, 83, 80, 0.3)";
	const openCloseColor = (d: ProcessedData) =>
		d.close > d.open ? "#26a69a" : "#ef5350";

	return (
		<Box
			sx={{
				width: "100%",
				height,
				position: "relative",
				overflow: "hidden", // 차트가 컨테이너를 벗어나지 않도록
			}}
		>
			<ChartCanvas
				height={height}
				width={width}
				ratio={ratio}
				margin={margin}
				data={chartData}
				displayXAccessor={displayXAccessor}
				seriesName={symbol}
				xScale={xScale}
				xAccessor={xAccessor}
				xExtents={xExtents}
				zoomAnchor={lastVisibleItemBasedZoomAnchor}
			>
				{/* Volume Chart (차트 2) - 별도 차트로 하되 오버레이 효과 */}
				{chartData.some((d: any) => d.volume) && (
					<Chart
						id={2}
						height={volumeHeight}
						origin={volumeOrigin}
						yExtents={barChartExtents}
					>
						<BarSeries fillStyle={volumeColor} yAccessor={barChartExtents} />
						{!indicators.elderRay && <XAxis showGridLines showTicks />}
					</Chart>
				)}

				{/* Main Price Chart (차트 3) - StockChart 패턴 */}
				<Chart id={3} height={adjustedMainHeight} yExtents={candleChartExtents}>
					<XAxis showGridLines showTicks={false} showTickLabel={false} />
					<YAxis showGridLines tickFormat={pricesDisplayFormat} />

					{/* 캔들스틱 차트 */}
					<CandlestickSeries />

					{/* 이동평균선 - EMA */}
					{indicators.ema?.map((period) => {
						const emaAccessor = (d: any) => d[`ema${period}`];
						const emaStroke = `hsl(${(period * 137) % 360}, 70%, 50%)`;
						return (
							<React.Fragment key={`ema-${period}`}>
								<LineSeries
									yAccessor={emaAccessor}
									strokeStyle={emaStroke}
									strokeWidth={2}
								/>
								<CurrentCoordinate
									yAccessor={emaAccessor}
									fillStyle={emaStroke}
								/>
							</React.Fragment>
						);
					})}

					{/* 이동평균선 - SMA */}
					{indicators.sma?.map((period) => {
						const smaAccessor = (d: any) => d[`sma${period}`];
						const smaStroke = `hsl(${((period * 137) % 360) + 60}, 70%, 50%)`;
						return (
							<React.Fragment key={`sma-${period}`}>
								<LineSeries
									yAccessor={smaAccessor}
									strokeStyle={smaStroke}
									strokeWidth={2}
								/>
								<CurrentCoordinate
									yAccessor={smaAccessor}
									fillStyle={smaStroke}
								/>
							</React.Fragment>
						);
					})}

					{/* Bollinger Bands */}
					{indicators.bollingerBand && (
						<BollingerSeries yAccessor={(d: any) => d.bb} />
					)}

					{/* SAR */}
					{indicators.sar && <SARSeries yAccessor={(d: any) => d.sar} />}

					{/* MouseCoordinates */}
					<MouseCoordinateY
						rectWidth={margin.right}
						displayFormat={pricesDisplayFormat}
					/>

					{/* Edge Indicator (StockChart 패턴) */}
					<EdgeIndicator
						itemType="last"
						rectWidth={margin.right}
						fill={openCloseColor}
						lineStroke={openCloseColor}
						displayFormat={pricesDisplayFormat}
						yAccessor={yEdgeIndicator}
					/>

					{/* Moving Average Tooltip */}
					{(indicators.ema || indicators.sma) && (
						<MovingAverageTooltip
							origin={[8, 24]}
							options={[
								...(indicators.ema?.map((period) => ({
									yAccessor: (d: any) => d[`ema${period}`],
									type: "EMA",
									stroke: `hsl(${(period * 137) % 360}, 70%, 50%)`,
									windowSize: period,
								})) || []),
								...(indicators.sma?.map((period) => ({
									yAccessor: (d: any) => d[`sma${period}`],
									type: "SMA",
									stroke: `hsl(${((period * 137) % 360) + 60}, 70%, 50%)`,
									windowSize: period,
								})) || []),
							]}
						/>
					)}

					{/* Volume도 없고 Elder Ray도 없을 때만 메인 차트에 XAxis 표시 */}
					{!chartData.some((d: any) => d.volume) && !indicators.elderRay && (
						<XAxis showGridLines showTicks />
					)}

					<ZoomButtons />
					<OHLCTooltip origin={[8, 16]} />

					{/* Hover Tooltip - Tooltips.tsx 예제 참고 */}
					<HoverTooltip
						yAccessor={(d: any) => d.close}
						tooltip={{
							content: ({ currentItem, xAccessor }) => {
								const dateStr = timeDisplayFormat(xAccessor(currentItem));
								return {
									x: dateStr,
									y: [
										{
											label: "open",
											value:
												currentItem.open &&
												pricesDisplayFormat(currentItem.open),
										},
										{
											label: "high",
											value:
												currentItem.high &&
												pricesDisplayFormat(currentItem.high),
										},
										{
											label: "low",
											value:
												currentItem.low && pricesDisplayFormat(currentItem.low),
										},
										{
											label: "close",
											value:
												currentItem.close &&
												pricesDisplayFormat(currentItem.close),
										},
									],
								};
							},
						}}
					/>
				</Chart>

				{/* Elder Ray Chart (차트 4) - StockChart 패턴 */}
				{indicators.elderRay && (
					<Chart
						id={4}
						height={elderRayHeight}
						yExtents={(d: any) => d.elderRay}
						origin={elderRayOrigin}
						padding={{ top: 8, bottom: 8 }}
					>
						<XAxis showGridLines showTicks />
						<YAxis ticks={4} tickFormat={pricesDisplayFormat} />

						<MouseCoordinateX displayFormat={timeDisplayFormat} />
						<MouseCoordinateY
							rectWidth={margin.right}
							displayFormat={pricesDisplayFormat}
						/>

						<ElderRaySeries yAccessor={(d: any) => d.elderRay} />

						<SingleValueTooltip
							yAccessor={(d: any) => d.elderRay}
							yLabel="Elder Ray"
							yDisplayFormat={(d: any) =>
								`${pricesDisplayFormat(d.bullPower)}, ${pricesDisplayFormat(
									d.bearPower,
								)}`
							}
							origin={[8, 16]}
						/>
					</Chart>
				)}

				{/* CrossHair Cursor - Customized */}
				<CrossHairCursor
					snapX={true}
					strokeStyle="rgba(100, 149, 237, 0.6)"
					strokeDasharray="ShortDash"
					strokeWidth={1}
				/>
			</ChartCanvas>
		</Box>
	);
}

export default ReactFinancialChart;
