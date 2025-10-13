"use client";

import { Box, Button, ButtonGroup, useTheme } from "@mui/material";
import type { Dayjs } from "dayjs";
import dayjs from "dayjs";
import React from "react";

interface ChartFooterProps {
	onStartDateChange: (date: Dayjs | null) => void;
	onEndDateChange: (date: Dayjs | null) => void;
	onIntervalChange?: (interval: string) => void;
}

// 기간 레인지 옵션
const RANGES = [
	{ label: "1D", value: "1d", days: 1 },
	{ label: "5D", value: "5d", days: 5 },
	{ label: "1M", value: "1m", days: 30 },
	{ label: "3M", value: "3m", days: 90 },
	{ label: "6M", value: "6m", days: 180 },
	{ label: "YTD", value: "ytd", days: null },
	{ label: "1Y", value: "1y", days: 365 },
	{ label: "5Y", value: "5y", days: 1825 },
	{ label: "전체", value: "all", days: null },
];

export default function ChartFooter({
	onStartDateChange,
	onEndDateChange,
	onIntervalChange,
}: ChartFooterProps) {
	const theme = useTheme();
	const [selectedRange, setSelectedRange] = React.useState("1y");

	// 레인지 변경 핸들러
	const handleRangeChange = (rangeValue: string) => {
		const range = RANGES.find((r) => r.value === rangeValue);
		if (!range) return;

		const end = dayjs();
		let start: Dayjs;

		if (rangeValue === "ytd") {
			start = dayjs().startOf("year");
		} else if (rangeValue === "all") {
			start = dayjs().subtract(10, "year");
		} else if (range.days) {
			start = dayjs().subtract(range.days, "day");
		} else {
			start = dayjs().subtract(1, "year");
		}

		setSelectedRange(rangeValue);
		onStartDateChange(start);
		onEndDateChange(end);

		// 레인지에 따라 적절한 인터벌 자동 설정
		if (onIntervalChange) {
			if (range.days && range.days <= 5) {
				// 5일 이하: 분봉
				onIntervalChange("5min");
			} else {
				// 그 외: 일봉
				onIntervalChange("daily");
			}
		}
	};

	return (
		<Box
			sx={{
				display: "flex",
				alignItems: "center",
				justifyContent: "center",
				gap: 1,
				px: 2,
				py: 1.5,
				borderTop: `1px solid ${theme.palette.divider}`,
				backgroundColor: theme.palette.background.paper,
			}}
		>
			<ButtonGroup size="small" variant="outlined">
				{RANGES.map((range) => (
					<Button
						key={range.value}
						onClick={() => handleRangeChange(range.value)}
						variant={selectedRange === range.value ? "contained" : "outlined"}
						sx={{
							minWidth: 50,
							fontSize: "0.75rem",
							px: 1.5,
							textTransform: "none",
							fontWeight: selectedRange === range.value ? "bold" : "normal",
						}}
					>
						{range.label}
					</Button>
				))}
			</ButtonGroup>
		</Box>
	);
}
