"use client";

import { Add } from "@mui/icons-material";
import {
	Alert,
	Box,
	Button,
	CircularProgress,
	Dialog,
	DialogActions,
	DialogContent,
	DialogContentText,
	DialogTitle,
	Grid,
	Typography,
} from "@mui/material";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useState } from "react";
import type { StrategyType } from "@/client/types.gen";
import PageContainer from "@/components/layout/PageContainer";
import StrategyCard from "@/components/strategies/StrategyCard";
import StrategyFilters from "@/components/strategies/StrategyFilters";
import {
	strategiesDeleteStrategyMutation,
	strategiesExecuteStrategyMutation,
	useStrategiesQuery,
} from "@/services/strategiesQuery";

export default function MyStrategiesPage() {
	const router = useRouter();
	const queryClient = useQueryClient();

	// 필터 상태
	const [searchQuery, setSearchQuery] = useState("");
	const [selectedType, setSelectedType] = useState<StrategyType | "all">("all");
	const [selectedDifficulty, setSelectedDifficulty] = useState("all");
	const [selectedTags, setSelectedTags] = useState<string[]>([]);

	// 삭제 확인 다이얼로그
	const [deleteDialog, setDeleteDialog] = useState<{
		open: boolean;
		strategy?: any;
	}>({ open: false });

	// 내 전략 데이터 조회 (템플릿 제외)
	const {
		data: strategiesData,
		isLoading,
		error,
	} = useQuery(useStrategiesQuery({}));

	// 전략 삭제 뮤테이션
	const deleteStrategy = useMutation({
		...strategiesDeleteStrategyMutation(),
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["strategiesGetStrategies"] });
			setDeleteDialog({ open: false });
		},
	});

	// 전략 실행 뮤테이션
	const executeStrategy = useMutation({
		...strategiesExecuteStrategyMutation(),
		onSuccess: (data: any) => {
			// 백테스트 결과 페이지로 이동
			router.push(`/backtests/${data.backtest_id}`);
		},
	});

	const strategies = strategiesData?.strategies || [];

	// 필터링된 전략 (템플릿 제외)
	const filteredStrategies = strategies.filter((strategy: any) => {
		// 템플릿 제외
		if (strategy.is_template) {
			return false;
		}

		// 검색어 필터
		if (
			searchQuery &&
			!strategy.name.toLowerCase().includes(searchQuery.toLowerCase()) &&
			!strategy.description?.toLowerCase().includes(searchQuery.toLowerCase())
		) {
			return false;
		}

		// 타입 필터
		if (selectedType !== "all" && strategy.strategy_type !== selectedType) {
			return false;
		}

		// 태그 필터
		if (
			selectedTags.length > 0 &&
			!selectedTags.some((tag: any) => strategy.tags?.includes(tag))
		) {
			return false;
		}

		return true;
	});

	// 모든 태그 수집
	const allTags = Array.from(
		new Set(strategies.flatMap((strategy: any) => strategy.tags || [])),
	);

	const handleEdit = (strategy: any) => {
		router.push(`/strategies/${strategy.id}/edit`);
	};

	const handleClone = (strategy: any) => {
		router.push(`/strategies/create?clone=${strategy.id}`);
	};

	const handleDelete = (strategy: any) => {
		setDeleteDialog({ open: true, strategy });
	};

	const confirmDelete = () => {
		if (deleteDialog.strategy) {
			deleteStrategy.mutate({
				path: { strategy_id: deleteDialog.strategy.id },
			});
		}
	};

	const handleExecute = (strategy: any) => {
		// 기본 설정으로 전략 실행
		executeStrategy.mutate({
			path: { strategy_id: strategy.id },
			body: {
				symbol: "AAPL",
				market_data: {
					start_date: new Date(
						Date.now() - 365 * 24 * 60 * 60 * 1000,
					).toISOString(),
					end_date: new Date().toISOString(),
				},
			},
		});
	};

	const handleViewPerformance = (strategy: any) => {
		router.push(`/strategies/${strategy.id}/performance`);
	};

	const handleCreateNew = () => {
		router.push("/strategies/create");
	};

	if (error) {
		return (
			<PageContainer
				title="My Strategies"
				breadcrumbs={[
					{ title: "Strategy Center" },
					{ title: "Strategies" },
					{ title: "My Strategies" },
				]}
			>
				<Alert severity="error">
					전략을 불러오는 중 오류가 발생했습니다: {(error as any)?.message}
				</Alert>
			</PageContainer>
		);
	}

	return (
		<PageContainer
			title="My Strategies"
			breadcrumbs={[
				{ title: "Strategy Center" },
				{ title: "Strategies" },
				{ title: "My Strategies" },
			]}
			actions={[
				<Button
					key="create"
					variant="contained"
					startIcon={<Add />}
					onClick={handleCreateNew}
				>
					새 전략 만들기
				</Button>,
			]}
		>
			<Box sx={{ mb: 3 }}>
				<Typography variant="body1" color="text.secondary">
					생성한 전략을 관리하고 백테스트를 실행할 수 있습니다.
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
				isTemplate={false}
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
							내 전략 ({filteredStrategies.length}개)
						</Typography>
					</Box>

					{filteredStrategies.length === 0 ? (
						<Alert severity="info">
							{strategies.length === 0
								? "아직 생성한 전략이 없습니다. 새 전략을 만들어보세요."
								: "조건에 맞는 전략이 없습니다. 필터 조건을 변경해보세요."}
						</Alert>
					) : (
						<Grid container spacing={3}>
							{filteredStrategies.map((strategy: any) => (
								<Grid key={strategy.id} size={{ xs: 12, sm: 6, md: 4, lg: 3 }}>
									<StrategyCard
										strategy={strategy}
										isTemplate={false}
										onEdit={handleEdit}
										onClone={handleClone}
										onDelete={handleDelete}
										onExecute={handleExecute}
										onViewPerformance={handleViewPerformance}
									/>
								</Grid>
							))}
						</Grid>
					)}
				</>
			)}

			{/* 삭제 확인 다이얼로그 */}
			<Dialog
				open={deleteDialog.open}
				onClose={() => setDeleteDialog({ open: false })}
			>
				<DialogTitle>전략 삭제</DialogTitle>
				<DialogContent>
					<DialogContentText>
						"{deleteDialog.strategy?.name}" 전략을 삭제하시겠습니까? 이 작업은
						되돌릴 수 없습니다.
					</DialogContentText>
				</DialogContent>
				<DialogActions>
					<Button onClick={() => setDeleteDialog({ open: false })}>취소</Button>
					<Button
						onClick={confirmDelete}
						color="error"
						variant="contained"
						disabled={deleteStrategy.isPending}
					>
						{deleteStrategy.isPending ? "삭제 중..." : "삭제"}
					</Button>
				</DialogActions>
			</Dialog>

			{/* 로딩 상태 */}
			{(executeStrategy.isPending || deleteStrategy.isPending) && (
				<Box sx={{ display: "flex", justifyContent: "center", py: 2 }}>
					<CircularProgress size={24} />
					<Typography variant="body2" sx={{ ml: 1 }}>
						{executeStrategy.isPending
							? "전략을 실행하는 중..."
							: "전략을 삭제하는 중..."}
					</Typography>
				</Box>
			)}
		</PageContainer>
	);
}
