// admin/app/api/tests/route.ts

import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

const API_BASE_URL =
  process.env.BACKEND_INTERNAL_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  'http://localhost:8002';

// ══════════════════════════════════════════════════════════════
// GET /api/tests — Testlar ro'yxati
// ══════════════════════════════════════════════════════════════

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const level = searchParams.get('level');
    const active_only = searchParams.get('active_only') || 'true';
    const limit = searchParams.get('limit') || '50';
    const offset = searchParams.get('offset') || '0';

    let url = `${API_BASE_URL}/api/tests?limit=${limit}&offset=${offset}&active_only=${active_only}`;
    if (level) {
      url += `&level=${level}`;
    }

    const backendResp = await fetch(url, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!backendResp.ok) {
      const errData = await backendResp.json().catch(() => ({}));
      return NextResponse.json(
        { detail: errData.detail || 'Backend xatosi' },
        { status: backendResp.status }
      );
    }

    const data = await backendResp.json();
    // Backend array yoki { tests: [...] } qaytarishi mumkin
    const result = Array.isArray(data) ? data : data.tests || [];
    return NextResponse.json(result, { status: 200 });
  } catch (error: any) {
    console.error('❌ Tests GET error:', error);
    return NextResponse.json(
      { detail: error?.message || "Noma'lum xato" },
      { status: 500 }
    );
  }
}

// ══════════════════════════════════════════════════════════════
// POST /api/tests — Yangi test yaratish
// ══════════════════════════════════════════════════════════════

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // Validatsiya
    if (!body.title || !body.title.trim()) {
      return NextResponse.json(
        { detail: 'Test sarlavhasi majburiy' },
        { status: 400 }
      );
    }

    if (!body.cefr_level) {
      return NextResponse.json(
        { detail: 'CEFR daraja majburiy' },
        { status: 400 }
      );
    }

    const backendResp = await fetch(`${API_BASE_URL}/api/tests`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (!backendResp.ok) {
      const errData = await backendResp.json().catch(() => ({}));
      return NextResponse.json(
        { detail: errData.detail || 'Backend xatosi' },
        { status: backendResp.status }
      );
    }

    const data = await backendResp.json();
    return NextResponse.json(data, { status: 201 });
  } catch (error: any) {
    console.error('❌ Tests POST error:', error);
    return NextResponse.json(
      { detail: error?.message || "Noma'lum xato" },
      { status: 500 }
    );
  }
}