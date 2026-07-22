import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.BACKEND_INTERNAL_URL || 'http://backend:8000';

export async function GET(
  _request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params;
    if (!id) {
      return NextResponse.json({ error: 'id majburiy' }, { status: 400 });
    }

    // Forward to backend /broadcast/status/{id}
    const backendResp = await fetch(`${API_BASE_URL}/broadcast/status/${id}`, {
      method: 'GET',
    });

    if (!backendResp.ok) {
      const errText = await backendResp.text();
      return NextResponse.json(
        { error: errText || 'Backend xatosi' },
        { status: backendResp.status }
      );
    }

    const data = await backendResp.json();

    // Convert backend response → admin BroadcastProgress format
    //   backend: { broadcast_id, title, status, total, sent, failed, created_at }
    //   admin:   { status, total, sent, failed }
    return NextResponse.json(
      {
        status: data.status || 'unknown',
        total: data.total || 0,
        sent: data.sent || 0,
        failed: data.failed || 0,
        created_at: data.created_at || '',
      },
      { status: 200 }
    );
  } catch (error: any) {
    return NextResponse.json(
      { error: error?.message || "Noma'lum xato" },
      { status: 500 }
    );
  }
}