"use client";

import { MyLogo } from "@/components/common/logo";
import AppTheme from "@/components/shared-theme/AppTheme";
import ColorModeSelect from "@/components/shared-theme/ColorModeSelect";
import { useRegister } from "@/hooks/useAuth";
import type { RegisterData } from "@/types/auth";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import MuiCard from "@mui/material/Card";
import Checkbox from "@mui/material/Checkbox";
import CircularProgress from "@mui/material/CircularProgress";
import CssBaseline from "@mui/material/CssBaseline";
import Divider from "@mui/material/Divider";
import FormControl from "@mui/material/FormControl";
import FormControlLabel from "@mui/material/FormControlLabel";
import FormLabel from "@mui/material/FormLabel";
import Link from "@mui/material/Link";
import Stack from "@mui/material/Stack";
import { styled } from "@mui/material/styles";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import * as React from "react";
import { FacebookIcon, GoogleIcon } from "./CustomIcons";

const Card = styled(MuiCard)(({ theme }) => ({
  display: "flex",
  flexDirection: "column",
  alignSelf: "center",
  width: "100%",
  padding: theme.spacing(4),
  gap: theme.spacing(2),
  boxShadow:
    "hsla(220, 30%, 5%, 0.05) 0px 5px 15px 0px, hsla(220, 25%, 10%, 0.05) 0px 15px 35px -5px",
  [theme.breakpoints.up("sm")]: {
    width: "450px",
  },
  ...theme.applyStyles("dark", {
    boxShadow:
      "hsla(220, 30%, 5%, 0.5) 0px 5px 15px 0px, hsla(220, 25%, 10%, 0.08) 0px 15px 35px -5px",
  }),
}));

const SignUpContainer = styled(Stack)(({ theme }) => ({
  height: "calc((1 - var(--template-frame-height, 0)) * 100dvh)",
  minHeight: "100%",
  padding: theme.spacing(2),
  [theme.breakpoints.up("sm")]: {
    padding: theme.spacing(4),
  },
  "&::before": {
    content: '""',
    display: "block",
    position: "absolute",
    zIndex: -1,
    inset: 0,
    backgroundImage:
      "radial-gradient(ellipse at 50% 50%, hsl(210, 100%, 97%), hsl(0, 0%, 100%))",
    backgroundRepeat: "no-repeat",
    ...theme.applyStyles("dark", {
      backgroundImage:
        "radial-gradient(at 50% 50%, hsla(210, 100%, 16%, 0.5), hsl(220, 30%, 5%))",
    }),
  },
}));

