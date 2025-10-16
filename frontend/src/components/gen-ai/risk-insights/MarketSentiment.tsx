import { TrendingDown, TrendingUp } from "@mui/icons-material";
import { Box, Card, CardContent, Chip, Typography } from "@mui/material";

/**
 * MarketSentiment 컴포넌트
 * 시장 센티먼트 분석
 */
export const MarketSentiment = () => {
	const sentiments = [
		{ symbol: "AAPL", sentiment: "Bullish", confidence: 85, change: 5.2 },
		{ symbol: "GOOGL", sentiment: "Neutral", confidence: 60, change: -1.3 },
		{ symbol: "MSFT", sentiment: "Bullish", confidence: 78, change: 3.8 },
		{ symbol: "TSLA", sentiment: "Bearish", confidence: 72, change: -8.5 },
	];

	const getSentimentColor = (sentiment: string) => {
		switch (sentiment) {
			case "Bullish":
				return "success";
			case "Bearish":
				return "error";
			case "Neutral":
				return "default";
			default:
				return "default";
		}
	};

	return (
		<Card>
			<CardContent>
				<Typography variant="h6" gutterBottom>
					Market Sentiment Analysis
				</Typography>

				<Box sx={{ display: "flex", flexDirection: "column", gap: 2, mt: 2 }}>
					{sentiments.map((item) => (
						<Box
							key={item.symbol}
							sx={{
								p: 2,
								border: 1,
								borderColor: "divider",
								borderRadius: 1,
								display: "flex",
								justifyContent: "space-between",
								alignItems: "center",
							}}
						>
							<Box>
								<Typography variant="h6">{item.symbol}</Typography>
								<Typography variant="caption" color="text.secondary">
									Confidence: {item.confidence}%
								</Typography>
							</Box>
							<Box sx={{ display: "flex", gap: 2, alignItems: "center" }}>
								<Chip
									label={item.sentiment}
									color={getSentimentColor(item.sentiment) as any}
								/>
								<Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
									{item.change > 0 ? (
										<TrendingUp color="success" />
									) : (
										<TrendingDown color="error" />
									)}
									<Typography
										variant="body2"
										color={item.change > 0 ? "success.main" : "error.main"}
									>
										{item.change > 0 ? "+" : ""}
										{item.change}%
									</Typography>
								</Box>
							</Box>
						</Box>
					))}
				</Box>
			</CardContent>
		</Card>
	);
};
