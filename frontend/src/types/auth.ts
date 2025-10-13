import type { UserResponse } from "@/client";

/**
 * 인증 상태 인터페이스
 */
export interface AuthState {
	/** 현재 로그인한 사용자 정보 */
	user: UserResponse | null;
	/** 액세스 토큰 */
	token: string | null;
	/** 로딩 상태 */
	isLoading: boolean;
	/** 인증 여부 */
	isAuthenticated: boolean;
	/** 초기화 완료 여부 */
	isInitialized: boolean;
}

/**
 * 로그인 자격 증명
 */
export interface LoginCredentials {
	username: string;
	password: string;
}

/**
 * 회원가입 데이터
 */
export interface RegisterData {
	email: string;
	password: string;
	fullname?: string;
}

/**
 * 인증 에러 인터페이스
 */
export interface AuthError {
	message: string;
	code?: string;
	details?: Record<string, unknown>;
}

/**
 * 인증 컨텍스트 액션 인터페이스
 */
export interface AuthActions {
	/** 로그인 */
	login: (credentials: LoginCredentials) => Promise<void>;
	/** 로그아웃 */
	logout: () => Promise<void>;
	/** 회원가입 */
	register: (data: RegisterData) => Promise<void>;
	/** 토큰 갱신 */
	refreshToken: () => Promise<void>;
	/** 사용자 정보 갱신 */
	refreshUser: () => Promise<void>;
	/** 초기화 */
	initialize: () => Promise<void>;
}

/**
 * 전체 AuthContext 인터페이스
 */
export interface AuthContextType extends AuthState, AuthActions {}

/**
 * 토큰 스토리지 인터페이스
 */
export interface TokenStorage {
	getToken: () => string | null;
	setToken: (token: string) => void;
	removeToken: () => void;
}
