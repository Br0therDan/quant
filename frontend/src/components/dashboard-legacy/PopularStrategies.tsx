/**
 * Popular Strategies - 인기 전략 추천
 *
 * Epic 1: Story 1.1 - 템플릿 기반 전략 추천
 */
"use client";

import { TrendingUp } from "@mui/icons-material";
import {
	Box,
	Button,
	Card,
	CardContent,
	List,
	ListItem,
	ListItemText,
	Typography,
} from "@mui/material";
import { useRouter } from "next/navigation";

export default function PopularStrategies() {
	const router = useRouter();

	const strategies = [
		{
			name: "SMA Crossover",
			description:
				"이동평균선 교차 전략 - 단기/장기 이동평균 교차 신호 기반 매매",
			successRate: 65,
		},
		{
			name: "RSI Mean Reversion",
			description: "RSI 평균회귀 전략 - 과매수/과매도 구간에서 반대 방향 진입",
			successRate: 58,
		},
		{
			name: "Momentum",
			description: "모멘텀 전략 - 가격 변화율 기반 추세 추종",
			successRate: 62,
		},
	];

	const handleCreateBacktest = (strategyName: string) => {
		// 전략 선택하여 백테스트 생성 페이지로 이동
		router.push(`/backtests/new?strategy=${encodeURIComponent(strategyName)}`);
	};

	return (
		<Card>
			<CardContent>
				<Box
					display="flex"
					justifyContent="space-between"
					alignItems="center"
					mb={2}
				>
					<Typography variant="h6">인기 전략</Typography>
					<TrendingUp color="primary" />
				</Box>
				<List>
					{strategies.map((strategy, index) => (
						<ListItem
							key={index}
							sx={{
								borderRadius: 1,
								mb: 1,
								flexDirection: "column",
								alignItems: "flex-start",
								"&:hover": {
									bgcolor: "action.hover",
								},
							}}
						>
							<ListItemText
								primary={
									<Typography variant="subtitle1" fontWeight="medium">
										{strategy.name}
									</Typography>
								}
								secondary={
									<Box>
										<Typography variant="body2" color="text.secondary">
											{strategy.description}
										</Typography>
										<Typography
											variant="caption"
											color="success.main"
											sx={{ mt: 0.5 }}
										>
											평균 성공률: {strategy.successRate}%
										</Typography>
									</Box>
								}
							/>
							<Button
								size="small"
								variant="outlined"
								onClick={() => handleCreateBacktest(strategy.name)}
								sx={{ mt: 1 }}
							>
								이 전략으로 백테스트 시작
							</Button>
						</ListItem>
					))}
				</List>
			</CardContent>
		</Card>
	);
}
