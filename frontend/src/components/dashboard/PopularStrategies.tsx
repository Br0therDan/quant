import { TrendingUp as TrendingUpIcon } from "@mui/icons-material";
import { Box, Card, CardContent, Chip, Grid, Typography } from "@mui/material";

/**
 * PopularStrategies Component
 *
 * 인기 전략 추천
 */
export function PopularStrategies() {
  const strategies = [
    { name: "BB + HARVARD-RSI", winRate: 68.5, avgReturn: 12.3 },
    { name: "Golden Cross", winRate: 65.2, avgReturn: 10.8 },
    { name: "Mean Reversion", winRate: 62.1, avgReturn: 9.5 },
  ];

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          인기 전략
        </Typography>
        <Grid container spacing={2}>
          {strategies.map((strategy, index) => (
            <Grid key={index} size={{ xs: 12, sm: 6, md: 4 }}>
              <Card variant="outlined">
                <CardContent>
                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      gap: 1,
                      mb: 1,
                    }}
                  >
                    <TrendingUpIcon color="primary" />
                    <Typography variant="subtitle2">{strategy.name}</Typography>
                  </Box>
                  <Box sx={{ display: "flex", gap: 1 }}>
                    <Chip
                      label={`승률: ${strategy.winRate}%`}
                      size="small"
                      color="success"
                    />
                    <Chip
                      label={`수익: ${strategy.avgReturn}%`}
                      size="small"
                      color="primary"
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </CardContent>
    </Card>
  );
}
