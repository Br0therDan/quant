"use client";

import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import CircularProgress from "@mui/material/CircularProgress";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import TextField from "@mui/material/TextField";
import * as React from "react";

interface ForgotPasswordProps {
  open: boolean;
  handleClose: () => void;
}

// TODO: useAuth에 useForgotPassword 훅 추가하고 실제 구현으로 교체
const useForgotPassword = () => {
  const [isLoading, setIsLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const forgotPassword = async (email: string) => {
    setIsLoading(true);
    setError(null);
    try {
      // Mock implementation - API 연동 필요
      await new Promise((resolve) => setTimeout(resolve, 1000));
      console.log("Password reset requested for:", email);
    } catch (err) {
      setError("비밀번호 재설정에 실패했습니다.");
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return { forgotPassword, isLoading, error };
};

export default function ForgotPassword({
  open,
  handleClose: onClose,
}: ForgotPasswordProps) {
  const [email, setEmail] = React.useState("");
  const [emailError, setEmailError] = React.useState(false);
  const [emailErrorMessage, setEmailErrorMessage] = React.useState("");
  const [success, setSuccess] = React.useState(false);
  const emailId = React.useId();

  const { forgotPassword, isLoading, error } = useForgotPassword();

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!validateEmail()) {
      return;
    }

    try {
      await forgotPassword(email);
      setSuccess(true);
    } catch (err) {
      console.error("Password reset failed:", err);
    }
  };

  const validateEmail = () => {
    if (!email || !/\S+@\S+\.\S+/.test(email)) {
      setEmailError(true);
      setEmailErrorMessage("올바른 이메일 주소를 입력해주세요.");
      return false;
    }
    setEmailError(false);
    setEmailErrorMessage("");
    return true;
  };

  const handleClose = () => {
    setEmail("");
    setEmailError(false);
    setEmailErrorMessage("");
    setSuccess(false);
    onClose();
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: { backgroundImage: "none" },
      }}
    >
      <form onSubmit={handleSubmit}>
        <DialogTitle>비밀번호 재설정</DialogTitle>
        <DialogContent
          sx={{
            display: "flex",
            flexDirection: "column",
            gap: 2,
            width: "100%",
          }}
        >
          {success ? (
            <Alert severity="success">
              비밀번호 재설정 링크를 이메일로 발송했습니다. 이메일을
              확인해주세요.
            </Alert>
          ) : (
            <>
              <DialogContentText>
                계정의 이메일 주소를 입력하시면, 비밀번호 재설정 링크를
                발송해드립니다.
              </DialogContentText>

              {error && <Alert severity="error">{error}</Alert>}

              <TextField
                autoFocus
                required
                margin="dense"
                id={emailId}
                name="email"
                label="이메일 주소"
                placeholder="your@email.com"
                type="email"
                fullWidth
                variant="outlined"
                error={emailError}
                helperText={emailErrorMessage}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={isLoading}
              />
            </>
          )}
        </DialogContent>
        <DialogActions sx={{ pb: 3, px: 3 }}>
          <Button onClick={handleClose} disabled={isLoading}>
            {success ? "확인" : "취소"}
          </Button>
          {!success && (
            <Button variant="contained" type="submit" disabled={isLoading}>
              {isLoading ? (
                <CircularProgress size={20} color="inherit" />
              ) : (
                "전송"
              )}
            </Button>
          )}
        </DialogActions>
      </form>
    </Dialog>
  );
}
