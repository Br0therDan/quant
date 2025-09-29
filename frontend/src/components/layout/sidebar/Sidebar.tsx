"use client";
import SidebarContext from "@/context/SidebarContext";
// Icons for quant platform
import AnalyticsIcon from "@mui/icons-material/Analytics";
import AutoFixHighIcon from "@mui/icons-material/AutoFixHigh";
import DashboardIcon from "@mui/icons-material/Dashboard";
import DataObjectIcon from "@mui/icons-material/DataObject";
import HistoryIcon from "@mui/icons-material/History";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import PsychologyIcon from "@mui/icons-material/Psychology";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import WatchlistIcon from "@mui/icons-material/Visibility";
import Box from "@mui/material/Box";
import Drawer from "@mui/material/Drawer";
import List from "@mui/material/List";
import Toolbar from "@mui/material/Toolbar";
import { useTheme } from "@mui/material/styles";
import type {} from "@mui/material/themeCssVarsAugmentation";
import useMediaQuery from "@mui/material/useMediaQuery";
import { usePathname } from "next/navigation";
import * as React from "react";
import SidebarDividerItem from "./SidebarDividerItem";
import SidebarHeaderItem from "./SidebarHeaderItem";
import SidebarPageItem from "./SidebarPageItem";
import { DRAWER_WIDTH, MINI_DRAWER_WIDTH } from "./constants";
import {
  getDrawerSxTransitionMixin,
  getDrawerWidthTransitionMixin,
} from "./mixins";

export interface SidebarProps {
  expanded?: boolean;
  setExpanded: (expanded: boolean) => void;
  disableCollapsibleSidebar?: boolean;
  container?: Element;
}

