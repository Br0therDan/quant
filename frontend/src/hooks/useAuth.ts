"use client";
import {  useMutation, useQueryClient } from "@tanstack/react-query";
import { AuthContext } from "@/contexts/AuthContext";
import { AuthService, UserService } from "@/client";
import type { NewPassword, UpdatePassword, AuthRegisterData, UserUpdateMe } from "@/client";
import { handleApiError } from "@/lib/errorHandler";
import { toast } from "sonner";
import { useMemo, useContext } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import Cookies from "js-cookie";
import type { LoginRequest } from "@/types/auth";

// 쿼리 키 정의
export const authQueryKeys = {
  all: ["auth"] as const,
  user: () => [...authQueryKeys.all, "user"] as const,
  profile: () => [...authQueryKeys.all, "profile"] as const,
};

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");

  const {
    user,
    loading: userLoading,
    refreshUser,
    refreshAccessToken,
    handleLogout,
  } = ctx;

  const queryClient = useQueryClient();
  const router = useRouter();
  const t = useTranslations();

  // 로그인 뮤테이션
  const createLoginMutation = useMutation({
    mutationFn: async (data: LoginRequest) => {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: data.username,
          password: data.password,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "로그인에 실패했습니다");
      }

      return response.json();
    },
    onSuccess: async () => {
      await refreshUser();
      queryClient.invalidateQueries({ queryKey: authQueryKeys.user() });

      const redirectTo = Cookies.get("redirectAfterLogin") || "/dashboard";
      Cookies.remove("redirectAfterLogin");
      router.push(redirectTo);

      toast.success("로그인 성공", {
        description: "대시보드로 이동합니다.",
      });
    },
    onError: (error: any) => {
      handleApiError(error, (message) => {
        toast.error(message.title, { description: message.description });
      });
    },
  });

  // OAuth 인증 URL 뮤테이션
  const createOAuthAuthorizationMutation = useMutation({
    mutationFn: async ({
      provider,
      state,
    }: {
      provider: string;
      state: string;
    }) => {
      const response = await AuthService.authOauthAuthorize(provider, state);
      return response;
    },
    onSuccess: (response) => {
      if (response?.data) {
        window.location.href = response.data;
      } else {
        throw new Error("인증 URL을 받을 수 없습니다.");
      }
    },
    onError: (error: any) => {
      handleApiError(error, (message) => {
        toast.error(message.title, { description: message.description });
      });
    },
  });

  // 비밀번호 찾기 뮤테이션
  const createForgotPasswordMutation = useMutation({
    mutationFn: async (email: string) => {
      const response = await AuthService.authRecoverPassword(
        email,
        window.location.origin
      );
      return response;
    },
    onSuccess: () => {
      toast.success("비밀번호 재설정 이메일 발송", {
        description: "이메일을 확인하여 비밀번호를 재설정하세요.",
      });
    },
    onError: (error: any) => {
      handleApiError(error, (message) => {
        toast.error(message.title, { description: message.description });
      });
    },
  });

  // 비밀번호 재설정 뮤테이션
  const createResetPasswordMutation = useMutation({
    mutationFn: async (data: NewPassword) => {
      const response = await AuthService.authResetPassword(data);
      return response;
    },
    onSuccess: () => {
      toast.success("비밀번호 재설정 완료", {
        description: "새 비밀번호로 로그인하세요.",
      });
      router.push("/auth/login");
    },
    onError: (error: any) => {
      handleApiError(error, (message) => {
        toast.error(message.title, { description: message.description });
      });
    },
  });

  // 사용자 정보 업데이트 뮤테이션
  const createUpdateUserMutation = useMutation({
    mutationFn: async (data: UserUpdateMe) => {
      const response = await UserService.userUpdateUser(data);
      return response;
    },
    onSuccess: async () => {
      await refreshUser();
      queryClient.invalidateQueries({ queryKey: authQueryKeys.user() });
      toast.success("사용자 정보 업데이트", {
        description: "정보가 성공적으로 업데이트되었습니다.",
      });
    },
    onError: (error: any) => {
      handleApiError(error, (message) => {
        toast.error(message.title, { description: message.description });
      });
    },
  });

  // 비밀번호 변경 뮤테이션
  const createChangePasswordMutation = useMutation({
    mutationFn: async (data: UpdatePassword) => {
      const response = await UserService.userUpdateUserPassword(data);
      return response;
    },
    onSuccess: () => {
      toast.success("비밀번호 변경 완료", {
        description: "새 비밀번호가 설정되었습니다.",
      });
    },
    onError: (error: any) => {
      handleApiError(error, (message) => {
        toast.error(message.title, { description: message.description });
      });
    },
  });

  // 계정 삭제 뮤테이션
  const createDeleteAccountMutation = useMutation({
    mutationFn: async () => {
      const response = await UserService.userDeleteUser();
      return response;
    },
    onSuccess: () => {
      toast.success("계정 삭제 완료", {
        description: "계정이 성공적으로 삭제되었습니다.",
      });
      handleLogout();
      router.push("/");
    },
    onError: (error: any) => {
      handleApiError(error, (message) => {
        toast.error(message.title, { description: message.description });
      });
    },
  });

  // 회원가입 뮤테이션
  const createSignupMutation = useMutation({
    mutationFn: async ({
      origin,
      userData,
    }: {
      origin: string;
      userData: UserRegister;
    }) => {
      const response = await AuthService.authRegisterUser(origin, userData);
      return response;
    },
    onSuccess: () => {
      toast.success("회원가입 완료", {
        description: "로그인 페이지로 이동합니다.",
      });
      router.push("/auth/login");
    },
    onError: (error: any) => {
      handleApiError(error, (message) => {
        toast.error(message.title, { description: message.description });
      });
    },
  });

  // 메모이제이션된 데이터
  const memoizedData = useMemo(
    () => ({
      user,
      isAuthenticated: !!user,
      isLoading: userLoading,
    }),
    [user, userLoading]
  );

  return {
    // 사용자 정보
    ...memoizedData,

    // 인증 관련 메서드
    refreshUser,
    refreshAccessToken,
    logout: handleLogout,

    // 뮤테이션 메서드
    login: (data: LoginRequest) => createLoginMutation.mutateAsync(data),
    signup: (origin: string, userData: UserRegister) =>
      createSignupMutation.mutateAsync({ origin, userData }),
    forgotPassword: (email: string) =>
      createForgotPasswordMutation.mutateAsync(email),
    resetPassword: (data: NewPassword) =>
      createResetPasswordMutation.mutateAsync(data),
    updateUser: (data: UserUpdateMe) =>
      createUpdateUserMutation.mutateAsync(data),
    changePassword: (data: UpdatePassword) =>
      createChangePasswordMutation.mutateAsync(data),
    deleteAccount: () => createDeleteAccountMutation.mutateAsync(),
    getOAuthAuthorizationUrl: (
      provider: string,
      origin: string,
      redirectPath?: string
    ) => {
      const state = `${origin}+${redirectPath || ""}`;
      return createOAuthAuthorizationMutation.mutateAsync({ provider, state });
    },

    // 뮤테이션 상태
    isLoginPending: createLoginMutation.isPending,
    isSignupPending: createSignupMutation.isPending,
    isOAuthPending: createOAuthAuthorizationMutation.isPending,
    isForgotPasswordPending: createForgotPasswordMutation.isPending,
    isResetPasswordPending: createResetPasswordMutation.isPending,
    isUpdateUserPending: createUpdateUserMutation.isPending,
    isChangePasswordPending: createChangePasswordMutation.isPending,
    isDeleteAccountPending: createDeleteAccountMutation.isPending,
    isMutating:
      createLoginMutation.isPending ||
      createSignupMutation.isPending ||
      createOAuthAuthorizationMutation.isPending ||
      createForgotPasswordMutation.isPending ||
      createResetPasswordMutation.isPending ||
      createUpdateUserMutation.isPending ||
      createChangePasswordMutation.isPending ||
      createDeleteAccountMutation.isPending,

    // 에러 상태
    loginError: createLoginMutation.error,
    signupError: createSignupMutation.error,
    oauthError: createOAuthAuthorizationMutation.error,
    forgotPasswordError: createForgotPasswordMutation.error,
    resetPasswordError: createResetPasswordMutation.error,
    updateUserError: createUpdateUserMutation.error,
    changePasswordError: createChangePasswordMutation.error,
    deleteAccountError: createDeleteAccountMutation.error,

    // 뮤테이션 직접 접근 (고급 사용)
    loginMutation: createLoginMutation,
    signupMutation: createSignupMutation,
    oauthAuthorizationMutation: createOAuthAuthorizationMutation,
    forgotPasswordMutation: createForgotPasswordMutation,
    resetPasswordMutation: createResetPasswordMutation,
    updateUserMutation: createUpdateUserMutation,
    changePasswordMutation: createChangePasswordMutation,
    deleteAccountMutation: createDeleteAccountMutation,
  };
}
