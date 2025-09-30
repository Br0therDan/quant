"use client";

import { Add as AddIcon } from "@mui/icons-material";
import {
	Autocomplete,
	Box,
	Button,
	Chip,
	Dialog,
	DialogActions,
	DialogContent,
	DialogTitle,
	FormHelperText,
	TextField,
	Typography,
} from "@mui/material";
import React from "react";

interface WatchlistFormData {
	name: string;
	description?: string;
	symbols: string[];
}

interface WatchlistFormErrors {
	name?: string;
	description?: string;
	symbols?: string;
}

interface CreateWatchlistDialogProps {
	open: boolean;
	onClose: () => void;
	onSubmit: (data: WatchlistFormData) => void;
	initialData?: Partial<WatchlistFormData>;
	isEdit?: boolean;
	loading?: boolean;
}

// 임시 종목 리스트 (나중에 API에서 가져올 예정)
const AVAILABLE_SYMBOLS = [
	"AAPL",
	"GOOGL",
	"MSFT",
	"AMZN",
	"TSLA",
	"NVDA",
	"META",
	"NFLX",
	"AMD",
	"INTC",
	"ORCL",
	"IBM",
	"CRM",
	"ADBE",
	"PYPL",
	"DIS",
	"JPM",
	"BAC",
	"WFC",
	"GS",
	"V",
	"MA",
	"BRK.B",
	"JNJ",
];

export default function CreateWatchlistDialog({
	open,
	onClose,
	onSubmit,
	initialData,
	isEdit = false,
	loading = false,
}: CreateWatchlistDialogProps) {
	const [formData, setFormData] = React.useState<WatchlistFormData>({
		name: "",
		description: "",
		symbols: [],
		...initialData,
	});
	const [errors, setErrors] = React.useState<WatchlistFormErrors>({});

	React.useEffect(() => {
		if (open) {
			setFormData({
				name: "",
				description: "",
				symbols: [],
				...initialData,
			});
			setErrors({});
		}
	}, [open, initialData]);

	const validateForm = (): boolean => {
		const newErrors: WatchlistFormErrors = {};

		if (!formData.name.trim()) {
			newErrors.name = "워치리스트 이름을 입력해주세요.";
		}

		if (formData.symbols.length === 0) {
			newErrors.symbols = "최소 하나 이상의 종목을 추가해주세요.";
		}

		setErrors(newErrors);
		return Object.keys(newErrors).length === 0;
	};

	const handleSubmit = () => {
		if (validateForm()) {
			onSubmit(formData);
		}
	};

	const handleSymbolChange = (event: any, newValue: string[]) => {
		setFormData((prev) => ({
			...prev,
			symbols: newValue,
		}));
		if (errors.symbols) {
			setErrors((prev) => ({ ...prev, symbols: undefined }));
		}
	};

	const handleNameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
		setFormData((prev) => ({
			...prev,
			name: event.target.value,
		}));
		if (errors.name) {
			setErrors((prev) => ({ ...prev, name: undefined }));
		}
	};

	return (
		<Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
			<DialogTitle>
				{isEdit ? "워치리스트 수정" : "새 워치리스트 만들기"}
			</DialogTitle>
			<DialogContent>
				<Box component="form" sx={{ mt: 1 }}>
					<TextField
						fullWidth
						label="워치리스트 이름"
						value={formData.name}
						onChange={handleNameChange}
						error={!!errors.name}
						helperText={errors.name}
						margin="normal"
						required
						autoFocus
					/>

					<TextField
						fullWidth
						label="설명 (선택사항)"
						value={formData.description}
						onChange={(e) =>
							setFormData((prev) => ({ ...prev, description: e.target.value }))
						}
						margin="normal"
						multiline
						rows={3}
						placeholder="이 워치리스트에 대한 간단한 설명을 입력하세요..."
					/>

					<Box sx={{ mt: 2, mb: 1 }}>
						<Typography variant="subtitle2" gutterBottom>
							종목 선택 *
						</Typography>
						<Autocomplete
							multiple
							options={AVAILABLE_SYMBOLS}
							value={formData.symbols}
							onChange={handleSymbolChange}
							filterSelectedOptions
							renderTags={(value, getTagProps) =>
								value.map((option, index) => (
									<Chip
										variant="outlined"
										label={option}
										{...getTagProps({ index })}
										key={option}
									/>
								))
							}
							renderInput={(params) => (
								<TextField
									{...params}
									placeholder="종목 검색 및 선택"
									error={!!errors.symbols}
								/>
							)}
						/>
						{errors.symbols && (
							<FormHelperText error>{errors.symbols}</FormHelperText>
						)}
					</Box>

					{formData.symbols.length > 0 && (
						<Box sx={{ mt: 2 }}>
							<Typography variant="caption" color="text.secondary">
								선택된 종목: {formData.symbols.length}개
							</Typography>
							<Box sx={{ mt: 1 }}>
								{formData.symbols.map((symbol) => (
									<Chip
										key={symbol}
										label={symbol}
										size="small"
										sx={{ mr: 0.5, mb: 0.5 }}
										onDelete={() =>
											setFormData((prev) => ({
												...prev,
												symbols: prev.symbols.filter((s) => s !== symbol),
											}))
										}
									/>
								))}
							</Box>
						</Box>
					)}
				</Box>
			</DialogContent>
			<DialogActions sx={{ px: 3, pb: 2 }}>
				<Button onClick={onClose} disabled={loading}>
					취소
				</Button>
				<Button
					onClick={handleSubmit}
					variant="contained"
					disabled={loading}
					startIcon={isEdit ? undefined : <AddIcon />}
				>
					{loading ? "처리 중..." : isEdit ? "수정" : "생성"}
				</Button>
			</DialogActions>
		</Dialog>
	);
}
