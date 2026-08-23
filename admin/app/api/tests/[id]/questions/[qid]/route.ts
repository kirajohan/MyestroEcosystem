// admin/app/api/tests/[id]/questions/[qid]/route.ts

import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL =
  process.env.BACKEND_INTERNAL_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  'http://localhost:8002';

// ══════════════════════════════════════════════════════════════
// PUT /api/tests/[id]/questions/[qid] — Savolni yangilash
// ══════════════════════════════════════════════════════════════

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string; qid: string } }
) {
  try {
    const { id, qid } = params;
    const body = await request.json();

    const backendResp = await fetch(
      `${API_BASE_URL}/api/tests/${id}/questions/${qid}`,
      {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      }
    );

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
    console.error('❌ Question PUT error:', error);
    return NextResponse.json(
      { detail: error?.message || "Noma'lum xato" },
      { status: 500 }
    );
  }
}

// ══════════════════════════════════════════════════════════════
// DELETE /api/tests/[id]/questions/[qid] — Savolni o'chirish
// ══════════════════════════════════════════════════════════════

export async function DELETE(
  _request: NextRequest,
  { params }: { params: { id: string; qid: string } }
) {
  try {
    const { id, qid } = params;

    const backendResp = await fetch(
      `${API_BASE_URL}/api/tests/${id}/questions/${qid}`,
      { method: 'DELETE' }
    );

    if (!backendResp.ok) {
      const errData = await backendResp.json().catch(() => ({}));
      return NextResponse.json(
        { detail: errData.detail || 'Backend xatosi' },
        { status: backendResp.status }
      );
    }

    if (backendResp.status === 204) {
      return NextResponse.json({ success: true }, { status: 200 });
    }

    const data = await backendResp.json();
    return NextResponse.json(data, { status: 200 });
  } catch (error: any) {
    console.error('❌ Question DELETE error:', error);
    return NextResponse.json(
      { detail: error?.message || "Noma'lum xato" },
      { status: 500 }
    );
  }
}