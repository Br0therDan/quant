"use client";

import { useAuth } from "@/contexts/AuthContext";
import { Box, CircularProgress } from "@mui/material";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function Home() {
	const { isAuthenticated, isInitialized } = useAuth();
	const router = useRouter();

	useEffect(() => {
		if (isInitialized) {
			if (isAuthenticated) {
				router.push("/dashboard");
			} else {
				router.push("/login");
			}
		}
	}, [isAuthenticated, isInitialized, router]);

	// 초기화 중일 때 로딩 표시
	return (
		<Box
			display="flex"
			justifyContent="center"
			alignItems="center"
			minHeight="100vh"
		>
			<CircularProgress />
		</Box>
	);
}
