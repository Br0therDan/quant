/**
 * Quick Actions - 신규 사용자 온보딩 가이드
 *
 * Epic 1: Story 1.1 - 4단계 프로세스 가이드
 */
"use client";

import {
	Assessment as AnalysisIcon,
	PlayArrow as RunIcon,
	Storage as StorageIcon,
	TrendingUp as StrategyIcon,
} from "@mui/icons-material";
import {
	Button,
	Card,
	CardContent,
	List,
	ListItem,
	ListItemIcon,
	ListItemText,
	Typography,
} from "@mui/material";
import { useRouter } from "next/navigation";

export default function QuickActions() {
	const router = useRouter();

	const steps = [
		{
			icon: <StorageIcon />,
			title: "데이터 수집",
			description: "관심 종목 데이터를 수집하세요",
			action: () => router.push("/market-data"),
			color: "#1976d2",
		},
		{
			icon: <StrategyIcon />,
			title: "전략 설계",
			description: "백테스트 전략을 선택하고 설정하세요",
			action: () => router.push("/strategies"),
			color: "#2e7d32",
		},
		{
			icon: <RunIcon />,
			title: "백테스트 실행",
			description: "전략을 백테스트하여 성과를 검증하세요",
			action: () => router.push("/backtests"),
			color: "#ed6c02",
		},
		{
			icon: <AnalysisIcon />,
			title: "결과 분석",
			description: "성과 지표를 분석하고 최적화하세요",
			action: () => router.push("/backtests"),
			color: "#9c27b0",
		},
	];

	return (
		<Card>
			<CardContent>
				<Typography variant="h6" gutterBottom>
					빠른 시작 가이드
				</Typography>
				<List>
					{steps.map((step, index) => (
						<ListItem
							key={index}
							sx={{
								borderRadius: 1,
								mb: 1,
								"&:hover": {
									bgcolor: "action.hover",
								},
							}}
						>
							<ListItemIcon sx={{ color: step.color }}>
								{step.icon}
							</ListItemIcon>
							<ListItemText
								primary={
									<Typography variant="subtitle1" fontWeight="medium">
										{index + 1}. {step.title}
									</Typography>
								}
								secondary={step.description}
							/>
							<Button size="small" onClick={step.action} sx={{ ml: 2 }}>
								시작
							</Button>
						</ListItem>
					))}
				</List>
			</CardContent>
		</Card>
	);
}
