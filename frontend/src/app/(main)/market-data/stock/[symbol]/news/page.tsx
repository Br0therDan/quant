"use client";

import {
	useIntelligenceNews,
	useIntelligenceSentiment,
} from "@/hooks/useIntelligence";
import {
	Article as ArticleIcon,
	TrendingDown as NegativeIcon,
	TrendingFlat as NeutralIcon,
	TrendingUp as PositiveIcon,
} from "@mui/icons-material";
import {
	Box,
	Card,
	CardContent,
	Chip,
	Container,
	Grid,
	Link,
	Paper,
	Typography,
} from "@mui/material";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import { useParams } from "next/navigation";

import LoadingSpinner from "@/components/common/LoadingSpinner";

dayjs.extend(relativeTime);

export default function SymbolNewsPage() {
	const params = useParams();
	const symbol = (params.symbol as string)?.toUpperCase();

	// 데이터 fetching
	const { data: newsData, isLoading: newsLoading } =
		useIntelligenceNews(symbol);
	const { data: sentimentData, isLoading: sentimentLoading } =
		useIntelligenceSentiment(symbol);

	const news = Array.isArray(newsData?.data) ? newsData.data : [];
	const sentiment = sentimentData?.data as any;

	return (
		<Container maxWidth="xl" sx={{ py: 4 }}>
			<Box display="flex" flexDirection="column" gap={3}>
				{/* 헤더 */}
				<Box>
					<Typography variant="h4" gutterBottom>
						{symbol} - News & Analysis
					</Typography>
					<Typography variant="body2" color="text.secondary">
						Latest news and market sentiment analysis
					</Typography>
				</Box>

				{/* 감정 분석 요약 */}
				{sentimentLoading ? (
					<LoadingSpinner
						variant="skeleton"
						height={150}
						message="감정 분석 로딩 중..."
					/>
				) : sentiment ? (
					<Paper elevation={1} sx={{ p: 3 }}>
						<Typography variant="h6" gutterBottom>
							Market Sentiment
						</Typography>
						<Grid container spacing={2}>
							<Grid size={{ xs: 12, sm: 4 }}>
								<Box textAlign="center">
									<PositiveIcon color="success" sx={{ fontSize: 40 }} />
									<Typography variant="h4" color="success.main">
										{sentiment.bullish_percent
											? `${(Number(sentiment.bullish_percent) * 100).toFixed(
													1,
												)}%`
											: "N/A"}
									</Typography>
									<Typography variant="body2" color="text.secondary">
										Bullish
									</Typography>
								</Box>
							</Grid>
							<Grid size={{ xs: 12, sm: 4 }}>
								<Box textAlign="center">
									<NeutralIcon color="warning" sx={{ fontSize: 40 }} />
									<Typography variant="h4" color="warning.main">
										{sentiment.neutral_percent
											? `${(Number(sentiment.neutral_percent) * 100).toFixed(
													1,
												)}%`
											: "N/A"}
									</Typography>
									<Typography variant="body2" color="text.secondary">
										Neutral
									</Typography>
								</Box>
							</Grid>
							<Grid size={{ xs: 12, sm: 4 }}>
								<Box textAlign="center">
									<NegativeIcon color="error" sx={{ fontSize: 40 }} />
									<Typography variant="h4" color="error.main">
										{sentiment.bearish_percent
											? `${(Number(sentiment.bearish_percent) * 100).toFixed(
													1,
												)}%`
											: "N/A"}
									</Typography>
									<Typography variant="body2" color="text.secondary">
										Bearish
									</Typography>
								</Box>
							</Grid>
						</Grid>
					</Paper>
				) : null}

				{/* 뉴스 리스트 */}
				<Box>
					<Typography variant="h6" gutterBottom>
						Latest News
					</Typography>
					{newsLoading ? (
						<LoadingSpinner
							variant="skeleton"
							height={400}
							message="뉴스 기사 로딩 중..."
						/>
					) : news.length > 0 ? (
						<Grid container spacing={2}>
							{news.map((article: any, index: number) => (
								<Grid size={12} key={index}>
									<NewsCard article={article} />
								</Grid>
							))}
						</Grid>
					) : (
						<Card>
							<CardContent>
								<Box
									display="flex"
									flexDirection="column"
									alignItems="center"
									gap={2}
									py={4}
								>
									<ArticleIcon sx={{ fontSize: 60, color: "text.disabled" }} />
									<Typography color="text.secondary">
										뉴스 데이터를 불러올 수 없습니다
									</Typography>
								</Box>
							</CardContent>
						</Card>
					)}
				</Box>
			</Box>
		</Container>
	);
}

// 뉴스 카드 컴포넌트
function NewsCard({ article }: { article: any }) {
	const sentiment = article.overall_sentiment_label || "Neutral";
	const sentimentScore = article.overall_sentiment_score
		? Number(article.overall_sentiment_score)
		: 0;

	const getSentimentColor = () => {
		if (sentiment === "Bullish" || sentimentScore > 0.15) return "success";
		if (sentiment === "Bearish" || sentimentScore < -0.15) return "error";
		return "default";
	};

	const getSentimentIcon = () => {
		if (sentiment === "Bullish" || sentimentScore > 0.15)
			return <PositiveIcon fontSize="small" />;
		if (sentiment === "Bearish" || sentimentScore < -0.15)
			return <NegativeIcon fontSize="small" />;
		return <NeutralIcon fontSize="small" />;
	};

	return (
		<Card>
			<CardContent>
				<Box display="flex" flexDirection="column" gap={2}>
					{/* 헤더 */}
					<Box
						display="flex"
						justifyContent="space-between"
						alignItems="flex-start"
						gap={2}
					>
						<Box flex={1}>
							<Link
								href={article.url}
								target="_blank"
								rel="noopener noreferrer"
								sx={{ textDecoration: "none" }}
							>
								<Typography
									variant="h6"
									gutterBottom
									sx={{ "&:hover": { color: "primary.main" } }}
								>
									{article.title}
								</Typography>
							</Link>
							<Box display="flex" gap={1} alignItems="center" flexWrap="wrap">
								<Typography variant="caption" color="text.secondary">
									{article.source || "Unknown Source"}
								</Typography>
								<Typography variant="caption" color="text.secondary">
									•
								</Typography>
								<Typography variant="caption" color="text.secondary">
									{article.time_published
										? dayjs(article.time_published).fromNow()
										: "Unknown Date"}
								</Typography>
							</Box>
						</Box>
						<Chip
							label={sentiment}
							color={getSentimentColor()}
							size="small"
							icon={getSentimentIcon()}
						/>
					</Box>

					{/* 요약 */}
					{article.summary && (
						<Typography variant="body2" color="text.secondary">
							{article.summary}
						</Typography>
					)}

					{/* 저자 및 카테고리 */}
					<Box display="flex" gap={1} flexWrap="wrap">
						{article.authors && article.authors.length > 0 && (
							<Chip
								label={`By ${article.authors[0]}`}
								size="small"
								variant="outlined"
							/>
						)}
						{article.category_within_source && (
							<Chip
								label={article.category_within_source}
								size="small"
								variant="outlined"
							/>
						)}
					</Box>
				</Box>
			</CardContent>
		</Card>
	);
}
