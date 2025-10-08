"use client";

import { Alert, Box, CircularProgress, Grid, Typography } from "@mui/material";
import { useRouter } from "next/navigation";
import { useState } from "react";
import type { StrategyType, TemplateResponse } from "@/client/types.gen";
import PageContainer from "@/components/layout/PageContainer";
import StrategyCard from "@/components/strategies/StrategyCard";
import StrategyFilters from "@/components/strategies/StrategyFilters";
import { useTemplates } from "@/hooks/useTemplates";

export default function StrategyTemplatesPage() {
	const router = useRouter();

	// 필터 상태
	const [searchQuery, setSearchQuery] = useState("");
	const [selectedType, setSelectedType] = useState<StrategyType | "all">("all");
	const [selectedDifficulty, setSelectedDifficulty] = useState("all");
	const [selectedTags, setSelectedTags] = useState<string[]>([]);

	// 템플릿 데이터 조회
	const {
		templates,
		isLoading,
		error,
		createStrategyFromTemplate,
		isMutating,
	} = useTemplates();

	// 필터링된 템플릿
	const filteredTemplates = templates?.filter((template: TemplateResponse) => {
		// 검색어 필터
		if (
			searchQuery &&
			!template.name.toLowerCase().includes(searchQuery.toLowerCase()) &&
			!template.description.toLowerCase().includes(searchQuery.toLowerCase())
		) {
			return false;
		}

		// 타입 필터
		if (selectedType !== "all" && template.strategy_type !== selectedType) {
			return false;
		}

		// 태그 필터
		if (
			selectedTags.length > 0 &&
			!selectedTags.some((tag: any) => template.tags?.includes(tag))
		) {
			return false;
		}

		return true;
	});

	// 모든 태그 수집
	const allTags = Array.from(
		new Set(templates?.flatMap((template: any) => template.tags || [])),
	);

	const handleCreateFromTemplate = (template: any) => {
		const strategyName = `${template.name} (사본)`;

		createStrategyFromTemplate({
			templateId: template.id,
			strategyData: { name: strategyName },
		});
	};

	const handleViewDetails = (template: any) => {
		// 템플릿 상세 보기 모달이나 페이지로 이동
		router.push(`/strategies/templates/${template.id}`);
	};

	if (error) {
		return (
			<PageContainer
				title="Strategy Templates"
				breadcrumbs={[
					{ title: "Strategy Center" },
					{ title: "Strategies" },
					{ title: "Templates" },
				]}
			>
				<Alert severity="error">
					템플릿을 불러오는 중 오류가 발생했습니다: {(error as any)?.message}
				</Alert>
			</PageContainer>
		);
	}

	return (
		<PageContainer
			title="Strategy Templates"
			breadcrumbs={[
				{ title: "Strategy Center" },
				{ title: "Strategies" },
				{ title: "Templates" },
			]}
		>
			<Box sx={{ mb: 3 }}>
				<Typography variant="body1" color="text.secondary">
					검증된 전략 템플릿을 선택하여 나만의 전략을 만들어보세요.
				</Typography>
			</Box>

			<StrategyFilters
				searchQuery={searchQuery}
				onSearchChange={setSearchQuery}
				selectedType={selectedType}
				onTypeChange={setSelectedType}
				selectedDifficulty={selectedDifficulty}
				onDifficultyChange={setSelectedDifficulty}
				selectedTags={selectedTags}
				onTagsChange={setSelectedTags}
				availableTags={allTags}
				isTemplate={true}
			/>

			{isLoading ? (
				<Box sx={{ display: "flex", justifyContent: "center", py: 4 }}>
					<CircularProgress />
				</Box>
			) : (
				<>
					<Box
						sx={{
							display: "flex",
							justifyContent: "space-between",
							alignItems: "center",
							mb: 2,
						}}
					>
						<Typography variant="h6">
							템플릿 목록 ({filteredTemplates?.length}개)
						</Typography>
					</Box>

					{filteredTemplates?.length === 0 ? (
						<Alert severity="info">
							조건에 맞는 템플릿이 없습니다. 필터 조건을 변경해보세요.
						</Alert>
					) : (
						<Grid container spacing={3}>
							{filteredTemplates?.map((template: any) => (
								<Grid key={template.id} size={{ xs: 12, sm: 6, md: 4, lg: 3 }}>
									<StrategyCard
										strategy={{
											...template,
											is_active: true,
											is_template: true,
											created_by: null,
											// 템플릿에는 difficulty와 performance_rating 추가
											difficulty: "중급", // 실제로는 백엔드에서 가져와야 함
											performance_rating: 4, // 실제로는 백엔드에서 가져와야 함
										}}
										isTemplate={true}
										onClone={handleCreateFromTemplate}
										onViewDetails={handleViewDetails}
									/>
								</Grid>
							))}
						</Grid>
					)}
				</>
			)}

			{isMutating.createStrategyFromTemplate && (
				<Box sx={{ display: "flex", justifyContent: "center", py: 2 }}>
					<CircularProgress size={24} />
					<Typography variant="body2" sx={{ ml: 1 }}>
						전략을 생성하는 중...
					</Typography>
				</Box>
			)}
		</PageContainer>
	);
}
