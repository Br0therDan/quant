/**
 * ShareDialog Component
 *
 * 내러티브 리포트 공유 다이얼로그
 *
 * 기능:
 * - 이메일 공유 (수신자, 메시지 입력)
 * - Slack 공유 (채널 선택, 메시지 입력)
 *
 * Phase: 3
 * 작성일: 2025-10-14
 */

import type { ShareOptions } from "@/hooks/useNarrativeReport";
import {
	Email as EmailIcon,
	Share as ShareIcon,
	Chat as SlackIcon,
} from "@mui/icons-material";
import {
	Box,
	Button,
	Chip,
	Dialog,
	DialogActions,
	DialogContent,
	DialogTitle,
	Stack,
	Tab,
	Tabs,
	TextField,
} from "@mui/material";
import type React from "react";
import { useState } from "react";

// ========================================================================================
// Props Interface
// ========================================================================================

export interface ShareDialogProps {
	backtestId: string;
	onShare: (options: ShareOptions) => Promise<void>;
	disabled?: boolean;
}

// ========================================================================================
// Main Component
// ========================================================================================

export const ShareDialog: React.FC<ShareDialogProps> = ({
	onShare,
	disabled = false,
}) => {
	const [open, setOpen] = useState(false);
	const [tab, setTab] = useState<"email" | "slack">("email");
	const [recipients, setRecipients] = useState<string>("");
	const [message, setMessage] = useState("");
	const [isSharing, setIsSharing] = useState(false);

	const handleOpen = () => setOpen(true);
	const handleClose = () => {
		setOpen(false);
		setRecipients("");
		setMessage("");
	};

	const handleShare = async () => {
		const recipientList = recipients
			.split(",")
			.map((r) => r.trim())
			.filter((r) => r.length > 0);

		if (recipientList.length === 0) {
			return;
		}

		setIsSharing(true);
		try {
			await onShare({
				method: tab,
				recipients: recipientList,
				message: message || undefined,
			});
			handleClose();
		} finally {
			setIsSharing(false);
		}
	};

	const recipientList = recipients
		.split(",")
		.map((r) => r.trim())
		.filter((r) => r.length > 0);

	return (
		<>
			<Button
				variant="outlined"
				startIcon={<ShareIcon />}
				onClick={handleOpen}
				disabled={disabled}
			>
				공유
			</Button>
			<Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
				<DialogTitle>리포트 공유</DialogTitle>
				<DialogContent>
					<Tabs
						value={tab}
						onChange={(_, newValue) => setTab(newValue)}
						sx={{ mb: 2 }}
					>
						<Tab
							value="email"
							label="이메일"
							icon={<EmailIcon />}
							iconPosition="start"
						/>
						<Tab
							value="slack"
							label="Slack"
							icon={<SlackIcon />}
							iconPosition="start"
						/>
					</Tabs>

					{tab === "email" && (
						<Box>
							<TextField
								fullWidth
								label="수신자 이메일"
								placeholder="user@example.com, admin@example.com"
								value={recipients}
								onChange={(e) => setRecipients(e.target.value)}
								helperText="쉼표(,)로 구분하여 여러 수신자 입력"
								sx={{ mb: 2 }}
							/>
						</Box>
					)}

					{tab === "slack" && (
						<Box>
							<TextField
								fullWidth
								label="Slack 채널"
								placeholder="#general, #trading, @username"
								value={recipients}
								onChange={(e) => setRecipients(e.target.value)}
								helperText="쉼표(,)로 구분하여 여러 채널 입력"
								sx={{ mb: 2 }}
							/>
						</Box>
					)}

					{recipientList.length > 0 && (
						<Stack direction="row" spacing={1} flexWrap="wrap" sx={{ mb: 2 }}>
							{recipientList.map((r, idx) => (
								<Chip
									key={idx}
									label={r}
									size="small"
									onDelete={() => {
										const newList = recipientList.filter((_, i) => i !== idx);
										setRecipients(newList.join(", "));
									}}
								/>
							))}
						</Stack>
					)}

					<TextField
						fullWidth
						multiline
						rows={3}
						label="메시지 (선택)"
						placeholder="백테스트 리포트를 공유합니다..."
						value={message}
						onChange={(e) => setMessage(e.target.value)}
					/>
				</DialogContent>
				<DialogActions>
					<Button onClick={handleClose}>취소</Button>
					<Button
						onClick={handleShare}
						variant="contained"
						disabled={recipientList.length === 0 || isSharing}
					>
						{isSharing ? "공유 중..." : "공유"}
					</Button>
				</DialogActions>
			</Dialog>
		</>
	);
};
