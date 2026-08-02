import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

const API_BASE_URL = process.env.BACKEND_INTERNAL_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const level = searchParams.get('level');
    const limit = searchParams.get('limit') || '50';
    const offset = searchParams.get('offset') || '0';

    let url = `${API_BASE_URL}/exams?limit=${limit}&offset=${offset}`;
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
    return NextResponse.json(data, { status: 200 });
  } catch (error: any) {
    console.error('Tests GET error:', error);
    return NextResponse.json(
      { detail: error?.message || "Noma'lum xato" },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const backendResp = await fetch(`${API_BASE_URL}/exams`, {
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
    console.error('Tests POST error:', error);
    return NextResponse.json(
      { detail: error?.message || "Noma'lum xato" },
      { status: 500 }
    );
  }
}