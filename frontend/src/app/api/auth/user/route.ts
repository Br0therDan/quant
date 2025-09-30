import { getCurrentUserServer } from '@/utils/serverClient';
import type { NextRequest } from 'next/server';
import { NextResponse } from 'next/server';

/**
 * 현재 사용자 정보 조회 Route Handler
 * GET /api/auth/user
 */
export async function GET(_request: NextRequest) {
    try {
        const user = await getCurrentUserServer();

        if (!user) {
            return NextResponse.json(
                { error: 'User not found or not authenticated' },
                { status: 401 }
            );
        }

        return NextResponse.json({ user });

    } catch (error) {
        console.error('Get user error:', error);
        return NextResponse.json(
            { error: 'Failed to fetch user information' },
            { status: 500 }
        );
    }
}
