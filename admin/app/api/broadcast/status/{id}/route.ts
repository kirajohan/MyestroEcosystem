import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_INTERNAL_URL || 'http://backend:8000';

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const broadcastId = params.id;

    if (!broadcastId) {
      return NextResponse.json(
        { error: 'Broadcast ID majburiy' },
        { status: 400 }
      );
    }

    // Backend status endpoint'iga proxy
    const response = await fetch(
      `${BACKEND_URL}/broadcast/status/${broadcastId}`,
      {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        cache: 'no-store',
      }
    );

    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      return NextResponse.json(
        { error: data.detail || 'Status olishda xato' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error: any) {
    console.error('Broadcast status proxy error:', error);
    return NextResponse.json(
      { error: error?.message || "Server xatosi" },
      { status: 500 }
    );
  }
}