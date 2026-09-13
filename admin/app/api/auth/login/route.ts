import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.BACKEND_INTERNAL_URL || 'http://backend:8000';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { email, password } = body;

    if (!email || !password) {
      return NextResponse.json(
        { detail: 'Email va parol majburiy' },
        { status: 400 }
      );
    }

    const backendResp = await fetch(`${API_BASE_URL}/api/auth/admin-login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
      cache: 'no-store',
    });

    const data = await backendResp.json();

    if (!backendResp.ok) {
      return NextResponse.json(
        { detail: data.detail || 'Login xatosi' },
        { status: backendResp.status }
      );
    }

    // ✅ XAVFSIZLIK TEKSHIRUVI
    const accessToken = data.access_token;
    const refreshToken = data.refresh_token;

    if (!accessToken || typeof accessToken !== 'string' || !accessToken.startsWith('eyJ')) {
      console.error('Backend javobida access_token yo\'q yoki noto\'g\'ri:', data);
      return NextResponse.json(
        { detail: 'Backend token qaytarmadi.' },
        { status: 500 }
      );
    }

    // ✅ HAMMASINI QAYTARAMIZ — access_token, refresh_token, user
    return NextResponse.json({
      success: true,
      user: data.user,
      token: accessToken,
      refresh_token: refreshToken,  // ✅ YANGI: refresh_token qaytaramiz
    });
  } catch (error: any) {
    console.error('Auth login error:', error);
    return NextResponse.json(
      { detail: error?.message || "Noma'lum xato" },
      { status: 500 }
    );
  }
}