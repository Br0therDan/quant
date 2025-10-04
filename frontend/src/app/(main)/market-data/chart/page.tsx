"use client";

import { Box, Container, Typography } from "@mui/material";
import { LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { useQuery } from "@tanstack/react-query";
import dayjs, { type Dayjs } from "dayjs";
import React from "react";
import {
	marketDataGetAvailableSymbolsOptions,
	marketDataGetMarketDataOptions,
} from "@/client/@tanstack/react-query.gen";
import PageContainer from "@/components/layout/PageContainer";
import CandlestickChart from "@/components/market-data/CandlestickChart";
import MarketDataControls from "@/components/market-data/MarketDataControls";
import MarketDataSummaryCard from "@/components/market-data/MarketDataSummaryCard";
import TechnicalIndicators from "@/components/market-data/TechnicalIndicators";

interface CandlestickData {
	time: string;
	open: number;
	high: number;
	low: number;
	close: number;
	volume: number;
}

export default function MarketDataChartPage() {
	const [selectedSymbol, setSelectedSymbol] = React.useState<string>("");
	const [startDate, setStartDate] = React.useState<Dayjs | null>(
		dayjs().subtract(3, "month"),
	);
	const [endDate, setEndDate] = React.useState<Dayjs | null>(dayjs());
	const [interval, setInterval] = React.useState<string>("1d");
	const [forceRefresh, setForceRefresh] = React.useState<boolean>(false);

	// 사용 가능한 심볼 목록 조회
	const { data: availableSymbols, isLoading: symbolsLoading } = useQuery(
		marketDataGetAvailableSymbolsOptions(),
	);

	// 선택된 심볼의 마켓 데이터 조회
	const {
		data: marketData,
		isLoading: dataLoading,
		refetch: refetchMarketData,
	} = useQuery({
		...marketDataGetMarketDataOptions({
			path: { symbol: selectedSymbol },
			query: {
				start_date: startDate?.format("YYYY-MM-DD") || dayjs().format("YYYY-MM-DD"),
				end_date: endDate?.format("YYYY-MM-DD") || dayjs().format("YYYY-MM-DD"),
				force_refresh: forceRefresh,
			},
		}),
		enabled: !!selectedSymbol && !!startDate && !!endDate,
	});

	// 첫 번째 심볼 자동 선택
	React.useEffect(() => {
		if (availableSymbols && availableSymbols.length > 0 && !selectedSymbol) {
			setSelectedSymbol(availableSymbols[0]);
		}
	}, [availableSymbols, selectedSymbol]);

	const handleRefresh = () => {
		setForceRefresh(true);
		refetchMarketData().finally(() => {
			setForceRefresh(false);
		});
	};

	// 마켓 데이터를 차트 데이터로 변환
	const chartData: CandlestickData[] = React.useMemo(() => {
		if (!marketData || !Array.isArray(marketData)) return [];

		return (marketData as any[])
			.map((item) => ({
				time: dayjs(item.date).format("YYYY-MM-DD"),
				open: item.open,
				high: item.high,
				low: item.low,
				close: item.close,
				volume: item.volume || 0,
			}))
			.sort((a, b) => a.time.localeCompare(b.time));
	}, [marketData]);

	// 요약 데이터 생성
	const summaryData = React.useMemo(() => {
		if (!chartData.length) return null;

		const latestData = chartData[chartData.length - 1];
		const previousData = chartData[chartData.length - 2];

		if (!latestData || !previousData) return null;

		const change = latestData.close - previousData.close;
		const changePercent = (change / previousData.close) * 100;

		return {
			symbol: selectedSymbol,
			currentPrice: latestData.close,
			change,
			changePercent,
			volume: latestData.volume,
			high: latestData.high,
			low: latestData.low,
			open: latestData.open,
			previousClose: previousData.close,
		};
	}, [chartData, selectedSymbol]);

	const isLoading = symbolsLoading || dataLoading;

	return (
		<LocalizationProvider dateAdapter={AdapterDayjs}>
			<PageContainer
				title="마켓 데이터"
				breadcrumbs={[{ title: "데이터 관리" }, { title: "마켓 데이터" }]}
			>
				<Container maxWidth="xl">
					<Box display="flex" flexDirection="column" gap={3}>
						{/* 상단 요약 정보 */}
						<MarketDataSummaryCard data={summaryData} isLoading={isLoading} />

						<Box display="flex" gap={3}>
							{/* 좌측 컨트롤 패널 */}
							<Box width={300} flexShrink={0}>
								<MarketDataControls
									selectedSymbol={selectedSymbol}
									onSymbolChange={setSelectedSymbol}
									availableSymbols={(availableSymbols as string[]) || []}
									startDate={startDate}
									endDate={endDate}
									onStartDateChange={setStartDate}
									onEndDateChange={setEndDate}
									interval={interval}
									onIntervalChange={setInterval}
									onRefresh={handleRefresh}
									isLoading={isLoading}
								/>
							</Box>

							{/* 우측 차트 영역 */}
							<Box flexGrow={1}>
								{chartData.length > 0 ? (
									<Box display="flex" flexDirection="column" gap={3}>
										{/* 메인 차트 */}
										<Box>
											<Typography variant="h6" gutterBottom>
												{selectedSymbol} 주가 차트
											</Typography>
											<CandlestickChart
												data={chartData}
												symbol={selectedSymbol}
												height={500}
												showVolume={true}
											/>
										</Box>

										{/* 기술적 지표 */}
										<Box>
											<TechnicalIndicators
												data={chartData}
												symbol={selectedSymbol}
												height={300}
											/>
										</Box>
									</Box>
								) : (
									<Box
										display="flex"
										alignItems="center"
										justifyContent="center"
										height={500}
										border={1}
										borderColor="divider"
										borderRadius={1}
									>
										<Typography variant="h6" color="text.secondary">
											{isLoading
												? "차트 데이터를 로딩 중입니다..."
												: "종목을 선택하면 차트가 표시됩니다"}
										</Typography>
									</Box>
								)}
							</Box>
						</Box>
					</Box>
				</Container>
			</PageContainer>
		</LocalizationProvider>
	);
}
