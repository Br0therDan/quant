/**
 * MLModelList Component
 *
 * Phase 1 Day 4: ML Model List View
 * - Material-UI Grid layout
 * - Model cards (version, accuracy, creation date)
 * - Sort/Filter (latest, accuracy)
 * - Empty state
 */

"use client";

import { useMLModel } from "@/hooks/useMLModel";
import type { SelectChangeEvent } from "@mui/material";
import {
	Alert,
	Box,
	Button,
	Card,
	CardActions,
	CardContent,
	Chip,
	CircularProgress,
	FormControl,
	InputLabel,
	MenuItem,
	Select,
	Stack,
	Typography,
} from "@mui/material";
import Grid from "@mui/material/Grid";
import { useMemo, useState } from "react";
import { MLModelDetail } from "./MLModelDetail";

type SortOption = "latest" | "accuracy" | "version";

export const MLModelList = () => {
	const { modelList, isLoading, error } = useMLModel();
	const [sortBy, setSortBy] = useState<SortOption>("latest");
	const [selectedVersion, setSelectedVersion] = useState<string | null>(null);

	// Sort models based on selected option
	const sortedModels = useMemo(() => {
		if (!modelList?.models) return [];

		const models = [...modelList.models];
		switch (sortBy) {
			case "latest":
				return models.sort(
					(a, b) =>
						new Date(b.created_at || 0).getTime() -
						new Date(a.created_at || 0).getTime(),
				);
			case "accuracy":
				return models.sort(
					(a, b) => (b.metrics?.accuracy || 0) - (a.metrics?.accuracy || 0),
				);
			case "version":
				return models.sort((a, b) =>
					(a.version || "").localeCompare(b.version || ""),
				);
			default:
				return models;
		}
	}, [modelList, sortBy]);

	const handleSortChange = (event: SelectChangeEvent<SortOption>) => {
		setSortBy(event.target.value as SortOption);
	};

	const handleViewDetail = (version: string) => {
		setSelectedVersion(version);
	};

	// Loading state
	if (isLoading) {
		return (
			<Box
				sx={{
					display: "flex",
					justifyContent: "center",
					alignItems: "center",
					minHeight: 400,
				}}
			>
				<CircularProgress />
			</Box>
		);
	}

	// Error state
	if (error) {
		return <Alert severity="error">모델 목록 조회 실패: {error.message}</Alert>;
	}

	// Empty state
	if (!sortedModels || sortedModels.length === 0) {
		return (
			<Box sx={{ textAlign: "center", py: 8 }}>
				<Typography variant="h6" color="text.secondary" gutterBottom>
					학습된 ML 모델이 없습니다
				</Typography>
				<Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
					새로운 모델을 학습하여 백테스트에 활용하세요
				</Typography>
				<Button variant="contained" color="primary">
					모델 학습 시작
				</Button>
			</Box>
		);
	}

	return (
		<Box sx={{ flexGrow: 1 }}>
			{/* Header */}
			<Box
				sx={{
					display: "flex",
					justifyContent: "space-between",
					alignItems: "center",
					mb: 3,
				}}
			>
				<Typography variant="h5" component="h2">
					ML 모델 목록
				</Typography>

				{/* Sort Controls */}
				<FormControl size="small" sx={{ minWidth: 150 }}>
					<InputLabel id="sort-label">정렬 기준</InputLabel>
					<Select
						labelId="sort-label"
						value={sortBy}
						label="정렬 기준"
						onChange={handleSortChange}
					>
						<MenuItem value="latest">최신순</MenuItem>
						<MenuItem value="accuracy">정확도순</MenuItem>
						<MenuItem value="version">버전순</MenuItem>
					</Select>
				</FormControl>
			</Box>

			{/* Model Grid */}
			<Grid container spacing={3}>
				{sortedModels.map((model) => (
					<Grid size={{ xs: 12, sm: 6, md: 4 }} key={model.version}>
						<Card
							sx={{
								height: "100%",
								display: "flex",
								flexDirection: "column",
								transition: "transform 0.2s, box-shadow 0.2s",
								"&:hover": {
									transform: "translateY(-4px)",
									boxShadow: 4,
								},
							}}
						>
							<CardContent sx={{ flexGrow: 1 }}>
								{/* Version Badge */}
								<Box
									sx={{
										display: "flex",
										justifyContent: "space-between",
										alignItems: "center",
										mb: 2,
									}}
								>
									<Chip label={model.version} color="primary" size="small" />
									<Typography variant="caption" color="text.secondary">
										{new Date(model.created_at || "").toLocaleDateString(
											"ko-KR",
										)}
									</Typography>
								</Box>

								{/* Accuracy */}
								<Stack spacing={1}>
									<Box>
										<Typography variant="body2" color="text.secondary">
											정확도
										</Typography>
										<Typography variant="h4" color="primary.main">
											{((model.metrics?.accuracy || 0) * 100).toFixed(2)}%
										</Typography>
									</Box>

									{/* Additional Metrics */}
									{model.metrics && (
										<Box>
											<Typography
												variant="caption"
												color="text.secondary"
												display="block"
											>
												Precision:{" "}
												{((model.metrics.precision || 0) * 100).toFixed(1)}%
											</Typography>
											<Typography
												variant="caption"
												color="text.secondary"
												display="block"
											>
												Recall: {((model.metrics.recall || 0) * 100).toFixed(1)}
												%
											</Typography>
											<Typography
												variant="caption"
												color="text.secondary"
												display="block"
											>
												F1 Score:{" "}
												{((model.metrics.f1_score || 0) * 100).toFixed(1)}%
											</Typography>
										</Box>
									)}

									{/* Feature Count */}
									{model.feature_names && (
										<Typography variant="caption" color="text.secondary">
											특징 수: {model.feature_names.length}개
										</Typography>
									)}
								</Stack>
							</CardContent>

							<CardActions sx={{ justifyContent: "flex-end", px: 2, pb: 2 }}>
								<Button
									size="small"
									onClick={() => handleViewDetail(model.version || "")}
								>
									상세 보기
								</Button>
							</CardActions>
						</Card>
					</Grid>
				))}
			</Grid>

			{/* Selected Model Detail (Modal or Sidebar) */}
			{selectedVersion && (
				<MLModelDetail
					version={selectedVersion}
					onClose={() => setSelectedVersion(null)}
				/>
			)}
		</Box>
	);
};
