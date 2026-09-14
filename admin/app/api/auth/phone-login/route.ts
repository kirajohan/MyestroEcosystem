import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.BACKEND_INTERNAL_URL || 'http://backend:8000';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { phone, password } = body;

    if (!phone || !password) {
      return NextResponse.json(
        { detail: 'Telefon va parol majburiy' },
        { status: 400 }
      );
    }

    const backendResp = await fetch(`${API_BASE_URL}/api/auth/phone-login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone, password, telegram_id: null }),
      cache: 'no-store',
    });

    const data = await backendResp.json();

    if (!backendResp.ok) {
      return NextResponse.json(
        { detail: data.detail || 'Telefon yoki parol notogri' },
        { status: backendResp.status }
      );
    }

    return NextResponse.json(data);
  } catch (error: any) {
    console.error('Phone login error:', error);
    return NextResponse.json(
      { detail: error?.message || 'Server xatosi' },
      { status: 500 }
    );
  }
}