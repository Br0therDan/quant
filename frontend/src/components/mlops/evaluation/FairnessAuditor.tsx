import { Card, CardContent, Typography } from "@mui/material";

/**
 * FairnessAuditor 컴포넌트
 * 공정성 감사 및 Bias 감지
 */
export const FairnessAuditor = () => {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Fairness Auditor
        </Typography>
        <Typography variant="body2" color="text.secondary">
          공정성 감사 기능은 곧 추가됩니다.
        </Typography>
      </CardContent>
    </Card>
  );
};
