"use client";
import type { BodyAuthLogin } from "@/client";
import { MyLogo } from "@/components/common/logo";
import { useAuth } from "@/hooks/useAuth";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import MuiCard from "@mui/material/Card";
import CircularProgress from "@mui/material/CircularProgress";
import Divider from "@mui/material/Divider";
import FormControl from "@mui/material/FormControl";
import FormLabel from "@mui/material/FormLabel";
import Link from "@mui/material/Link";
import { styled } from "@mui/material/styles";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import * as React from "react";
import { FacebookIcon, GoogleIcon } from "./CustomIcons";
import ForgotPassword from "./ForgotPassword";

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

export default function SignInCard() {
	const [email, setEmail] = React.useState("");
	const [password, setPassword] = React.useState("");
	const [emailError, setEmailError] = React.useState(false);
	const [emailErrorMessage, setEmailErrorMessage] = React.useState("");
	const [passwordError, setPasswordError] = React.useState(false);
	const [passwordErrorMessage, setPasswordErrorMessage] = React.useState("");
	const [open, setOpen] = React.useState(false);
	const [mounted, setMounted] = React.useState(false);

	const { login, isLoading } = useAuth();
	const [loginError, setLoginError] = React.useState<string | null>(null);

	// hydration mismatch 방지
	React.useEffect(() => {
		setMounted(true);
	}, []);

	// 서버 사이드에서는 항상 loading 상태가 false
	const actualIsLoading = mounted ? isLoading : false;

	const handleClickOpen = () => {
		setOpen(true);
	};

	const handleClose = () => {
		setOpen(false);
	};

	const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
		event.preventDefault();

		if (!validateInputs()) {
			return;
		}

		setLoginError(null); // 이전 에러 초기화

		try {
			await login({ username: email, password } as BodyAuthLogin);

			// 로그인 성공 후 리다이렉트 처리는 AuthContext에서 자동으로 수행됨
			// AuthContext는 URL 쿼리 파라미터나 기본값으로 리다이렉트
			console.log("[Auth] 로그인 성공 - AuthContext에서 리다이렉트 처리");
		} catch (error) {
			console.error("[Auth] 로그인 처리 중 오류:", error);
			// 에러 메시지 설정
			if (error instanceof Error) {
				setLoginError(error.message);
			} else {
				setLoginError("로그인에 실패했습니다. 다시 시도해주세요.");
			}
		}
	};

	const validateInputs = () => {
		let isValid = true;

		if (!email || !/\S+@\S+\.\S+/.test(email)) {
			setEmailError(true);
			setEmailErrorMessage("올바른 이메일 주소를 입력해주세요.");
			isValid = false;
		} else {
			setEmailError(false);
			setEmailErrorMessage("");
		}

		if (!password || password.length < 6) {
			setPasswordError(true);
			setPasswordErrorMessage("비밀번호는 최소 6자 이상이어야 합니다.");
			isValid = false;
		} else {
			setPasswordError(false);
			setPasswordErrorMessage("");
		}

		return isValid;
	};

	return (
		<Card variant="outlined">
			<Box sx={{ display: { xs: "flex", md: "none" } }}>
				<MyLogo icon noLink width={40} height={40} />
			</Box>
			<Typography
				component="h1"
				variant="h4"
				sx={{ width: "100%", fontSize: "clamp(2rem, 10vw, 2.15rem)" }}
			>
				로그인
			</Typography>

			{loginError && (
				<Alert severity="error" sx={{ mb: 2 }}>
					{loginError.includes("401") || loginError.includes("Unauthorized")
						? "이메일 또는 비밀번호가 올바르지 않습니다."
						: loginError.includes("Network")
							? "네트워크 연결을 확인해주세요."
							: loginError}
				</Alert>
			)}
			<Box
				component="form"
				onSubmit={handleSubmit}
				noValidate
				sx={{ display: "flex", flexDirection: "column", width: "100%", gap: 2 }}
			>
				<FormControl>
					<FormLabel htmlFor="email">이메일</FormLabel>
					<TextField
						error={emailError}
						helperText={emailErrorMessage}
						type="email"
						name="email"
						placeholder="your@email.com"
						autoComplete="email"
						autoFocus
						required
						fullWidth
						variant="outlined"
						color={emailError ? "error" : "primary"}
						value={email}
						onChange={(e) => setEmail(e.target.value)}
						disabled={actualIsLoading}
					/>
				</FormControl>
				<FormControl>
					<Box sx={{ display: "flex", justifyContent: "space-between" }}>
						<FormLabel htmlFor="password">비밀번호</FormLabel>
						<Link
							component="button"
							type="button"
							onClick={handleClickOpen}
							variant="body2"
							sx={{ alignSelf: "baseline" }}
						>
							비밀번호를 잊으셨나요?
						</Link>
					</Box>
					<TextField
						error={passwordError}
						helperText={passwordErrorMessage}
						name="password"
						placeholder="••••••"
						type="password"
						autoComplete="current-password"
						required
						fullWidth
						variant="outlined"
						color={passwordError ? "error" : "primary"}
						value={password}
						onChange={(e) => setPassword(e.target.value)}
						disabled={actualIsLoading}
					/>
				</FormControl>
				<ForgotPassword open={open} handleClose={handleClose} />
				<Button
					type="submit"
					fullWidth
					variant="contained"
					disabled={actualIsLoading}
					sx={{ mt: 3, mb: 2 }}
				>
					{actualIsLoading ? (
						<CircularProgress size={24} color="inherit" />
					) : (
						"로그인"
					)}
				</Button>
				<Typography sx={{ textAlign: "center" }}>
					계정이 없으신가요?{" "}
					<span>
						<Link
							href="/auth/register"
							variant="body2"
							sx={{ alignSelf: "center" }}
						>
							회원가입
						</Link>
					</span>
				</Typography>
			</Box>
			<Divider>또는</Divider>
			<Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
				<Button
					fullWidth
					variant="outlined"
					onClick={() => alert("Google 로그인 기능 구현 예정")}
					startIcon={<GoogleIcon />}
					disabled={actualIsLoading}
				>
					Google로 로그인
				</Button>
				<Button
					fullWidth
					variant="outlined"
					onClick={() => alert("Facebook 로그인 기능 구현 예정")}
					startIcon={<FacebookIcon />}
					disabled={actualIsLoading}
				>
					Facebook으로 로그인
				</Button>
			</Box>
		</Card>
	);
}
