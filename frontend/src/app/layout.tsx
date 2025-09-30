import QueryProvider from "@/components/providers/QueryProvider";
import { AuthProvider } from "@/context/AuthContext";
import theme from "@/theme";
import { AppRouterCacheProvider } from "@mui/material-nextjs/v15-appRouter";
import CssBaseline from "@mui/material/CssBaseline";
import InitColorSchemeScript from "@mui/material/InitColorSchemeScript";
import { ThemeProvider } from "@mui/material/styles";
import type * as React from "react";

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
    <html lang="en" suppressHydrationWarning>
      <head>
        <meta charSet="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      </head>
      <body>
        <InitColorSchemeScript attribute="class" />
        <AppRouterCacheProvider options={{ enableCssLayer: true }}>
          <ThemeProvider theme={theme}>
            <QueryProvider>
              <AuthProvider>
                <CssBaseline enableColorScheme />
                {props.children}
              </AuthProvider>
            </QueryProvider>
          </ThemeProvider>
        </AppRouterCacheProvider>
      </body>
    </html>
  );
}
