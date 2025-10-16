import {
	Box,
	Card,
	CardContent,
	Chip,
	List,
	ListItemButton,
	ListItemText,
	Typography,
} from "@mui/material";

/**
 * ChatHistoryPanel 컴포넌트
 * 채팅 히스토리 목록 표시
 */
export const ChatHistoryPanel = () => {
	// Mock data
	const chatHistory = [
		{ id: 1, title: "전략 최적화 논의", date: "2024-01-15", messages: 12 },
		{ id: 2, title: "백테스트 결과 분석", date: "2024-01-14", messages: 8 },
		{ id: 3, title: "리스크 관리 전략", date: "2024-01-13", messages: 15 },
	];

	return (
		<Card sx={{ height: "600px", display: "flex", flexDirection: "column" }}>
			<CardContent sx={{ flex: 1, overflow: "auto" }}>
				<Typography variant="h6" gutterBottom>
					Chat History
				</Typography>
				<List>
					{chatHistory.map((chat) => (
						<ListItemButton key={chat.id} sx={{ borderRadius: 1, mb: 1 }}>
							<ListItemText
								primary={chat.title}
								secondary={
									<Box sx={{ display: "flex", gap: 1, mt: 0.5 }}>
										<Typography variant="caption" color="text.secondary">
											{chat.date}
										</Typography>
										<Chip label={`${chat.messages} msgs`} size="small" />
									</Box>
								}
							/>
						</ListItemButton>
					))}
				</List>
			</CardContent>
		</Card>
	);
};
