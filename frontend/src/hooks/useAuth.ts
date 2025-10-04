"use client";
import type {
  BodyAuthLogin,
  BodyAuthResetResetPassword,
  UserCreate,
  UserUpdate
} from "@/client";
import { AuthService, UserService } from "@/client";
import { AuthContext } from "@/contexts/AuthContext";
import { useSnackbar } from "@/contexts/SnackbarContext";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import Cookies from "js-cookie";
import { useRouter } from "next/navigation";
import { useContext, useMemo } from "react";

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
    isLoading: userLoading,
    refreshUser,
    logout: handleLogout,
  } = ctx;

  const queryClient = useQueryClient();
  const router = useRouter();
  const { showSuccess, showError } = useSnackbar();

  // 로그인 뮤테이션
  const createLoginMutation = useMutation({
    mutationFn: async (data: BodyAuthLogin) => {
      const response = await AuthService.authLogin({
        body: {
          username: data.username,
          password: data.password,
        },
      });

      if (response.error) {
        throw new Error(typeof response.error.detail === "string" ? response.error.detail : "로그인에 실패했습니다");
      }
      Cookies.set("access_token", response.data.access_token);
      Cookies.set("refresh_token", response.data.refresh_token ?? "");
      Cookies.set("token_type", response.data.token_type ?? "");
      Cookies.set("user_info", JSON.stringify(response.data.user_info));
      return response.data.user_info;
    },
    onSuccess: async () => {
      await refreshUser();
      queryClient.invalidateQueries({ queryKey: authQueryKeys.user() });

      const redirectTo = Cookies.get("redirectAfterLogin") || "/dashboard";
      Cookies.remove("redirectAfterLogin");
      router.push(redirectTo);

      showSuccess("로그인 성공");
    },
    onError: (error: any) => {
      showError(error.message || "로그인에 실패했습니다");
    },
  });

  // 비밀번호 찾기 뮤테이션
  const createForgotPasswordMutation = useMutation({
    mutationFn: async (email: string) => {
      const response = await AuthService.authResetForgotPassword({
        body: {
          email,
        }
      });
      return response;
    },
    onSuccess: () => {
      showSuccess("비밀번호 재설정 이메일 발송");
    },
    onError: (error: any) => {
      showError(error.message || "비밀번호 재설정 요청에 실패했습니다");
    },
  });

  // 비밀번호 재설정 뮤테이션
  const createResetPasswordMutation = useMutation({
    mutationFn: async (data: BodyAuthResetResetPassword) => {
      const response = await AuthService.authResetResetPassword({
        body: data,
      });
      return response;
    },
    onSuccess: () => {
      showSuccess("비밀번호 재설정 완료");
      router.push("/auth/login");
    },
    onError: (error: any) => {
      showError(error.message || "비밀번호 재설정에 실패했습니다");
    },
  });

  // 사용자 정보 업데이트 뮤테이션
  const createUpdateUserMutation = useMutation({
    mutationFn: async (data: UserUpdate) => {
      const response = await UserService.userUpdateUserMe({
        body: data,
      });
      return response;
    },
    onSuccess: async () => {
      await refreshUser();
      queryClient.invalidateQueries({ queryKey: authQueryKeys.user() });
      showSuccess("사용자 정보 업데이트");
    },
    onError: (error: any) => {
      showError(error.message || "사용자 정보 업데이트에 실패했습니다");
    },
  });

  // 계정 삭제 뮤테이션 (현재 사용자 계정 삭제)
  const createDeleteAccountMutation = useMutation({
    mutationFn: async () => {
      if (!user?.email) {
        throw new Error("사용자 정보를 찾을 수 없습니다");
      }
      // 현재 사용자의 ID를 사용하여 계정 삭제
      const response = await UserService.userDeleteUser({
        path: { id: user.email }, // 이메일을 ID로 사용
      });
      return response;
    },
    onSuccess: () => {
      showSuccess("계정 삭제 완료");
      handleLogout();
      router.push("/");
    },
    onError: (error: any) => {
      showError(error.message || "계정 삭제에 실패했습니다");
    },
  });

  // 회원가입 뮤테이션
  const createSignupMutation = useMutation({
    mutationFn: async (userData: UserCreate) => {
      const response = await AuthService.authRegister({
        body: userData,
      });
      return response;
    },
    onSuccess: () => {
      showSuccess("회원가입 완료");
      router.push("/auth/login");
    },
    onError: (error: any) => {
      showError(error.message || "회원가입에 실패했습니다");
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
    logout: handleLogout,

    // 뮤테이션 메서드
    login: (data: BodyAuthLogin) => createLoginMutation.mutateAsync(data),
    signup: (userData: UserCreate) => createSignupMutation.mutateAsync(userData),
    forgotPassword: (email: string) => createForgotPasswordMutation.mutateAsync(email),
    resetPassword: (data: BodyAuthResetResetPassword) => createResetPasswordMutation.mutateAsync(data),
    updateUser: (data: UserUpdate) => createUpdateUserMutation.mutateAsync(data),
    deleteAccount: () => createDeleteAccountMutation.mutateAsync(),

    // 뮤테이션 상태
    isLoginPending: createLoginMutation.isPending,
    isSignupPending: createSignupMutation.isPending,
    isForgotPasswordPending: createForgotPasswordMutation.isPending,
    isResetPasswordPending: createResetPasswordMutation.isPending,
    isUpdateUserPending: createUpdateUserMutation.isPending,
    isDeleteAccountPending: createDeleteAccountMutation.isPending,
    isMutating:
      createLoginMutation.isPending ||
      createSignupMutation.isPending ||
      createForgotPasswordMutation.isPending ||
      createResetPasswordMutation.isPending ||
      createUpdateUserMutation.isPending ||
      createDeleteAccountMutation.isPending,

    // 에러 상태
    loginError: createLoginMutation.error,
    signupError: createSignupMutation.error,
    forgotPasswordError: createForgotPasswordMutation.error,
    resetPasswordError: createResetPasswordMutation.error,
    updateUserError: createUpdateUserMutation.error,
    deleteAccountError: createDeleteAccountMutation.error,

    // 뮤테이션 직접 접근 (고급 사용)
    loginMutation: createLoginMutation,
    signupMutation: createSignupMutation,
    forgotPasswordMutation: createForgotPasswordMutation,
    resetPasswordMutation: createResetPasswordMutation,
    updateUserMutation: createUpdateUserMutation,
    deleteAccountMutation: createDeleteAccountMutation,
  };
}
