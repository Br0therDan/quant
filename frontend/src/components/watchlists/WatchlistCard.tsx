"use client";

import {
	Delete as DeleteIcon,
	Edit as EditIcon,
	MoreVert as MoreVertIcon,
	TrendingUp as TrendingUpIcon,
} from "@mui/icons-material";
import {
	Box,
	Button,
	Card,
	CardActions,
	CardContent,
	Chip,
	IconButton,
	Menu,
	MenuItem,
	Typography,
} from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import React from "react";

import { pipelineGetWatchlistOptions } from "@/client/@tanstack/react-query.gen";

interface WatchlistCardProps {
	watchlist: {
		name: string;
		description?: string;
		symbol_count: number;
		auto_update: boolean;
		last_updated: string;
		created_at: string;
	};
	onEdit?: (watchlist: any) => void;
	onDelete?: (watchlistName: string) => void;
	onView?: (watchlist: any) => void;
}

export default function WatchlistCard({
	watchlist,
	onEdit,
	onDelete,
	onView,
}: WatchlistCardProps) {
	const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
	const open = Boolean(anchorEl);

	// 워치리스트 상세 정보 가져오기
	const { data: watchlistDetails } = useQuery(
		pipelineGetWatchlistOptions({
			path: { name: watchlist.name },
		}),
	);

	// 실제 심볼 리스트 (상세 정보에서 가져오거나 빈 배열)
	const symbols = (watchlistDetails as any)?.symbols || [];

	const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
		setAnchorEl(event.currentTarget);
	};

	const handleMenuClose = () => {
		setAnchorEl(null);
	};

	const handleEdit = () => {
		handleMenuClose();
		onEdit?.(watchlist);
	};

	const handleDelete = () => {
		handleMenuClose();
		onDelete?.(watchlist.name);
	};

	const handleView = () => {
		if (onView) {
			// 상세 정보가 있으면 전달, 없으면 기본 정보 전달
			onView(watchlistDetails || watchlist);
		}
	};

	const formatDate = (dateString?: string) => {
		if (!dateString) return "날짜 없음";
		return new Date(dateString).toLocaleDateString("ko-KR", {
			year: "numeric",
			month: "short",
			day: "numeric",
		});
	};

	return (
		<Card
			sx={{
				height: "100%",
				display: "flex",
				flexDirection: "column",
				transition: "all 0.2s ease-in-out",
				"&:hover": {
					transform: "translateY(-2px)",
					boxShadow: (theme) => theme.shadows[4],
				},
			}}
		>
			<CardContent sx={{ flexGrow: 1, pb: 1 }}>
				<Box
					display="flex"
					justifyContent="space-between"
					alignItems="flex-start"
					mb={1}
				>
					<Typography
						variant="h6"
						component="h3"
						noWrap
						sx={{ flexGrow: 1, mr: 1 }}
					>
						{watchlist.name}
					</Typography>
					<IconButton
						size="small"
						onClick={handleMenuClick}
						aria-label="워치리스트 옵션"
					>
						<MoreVertIcon />
					</IconButton>
				</Box>

				{watchlist.description && (
					<Typography
						variant="body2"
						color="text.secondary"
						sx={{
							mb: 2,
							display: "-webkit-box",
							WebkitLineClamp: 2,
							WebkitBoxOrient: "vertical",
							overflow: "hidden",
						}}
					>
						{watchlist.description}
					</Typography>
				)}

				<Box display="flex" alignItems="center" gap={1} mb={2}>
					<TrendingUpIcon color="primary" fontSize="small" />
					<Chip
						label={`${watchlist.symbol_count || 0}개 종목`}
						size="small"
						variant="outlined"
						color="primary"
					/>
				</Box>

				{watchlist.symbol_count > 0 && (
					<Box mb={2}>
						<Typography variant="caption" color="text.secondary" gutterBottom>
							포함 종목 ({watchlist.symbol_count}개)
						</Typography>
						<Box display="flex" flexWrap="wrap" gap={0.5}>
							{symbols.length > 0 ? (
								<>
									{symbols.slice(0, 6).map((symbol: string) => (
										<Chip
											key={symbol}
											label={symbol}
											size="small"
											variant="outlined"
										/>
									))}
									{symbols.length > 6 && (
										<Chip
											label={`+${symbols.length - 6}개`}
											size="small"
											variant="outlined"
											color="secondary"
										/>
									)}
								</>
							) : (
								<Chip
									label={`총 ${watchlist.symbol_count}개 종목`}
									size="small"
									variant="outlined"
									color="secondary"
								/>
							)}
							{watchlist.auto_update && (
								<Chip
									label="자동 업데이트"
									size="small"
									variant="outlined"
									color="success"
								/>
							)}
						</Box>
					</Box>
				)}

				<Typography variant="caption" color="text.secondary">
					업데이트: {formatDate(watchlist.last_updated)}
				</Typography>
			</CardContent>

			<CardActions sx={{ pt: 0, px: 2, pb: 2 }}>
				<Button
					size="small"
					variant="contained"
					onClick={handleView}
					sx={{ flexGrow: 1 }}
				>
					상세보기
				</Button>
			</CardActions>

			<Menu
				anchorEl={anchorEl}
				open={open}
				onClose={handleMenuClose}
				anchorOrigin={{
					vertical: "top",
					horizontal: "right",
				}}
				transformOrigin={{
					vertical: "top",
					horizontal: "right",
				}}
			>
				<MenuItem onClick={handleEdit}>
					<EditIcon fontSize="small" sx={{ mr: 1 }} />
					수정
				</MenuItem>
				<MenuItem onClick={handleDelete} sx={{ color: "error.main" }}>
					<DeleteIcon fontSize="small" sx={{ mr: 1 }} />
					삭제
				</MenuItem>
			</Menu>
		</Card>
	);
}
