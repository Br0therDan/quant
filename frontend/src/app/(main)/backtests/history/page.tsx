"use client";

import PageContainer from "@/components/layout/PageContainer";
import { useBacktest } from "@/hooks/useBacktests";
import {
  Alert,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import Grid from "@mui/material/Unstable_Grid2";
import { useMemo } from "react";
import { backtestUtils } from "../utils";

export default function BacktestHistoryPage() {
  const {
    backtestList,
    isLoading: { backtestList: loading },
    isError: { backtestList: listError },
  } = useBacktest();

  const completedBacktests = useMemo(
    () => (backtestList?.backtests ?? []).filter((item) => backtestUtils.isCompleted(item.status)),
    [backtestList?.backtests],
  );

  return (
    <PageContainer
      title="백테스트 히스토리"
      breadcrumbs={[{ title: "백테스트" }, { title: "히스토리" }]}
    >
      <Grid container spacing={3}>
        <Grid xs={12}>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
            완료된 백테스트 목록과 핵심 성과를 확인할 수 있습니다.
          </Typography>
        </Grid>

        {listError && (
          <Grid xs={12}>
            <Alert severity="error">백테스트 기록을 불러오는 중 오류가 발생했습니다.</Alert>
          </Grid>
        )}

        <Grid xs={12}>
          <Paper sx={{ p: 2 }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>이름</TableCell>
                  <TableCell>기간</TableCell>
                  <TableCell>심볼</TableCell>
                  <TableCell align="right">총 수익률</TableCell>
                  <TableCell align="right">샤프 비율</TableCell>
                  <TableCell align="right">최대 낙폭</TableCell>
                  <TableCell align="right">승률</TableCell>
                  <TableCell>완료 시간</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {completedBacktests.map((backtest) => {
                  const performance = backtest.performance;
                  return (
                    <TableRow key={backtest.id} hover>
                      <TableCell>{backtest.name}</TableCell>
                      <TableCell>
                        {backtest.config
                          ? `${backtestUtils.formatDate(backtest.config.start_date)} ~ ${backtestUtils.formatDate(backtest.config.end_date)}`
                          : "-"}
                      </TableCell>
                      <TableCell>{backtestUtils.extractSymbols(backtest)}</TableCell>
                      <TableCell align="right">
                        {backtestUtils.formatPercentage(performance?.total_return)}
                      </TableCell>
                      <TableCell align="right">
                        {backtestUtils.formatNumber(performance?.sharpe_ratio)}
                      </TableCell>
                      <TableCell align="right">
                        {backtestUtils.formatPercentage(
                          performance?.max_drawdown
                            ? Math.abs(performance.max_drawdown)
                            : performance?.max_drawdown,
                        )}
                      </TableCell>
                      <TableCell align="right">
                        {backtestUtils.formatPercentage(performance?.win_rate)}
                      </TableCell>
                      <TableCell>{backtestUtils.formatDate(backtest.end_time)}</TableCell>
                    </TableRow>
                  );
                })}

                {!loading && completedBacktests.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={8} align="center">
                      완료된 백테스트가 없습니다.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </Paper>
        </Grid>
      </Grid>
    </PageContainer>
  );
}
