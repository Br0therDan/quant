"use client";
// Icons for quant platform
import SidebarContext from "@/contexts/SidebarContext";
import AnalyticsIcon from "@mui/icons-material/Analytics";
import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome";
import ChatIcon from "@mui/icons-material/Chat";
import DashboardIcon from "@mui/icons-material/Dashboard";
import DataObjectIcon from "@mui/icons-material/DataObject";
import DescriptionIcon from "@mui/icons-material/Description";
import HistoryIcon from "@mui/icons-material/History";
import ModelTrainingIcon from "@mui/icons-material/ModelTraining";
import MonitorHeartIcon from "@mui/icons-material/MonitorHeart";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import PsychologyIcon from "@mui/icons-material/Psychology";
import SecurityIcon from "@mui/icons-material/Security";
import StorageIcon from "@mui/icons-material/Storage";
import TimelineIcon from "@mui/icons-material/Timeline";
import TuneIcon from "@mui/icons-material/Tune";
import WatchlistIcon from "@mui/icons-material/Visibility";
import WarningIcon from "@mui/icons-material/Warning";
import Box from "@mui/material/Box";
import Drawer from "@mui/material/Drawer";
import List from "@mui/material/List";
import { useTheme } from "@mui/material/styles";
import type {} from "@mui/material/themeCssVarsAugmentation";
import Toolbar from "@mui/material/Toolbar";
import useMediaQuery from "@mui/material/useMediaQuery";
import { usePathname } from "next/navigation";
import * as React from "react";
import { DRAWER_WIDTH, MINI_DRAWER_WIDTH } from "./constants";
import {
  getDrawerSxTransitionMixin,
  getDrawerWidthTransitionMixin,
} from "./mixins";
import SidebarDividerItem from "./SidebarDividerItem";
import SidebarHeaderItem from "./SidebarHeaderItem";
import SidebarPageItem from "./SidebarPageItem";

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
            <SidebarHeaderItem>Market Data</SidebarHeaderItem>
            <SidebarPageItem
              id="market-data-stock"
              title="Stock"
              icon={<WatchlistIcon />}
              href="/market-data/stock"
              selected={
                pathname === "/market-data/stock" ||
                pathname.startsWith("/market-data/stock/")
              }
            />
            <SidebarPageItem
              id="market-data-crypto"
              title="Crypto"
              icon={<DataObjectIcon />}
              href="/market-data/crypto"
              selected={
                pathname === "/market-data/crypto" ||
                pathname.startsWith("/market-data/crypto/")
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
            <SidebarDividerItem />
            <SidebarHeaderItem>MLOps</SidebarHeaderItem>
            <SidebarPageItem
              id="mlops-feature-store"
              title="Feature Store"
              icon={<StorageIcon />}
              href="/mlops/feature-store"
              selected={
                pathname === "/mlops/feature-store" ||
                pathname.startsWith("/mlops/feature-store/")
              }
            />
            <SidebarPageItem
              id="mlops-model-lifecycle"
              title="Model Lifecycle"
              icon={<ModelTrainingIcon />}
              href="/mlops/model-lifecycle"
              selected={
                pathname === "/mlops/model-lifecycle" ||
                pathname.startsWith("/mlops/model-lifecycle/")
              }
            />
            <SidebarPageItem
              id="mlops-evaluation"
              title="Evaluation"
              icon={<AnalyticsIcon />}
              href="/mlops/evaluation"
              selected={
                pathname === "/mlops/evaluation" ||
                pathname.startsWith("/mlops/evaluation/")
              }
            />
            <SidebarDividerItem />
            <SidebarHeaderItem>GenAI</SidebarHeaderItem>
            <SidebarPageItem
              id="gen-ai-chatops"
              title="ChatOps"
              icon={<ChatIcon />}
              href="/gen-ai/chatops"
              selected={
                pathname === "/gen-ai/chatops" ||
                pathname.startsWith("/gen-ai/chatops/")
              }
            />
            <SidebarPageItem
              id="gen-ai-strategy-builder"
              title="Strategy Builder"
              icon={<AutoAwesomeIcon />}
              href="/gen-ai/strategy-builder"
              selected={
                pathname === "/gen-ai/strategy-builder" ||
                pathname.startsWith("/gen-ai/strategy-builder/")
              }
            />
            <SidebarPageItem
              id="gen-ai-narrative-reports"
              title="Narrative Reports"
              icon={<DescriptionIcon />}
              href="/gen-ai/narrative-reports"
              selected={
                pathname === "/gen-ai/narrative-reports" ||
                pathname.startsWith("/gen-ai/narrative-reports/")
              }
            />
            <SidebarPageItem
              id="gen-ai-prompt-governance"
              title="Prompt Governance"
              icon={<SecurityIcon />}
              href="/gen-ai/prompt-governance"
              selected={
                pathname === "/gen-ai/prompt-governance" ||
                pathname.startsWith("/gen-ai/prompt-governance/")
              }
            />
            <SidebarPageItem
              id="gen-ai-compliance"
              title="Compliance"
              icon={<SecurityIcon />}
              href="/gen-ai/compliance"
              selected={
                pathname === "/gen-ai/compliance" ||
                pathname.startsWith("/gen-ai/compliance/")
              }
            />
            <SidebarPageItem
              id="gen-ai-risk-insights"
              title="Risk Insights"
              icon={<WarningIcon />}
              href="/gen-ai/risk-insights"
              selected={
                pathname === "/gen-ai/risk-insights" ||
                pathname.startsWith("/gen-ai/risk-insights/")
              }
            />
            <SidebarDividerItem />
            <SidebarHeaderItem>Optimization</SidebarHeaderItem>
            <SidebarPageItem
              id="optimization-hyperparameter-tuning"
              title="Hyperparameter Tuning"
              icon={<TuneIcon />}
              href="/optimization/hyperparameter-tuning"
              selected={
                pathname === "/optimization/hyperparameter-tuning" ||
                pathname.startsWith("/optimization/hyperparameter-tuning/")
              }
            />
            <SidebarPageItem
              id="optimization-cost-optimizer"
              title="Cost Optimizer"
              icon={<MonitorHeartIcon />}
              href="/optimization/cost-optimizer"
              selected={
                pathname === "/optimization/cost-optimizer" ||
                pathname.startsWith("/optimization/cost-optimizer/")
              }
            />
            <SidebarDividerItem />
            <SidebarHeaderItem>Data Quality</SidebarHeaderItem>
            <SidebarPageItem
              id="data-quality-monitor"
              title="Monitor"
              icon={<MonitorHeartIcon />}
              href="/data-quality/monitor"
              selected={
                pathname === "/data-quality/monitor" ||
                pathname.startsWith("/data-quality/monitor/")
              }
            />
            <SidebarPageItem
              id="data-quality-lineage-tracker"
              title="Lineage Tracker"
              icon={<TimelineIcon />}
              href="/data-quality/lineage-tracker"
              selected={
                pathname === "/data-quality/lineage-tracker" ||
                pathname.startsWith("/data-quality/lineage-tracker/")
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
