import QueryProvider from "@/components/providers/QueryProvider";
import theme from "@/theme";
import { AppRouterCacheProvider } from "@mui/material-nextjs/v15-appRouter";
import CssBaseline from "@mui/material/CssBaseline";
import InitColorSchemeScript from "@mui/material/InitColorSchemeScript";
import { ThemeProvider } from "@mui/material/styles";
import * as React from "react";

export const metadata = {
  title: "MySingle Quant",
  description:
    'MySingle is a unified platform built to support businesspeople in achieving a more fulfilling and integrated life. It challenges the concept of "work-life balance" as an unrealistic ideal and proposes a system that seamlessly integrates both work and personal life.',
  keywords: ["crm", "mysingle", "sales", "kids care", "note"],
  author: "Dan Kim",
  siteName: "MySingle",
};

export default function RootLayout(props: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <InitColorSchemeScript attribute="class" />
        <AppRouterCacheProvider options={{ enableCssLayer: true }}>
          <ThemeProvider theme={theme}>
            <QueryProvider>
              <CssBaseline enableColorScheme />
              {props.children}
            </QueryProvider>
          </ThemeProvider>
        </AppRouterCacheProvider>
      </body>
    </html>
  );
}
