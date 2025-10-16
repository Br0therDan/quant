"use client";

import { useWatchlist } from "@/hooks/useWatchList";
import {
	Alert,
	Autocomplete,
	Box,
	CircularProgress,
	TextField,
	Typography,
} from "@mui/material";

interface WatchListSymbolSelectorProps {
	value: string;
	onChange: (symbol: string) => void;
	label?: string;
	placeholder?: string;
	error?: boolean;
	helperText?: string;
	required?: boolean;
}

export default function WatchListSymbolSelector({
	value,
	onChange,
	label = "심볼 선택",
	placeholder = "워치리스트에서 심볼을 선택하세요",
	error = false,
	helperText,
	required = false,
}: WatchListSymbolSelectorProps) {
	const {
		watchlistList,
		isLoading: { watchlistList: isLoading },
		error: { watchlistList: loadError },
	} = useWatchlist();

	// 모든 워치리스트에서 심볼 추출 (중복 제거)
	const allSymbols = Array.from(
		new Set(
			(watchlistList?.watchlists || []).flatMap(
				(watchlist) => watchlist.symbols || [],
			),
		),
	).sort();

	if (loadError) {
		return (
			<Alert severity="error">
				워치리스트를 불러오는 중 오류가 발생했습니다:{" "}
				{(loadError as any)?.message}
			</Alert>
		);
	}

	if (isLoading) {
		return (
			<Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
				<CircularProgress size={20} />
				<Typography variant="body2" color="text.secondary">
					워치리스트 불러오는 중...
				</Typography>
			</Box>
		);
	}

	if (allSymbols.length === 0) {
		return (
			<Alert severity="info">
				워치리스트에 심볼이 없습니다. 먼저 워치리스트를 생성하고 심볼을
				추가해주세요.
			</Alert>
		);
	}

	return (
		<Autocomplete
			value={value}
			onChange={(_, newValue) => {
				onChange(newValue || "");
			}}
			options={allSymbols}
			renderInput={(params) => (
				<TextField
					{...params}
					label={label}
					placeholder={placeholder}
					required={required}
					error={error}
					helperText={helperText}
				/>
			)}
			renderOption={(props, option) => (
				<Box component="li" {...props}>
					<Typography variant="body1">{option}</Typography>
				</Box>
			)}
			noOptionsText="워치리스트에 심볼이 없습니다"
			clearOnEscape
			disableClearable={required}
		/>
	);
}
