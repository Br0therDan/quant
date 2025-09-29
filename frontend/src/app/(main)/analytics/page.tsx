"use client";

import PageContainer from "@/components/layout/PageContainer";

export default function AnalyticsPage() {
  return (
    <PageContainer title="Analytics" breadcrumbs={[{ title: "Analytics" }]}>
      <div>
        <h1>분석 결과</h1>
        <p>백테스트 결과를 직관적으로 이해하고 심층 분석할 수 있습니다.</p>
      </div>
    </PageContainer>
  );
}
