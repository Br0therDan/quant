import QueryProvider from "@/components/providers/QueryProvider";
import AppTheme from "@/components/shared-theme/AppTheme";
import { AuthProvider } from "@/contexts/AuthContext";
import { SnackbarProvider } from "@/contexts/SnackbarContext";
import { AppRouterCacheProvider } from "@mui/material-nextjs/v15-appRouter";
import CssBaseline from "@mui/material/CssBaseline";
import InitColorSchemeScript from "@mui/material/InitColorSchemeScript";
import { Roboto, Inter, JetBrains_Mono } from "next/font/google";
import type * as React from "react";

const roboto = Roboto({
	weight: ["300", "400", "500", "700"],
	subsets: ["latin"],
	display: "swap",
	variable: "--font-roboto",
});

const inter = Inter({
	weight: ["400", "500", "600", "700"],
	subsets: ["latin"],
	display: "swap",
	variable: "--font-inter",
});

const jetbrainsMono = JetBrains_Mono({
	weight: ["400", "500", "600"],
	subsets: ["latin"],
	display: "swap",
	variable: "--font-jetbrains-mono",
});

export const metadata = {
	title: "MySingle Quant",
	icons: "/images/favicon.ico",
	description:
		'MySingle is a unified platform built to support businesspeople in achieving a more fulfilling and integrated life. It challenges the concept of "work-life balance" as an unrealistic ideal and proposes a system that seamlessly integrates both work and personal life.',
	keywords: ["crm", "mysingle", "sales", "kids care", "note"],
	authors: [{ name: "Dan Kim" }],
};

export default function RootLayout(props: { children: React.ReactNode }) {
	return (
		<html
			lang="en"
			suppressHydrationWarning
			className={`${roboto.variable} ${inter.variable} ${jetbrainsMono.variable}`}
		>
			<head>
				<meta charSet="UTF-8" />
				<meta name="viewport" content="width=device-width, initial-scale=1.0" />
			</head>
			<body>
				<InitColorSchemeScript attribute="class" />
				<AppRouterCacheProvider options={{ enableCssLayer: true }}>
					<AppTheme>
						<SnackbarProvider>
							<QueryProvider>
								<AuthProvider>
									<CssBaseline enableColorScheme />
									{props.children}
								</AuthProvider>
							</QueryProvider>
						</SnackbarProvider>
					</AppTheme>
				</AppRouterCacheProvider>
			</body>
		</html>
	);
}
