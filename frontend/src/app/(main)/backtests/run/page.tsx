"use client";

import PageContainer from "@/components/layout/PageContainer";

export default function RunBacktestPage() {
	return (
		<PageContainer
			title="Run Backtest"
			breadcrumbs={[
				{ title: "Backtesting" },
				{ title: "Backtests" },
				{ title: "Run" },
			]}
		>
			<div>
				<h1>백테스트 실행</h1>
				<p>워치리스트, 전략, 기간을 선택하여 백테스트를 실행할 수 있습니다.</p>
			</div>
		</PageContainer>
	);
}
