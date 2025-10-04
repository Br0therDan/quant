import type { CreateClientConfig } from "./client/client.gen";

/**
 * 쿠키에서 토큰 가져오기 (클라이언트 사이드)
 */
function getTokenFromCookie(): string | null {
	if (typeof window === "undefined") return null;

	const cookies = document.cookie
		.split(";")
		.map((cookie) => cookie.trim())
		.find((cookie) => cookie.startsWith("access_token"));

	return cookies ? cookies.split("=")[1] : null;
}

export const createClientConfig: CreateClientConfig = (config) => ({
	...config,
	baseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8500",
	interceptors: {
		request: [
			{
				onFulfilled: (request: any) => {
					// 인증 토큰 자동 추가
					const token = getTokenFromCookie();
					if (token && request.headers) {
						request.headers.set('Authorization', `Bearer ${token}`);
					}
					return request;
				},
			},
		],
		response: [
			{
				onRejected: (error: any) => {
					// 401 에러 시 로그아웃 처리
					if (error.status === 401) {
						// 토큰 쿠키 삭제
						if (typeof window !== "undefined") {
							document.cookie = 'access_token=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT; SameSite=Strict;';
							// 로그인 페이지로 리다이렉트 (필요시)
							window.location.href = '/auth/login';
						}
					}
					return Promise.reject(error);
				},
			},
		],
	},
});
