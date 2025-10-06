import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

/**
 * HTTPOnly 쿠키의 JWT 토큰 검증 - 간소화된 버전
 */
function isTokenValid(request: NextRequest): boolean {
    const token = request.cookies.get("access_token")?.value;

    if (!token) {
        return false;
    }

    try {
        // JWT 토큰 구조 확인 (header.payload.signature)
        const parts = token.split('.');
        if (parts.length !== 3) {
            return false;
        }

        // payload 디코딩 및 만료 시간 확인
        const payload = JSON.parse(atob(parts[1]));
        if (payload.exp && payload.exp * 1000 < Date.now()) {
            return false;
        }

        return true;
    } catch {
        return false;
    }
}

/**
 * 보호된 경로 목록
 */
const PROTECTED_ROUTES = [
    "/dashboard",
    "/backtests",
    "/strategies",
    "/portfolio",
    "/profile",
    "/settings",
];

/**
 * 공개 경로 목록
 */
const PUBLIC_ROUTES = [
    "/login",
    "/register",
    "/auth/login",
    "/auth/register",
    "/auth",
];

/**
 * 경로가 보호된 경로인지 확인
 */
function isProtectedRoute(pathname: string): boolean {
    return PROTECTED_ROUTES.some(route => pathname.startsWith(route));
}

/**
 * 경로가 공개 경로인지 확인
 */
function isPublicRoute(pathname: string): boolean {
    return PUBLIC_ROUTES.some(route => pathname.startsWith(route));
}

/**
 * 간소화된 인증 미들웨어 - 리다이렉트 최소화로 쿠키 보존
 */
export function middleware(request: NextRequest) {
    const { pathname } = request.nextUrl;

    // API 경로와 정적 파일은 처리하지 않음
    if (pathname.startsWith("/api") ||
        pathname.startsWith("/_next") ||
        pathname.startsWith("/favicon") ||
        pathname.includes(".")) {
        return NextResponse.next();
    }

    const isAuthenticated = isTokenValid(request);

    // 루트 경로는 클라이언트에서 처리하도록 통과 (리다이렉트로 인한 쿠키 손실 방지)
    if (pathname === "/") {
        return NextResponse.next();
    }

    // 보호된 경로 처리 - 인증되지 않은 경우만 리다이렉트
    if (isProtectedRoute(pathname)) {
        if (!isAuthenticated) {
            const loginUrl = new URL("/login", request.url);
            loginUrl.searchParams.set("redirect", pathname);
            return NextResponse.redirect(loginUrl);
        }
        return NextResponse.next();
    }

    // 공개 경로는 모두 통과 (클라이언트에서 인증된 사용자 처리)
    if (isPublicRoute(pathname)) {
        return NextResponse.next();
    }

    // 기타 모든 경로는 통과
    return NextResponse.next();
}

/**
 * 미들웨어가 실행될 경로 매칭 설정
 */
export const config = {
    matcher: [
        /*
         * 다음을 제외한 모든 요청에 매칭:
         * - api (API routes)
         * - _next/static (static files)
         * - _next/image (image optimization files)
         * - favicon.ico (favicon file)
         * - 파일 확장자가 있는 경로
         */
        "/((?!api|_next/static|_next/image|favicon.ico).*)",
    ],
};
