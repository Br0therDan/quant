import { Card, CardContent, Typography } from "@mui/material";

/**
 * UsageAnalytics 컴포넌트
 * 프롬프트 사용 분석 (토큰 소비, 성능 메트릭)
 */
export const UsageAnalytics = () => {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Usage Analytics
        </Typography>
        <Typography variant="body2" color="text.secondary">
          사용 분석 기능은 곧 추가됩니다.
        </Typography>
      </CardContent>
    </Card>
  );
};