export default function SignUpCard(props: { disableCustomTheme?: boolean }) {
  const [fullname, setFullname] = React.useState("");
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [confirmPassword, setConfirmPassword] = React.useState("");
  const [agreeToTerms, setAgreeToTerms] = React.useState(false);

  const [fullnameError, setFullnameError] = React.useState(false);
  const [fullnameErrorMessage, setFullnameErrorMessage] = React.useState("");
  const [emailError, setEmailError] = React.useState(false);
  const [emailErrorMessage, setEmailErrorMessage] = React.useState("");
  const [passwordError, setPasswordError] = React.useState(false);
  const [passwordErrorMessage, setPasswordErrorMessage] = React.useState("");
  const [confirmPasswordError, setConfirmPasswordError] = React.useState(false);
  const [confirmPasswordErrorMessage, setConfirmPasswordErrorMessage] =
    React.useState("");

  const { register, isLoading, error } = useRegister();
  // const { isAuthenticated } = useAuthStatus();

  // 이미 로그인된 경우 리다이렉트
  // React.useEffect(() => {
  //   if (isAuthenticated) {
  //     // URL 파라미터에서 redirect 값 가져오기
  //     const urlParams = new URLSearchParams(window.location.search);
  //     const redirectUrl = urlParams.get("redirect") || "/dashboard";
  //     console.log("Register successful, redirecting to:", redirectUrl);

  //     // router.push가 작동하지 않으므로 window.location.href 사용
  //     setTimeout(() => {
  //       window.location.href = redirectUrl;
  //     }, 100); // 약간의 지연을 추가하여 state 업데이트 완료 보장
  //   }
  // }, [isAuthenticated]);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!validateInputs()) {
      return;
    }

    try {
      await register({
        email,
        password,
        fullname: fullname || undefined,
      } as RegisterData);
      // 성공 시 useAuthStatus의 useEffect에서 자동으로 리다이렉트됨
    } catch (err) {
      // 에러는 useRegister에서 자동으로 처리됨
      console.error("Registration failed:", err);
    }
  };

  const validateInputs = () => {
    let isValid = true;

    // 이름 검증 (선택사항)
    if (fullname && fullname.length < 2) {
      setFullnameError(true);
      setFullnameErrorMessage("이름은 2자 이상이어야 합니다.");
      isValid = false;
    } else {
      setFullnameError(false);
      setFullnameErrorMessage("");
    }

    // 이메일 검증
    if (!email || !/\S+@\S+\.\S+/.test(email)) {
      setEmailError(true);
      setEmailErrorMessage("올바른 이메일 주소를 입력해주세요.");
      isValid = false;
    } else {
      setEmailError(false);
      setEmailErrorMessage("");
    }

    // 비밀번호 검증
    if (!password || password.length < 8) {
      setPasswordError(true);
      setPasswordErrorMessage("비밀번호는 최소 8자 이상이어야 합니다.");
      isValid = false;
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])/.test(password)) {
      setPasswordError(true);
      setPasswordErrorMessage(
        "비밀번호는 대문자, 소문자, 숫자를 포함해야 합니다."
      );
      isValid = false;
    } else {
      setPasswordError(false);
      setPasswordErrorMessage("");
    }

    // 비밀번호 확인 검증
    if (!confirmPassword || confirmPassword !== password) {
      setConfirmPasswordError(true);
      setConfirmPasswordErrorMessage("비밀번호가 일치하지 않습니다.");
      isValid = false;
    } else {
      setConfirmPasswordError(false);
      setConfirmPasswordErrorMessage("");
    }

    // 약관 동의 검증
    if (!agreeToTerms) {
      alert("이용약관에 동의해주세요.");
      isValid = false;
    }

    return isValid;
  };

  return (
    <AppTheme {...props}>
      <CssBaseline enableColorScheme />
      <ColorModeSelect sx={{ position: "fixed", top: "1rem", right: "1rem" }} />
      <SignUpContainer direction="column" justifyContent="space-between">
        <Card variant="outlined">
          <MyLogo />
          <Typography
            component="h1"
            variant="h4"
            sx={{ width: "100%", fontSize: "clamp(2rem, 10vw, 2.15rem)" }}
          >
            Sign up
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              회원가입에 실패했습니다. 입력 정보를 확인해주세요.
            </Alert>
          )}

          <Box
            component="form"
            onSubmit={handleSubmit}
            noValidate
            sx={{
              display: "flex",
              flexDirection: "column",
              width: "100%",
              gap: 2,
            }}
          >
            <FormControl>
              <FormLabel htmlFor="fullname">이름 (선택사항)</FormLabel>
              <TextField
                error={fullnameError}
                helperText={fullnameErrorMessage}
                name="fullname"
                placeholder="홍길동"
                type="text"
                autoComplete="name"
                autoFocus
                fullWidth
                variant="outlined"
                color={fullnameError ? "error" : "primary"}
                value={fullname}
                onChange={(e) => setFullname(e.target.value)}
                disabled={isLoading}
              />
            </FormControl>

            <FormControl>
              <FormLabel htmlFor="email">이메일</FormLabel>
              <TextField
                error={emailError}
                helperText={emailErrorMessage}
                name="email"
                placeholder="your@email.com"
                type="email"
                autoComplete="email"
                required
                fullWidth
                variant="outlined"
                color={emailError ? "error" : "primary"}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={isLoading}
              />
            </FormControl>

            <FormControl>
              <FormLabel htmlFor="password">비밀번호</FormLabel>
              <TextField
                error={passwordError}
                helperText={passwordErrorMessage}
                name="password"
                placeholder="••••••••"
                type="password"
                autoComplete="new-password"
                required
                fullWidth
                variant="outlined"
                color={passwordError ? "error" : "primary"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isLoading}
              />
            </FormControl>

            <FormControl>
              <FormLabel htmlFor="confirmPassword">비밀번호 확인</FormLabel>
              <TextField
                error={confirmPasswordError}
                helperText={confirmPasswordErrorMessage}
                name="confirmPassword"
                placeholder="••••••••"
                type="password"
                autoComplete="new-password"
                required
                fullWidth
                variant="outlined"
                color={confirmPasswordError ? "error" : "primary"}
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                disabled={isLoading}
              />
            </FormControl>

            <FormControlLabel
              control={
                <Checkbox
                  color="primary"
                  checked={agreeToTerms}
                  onChange={(e) => setAgreeToTerms(e.target.checked)}
                  disabled={isLoading}
                />
              }
              label={
                <Typography variant="body2">
                  <Link href="/terms" target="_blank">
                    이용약관
                  </Link>{" "}
                  및{" "}
                  <Link href="/privacy" target="_blank">
                    개인정보처리방침
                  </Link>
                  에 동의합니다.
                </Typography>
              }
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              disabled={isLoading}
              sx={{ mt: 3, mb: 2 }}
            >
              {isLoading ? (
                <CircularProgress size={24} color="inherit" />
              ) : (
                "회원가입"
              )}
            </Button>

            <Typography sx={{ textAlign: "center" }}>
              이미 계정이 있으신가요?{" "}
              <span>
                <Link
                  href="/login"
                  variant="body2"
                  sx={{ alignSelf: "center" }}
                >
                  로그인
                </Link>
              </span>
            </Typography>
          </Box>

          <Divider>또는</Divider>

          <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
            <Button
              fullWidth
              variant="outlined"
              onClick={() => alert("Google 회원가입 기능 구현 예정")}
              startIcon={<GoogleIcon />}
              disabled={isLoading}
            >
              Google로 회원가입
            </Button>
            <Button
              fullWidth
              variant="outlined"
              onClick={() => alert("Facebook 회원가입 기능 구현 예정")}
              startIcon={<FacebookIcon />}
              disabled={isLoading}
            >
              Facebook으로 회원가입
            </Button>
          </Box>
        </Card>
      </SignUpContainer>
    </AppTheme>
  );
}
