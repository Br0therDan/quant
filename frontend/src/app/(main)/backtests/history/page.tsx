"use client";

import PageContainer from "@/components/layout/PageContainer";

export default function BacktestHistoryPage() {
  return (
    <PageContainer
      title="Backtest History"
      breadcrumbs={[
        { title: "Backtesting" },
        { title: "Backtests" },
        { title: "History" },
      ]}
    >
      <div>
        <h1>백테스트 히스토리</h1>
        <p>
          과거 실행한 모든 백테스트를 체계적으로 관리하고 결과를 비교할 수
          있습니다.
        </p>
      </div>
    </PageContainer>
  );
}
