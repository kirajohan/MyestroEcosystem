import { NextRequest, NextResponse } from 'next/server';

// DIQQAT: Faqat ichki tarmoq URL ishlatiladi. NEXT_PUBLIC_API_URL client-side uchun, bu yerda ishlamaydi.
const API_BASE_URL = process.env.BACKEND_INTERNAL_URL || 'http://backend:8000';

// ══════════════════════════════════════════════════════════════
// GET /api/tests/[id]/questions — Test savollarini olish
// ══════════════════════════════════════════════════════════════
export async function GET(
  _request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params;

    // DIQQAT: "/api/tests" emas, faqat "/tests"
    const backendResp = await fetch(`${API_BASE_URL}/tests/${id}/questions`, {
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
    return NextResponse.json(data, { status: 200 });
  } catch (error: any) {
    console.error('❌ Test questions GET error:', error);
    return NextResponse.json(
      { detail: error?.message || "Noma'lum xato" },
      { status: 500 }
    );
  }
}

// ══════════════════════════════════════════════════════════════
// POST /api/tests/[id]/questions — Yangi savol qo'shish
// ══════════════════════════════════════════════════════════════
export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params;
    const body = await request.json();

    if (!body.question_text || !body.question_text.trim()) {
      return NextResponse.json({ detail: 'Savol matni majburiy' }, { status: 400 });
    }

    if (!body.options || !Array.isArray(body.options) || body.options.length < 2) {
      return NextResponse.json({ detail: 'Kamida 2 ta variant majburiy' }, { status: 400 });
    }

    if (
      body.correct_option_index === undefined ||
      body.correct_option_index < 0 ||
      body.correct_option_index >= body.options.length
    ) {
      return NextResponse.json({ detail: "To'g'ri javob indeksi noto'g'ri" }, { status: 400 });
    }

    // DIQQAT: "/api/tests" emas, faqat "/tests"
    const backendResp = await fetch(`${API_BASE_URL}/tests/${id}/questions`, {
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
    console.error('❌ Test questions POST error:', error);
    return NextResponse.json(
      { detail: error?.message || "Noma'lum xato" },
      { status: 500 }
    );
  }
}