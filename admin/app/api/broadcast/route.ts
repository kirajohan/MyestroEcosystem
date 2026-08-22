import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.BACKEND_INTERNAL_URL || 'http://backend:8000';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { title, content, message_type, file_id, target_mode, target_user_ids } = body;

    // Backend schema (BroadcastCreate) bilan to'liq moslashtiramiz
    const broadcastPayload: Record<string, any> = {
      title: title || `Broadcast - ${new Date().toLocaleString('uz-UZ')}`,
      content: content,
      message_type: message_type || 'text',
      file_id: file_id || null,
      target_all_users: target_mode === 'all', // true yoki false
    };

    if (target_mode === 'manual' && target_user_ids) {
      broadcastPayload.target_user_ids = target_user_ids;
    }

    // Backendga so'rov yuboramiz (JWTsiz, to'g'ridan-to'g'ri)
    const backendResp = await fetch(`${API_BASE_URL}/broadcast/send`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(broadcastPayload),
    });

    const data = await backendResp.json();

    if (!backendResp.ok) {
      return NextResponse.json(
        { error: data.detail || 'Backend xatosi' },
        { status: backendResp.status }
      );
    }

    return NextResponse.json(
      {
        broadcastId: data.broadcast_id,
        broadcast_id: data.broadcast_id,
        total: data.total_users,
        status: data.status,
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