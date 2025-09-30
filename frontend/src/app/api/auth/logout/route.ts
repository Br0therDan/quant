import type { NextRequest } from 'next/server';
import { NextResponse } from 'next/server';
import { client } from '@/utils/serverClient';
/**
 * 로그아웃 Route Handler
 * POST /api/auth/logout
 */
export async function POST(request: NextRequest) {
    try {

        await client.post({ url: '/auth/jwt/logout' });
        // 쿠키 삭제
        const response = NextResponse.json({
            success: true,
            message: 'Logout successful'
        });

        // access_token 쿠키 삭제
        response.cookies.set('access_token', '', {
            maxAge: 0,
            httpOnly: false,
            secure: process.env.NODE_ENV === 'production',
            sameSite: 'lax',
            path: '/'
        });

        return response;

    } catch (error) {
        console.error('Logout error:', error);
        return NextResponse.json(
            { error: 'Internal server error' },
            { status: 500 }
        );
    }
}
