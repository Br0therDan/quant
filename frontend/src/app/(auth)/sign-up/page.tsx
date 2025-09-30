"use client";

import SignUp from "@/components/auth/SignUp";
import Box from "@mui/material/Box";

export default function SignUpPage() {
  return (
    <Box
      sx={{
        height: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <SignUp />
    </Box>
  );
}
