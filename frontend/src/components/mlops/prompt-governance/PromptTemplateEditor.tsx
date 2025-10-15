import { Card, CardContent, Typography } from "@mui/material";

/**
 * PromptTemplateEditor 컴포넌트
 * 프롬프트 템플릿 생성, 수정, 테스트
 */
export const PromptTemplateEditor = () => {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Prompt Template Editor
        </Typography>
        <Typography variant="body2" color="text.secondary">
          프롬프트 템플릿 에디터는 곧 추가됩니다.
        </Typography>
      </CardContent>
    </Card>
  );
};
