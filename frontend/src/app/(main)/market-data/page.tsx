"use client";

import {
	Analytics as AnalyticsIcon,
	Assessment as AssessmentIcon,
	Refresh as RefreshIcon,
	ShowChart as ShowChartIcon,
	TrendingUp as TrendingUpIcon,
} from "@mui/icons-material";
import {
	Box,
	Button,
	Card,
	CardActions,
	CardContent,
	Container,
	Typography,
} from "@mui/material";
import { useRouter } from "next/navigation";

import PageContainer from "@/components/layout/PageContainer";

const marketDataFeatures = [
	{
		title: "실시간 차트",
		description: "TradingView 기반 캔들스틱 차트로 주가 데이터를 시각화합니다.",
		icon: <ShowChartIcon fontSize="large" color="primary" />,
		path: "/market-data/chart",
		buttonText: "차트 보기",
	},
	{
		title: "시장 분석",
		description: "시장 동향과 기술적 지표를 분석합니다.",
		icon: <AnalyticsIcon fontSize="large" color="secondary" />,
		path: "/market-data/analysis",
		buttonText: "분석 도구",
		disabled: false,
	},
	{
		title: "포트폴리오 성과",
		description: "투자 포트폴리오의 성과를 추적하고 분석합니다.",
		icon: <AssessmentIcon fontSize="large" color="success" />,
		path: "/market-data/portfolio",
		buttonText: "성과 분석",
		disabled: true,
	},
	{
		title: "알림 설정",
		description: "가격 변동 알림과 시장 이벤트를 설정합니다.",
		icon: <TrendingUpIcon fontSize="large" color="warning" />,
		path: "/market-data/alerts",
		buttonText: "알림 설정",
		disabled: true,
	},
];

export default function MarketDataPage() {
	const router = useRouter();

	const handleNavigate = (path: string) => {
		router.push(path);
	};

	return (
		<PageContainer
			title="마켓 데이터"
			breadcrumbs={[{ title: "데이터 관리" }, { title: "마켓 데이터" }]}
			actions={
				<Box display="flex" gap={2}>
					<Button
						variant="outlined"
						startIcon={<RefreshIcon />}
						onClick={() => window.location.reload()}
					>
						새로고침
					</Button>
					<Button
						variant="contained"
						startIcon={<ShowChartIcon />}
						onClick={() => handleNavigate("/market-data/chart")}
					>
						차트 보기
					</Button>
				</Box>
			}
		>
			<Container maxWidth="lg">
				<Box
					display="grid"
					gridTemplateColumns="repeat(auto-fit, minmax(300px, 1fr))"
					gap={3}
				>
					{marketDataFeatures.map((feature) => (
						<Card
							key={feature.title}
							sx={{
								height: "100%",
								display: "flex",
								flexDirection: "column",
								opacity: feature.disabled ? 0.6 : 1,
							}}
						>
							<CardContent sx={{ flexGrow: 1 }}>
								<Box display="flex" alignItems="center" gap={2} mb={2}>
									{feature.icon}
									<Typography variant="h6" component="h2">
										{feature.title}
									</Typography>
								</Box>
								<Typography variant="body2" color="text.secondary">
									{feature.description}
								</Typography>
								{feature.disabled && (
									<Typography
										variant="caption"
										color="warning.main"
										sx={{ display: "block", mt: 1 }}
									>
										* 곧 출시 예정
									</Typography>
								)}
							</CardContent>
							<CardActions>
								<Button
									variant="contained"
									onClick={() => handleNavigate(feature.path)}
									disabled={feature.disabled}
									fullWidth
								>
									{feature.buttonText}
								</Button>
							</CardActions>
						</Card>
					))}
				</Box>

				<Box mt={6}>
					<Card>
						<CardContent>
							<Typography variant="h6" gutterBottom>
								주요 기능
							</Typography>
							<Box display="flex" flexDirection="column" gap={2}>
								<Typography variant="body2">
									• <strong>실시간 데이터:</strong> Alpha Vantage API를 통한
									실시간 주식 데이터
								</Typography>
								<Typography variant="body2">
									• <strong>고성능 캐싱:</strong> DuckDB를 활용한 빠른 데이터
									조회
								</Typography>
								<Typography variant="body2">
									• <strong>인터랙티브 차트:</strong> TradingView Lightweight
									Charts 기반
								</Typography>
								<Typography variant="body2">
									• <strong>다양한 시간 범위:</strong> 일봉, 주봉, 월봉 데이터
									지원
								</Typography>
								<Typography variant="body2">
									• <strong>볼륨 분석:</strong> 거래량과 함께 종합적인 시장 분석
								</Typography>
							</Box>
						</CardContent>
					</Card>
				</Box>
			</Container>
		</PageContainer>
	);
}
