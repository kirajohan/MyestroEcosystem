import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.BACKEND_INTERNAL_URL || 'http://backend:8000';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { title, content, message_type, file_id, target_mode, target_user_ids, target_filter } = body;

    // Convert admin form schema → backend BroadcastCreate schema
    const broadcastPayload: Record<string, any> = {
      title: title || `Broadcast - ${new Date().toLocaleString('uz-UZ')}`,
      content: content,
      message_type: message_type || 'text',
      file_id: file_id || null,
      target_mode: target_mode || 'all',
    };

    if (target_mode === 'manual' && target_user_ids) {
      broadcastPayload.target_user_ids = target_user_ids;
    }
    if (target_mode === 'filter' && target_filter) {
      broadcastPayload.target_filter = target_filter;
    }

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

    // Convert backend response → admin format
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
