import { Card, CardContent, Typography } from "@mui/material";

/**
 * VersionControl 컴포넌트
 * 프롬프트 버전 히스토리 및 롤백
 */
export const VersionControl = () => {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Version Control
        </Typography>
        <Typography variant="body2" color="text.secondary">
          버전 제어 기능은 곧 추가됩니다.
        </Typography>
      </CardContent>
    </Card>
  );
};
