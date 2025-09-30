import { getCurrentUserServer } from '@/utils/serverClient';
import { type NextRequest, NextResponse } from 'next/server';

/**
 * 토큰 검증 Route Handler
 * GET /api/auth/verify
 */
export async function GET(request: NextRequest) {
    try {
        const user = await getCurrentUserServer();

        if (!user) {
            return NextResponse.json(
                {
                    valid: false,
                    user: null,
                    message: 'Invalid or expired token'
                },
                { status: 401 }
            );
        }

        return NextResponse.json({
            valid: true,
            user,
            message: 'Token is valid'
        });

    } catch (error) {
        console.error('Token verification error:', error);
        return NextResponse.json(
            {
                valid: false,
                user: null,
                error: 'Token verification failed'
            },
            { status: 500 }
        );
    }
}
