"use client";

import type { UserRead } from "@/client";
import type {
  AuthContextType,
  LoginCredentials,
  RegisterData,
} from "@/types/auth";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { createContext, useCallback, useContext, type ReactNode } from "react";

/**
 * 인증 컨텍스트
 */
export const AuthContext = createContext<AuthContextType | undefined>(
  undefined
);

/**
 * 쿠키에서 토큰 가져오기 (클라이언트 사이드)
 */
function getTokenFromCookie(): string | null {
  if (typeof window === "undefined") return null;

  const cookies = document.cookie
    .split(";")
    .map((cookie) => cookie.trim())
    .find((cookie) => cookie.startsWith("auth_token="));

  return cookies ? cookies.split("=")[1] : null;
}

/**
 * Route Handler API 호출 함수들
 */

/**
 * 로그인 API 호출
 */
async function loginApi(credentials: LoginCredentials) {
  const response = await fetch("/api/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({
      username: credentials.email,
      password: credentials.password,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "로그인에 실패했습니다.");
  }

  return response.json();
}

/**
 * 로그아웃 API 호출
 */
async function logoutApi() {
  const response = await fetch("/api/auth/logout", {
    method: "POST",
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "로그아웃에 실패했습니다.");
  }

  return response.json();
}

/**
 * 현재 사용자 정보 API 호출
 */
async function getCurrentUserApi(): Promise<UserRead> {
  const response = await fetch("/api/auth/user", {
    method: "GET",
  });

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error("인증이 필요합니다.");
    }
    const error = await response.json();
    throw new Error(error.detail || "사용자 정보를 가져올 수 없습니다.");
  }

  return response.json();
}

/**
 * 회원가입 API 호출 (백엔드 직접 호출)
 */
async function registerApi(data: RegisterData) {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/auth/register`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "회원가입에 실패했습니다.");
  }

  return response.json();
}

/**
 * AuthProvider Props
 */
interface AuthProviderProps {
  children: ReactNode;
}

/**
 * 통합된 AuthProvider 컴포넌트
 */
export function AuthProvider({ children }: AuthProviderProps) {
  const queryClient = useQueryClient();
  const router = useRouter();

  // 현재 사용자 정보 쿼리
  const { data: user, isLoading } = useQuery({
    queryKey: ["auth", "user"],
    queryFn: getCurrentUserApi,
    retry: false,
    staleTime: 5 * 60 * 1000, // 5분
    gcTime: 10 * 60 * 1000, // 10분
  });

  // 로그인 뮤테이션
  const loginMutation = useMutation({
    mutationFn: loginApi,
    onSuccess: () => {
      console.log("Login successful");

      // 사용자 정보 쿼리 무효화 및 재조회
      queryClient.invalidateQueries({
        queryKey: ["auth", "user"],
      });

      // 대시보드로 리다이렉트
      router.push("/dashboard");
    },
    onError: (error) => {
      console.error("Login failed:", error);
      // 실패시 캐시 정리
      queryClient.removeQueries({
        queryKey: ["auth", "user"],
      });
    },
  });

  // 로그아웃 뮤테이션
  const logoutMutation = useMutation({
    mutationFn: logoutApi,
    onSettled: () => {
      // 성공/실패 관계없이 클라이언트 상태 정리
      queryClient.clear(); // 모든 쿼리 캐시 정리
      router.push("/login");
    },
  });

  // 회원가입 뮤테이션
  const registerMutation = useMutation({
    mutationFn: registerApi,
    onSuccess: () => {
      // 회원가입 성공 후 사용자 정보 쿼리 무효화
      queryClient.invalidateQueries({
        queryKey: ["auth", "user"],
      });
    },
  });

  // 사용자 정보 갱신 뮤테이션
  const refreshUserMutation = useMutation({
    mutationFn: getCurrentUserApi,
    onSuccess: (userData) => {
      // 쿼리 캐시 업데이트
      queryClient.setQueryData(["auth", "user"], userData);
    },
  });

  // 상태 계산
  const token = getTokenFromCookie();
  const isAuthenticated = !!user && !!token;
  const isInitialized = !isLoading;

  // 액션 함수들
  const login = useCallback(
    async (credentials: LoginCredentials) => {
      await loginMutation.mutateAsync(credentials);
    },
    [loginMutation]
  );

  const logout = useCallback(async () => {
    await logoutMutation.mutateAsync();
  }, [logoutMutation]);

  const register = useCallback(
    async (data: RegisterData) => {
      await registerMutation.mutateAsync(data);
    },
    [registerMutation]
  );

  const refreshToken = useCallback(async () => {
    // Route Handler 패턴에서는 토큰 갱신이 자동으로 처리됨
    await refreshUserMutation.mutateAsync();
  }, [refreshUserMutation]);

  const refreshUser = useCallback(async () => {
    await refreshUserMutation.mutateAsync();
  }, [refreshUserMutation]);

  const initialize = useCallback(async () => {
    // React Query가 자동으로 처리하므로 별도 초기화 불필요
    queryClient.invalidateQueries({
      queryKey: ["auth", "user"],
    });
  }, [queryClient]);

  // Context 값
  const contextValue: AuthContextType = {
    // 상태
    user: user || null,
    token,
    isLoading:
      isLoading ||
      loginMutation.isPending ||
      registerMutation.isPending ||
      logoutMutation.isPending,
    isAuthenticated,
    isInitialized,

    // 액션들
    login,
    logout,
    register,
    refreshToken,
    refreshUser,
    initialize,
  };

  return (
    <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>
  );
}

/**
 * AuthContext 사용을 위한 Hook
 * @returns AuthContext 값
 * @throws AuthContext가 초기화되지 않은 경우 에러
 */
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);

  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }

  return context;
};
