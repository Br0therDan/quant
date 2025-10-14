import type { OptimizationResult } from "@/client/types.gen";
import {
  PlayArrow as PlayArrowIcon,
  Save as SaveIcon,
  TrendingUp as TrendingUpIcon,
} from "@mui/icons-material";
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Grid,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";

interface BestParamsPanelProps {
  result: OptimizationResult;
  onRunBacktest?: (params: { [key: string]: unknown }) => void;
  onSaveStrategy?: (params: { [key: string]: unknown }) => void;
  showActions?: boolean;
}

/**
 * BestParamsPanel Component
 *
 * Displays optimization results with:
 * - Best parameter values in a table
 * - Objective value (best_value)
 * - Trial number of best result
 * - Actions: Run backtest, Save strategy
 *
 * @example
 * ```tsx
 * <BestParamsPanel
 *   result={optimizationResult}
 *   onRunBacktest={(params) => console.log("Run backtest with:", params)}
 *   onSaveStrategy={(params) => console.log("Save strategy with:", params)}
 *   showActions
 * />
 * ```
 */
export function BestParamsPanel({
  result,
  onRunBacktest,
  onSaveStrategy,
  showActions = true,
}: BestParamsPanelProps) {
  const handleRunBacktest = () => {
    if (onRunBacktest && result.best_params) {
      onRunBacktest(result.best_params);
    }
  };

  const handleSaveStrategy = () => {
    if (onSaveStrategy && result.best_params) {
      onSaveStrategy(result.best_params);
    }
  };

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: "flex", alignItems: "center", mb: 3 }}>
          <TrendingUpIcon color="success" sx={{ mr: 1 }} />
          <Typography variant="h6">최적 파라미터</Typography>
        </Box>

        {/* Optimization Info */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid size={12}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="caption" color="text.secondary">
                  스터디 이름
                </Typography>
                <Typography variant="body1" fontWeight="bold">
                  {result.study_name}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid size={6}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="caption" color="text.secondary">
                  전략
                </Typography>
                <Typography variant="body1">{result.strategy_name}</Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid size={6}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="caption" color="text.secondary">
                  심볼
                </Typography>
                <Typography variant="body1">{result.symbol}</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Best Value */}
        <Card
          variant="outlined"
          sx={{
            mb: 3,
            bgcolor: "success.light",
            borderColor: "success.main",
          }}
        >
          <CardContent>
            <Typography variant="caption" color="text.secondary">
              최적 값 (Objective Value)
            </Typography>
            <Typography variant="h3" color="success.dark">
              {typeof result.best_value === "number"
                ? result.best_value.toFixed(4)
                : result.best_value}
            </Typography>

            <Box sx={{ mt: 2, display: "flex", gap: 1 }}>
              <Chip
                label={`Trial #${result.best_trial_number}`}
                size="small"
                color="success"
              />
              <Chip
                label={`${result.trials_completed} trials completed`}
                size="small"
                variant="outlined"
              />
            </Box>
          </CardContent>
        </Card>

        {/* Parameters Table */}
        {result.best_params && Object.keys(result.best_params).length > 0 ? (
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" gutterBottom>
              파라미터 값
            </Typography>

            <TableContainer component={Paper} variant="outlined">
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>
                      <strong>파라미터</strong>
                    </TableCell>
                    <TableCell align="right">
                      <strong>최적 값</strong>
                    </TableCell>
                    <TableCell align="right">
                      <strong>타입</strong>
                    </TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {Object.entries(result.best_params).map(([key, value]) => (
                    <TableRow
                      key={key}
                      sx={{
                        "&:last-child td, &:last-child th": { border: 0 },
                      }}
                    >
                      <TableCell component="th" scope="row">
                        {key}
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" fontWeight="bold">
                          {typeof value === "number"
                            ? value.toFixed(4)
                            : String(value)}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Chip
                          label={typeof value}
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        ) : (
          <Typography variant="body2" color="text.secondary" align="center">
            파라미터 데이터가 없습니다
          </Typography>
        )}

        {/* Action Buttons */}
        {showActions && (
          <Box sx={{ display: "flex", gap: 2 }}>
            {onRunBacktest && (
              <Button
                variant="contained"
                color="primary"
                startIcon={<PlayArrowIcon />}
                onClick={handleRunBacktest}
                fullWidth
              >
                백테스트 실행
              </Button>
            )}

            {onSaveStrategy && (
              <Button
                variant="outlined"
                color="primary"
                startIcon={<SaveIcon />}
                onClick={handleSaveStrategy}
                fullWidth
              >
                전략 저장
              </Button>
            )}
          </Box>
        )}

        {/* Additional Info */}
        <Box sx={{ mt: 3, p: 2, bgcolor: "action.hover", borderRadius: 1 }}>
          <Typography variant="caption" color="text.secondary" display="block">
            💡 최적 파라미터는 과거 데이터 기반으로 계산되었습니다. 실전 적용 전
            충분한 검증이 필요합니다.
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
}
