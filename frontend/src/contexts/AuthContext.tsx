"use client";

import { UserService, type BodyAuthLogin } from "@/client";
import type { AuthActions, AuthState } from "@/types/auth";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { createContext, useContext, type ReactNode } from "react";

interface AuthContextType extends AuthState, AuthActions {}

export const AuthContext = createContext<AuthContextType | undefined>(
  undefined
);

async function loginApi(credentials: BodyAuthLogin) {
  const response = await fetch("/api/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      username: credentials.username,
      password: credentials.password,
    }),
  });

  if (response.status !== 200) {
    console.error("[Auth] 로그인 API 에러:", response.statusText);
    throw new Error("로그인에 실패했습니다.");
  }

  return response;
}

async function logoutApi() {
  const response = await fetch("/api/auth/logout", {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (response.status !== 200) {
    throw new Error("로그아웃에 실패했습니다.");
  }
  return response;
}

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const queryClient = useQueryClient();
  const router = useRouter();

  // 현재 사용자 정보 쿼리 (HTTPOnly 쿠키 기반)
  const {
    data: user,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["auth", "user"],
    queryFn: async () => {
      const response = await UserService.getUserMe();

      if (response.error) {
        throw new Error("사용자 정보를 가져올 수 없습니다.");
      }
      return response.data;
    },
    retry: (failureCount, error: any) => {
      // 401 또는 404 에러의 경우 재시도하지 않음 (토큰 만료 또는 무효)
      if (
        error?.status === 401 ||
        error?.status === 404 ||
        error?.message?.includes("401") ||
        error?.message?.includes("404")
      ) {
        return false;
      }
      return failureCount < 1; // 재시도 횟수 감소
    },
    staleTime: 60 * 60 * 1000, // 5분
    gcTime: 10 * 60 * 1000, // 10분
    // 클라이언트에서만 활성화 (서버 사이드는 비활성화)
    enabled: typeof window !== "undefined",
    refetchOnWindowFocus: false, // 창 포커스 시 재조회 비활성화
    refetchOnReconnect: false, // 재연결 시 재조회 비활성화
  });

  // 로그인 뮤테이션
  const loginMutation = useMutation({
    mutationFn: loginApi,
    onSuccess: async () => {
      console.log("로그인 성공");

      // HTTPOnly 쿠키가 완전히 설정될 때까지 충분히 대기 (500ms)
      await new Promise((resolve) => setTimeout(resolve, 500));

      // 사용자 정보 쿼리 무효화 및 재조회
      await queryClient.invalidateQueries({
        queryKey: ["auth", "user"],
      });

      // 성공적으로 로그인하면 리다이렉트
      const urlParams = new URLSearchParams(window.location.search);
      const redirectTo = urlParams.get("redirect") || "/dashboard";

      router.push(redirectTo);
    },
    onError: (error) => {
      console.error("로그인 실패:", error);
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
      queryClient.clear(); // 모든 쿼리 캐시 정리
      router.push("/login");
    },
  });

  // Context 값 (HTTPOnly 쿠키 기반)
  const contextValue: AuthContextType = {
    user: user || null,
    isLoading:
      typeof window !== "undefined"
        ? isLoading || loginMutation.isPending || logoutMutation.isPending
        : false,
    token: null, // HTTPOnly 쿠키는 클라이언트에서 접근 불가
    isAuthenticated: !!user && !error,
    isInitialized: typeof window !== "undefined" ? !isLoading : true, // 서버에서는 항상 초기화됨

    // 액션
    login: async (credentials) => {
      await loginMutation.mutateAsync(credentials);
    },
    logout: async () => {
      await logoutMutation.mutateAsync();
    },
    register: async () => {
      console.warn("Register function is not implemented yet.");
    },
    refreshToken: async () => {
      await queryClient.invalidateQueries({
        queryKey: ["auth", "user"],
      });
    },
    refreshUser: async () => {
      await queryClient.invalidateQueries({
        queryKey: ["auth", "user"],
      });
    },
    initialize: async () => {
      await queryClient.invalidateQueries({
        queryKey: ["auth", "user"],
      });
    },
  };

  // Workaround for React type mismatches between @types/react instances:
  // create an alias and cast to any to satisfy JSX typing.
  const Provider = AuthContext.Provider as any;

  return <Provider value={contextValue}>{children}</Provider>;
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
