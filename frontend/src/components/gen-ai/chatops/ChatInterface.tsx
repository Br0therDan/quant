import { Send } from "@mui/icons-material";
import {
	Box,
	Card,
	CardContent,
	IconButton,
	Paper,
	TextField,
	Typography,
} from "@mui/material";
import { useState } from "react";

/**
 * ChatInterface 컴포넌트
 * 대화형 채팅 인터페이스
 */
export const ChatInterface = () => {
	const [message, setMessage] = useState("");

	// Mock messages
	const messages = [
		{ id: 1, role: "user", content: "최근 백테스트 결과를 요약해줘" },
		{
			id: 2,
			role: "assistant",
			content:
				"최근 백테스트 결과를 분석했습니다. 주요 지표는 다음과 같습니다...",
		},
	];

	const handleSend = () => {
		if (message.trim()) {
			console.log("Sending:", message);
			setMessage("");
		}
	};

	return (
		<Card sx={{ height: "600px", display: "flex", flexDirection: "column" }}>
			<CardContent sx={{ flex: 1, display: "flex", flexDirection: "column" }}>
				<Typography variant="h6" gutterBottom>
					Chat Interface
				</Typography>

				{/* Messages Area */}
				<Box sx={{ flex: 1, overflow: "auto", mb: 2 }}>
					{messages.map((msg) => (
						<Paper
							key={msg.id}
							sx={{
								p: 2,
								mb: 1,
								bgcolor: msg.role === "user" ? "primary.light" : "grey.100",
								ml: msg.role === "user" ? "auto" : 0,
								mr: msg.role === "assistant" ? "auto" : 0,
								maxWidth: "80%",
							}}
						>
							<Typography variant="body2">{msg.content}</Typography>
						</Paper>
					))}
				</Box>

				{/* Input Area */}
				<Box sx={{ display: "flex", gap: 1 }}>
					<TextField
						fullWidth
						placeholder="메시지를 입력하세요..."
						value={message}
						onChange={(e) => setMessage(e.target.value)}
						onKeyPress={(e) => e.key === "Enter" && handleSend()}
						size="small"
					/>
					<IconButton color="primary" onClick={handleSend}>
						<Send />
					</IconButton>
				</Box>
			</CardContent>
		</Card>
	);
};
