/**
 * MLTrainingDialog Component
 *
 * Phase 1 Day 5: ML Model Training Dialog
 * - Training parameter form (react-hook-form)
 * - Validation logic (Pydantic schema compatible)
 * - Progress indicator (isTraining)
 */

"use client";

import { useTrainModel } from "@/hooks/useMLModel";
import ModelTrainingIcon from "@mui/icons-material/Psychology";
import {
	Alert,
	Box,
	Button,
	Chip,
	CircularProgress,
	Dialog,
	DialogActions,
	DialogContent,
	DialogTitle,
	FormHelperText,
	Slider,
	Stack,
	TextField,
	Typography,
} from "@mui/material";
import Grid from "@mui/material/Grid";
import { useState } from "react";
import { Controller, useForm } from "react-hook-form";

interface MLTrainingDialogProps {
	open: boolean;
	onClose: () => void;
}

interface TrainingFormData {
	symbols: string;
	lookback_days: number;
	test_size: number;
	num_boost_round: number;
	threshold: number;
}

const DEFAULT_VALUES: TrainingFormData = {
	symbols: "AAPL,MSFT,GOOGL",
	lookback_days: 500,
	test_size: 0.2,
	num_boost_round: 100,
	threshold: 0.02,
};

export const MLTrainingDialog = ({ open, onClose }: MLTrainingDialogProps) => {
	const { trainModel, isTraining } = useTrainModel();
	const [trainingStarted, setTrainingStarted] = useState(false);

	const {
		control,
		handleSubmit,
		formState: { errors },
		reset,
	} = useForm<TrainingFormData>({
		defaultValues: DEFAULT_VALUES,
	});

	const handleClose = () => {
		if (!isTraining) {
			reset();
			setTrainingStarted(false);
			onClose();
		}
	};

	const onSubmit = async (data: TrainingFormData) => {
		// Parse symbols from comma-separated string
		const symbolsArray = data.symbols
			.split(",")
			.map((s) => s.trim())
			.filter(Boolean);

		await trainModel.mutateAsync({
			body: {
				symbols: symbolsArray,
				lookback_days: data.lookback_days,
				test_size: data.test_size,
				num_boost_round: data.num_boost_round,
				threshold: data.threshold,
			},
		});

		setTrainingStarted(true);
		// Dialog will close automatically via mutation onSuccess
	};

	return (
		<Dialog
			open={open}
			onClose={handleClose}
			maxWidth="md"
			fullWidth
			disableEscapeKeyDown={isTraining}
		>
			<DialogTitle>
				<Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
					<ModelTrainingIcon color="primary" />
					<Typography variant="h6">ML 모델 학습</Typography>
				</Box>
			</DialogTitle>

			<form onSubmit={handleSubmit(onSubmit)}>
				<DialogContent dividers>
					{trainingStarted ? (
						// Training in Progress
						<Box sx={{ textAlign: "center", py: 4 }}>
							<CircularProgress size={60} sx={{ mb: 3 }} />
							<Typography variant="h6" gutterBottom>
								모델 학습 진행 중...
							</Typography>
							<Typography variant="body2" color="text.secondary">
								백그라운드에서 학습이 진행됩니다. 완료되면 모델 목록에서 확인할
								수 있습니다.
							</Typography>
						</Box>
					) : (
						// Training Configuration Form
						<Stack spacing={3}>
							<Alert severity="info">
								LightGBM 모델을 학습합니다. 학습은 백그라운드에서 진행되며 수
								분이 소요될 수 있습니다.
							</Alert>

							{/* Symbols */}
							<Box>
								<Controller
									name="symbols"
									control={control}
									rules={{
										required: "심볼을 입력하세요",
										validate: (value) => {
											const symbols = value.split(",").map((s) => s.trim());
											if (symbols.length === 0) {
												return "최소 1개의 심볼이 필요합니다";
											}
											if (symbols.some((s) => s.length < 1)) {
												return "유효하지 않은 심볼이 포함되어 있습니다";
											}
											return true;
										},
									}}
									render={({ field }) => (
										<TextField
											{...field}
											label="학습 종목 (심볼)"
											placeholder="AAPL,MSFT,GOOGL"
											fullWidth
											error={!!errors.symbols}
											helperText={
												errors.symbols?.message ||
												"쉼표(,)로 구분하여 여러 종목 입력 가능"
											}
											disabled={isTraining}
										/>
									)}
								/>
								{/* Symbol Chips Preview */}
								<Box sx={{ mt: 1, display: "flex", gap: 1, flexWrap: "wrap" }}>
									{control._formValues.symbols
										?.split(",")
										.map((s) => s.trim())
										.filter(Boolean)
										.map((symbol, index) => (
											<Chip key={index} label={symbol} size="small" />
										))}
								</Box>
							</Box>

							{/* Grid for numeric parameters */}
							<Grid container spacing={2}>
								{/* Lookback Days */}
								<Grid size={{ xs: 12, sm: 6 }}>
									<Controller
										name="lookback_days"
										control={control}
										rules={{
											required: "조회 기간을 입력하세요",
											min: { value: 100, message: "최소 100일 이상" },
											max: { value: 2000, message: "최대 2000일 이하" },
										}}
										render={({ field }) => (
											<TextField
												{...field}
												label="조회 기간 (일)"
												type="number"
												fullWidth
												error={!!errors.lookback_days}
												helperText={
													errors.lookback_days?.message ||
													"과거 몇 일의 데이터를 사용할지 (100-2000)"
												}
												disabled={isTraining}
												onChange={(e) => field.onChange(Number(e.target.value))}
											/>
										)}
									/>
								</Grid>

								{/* Num Boost Round */}
								<Grid size={{ xs: 12, sm: 6 }}>
									<Controller
										name="num_boost_round"
										control={control}
										rules={{
											required: "부스팅 라운드를 입력하세요",
											min: { value: 10, message: "최소 10 이상" },
											max: { value: 500, message: "최대 500 이하" },
										}}
										render={({ field }) => (
											<TextField
												{...field}
												label="부스팅 라운드"
												type="number"
												fullWidth
												error={!!errors.num_boost_round}
												helperText={
													errors.num_boost_round?.message ||
													"LightGBM 반복 횟수 (10-500)"
												}
												disabled={isTraining}
												onChange={(e) => field.onChange(Number(e.target.value))}
											/>
										)}
									/>
								</Grid>
							</Grid>

							{/* Test Size Slider */}
							<Box>
								<Typography variant="body2" gutterBottom>
									테스트 데이터 비율:{" "}
									{(control._formValues.test_size * 100).toFixed(0)}%
								</Typography>
								<Controller
									name="test_size"
									control={control}
									rules={{
										required: true,
										min: { value: 0.1, message: "최소 10%" },
										max: { value: 0.5, message: "최대 50%" },
									}}
									render={({ field }) => (
										<Box>
											<Slider
												{...field}
												min={0.1}
												max={0.5}
												step={0.05}
												marks
												valueLabelDisplay="auto"
												valueLabelFormat={(value) =>
													`${(value * 100).toFixed(0)}%`
												}
												disabled={isTraining}
												onChange={(_, value) => field.onChange(value)}
											/>
											<FormHelperText>
												전체 데이터 중 테스트용으로 사용할 비율 (10-50%)
											</FormHelperText>
										</Box>
									)}
								/>
							</Box>

							{/* Threshold Slider */}
							<Box>
								<Typography variant="body2" gutterBottom>
									매수 신호 임계값:{" "}
									{(control._formValues.threshold * 100).toFixed(1)}%
								</Typography>
								<Controller
									name="threshold"
									control={control}
									rules={{
										required: true,
										min: { value: 0.01, message: "최소 1%" },
										max: { value: 0.1, message: "최대 10%" },
									}}
									render={({ field }) => (
										<Box>
											<Slider
												{...field}
												min={0.01}
												max={0.1}
												step={0.005}
												marks
												valueLabelDisplay="auto"
												valueLabelFormat={(value) =>
													`${(value * 100).toFixed(1)}%`
												}
												disabled={isTraining}
												onChange={(_, value) => field.onChange(value)}
											/>
											<FormHelperText>
												미래 수익률이 이 값 이상일 때 매수 신호 생성 (1-10%)
											</FormHelperText>
										</Box>
									)}
								/>
							</Box>

							{/* Training Info */}
							<Alert severity="warning">
								<Typography variant="body2">
									<strong>참고:</strong> 학습 시간은 데이터 양과 파라미터에 따라
									다르며, 통상 2-10분 소요됩니다. 백그라운드 작업으로 진행되므로
									창을 닫아도 학습이 계속됩니다.
								</Typography>
							</Alert>
						</Stack>
					)}
				</DialogContent>

				<DialogActions>
					<Button onClick={handleClose} disabled={isTraining}>
						{trainingStarted ? "확인" : "취소"}
					</Button>
					{!trainingStarted && (
						<Button
							type="submit"
							variant="contained"
							disabled={isTraining}
							startIcon={isTraining ? <CircularProgress size={20} /> : null}
						>
							{isTraining ? "학습 중..." : "학습 시작"}
						</Button>
					)}
				</DialogActions>
			</form>
		</Dialog>
	);
};
