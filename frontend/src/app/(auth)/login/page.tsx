"use client";

import SignIn from "@/components/auth/SignIn";
import { Box } from "@mui/material";

export default function LoginPage() {
  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        px: 2,
      }}
    >
      <SignIn />
    </Box>
  );
}
