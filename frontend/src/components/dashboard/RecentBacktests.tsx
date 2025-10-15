import { Box, Card, CardContent, Typography } from "@mui/material";

/**
 * RecentBacktests Component
 *
 * 최근 백테스트 목록
 */
export function RecentBacktests() {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          최근 백테스트
        </Typography>
        <Box
          sx={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            minHeight: 200,
          }}
        >
          <Typography variant="body2" color="text.secondary">
            최근 백테스트가 없습니다.
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
}
