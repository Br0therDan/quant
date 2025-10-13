"use client";
import SidebarContext from "@/contexts/SidebarContext";
import ListSubheader from "@mui/material/ListSubheader";
import type {} from "@mui/material/themeCssVarsAugmentation";
import * as React from "react";
import { DRAWER_WIDTH } from "./constants";
import { getDrawerSxTransitionMixin } from "./mixins";

export interface SidebarHeaderItemProps {
	children?: React.ReactNode;
}

export default function SidebarHeaderItem({
	children,
}: SidebarHeaderItemProps) {
	const sidebarContext = React.useContext(SidebarContext);
	if (!sidebarContext) {
		throw new Error("Sidebar context was used without a provider.");
	}
	const {
		mini = false,
		fullyExpanded = true,
		hasDrawerTransitions,
	} = sidebarContext;

	return (
		<ListSubheader
			sx={{
				fontSize: 13,
				fontWeight: "700",
				height: mini ? 0 : 36,
				...(hasDrawerTransitions
					? getDrawerSxTransitionMixin(fullyExpanded, "height")
					: {}),
				px: 1.5,
				py: 0,
				minWidth: DRAWER_WIDTH,
				overflow: "hidden",
				textOverflow: "ellipsis",
				whiteSpace: "nowrap",
				zIndex: 2,
			}}
		>
			{children}
		</ListSubheader>
	);
}
