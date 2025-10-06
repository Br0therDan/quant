/**
 * 인증 디버깅 유틸리티
 * HTTPOnly 쿠키 문제 진단을 위한 도구들
 */

export function debugCookies() {
    if (typeof window === 'undefined') return;

    console.log('=== 쿠키 디버깅 정보 ===');
    console.log('document.cookie:', document.cookie);
    console.log('HTTPOnly 쿠키는 document.cookie로 접근할 수 없습니다.');

    // 브라우저 개발자 도구에서 확인할 수 있는 명령어 안내
    console.log('브라우저 개발자 도구에서 확인:');
    console.log('Application > Storage > Cookies > localhost:3000');
}

export function debugAuthState() {
    console.log('=== 인증 상태 디버깅 ===');
    console.log('현재 URL:', window.location.href);
    console.log('URL 쿼리 파라미터:', new URLSearchParams(window.location.search).toString());
    console.log('세션 스토리지 redirect:', sessionStorage.getItem('redirectAfterLogin'));
}

export async function testAuthAPI() {
    try {
        console.log('=== 인증 API 테스트 ===');
        const response = await fetch('/api/v1/auth/token/verify', {
            credentials: 'include'
        });

        if (response.ok) {
            const data = await response.json();
            console.log('토큰 검증 성공:', data);
        } else {
            console.log('토큰 검증 실패:', response.status, response.statusText);
        }
    } catch (error) {
        console.error('API 테스트 실패:', error);
    }
}
