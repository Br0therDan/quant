"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { PageLoading } from "@/components/common/LoadingSpinner";
import { useWatchlist } from "@/hooks/useWatchList";

export default function StockMainPage() {
	const router = useRouter();
	const { watchlistList, isLoading } = useWatchlist();

	useEffect(() => {
		if (!isLoading.watchlistList && watchlistList) {
			// Get first watchlist and first symbol
			const firstWatchlist = watchlistList.watchlists?.[0];
			const firstSymbol = firstWatchlist?.symbols?.[0];

			if (firstSymbol) {
				// Redirect to first symbol page
				router.replace(`/market-data/stock/${firstSymbol}`);
			} else {
				// No symbols found, redirect to dashboard or watchlist page
				router.replace("/dashboard");
			}
		}
	}, [isLoading.watchlistList, watchlistList, router]);

	return <PageLoading message="워치리스트에서 심볼을 불러오는 중..." />;
}
