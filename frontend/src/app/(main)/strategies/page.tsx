"use client";

import PageContainer from "@/components/layout/PageContainer";

export default function StrategiesPage() {
	return (
		<PageContainer
			title="Strategies"
			breadcrumbs={[{ title: "Strategy Center" }, { title: "Strategies" }]}
		>
			<div>
				<h1>전략 관리</h1>
				<p>다양한 퀀트 전략을 설정하고 관리할 수 있습니다.</p>
			</div>
		</PageContainer>
	);
}
