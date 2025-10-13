"use client";

import {
	useFundamentalBalanceSheet,
	useFundamentalCashFlow,
	useFundamentalIncomeStatement,
} from "@/hooks/ussFundamental";
import {
	AccountBalance as BalanceIcon,
	Water as CashFlowIcon,
	TrendingUp as IncomeIcon,
} from "@mui/icons-material";
import {
	Box,
	Card,
	CardContent,
	Container,
	Grid,
	Paper,
	Tab,
	Tabs,
	Typography,
} from "@mui/material";
import { useParams } from "next/navigation";
import { useState } from "react";

import LoadingSpinner from "@/components/common/LoadingSpinner";

type FinancialTab = "income" | "balance" | "cashflow";

export default function SymbolFinancialsPage() {
	const params = useParams();
	const symbol = (params.symbol as string)?.toUpperCase();

	const [activeTab, setActiveTab] = useState<FinancialTab>("income");

	// 데이터 fetching
	const { data: incomeData, isLoading: incomeLoading } =
		useFundamentalIncomeStatement(symbol);
	const { data: balanceData, isLoading: balanceLoading } =
		useFundamentalBalanceSheet(symbol);
	const { data: cashFlowData, isLoading: cashFlowLoading } =
		useFundamentalCashFlow(symbol);

	return (
		<Container maxWidth="xl" sx={{ py: 4 }}>
			<Box display="flex" flexDirection="column" gap={3}>
				{/* 헤더 */}
				<Box>
					<Typography variant="h4" gutterBottom>
						{symbol} - Financial Statements
					</Typography>
					<Typography variant="body2" color="text.secondary">
						Quarterly and annual financial data
					</Typography>
				</Box>

				{/* 탭 */}
				<Paper elevation={1}>
					<Tabs
						value={activeTab}
						onChange={(_, newValue) => setActiveTab(newValue)}
						variant="fullWidth"
					>
						<Tab
							label="손익계산서"
							value="income"
							icon={<IncomeIcon />}
							iconPosition="start"
						/>
						<Tab
							label="재무상태표"
							value="balance"
							icon={<BalanceIcon />}
							iconPosition="start"
						/>
						<Tab
							label="현금흐름표"
							value="cashflow"
							icon={<CashFlowIcon />}
							iconPosition="start"
						/>
					</Tabs>
				</Paper>

				{/* 내용 */}
				{activeTab === "income" && (
					<IncomeStatementSection data={incomeData} isLoading={incomeLoading} />
				)}
				{activeTab === "balance" && (
					<BalanceSheetSection data={balanceData} isLoading={balanceLoading} />
				)}
				{activeTab === "cashflow" && (
					<CashFlowSection data={cashFlowData} isLoading={cashFlowLoading} />
				)}
			</Box>
		</Container>
	);
}

// 손익계산서 섹션
function IncomeStatementSection({
	data,
	isLoading,
}: {
	data: any;
	isLoading: boolean;
}) {
	if (isLoading) {
		return (
			<LoadingSpinner
				variant="skeleton"
				height={400}
				message="손익계산서 로딩 중..."
			/>
		);
	}

	// API 응답이 배열이므로 첫 번째 요소를 가져옴
	if (!data?.data || !Array.isArray(data.data) || data.data.length === 0) {
		return (
			<Card>
				<CardContent>
					<Typography color="text.secondary">
						손익계산서 데이터를 불러올 수 없습니다
					</Typography>
				</CardContent>
			</Card>
		);
	}

	const financialData = data.data[0]; // 배열의 첫 번째 요소

	return (
		<Grid container spacing={3}>
			<Grid size={{ xs: 12, md: 6 }}>
				<StatCard
					title="총 매출"
					value={formatCurrency(financialData.total_revenue)}
					description="Total Revenue"
				/>
			</Grid>
			<Grid size={{ xs: 12, md: 6 }}>
				<StatCard
					title="매출총이익"
					value={formatCurrency(financialData.gross_profit)}
					description="Gross Profit"
				/>
			</Grid>
			<Grid size={{ xs: 12, md: 6 }}>
				<StatCard
					title="영업이익"
					value={formatCurrency(financialData.operating_income)}
					description="Operating Income"
				/>
			</Grid>
			<Grid size={{ xs: 12, md: 6 }}>
				<StatCard
					title="순이익"
					value={formatCurrency(financialData.net_income)}
					description="Net Income"
				/>
			</Grid>
			<Grid size={{ xs: 12, md: 6 }}>
				<StatCard
					title="기본 주당순이익 (EPS)"
					value={financialData.basic_eps || "N/A"}
					description="Basic Earnings Per Share"
				/>
			</Grid>
			<Grid size={{ xs: 12, md: 6 }}>
				<StatCard
					title="희석 주당순이익"
					value={financialData.diluted_eps || "N/A"}
					description="Diluted Earnings Per Share"
				/>
			</Grid>
		</Grid>
	);
}

