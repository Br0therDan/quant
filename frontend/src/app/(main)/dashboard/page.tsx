"use client";

import PageContainer from "@/components/layout/PageContainer";

export default function Dashboard() {
	return (
		<PageContainer title="Dashboard" breadcrumbs={[{ title: "Dashboard" }]}>
			<h1>대시보드 입니다.</h1>
		</PageContainer>
	);
}
