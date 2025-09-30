
import { type NextRequest, NextResponse } from 'next/server';
import { AuthAuthJwt, type Login } from '@/client';
import { LoginCredentials } from '@/types/auth';

/**
 * 로그인 Route Handler
 * POST /api/auth/login
 */
export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { username, password } = body;

        // 백엔드 API 호출
        const response = await AuthAuthJwt.login<LoginCredentials>({
            username,
            password
        });

        if (response.error) {
            return NextResponse.json(
                { error: 'Invalid credentials' },
                { status: 401 }
            );
        }

    } catch (error) {
        console.error('Login error:', error);
        return NextResponse.json(
            { error: 'Internal server error' },
            { status: 500 }
        );
    }
}

        if (response.error) {
            return NextResponse.json(
                { error: 'Invalid credentials' },
                { status: 401 }
            );
        }

        // 로그인 성공 시 쿠키에 토큰 저장
        const { access_token } = response.data as { access_token: string };

        const nextResponse = NextResponse.json({
            success: true,
            message: 'Login successful'
        });

        // 쿠키 설정 (Non-HttpOnly로 JavaScript 접근 가능)
        nextResponse.cookies.set('access_token', access_token, {
            maxAge: 30 * 24 * 60 * 60, // 30일
            httpOnly: false, // JavaScript 접근 허용
            secure: process.env.NODE_ENV === 'production',
            sameSite: 'lax',
            path: '/'
        });

        return nextResponse;

    } catch (error) {
        console.error('Login error:', error);
        return NextResponse.json(
            { error: 'Internal server error' },
            { status: 500 }
        );
    }
}
