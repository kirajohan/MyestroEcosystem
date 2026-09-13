import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';
export const revalidate = 0; // ✅ YANGI: Hech qachon cache qilma

const API_BASE_URL = process.env.BACKEND_INTERNAL_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const is_read = searchParams.get('is_read');
    const limit = searchParams.get('limit') || '50';
    const offset = searchParams.get('offset') || '0';

    let url = `${API_BASE_URL}/admin-messages?limit=${limit}&offset=${offset}`;
    if (is_read) {
      url += `&is_read=${is_read}`;
    }

    const authHeader = request.headers.get('authorization');

    const backendResp = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache, no-store, must-revalidate', // ✅ YANGI
        ...(authHeader ? { Authorization: authHeader } : {}),
      },
      cache: 'no-store', // ✅ YANGI: Next.js fetch cache'ni o'chirish
    });

    if (!backendResp.ok) {
      const errData = await backendResp.json().catch(() => ({}));
      return NextResponse.json(
        { detail: errData.detail || 'Backend xatosi' },
        { status: backendResp.status }
      );
    }

    const data = await backendResp.json();
    
    // ✅ YANGI: Response'ga Cache-Control header qo'shish
    return NextResponse.json(data, { 
      status: 200,
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
      },
    });
  } catch (error: any) {
    console.error('Inbox GET error:', error);
    return NextResponse.json(
      { detail: error?.message || "Noma'lum xato" },
      { status: 500 }
    );
  }
}