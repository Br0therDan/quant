"use client";
import MenuIcon from "@mui/icons-material/Menu";
import MenuOpenIcon from "@mui/icons-material/MenuOpen";
import MuiAppBar from "@mui/material/AppBar";
import Box from "@mui/material/Box";
import IconButton from "@mui/material/IconButton";
import Stack from "@mui/material/Stack";
import { styled, useTheme } from "@mui/material/styles";
import Toolbar from "@mui/material/Toolbar";
import Tooltip from "@mui/material/Tooltip";
import Typography from "@mui/material/Typography";
import Link from "next/link";
import * as React from "react";
import UserAvatars from './UserButton';
import ColorModeIconDropdown from '../shared-theme/ColorModeIconDropdown';

const AppBar = styled(MuiAppBar)(({ theme }) => ({
	borderWidth: 0,
	borderBottomWidth: 1,
	borderStyle: "solid",
	borderColor: (theme.vars ?? theme).palette.divider,
	boxShadow: "none",
	zIndex: theme.zIndex.drawer + 1,
}));

const LogoContainer = styled(Box)({
	display: "flex",
	height: 45,
	alignItems: "center",
	"& img": {
		maxHeight: 45,
		width: 100
	},
});

export interface HeaderProps {
	logo?: React.ReactNode;
	title?: string;
	menuOpen: boolean;
	onToggleMenu: (open: boolean) => void;
}

export default function Header({
	logo,
	title,
	menuOpen,
	onToggleMenu,
}: HeaderProps) {
	const theme = useTheme();

	const handleMenuOpen = React.useCallback(() => {
		onToggleMenu(!menuOpen);
	}, [menuOpen, onToggleMenu]);

	const getMenuIcon = React.useCallback(
		(isExpanded: boolean) => {
			const expandMenuActionText = "Expand";
			const collapseMenuActionText = "Collapse";

			return (
				<Tooltip
					title={`${
						isExpanded ? collapseMenuActionText : expandMenuActionText
					} menu`}
					enterDelay={1000}
				>
					<div>
						<IconButton
							size="small"
							aria-label={`${
								isExpanded ? collapseMenuActionText : expandMenuActionText
							} navigation menu`}
							onClick={handleMenuOpen}
						>
							{isExpanded ? <MenuOpenIcon /> : <MenuIcon />}
						</IconButton>
					</div>
				</Tooltip>
			);
		},
		[handleMenuOpen],
	);

	return (
		<AppBar color="inherit" position="fixed" sx={{ displayPrint: "none", height: 60 }}>
			<Toolbar sx={{ mx: { xs: -0.75, sm: -1 } }}>
				<Stack
					direction="row"
					justifyContent="space-between"
					alignItems="center"
					sx={{
						flexWrap: "wrap",
						width: "100%",
					}}
				>
					<Stack direction="row" alignItems="center">
						<Box sx={{ mr: 1 }}>{getMenuIcon(menuOpen)}</Box>
						<Link href="/" style={{ textDecoration: "none" }}>
							<Stack direction="row" alignItems="center">
								{logo ? <LogoContainer>{logo}</LogoContainer> : null}
								{title ? (
									<Typography
										variant="h6"
										sx={{
											color: (theme.vars ?? theme).palette.primary.main,
											fontWeight: "700",
											ml: 1,
											whiteSpace: "nowrap",
											lineHeight: 1,
										}}
									>
										{title}
									</Typography>
								) : null}
							</Stack>
						</Link>
					</Stack>
					<Stack
						direction="row"
						alignItems="center"
						spacing={1}
						sx={{ marginLeft: "auto" }}
					>
						<Stack direction="row" alignItems="center">
							<ColorModeIconDropdown />
						</Stack>
						<Stack direction="row" alignItems="center">
							<UserAvatars />
						</Stack>
					</Stack>
				</Stack>
			</Toolbar>
		</AppBar>
	);
}