// 재무상태표 섹션
function BalanceSheetSection({
	data,
	isLoading,
}: {
	data: any;
	isLoading: boolean;
}) {
	if (isLoading) {
		return (
			<LoadingSpinner
				variant="skeleton"
				height={400}
				message="재무상태표 로딩 중..."
			/>
		);
	}

	// API 응답이 배열이므로 첫 번째 요소를 가져옴
	if (!data?.data || !Array.isArray(data.data) || data.data.length === 0) {
		return (
			<Card>
				<CardContent>
					<Typography color="text.secondary">
						재무상태표 데이터를 불러올 수 없습니다
					</Typography>
				</CardContent>
			</Card>
		);
	}

	const financialData = data.data[0]; // 배열의 첫 번째 요소

	return (
		<Grid container spacing={3}>
			<Grid size={{ xs: 12, md: 6 }}>
				<StatCard
					title="총 자산"
					value={formatCurrency(financialData.total_assets)}
					description="Total Assets"
				/>
			</Grid>
			<Grid size={{ xs: 12, md: 6 }}>
				<StatCard
					title="총 부채"
					value={formatCurrency(financialData.total_liabilities)}
					description="Total Liabilities"
				/>
			</Grid>
			<Grid size={{ xs: 12, md: 6 }}>
				<StatCard
					title="자본총계"
					value={formatCurrency(financialData.total_shareholder_equity)}
					description="Total Shareholder Equity"
				/>
			</Grid>
			<Grid size={{ xs: 12, md: 6 }}>
				<StatCard
					title="유동자산"
					value={formatCurrency(financialData.total_current_assets)}
					description="Current Assets"
				/>
			</Grid>
			<Grid size={{ xs: 12, md: 6 }}>
				<StatCard
					title="유동부채"
					value={formatCurrency(financialData.total_current_liabilities)}
					description="Current Liabilities"
				/>
			</Grid>
			<Grid size={{ xs: 12, md: 6 }}>
				<StatCard
					title="장기부채"
					value={formatCurrency(financialData.long_term_debt)}
					description="Long-term Debt"
				/>
			</Grid>
		</Grid>
	);
}

// 현금흐름표 섹션
function CashFlowSection({
	data,
	isLoading,
}: {
	data: any;
	isLoading: boolean;
}) {
	if (isLoading) {
		return (
			<LoadingSpinner
				variant="skeleton"
				height={400}
				message="현금흐름표 로딩 중..."
			/>
		);
	}

	// API 응답이 배열이므로 첫 번째 요소를 가져옴
	if (!data?.data || !Array.isArray(data.data) || data.data.length === 0) {
		return (
			<Card>
				<CardContent>
					<Typography color="text.secondary">
						현금흐름표 데이터를 불러올 수 없습니다
					</Typography>
				</CardContent>
			</Card>
		);
	}

	const financialData = data.data[0]; // 배열의 첫 번째 요소

	return (
		<Grid container spacing={3}>
			<Grid size={{ xs: 12, md: 4 }}>
				<StatCard
					title="영업활동 현금흐름"
					value={formatCurrency(financialData.operating_cashflow)}
					description="Operating Cash Flow"
				/>
			</Grid>
			<Grid size={{ xs: 12, md: 4 }}>
				<StatCard
					title="투자활동 현금흐름"
					value={formatCurrency(financialData.cashflow_from_investment)}
					description="Cash Flow from Investment"
				/>
			</Grid>
			<Grid size={{ xs: 12, md: 4 }}>
				<StatCard
					title="재무활동 현금흐름"
					value={formatCurrency(financialData.cashflow_from_financing)}
					description="Cash Flow from Financing"
				/>
			</Grid>
		</Grid>
	);
}

// 통계 카드 컴포넌트
function StatCard({
	title,
	value,
	description,
}: {
	title: string;
	value: string;
	description: string;
}) {
	return (
		<Card>
			<CardContent>
				<Typography variant="subtitle2" color="text.secondary" gutterBottom>
					{title}
				</Typography>
				<Typography variant="h5" fontWeight="bold" gutterBottom>
					{value}
				</Typography>
				<Typography variant="caption" color="text.secondary">
					{description}
				</Typography>
			</CardContent>
		</Card>
	);
}

// 통화 포맷 헬퍼
function formatCurrency(value: string | number | null | undefined): string {
	if (!value) return "N/A";
	const num = typeof value === "string" ? Number.parseFloat(value) : value;
	if (Number.isNaN(num)) return "N/A";

	// 억 단위로 변환
	if (num >= 1e9) {
		return `$${(num / 1e9).toFixed(2)}B`;
	}
	if (num >= 1e6) {
		return `$${(num / 1e6).toFixed(2)}M`;
	}
	return `$${num.toLocaleString()}`;
}
