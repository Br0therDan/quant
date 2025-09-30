import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

/**
 * JWT 토큰 디코딩 및 검증
 */
function isTokenValid(token: string | null | undefined): boolean {
    if (!token) return false;

    try {
        // JWT 토큰 구조 확인 (header.payload.signature)
        const parts = token.split('.');
        if (parts.length !== 3) return false;

        // payload 디코딩
        const payload = JSON.parse(atob(parts[1]));

        // 만료 시간 확인
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
 * 공개 경로 목록 (인증된 사용자가 접근하면 리다이렉트)
 */
const PUBLIC_ROUTES = [
    "/login",
    "/register",
    "/auth",
];

/**
 * 루트 경로
 */
const ROOT_PATH = "/";

/**
 * 기본 리다이렉트 경로
 */
const DEFAULT_PROTECTED_REDIRECT = "/dashboard";
const DEFAULT_PUBLIC_REDIRECT = "/login";

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
 * 인증 미들웨어
 */
export function middleware(request: NextRequest) {
    const { pathname } = request.nextUrl;

    // API 경로는 처리하지 않음
    if (pathname.startsWith("/api")) {
        return NextResponse.next();
    }

    // 정적 파일은 처리하지 않음
    if (pathname.startsWith("/_next") ||
        pathname.startsWith("/favicon") ||
        pathname.includes(".")) {
        return NextResponse.next();
    }

    // 쿠키에서 토큰 확인
    const token = request.cookies.get("auth_token")?.value;
    const isAuthenticated = isTokenValid(token);

    // 루트 경로 처리
    if (pathname === ROOT_PATH) {
        if (isAuthenticated) {
            return NextResponse.redirect(
                new URL(DEFAULT_PROTECTED_REDIRECT, request.url)
            );
        } else {
            return NextResponse.redirect(
                new URL(DEFAULT_PUBLIC_REDIRECT, request.url)
            );
        }
    }

    // 보호된 경로 처리
    if (isProtectedRoute(pathname)) {
        if (!isAuthenticated) {
            // 로그인 페이지로 리다이렉트하면서 원래 경로 저장
            const loginUrl = new URL(DEFAULT_PUBLIC_REDIRECT, request.url);
            loginUrl.searchParams.set("redirect", pathname);
            return NextResponse.redirect(loginUrl);
        }
        return NextResponse.next();
    }

    // 공개 경로 처리
    if (isPublicRoute(pathname)) {
        if (isAuthenticated) {
            // 이미 로그인된 사용자는 대시보드로 리다이렉트
            const redirectTo = request.nextUrl.searchParams.get("redirect") ||
                DEFAULT_PROTECTED_REDIRECT;
            return NextResponse.redirect(new URL(redirectTo, request.url));
        }
        return NextResponse.next();
    }

    // 기타 경로는 통과
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
