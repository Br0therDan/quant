import {
	Add as AddIcon,
	TrendingUp as TrendingUpIcon,
} from "@mui/icons-material";
import { Button, Card, CardContent, Stack, Typography } from "@mui/material";
import Link from "next/link";

/**
 * QuickActions Component
 *
 * 빠른 시작 액션
 */
export function QuickActions() {
	return (
		<Card>
			<CardContent>
				<Typography variant="h6" gutterBottom>
					빠른 시작
				</Typography>
				<Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
					<Button
						component={Link}
						href="/backtests/new"
						variant="contained"
						startIcon={<AddIcon />}
						fullWidth
					>
						새 백테스트 생성
					</Button>
					<Button
						component={Link}
						href="/strategies"
						variant="outlined"
						startIcon={<TrendingUpIcon />}
						fullWidth
					>
						전략 탐색
					</Button>
				</Stack>
			</CardContent>
		</Card>
	);
}