export default function Sidebar({
  expanded = true,
  setExpanded,
  disableCollapsibleSidebar = false,
  container,
}: SidebarProps) {
  const theme = useTheme();

  const pathname = usePathname();

  const [expandedItemIds, setExpandedItemIds] = React.useState<string[]>([]);

  const isOverSmViewport = useMediaQuery(theme.breakpoints.up("sm"));
  const isOverMdViewport = useMediaQuery(theme.breakpoints.up("md"));

  const [isFullyExpanded, setIsFullyExpanded] = React.useState(expanded);
  const [isFullyCollapsed, setIsFullyCollapsed] = React.useState(!expanded);

  React.useEffect(() => {
    if (expanded) {
      const drawerWidthTransitionTimeout = setTimeout(() => {
        setIsFullyExpanded(true);
      }, theme.transitions.duration.enteringScreen);

      return () => clearTimeout(drawerWidthTransitionTimeout);
    }

    setIsFullyExpanded(false);

    return () => {};
  }, [expanded, theme.transitions.duration.enteringScreen]);

  React.useEffect(() => {
    if (!expanded) {
      const drawerWidthTransitionTimeout = setTimeout(() => {
        setIsFullyCollapsed(true);
      }, theme.transitions.duration.leavingScreen);

      return () => clearTimeout(drawerWidthTransitionTimeout);
    }

    setIsFullyCollapsed(false);

    return () => {};
  }, [expanded, theme.transitions.duration.leavingScreen]);

  const mini = !disableCollapsibleSidebar && !expanded;

  const handleSetSidebarExpanded = React.useCallback(
    (newExpanded: boolean) => () => {
      setExpanded(newExpanded);
    },
    [setExpanded]
  );

  const handlePageItemClick = React.useCallback(
    (itemId: string, hasNestedNavigation: boolean) => {
      if (hasNestedNavigation && !mini) {
        setExpandedItemIds((previousValue) =>
          previousValue.includes(itemId)
            ? previousValue.filter(
                (previousValueItemId) => previousValueItemId !== itemId
              )
            : [...previousValue, itemId]
        );
      } else if (!isOverSmViewport && !hasNestedNavigation) {
        setExpanded(false);
      }
    },
    [mini, setExpanded, isOverSmViewport]
  );

  const hasDrawerTransitions =
    isOverSmViewport && (!disableCollapsibleSidebar || isOverMdViewport);

  const getDrawerContent = React.useCallback(
    (viewport: "phone" | "tablet" | "desktop") => (
      <React.Fragment>
        <Toolbar />
        <Box
          component="nav"
          aria-label={`${viewport.charAt(0).toUpperCase()}${viewport.slice(1)}`}
          sx={{
            height: "100%",
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
            overflow: "auto",
            scrollbarGutter: mini ? "stable" : "auto",
            overflowX: "hidden",
            pt: !mini ? 0 : 2,
            ...(hasDrawerTransitions
              ? getDrawerSxTransitionMixin(isFullyExpanded, "padding")
              : {}),
          }}
        >
          <List
            dense
            sx={{
              padding: mini ? 0 : 0.5,
              mb: 4,
              width: mini ? MINI_DRAWER_WIDTH : "auto",
            }}
          >
            <SidebarHeaderItem>Core Features</SidebarHeaderItem>
            <SidebarPageItem
              id="dashboard"
              title="Dashboard"
              icon={<DashboardIcon />}
              href="/dashboard"
              selected={pathname === "/dashboard" || pathname === "/"}
            />
            <SidebarDividerItem />
            <SidebarHeaderItem>Data Management</SidebarHeaderItem>
            <SidebarPageItem
              id="watchlists"
              title="Watchlists"
              icon={<WatchlistIcon />}
              href="/watchlists"
              selected={
                pathname === "/watchlists" ||
                pathname.startsWith("/watchlists/")
              }
            />
            <SidebarPageItem
              id="market-data"
              title="Market Data"
              icon={<DataObjectIcon />}
              href="/market-data"
              selected={
                pathname === "/market-data" ||
                pathname.startsWith("/market-data/")
              }
            />
            <SidebarDividerItem />
            <SidebarHeaderItem>Strategy Center</SidebarHeaderItem>
            <SidebarPageItem
              id="strategies"
              title="Strategies"
              icon={<PsychologyIcon />}
              href="/strategies"
              selected={
                pathname === "/strategies" ||
                pathname.startsWith("/strategies/")
              }
              defaultExpanded={pathname.startsWith("/strategies")}
              expanded={expandedItemIds.includes("strategies")}
              nestedNavigation={
                <List
                  dense
                  sx={{
                    padding: 0,
                    my: 1,
                    pl: mini ? 0 : 1,
                    minWidth: 240,
                  }}
                >
                  <SidebarPageItem
                    id="strategy-templates"
                    title="Templates"
                    icon={<AutoFixHighIcon />}
                    href="/strategies/templates"
                    selected={
                      pathname === "/strategies/templates" ||
                      pathname.startsWith("/strategies/templates/")
                    }
                  />
                  <SidebarPageItem
                    id="my-strategies"
                    title="My Strategies"
                    icon={<TrendingUpIcon />}
                    href="/strategies/my-strategies"
                    selected={
                      pathname === "/strategies/my-strategies" ||
                      pathname.startsWith("/strategies/my-strategies/")
                    }
                  />
                </List>
              }
            />
            <SidebarDividerItem />
            <SidebarHeaderItem>Backtesting</SidebarHeaderItem>
            <SidebarPageItem
              id="backtests"
              title="Backtests"
              icon={<PlayArrowIcon />}
              href="/backtests"
              selected={
                pathname === "/backtests" || pathname.startsWith("/backtests/")
              }
              defaultExpanded={pathname.startsWith("/backtests")}
              expanded={expandedItemIds.includes("backtests")}
              nestedNavigation={
                <List
                  dense
                  sx={{
                    padding: 0,
                    my: 1,
                    pl: mini ? 0 : 1,
                    minWidth: 240,
                  }}
                >
                  <SidebarPageItem
                    id="run-backtest"
                    title="Create New"
                    icon={<PlayArrowIcon />}
                    href="/backtests/create"
                    selected={
                      pathname === "/backtests/create" ||
                      pathname.startsWith("/backtests/create/")
                    }
                  />
                  <SidebarPageItem
                    id="run-backtest-direct"
                    title="Quick Run"
                    icon={<PlayArrowIcon />}
                    href="/backtests/run"
                    selected={
                      pathname === "/backtests/run" ||
                      pathname.startsWith("/backtests/run/")
                    }
                  />
                  <SidebarPageItem
                    id="backtest-history"
                    title="History"
                    icon={<HistoryIcon />}
                    href="/backtests/history"
                    selected={
                      pathname === "/backtests/history" ||
                      pathname.startsWith("/backtests/history/")
                    }
                  />
                </List>
              }
            />
            <SidebarPageItem
              id="analytics"
              title="Analytics"
              icon={<AnalyticsIcon />}
              href="/analytics"
              selected={
                pathname === "/analytics" || pathname.startsWith("/analytics/")
              }
            />
          </List>
        </Box>
      </React.Fragment>
    ),
    [mini, hasDrawerTransitions, isFullyExpanded, expandedItemIds, pathname]
  );

  const getDrawerSharedSx = React.useCallback(
    (isTemporary: boolean) => {
      const drawerWidth = mini ? MINI_DRAWER_WIDTH : DRAWER_WIDTH;

      return {
        displayPrint: "none",
        width: drawerWidth,
        flexShrink: 0,
        ...getDrawerWidthTransitionMixin(expanded),
        ...(isTemporary ? { position: "absolute" } : {}),
        [`& .MuiDrawer-paper`]: {
          position: "absolute",
          width: drawerWidth,
          boxSizing: "border-box",
          backgroundImage: "none",
          ...getDrawerWidthTransitionMixin(expanded),
        },
      };
    },
    [expanded, mini]
  );

  const sidebarContextValue = React.useMemo(() => {
    return {
      onPageItemClick: handlePageItemClick,
      mini,
      fullyExpanded: isFullyExpanded,
      fullyCollapsed: isFullyCollapsed,
      hasDrawerTransitions,
    };
  }, [
    handlePageItemClick,
    mini,
    isFullyExpanded,
    isFullyCollapsed,
    hasDrawerTransitions,
  ]);

  return (
    <SidebarContext.Provider value={sidebarContextValue}>
      <Drawer
        container={container}
        variant="temporary"
        open={expanded}
        onClose={handleSetSidebarExpanded(false)}
        ModalProps={{
          keepMounted: true, // Better open performance on mobile.
        }}
        sx={{
          display: {
            xs: "block",
            sm: disableCollapsibleSidebar ? "block" : "none",
            md: "none",
          },
          ...getDrawerSharedSx(true),
        }}
      >
        {getDrawerContent("phone")}
      </Drawer>
      <Drawer
        variant="permanent"
        sx={{
          display: {
            xs: "none",
            sm: disableCollapsibleSidebar ? "none" : "block",
            md: "none",
          },
          ...getDrawerSharedSx(false),
        }}
      >
        {getDrawerContent("tablet")}
      </Drawer>
      <Drawer
        variant="permanent"
        sx={{
          display: { xs: "none", md: "block" },
          ...getDrawerSharedSx(false),
        }}
      >
        {getDrawerContent("desktop")}
      </Drawer>
    </SidebarContext.Provider>
  );
}
