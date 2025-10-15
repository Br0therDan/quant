import type { DataQualitySeverity } from "@/client/types.gen";
import { Box, Card, CardContent, Typography, useTheme } from "@mui/material";
import {
	Cell,
	Legend,
	Pie,
	PieChart,
	ResponsiveContainer,
	Tooltip,
} from "recharts";

interface SeverityData {
	severity: DataQualitySeverity;
	count: number;
	name: string;
	color: string;
}

interface SeverityPieChartProps {
	data: SeverityData[];
	title?: string;
}

// 커스텀 툴팁 (외부 컴포넌트)
function CustomTooltip({ active, payload }: any) {
	if (active && payload && payload.length) {
		const data = payload[0].payload as SeverityData & {
			color: string;
			totalCount: number;
		};
		const percentage = ((data.count / data.totalCount) * 100).toFixed(1);

		return (
			<Card sx={{ p: 1 }}>
				<Typography variant="body2" fontWeight="bold">
					{data.name}
				</Typography>
				<Typography variant="body2" color="text.secondary">
					{data.count}개 ({percentage}%)
				</Typography>
			</Card>
		);
	}
	return null;
}

// 커스텀 범례 (외부 컴포넌트)
function CustomLegend({ payload }: any) {
	return (
		<Box
			sx={{
				display: "flex",
				flexWrap: "wrap",
				justifyContent: "center",
				gap: 2,
				mt: 2,
			}}
		>
			{payload?.map((entry: any, index: number) => (
				<Box
					key={`legend-${index}`}
					sx={{ display: "flex", alignItems: "center", gap: 0.5 }}
				>
					<Box
						sx={{
							width: 12,
							height: 12,
							bgcolor: entry.color,
							borderRadius: "50%",
						}}
					/>
					<Typography variant="caption">
						{entry.value} ({(entry.payload as SeverityData).count})
					</Typography>
				</Box>
			))}
		</Box>
	);
}

/**
 * SeverityPieChart Component
 *
 * 심각도별 알림 비율 파이 차트
 *
 * Features:
 * - Recharts PieChart 사용
 * - 심각도별 색상 코딩 (CRITICAL 🔴, HIGH 🟠, MEDIUM 🟡, LOW 🔵, NORMAL 🟢)
 * - 범례 (Legend) 표시
 * - CustomTooltip (비율, 개수 표시)
 *
 * @example
 * ```tsx
 * import { SeverityPieChart } from "@/components/data-quality/SeverityPieChart";
 * import { useDataQuality } from "@/hooks/useDataQuality";
 *
 * function SeverityPage() {
 *   const { severityStats } = useDataQuality();
 *   return <SeverityPieChart data={severityStats} title="심각도별 알림 분포" />;
 * }
 * ```
 */
export function SeverityPieChart({
	data,
	title = "심각도별 알림 분포",
}: SeverityPieChartProps) {
	const theme = useTheme();

	// 심각도별 색상 맵핑
	const getSeverityColor = (severity: DataQualitySeverity): string => {
		const colors: Record<DataQualitySeverity, string> = {
			critical: theme.palette.error.dark,
			high: theme.palette.error.main,
			medium: theme.palette.warning.main,
			low: theme.palette.info.main,
			normal: theme.palette.success.main,
		};
		return colors[severity] || theme.palette.grey[500];
	};

	// 데이터 가공 (color 추가)
	const chartData = data
		.filter((item) => item.count > 0)
		.map((item) => ({
			...item,
			color: getSeverityColor(item.severity),
		}));

	// 전체 카운트
	const totalCount = chartData.reduce((acc, item) => acc + item.count, 0);

	// chartData에 totalCount 추가 (툴팁용)
	const chartDataWithTotal = chartData.map((item) => ({
		...item,
		totalCount,
	}));

	// 데이터가 없을 때
	if (!data || data.length === 0 || totalCount === 0) {
		return (
			<Card>
				<CardContent>
					<Typography variant="h6" gutterBottom>
						{title}
					</Typography>
					<Box
						sx={{
							display: "flex",
							justifyContent: "center",
							alignItems: "center",
							height: 300,
						}}
					>
						<Typography variant="body2" color="text.secondary">
							데이터가 없습니다.
						</Typography>
					</Box>
				</CardContent>
			</Card>
		);
	}

	return (
		<Card>
			<CardContent>
				<Typography variant="h6" gutterBottom>
					{title}
				</Typography>
				<Typography variant="body2" color="text.secondary" gutterBottom>
					총 {totalCount}개 알림
				</Typography>

				<ResponsiveContainer width="100%" height={300}>
					<PieChart>
						<Pie
							data={chartDataWithTotal}
							dataKey="count"
							nameKey="name"
							cx="50%"
							cy="50%"
							outerRadius={80}
							label={(entry: any) => {
								const percentage = (
									(entry.count / entry.totalCount) *
									100
								).toFixed(0);
								return `${percentage}%`;
							}}
							labelLine={true}
						>
							{chartDataWithTotal.map((entry, index) => (
								<Cell key={`cell-${index}`} fill={entry.color} />
							))}
						</Pie>
						<Tooltip content={<CustomTooltip />} />
						<Legend content={<CustomLegend />} />
					</PieChart>
				</ResponsiveContainer>
			</CardContent>
		</Card>
	);
}
