import { Card, CardContent, Typography } from "@mui/material";

/**
 * ABTestingPanel 컴포넌트
 * A/B 테스트 실험 비교
 */
export const ABTestingPanel = () => {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          A/B Testing Panel
        </Typography>
        <Typography variant="body2" color="text.secondary">
          A/B 테스트 패널은 곧 추가됩니다.
        </Typography>
      </CardContent>
    </Card>
  );
};
