import { CheckCircle as CheckCircleIcon } from "@mui/icons-material";
import { Box, Card, CardContent, Chip, Stack, Typography } from "@mui/material";

/**
 * SystemStatus Component
 *
 * 시스템 상태 표시
 */
export function SystemStatus() {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          시스템 상태
        </Typography>
        <Stack spacing={2}>
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <Typography variant="body2" color="text.secondary">
              API 연결
            </Typography>
            <Chip
              label="정상"
              color="success"
              size="small"
              icon={<CheckCircleIcon />}
            />
          </Box>
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <Typography variant="body2" color="text.secondary">
              데이터베이스
            </Typography>
            <Chip
              label="정상"
              color="success"
              size="small"
              icon={<CheckCircleIcon />}
            />
          </Box>
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <Typography variant="body2" color="text.secondary">
              시장 데이터
            </Typography>
            <Chip
              label="정상"
              color="success"
              size="small"
              icon={<CheckCircleIcon />}
            />
          </Box>
        </Stack>
      </CardContent>
    </Card>
  );
}
