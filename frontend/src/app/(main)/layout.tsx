"use client";
import { MyLogo } from "@/components/common/logo";
import Header from "@/components/layout/Header";
import Sidebar from "@/components/layout/sidebar";
import DialogsProvider from "@/hooks/useDialogs/DialogsProvider";
import NotificationsProvider from "@/hooks/useNotifications/NotificationsProvider";
import Box from "@mui/material/Box";
import CssBaseline from "@mui/material/CssBaseline";
import { useTheme } from "@mui/material/styles";
import Toolbar from "@mui/material/Toolbar";
import useMediaQuery from "@mui/material/useMediaQuery";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import * as React from "react";
import { useState } from "react";

export default function MainLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const theme = useTheme();

  const [isDesktopNavigationExpanded, setIsDesktopNavigationExpanded] =
    useState(true);
  const [isMobileNavigationExpanded, setIsMobileNavigationExpanded] =
    useState(false);

  const isOverMdViewport = useMediaQuery(theme.breakpoints.up("md"));

  const isNavigationExpanded = isOverMdViewport
    ? isDesktopNavigationExpanded
    : isMobileNavigationExpanded;

  const setIsNavigationExpanded = React.useCallback(
    (newExpanded: boolean) => {
      if (isOverMdViewport) {
        setIsDesktopNavigationExpanded(newExpanded);
      } else {
        setIsMobileNavigationExpanded(newExpanded);
      }
    },
    [isOverMdViewport]
  );

  const handleToggleHeaderMenu = React.useCallback(
    (isExpanded: boolean) => {
      setIsNavigationExpanded(isExpanded);
    },
    [setIsNavigationExpanded]
  );
  const layoutRef = React.useRef(null);

  return (
    <>
      <CssBaseline enableColorScheme />
      <LocalizationProvider dateAdapter={AdapterDayjs}>
        <NotificationsProvider>
          <DialogsProvider>
            <Box
              ref={layoutRef}
              sx={{
                position: "relative",
                display: "flex",
                overflow: "hidden",
                height: "100vh",
                width: "100%",
              }}
            >
              <Header
                logo={<MyLogo noLink />}
                title=""
                menuOpen={isNavigationExpanded}
                onToggleMenu={handleToggleHeaderMenu}
              />
              <Sidebar
                expanded={isNavigationExpanded}
                setExpanded={setIsNavigationExpanded}
                container={layoutRef?.current ?? undefined}
              />
              <Box
                sx={{
                  display: "flex",
                  flexDirection: "column",
                  flex: 1,
                  minWidth: 0,
                }}
              >
                <Toolbar sx={{ displayPrint: "none" }} />
                <Box
                  component="main"
                  sx={{
                    display: "flex",
                    flexDirection: "column",
                    flex: 1,
                    overflow: "auto",
                  }}
                >
                  {children}
                </Box>
              </Box>
            </Box>
          </DialogsProvider>
        </NotificationsProvider>
      </LocalizationProvider>
    </>
  );
}
