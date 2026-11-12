// admin/app/api/tests/[id]/route.ts

import { backendFetch } from '@/lib/proxy';
import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.BACKEND_INTERNAL_URL || 'http://backend:8000';

// GET
export async function GET(_request: NextRequest, { params }: { params: { id: string } }) {
  try {
    const { id } = params;
    const backendResp = await backendFetch(`${API_BASE_URL}/tests/${id}`, { // "/api" olib tashlandi
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
    // ... (qolgan qismi o'zgarishsiz, faqat URL to'g'rilandi)
    if (!backendResp.ok) {
      const errData = await backendResp.json().catch(() => ({}));
      return NextResponse.json(
        { detail: errData.detail || 'Backend xatosi' },
        { status: backendResp.status }
      );
    }

    const data = await backendResp.json();
    return NextResponse.json(data, { status: 200 });
  } catch (error: any) {
    console.error('❌ Test GET error:', error);
    return NextResponse.json(
      { detail: error?.message || "Noma'lum xato" },
      { status: 500 }
    );
  }
}

// ══════════════════════════════════════════════════════════════
// PUT /api/tests/[id] — Testni yangilash
// ══════════════════════════════════════════════════════════════

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params;
    const body = await request.json();

    const backendResp = await backendFetch(`${API_BASE_URL}/api/tests/${id}`, {
      method: 'PUT',
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
    return NextResponse.json(data, { status: 200 });
  } catch (error: any) {
    console.error('❌ Test PUT error:', error);
    return NextResponse.json(
      { detail: error?.message || "Noma'lum xato" },
      { status: 500 }
    );
  }
}

// ══════════════════════════════════════════════════════════════
// DELETE /api/tests/[id] — Testni o'chirish
// ══════════════════════════════════════════════════════════════

export async function DELETE(
  _request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params;

    const backendResp = await backendFetch(`${API_BASE_URL}/api/tests/${id}`, {
      method: 'DELETE',
    });

    if (!backendResp.ok) {
      const errData = await backendResp.json().catch(() => ({}));
      return NextResponse.json(
        { detail: errData.detail || 'Backend xatosi' },
        { status: backendResp.status }
      );
    }

    // 204 No Content yoki JSON qaytarishi mumkin
    if (backendResp.status === 204) {
      return NextResponse.json({ success: true }, { status: 200 });
    }

    const data = await backendResp.json();
    return NextResponse.json(data, { status: 200 });
  } catch (error: any) {
    console.error('❌ Test DELETE error:', error);
    return NextResponse.json(
      { detail: error?.message || "Noma'lum xato" },
      { status: 500 }
    );
  }
}