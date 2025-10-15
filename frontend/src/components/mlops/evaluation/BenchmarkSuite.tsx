import { Card, CardContent, Typography } from "@mui/material";

/**
 * BenchmarkSuite 컴포넌트
 * 벤치마크 성능 비교
 */
export const BenchmarkSuite = () => {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Benchmark Suite
        </Typography>
        <Typography variant="body2" color="text.secondary">
          벤치마크 스위트는 곧 추가됩니다.
        </Typography>
      </CardContent>
    </Card>
  );
};
