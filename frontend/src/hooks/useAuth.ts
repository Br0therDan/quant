/**
 * 인증 관련 훅들 - 통합된 AuthContext 사용
 */

import { useAuth as useAuthContext } from "@/context/AuthContext";

// 기본 useAuth는 Context 사용
export const useAuth = useAuthContext;

/**
 * 인증 여부 확인 훅
 */
export function useRequireAuth() {
	const { isAuthenticated } = useAuthContext();
	return { isAuthenticated };
}

/**
 * 사용자 정보 훅
 */
export function useUser() {
	const { user, isAuthenticated, isLoading } = useAuthContext();
	return {
		user,
		isAuthenticated,
		isLoading,
	};
}

/**
 * 인증 액션 훅들
 */
export function useAuthActions() {
	const { login, logout, register } = useAuthContext();

	return {
		login,
		logout,
		register,
	};
}

/**
 * 로그인 전용 훅 (기존 호환성)
 */
export function useLogin() {
	const { login, isLoading } = useAuthContext();
	return {
		login,
		isLoading,
		error: null, // 에러는 AuthContext 내부에서 처리
	};
}

/**
 * 인증 초기화 훅
 */
export function useAuthInitialization() {
	const { isInitialized, isLoading } = useAuthContext();
	return {
		isInitialized,
		isLoading,
	};
}
