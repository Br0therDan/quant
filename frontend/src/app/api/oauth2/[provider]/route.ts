import { AuthService } from '@/client'

import { NextResponse } from 'next/server'


export async function GET(request: Request, { params: { provider } }: { params: { provider: string } }) {
  const { searchParams } = new URL(request.url)
  const code = searchParams.get('code')
  const state = searchParams.get('state')

  if (!code) {
    return NextResponse.json({ error: 'Authorization code is missing' }, { status: 400 })
  }

}
