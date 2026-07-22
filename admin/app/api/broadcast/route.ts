import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.BACKEND_INTERNAL_URL || 'http://backend:8000';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { message, mediaType, mediaUrl, userIds } = body;

    // Get JWT token from Authorization header (forwarded from client)
    const authHeader = request.headers.get('authorization') || '';
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    if (authHeader) {
      headers['Authorization'] = authHeader;
    }

    // Convert admin form schema → backend BroadcastCreate schema
    //   admin: { message, mediaType, mediaUrl, userIds }
    //   backend: { title, content, message_type, file_id, target_all_users, target_user_ids }
    const broadcastPayload = {
      title: `Broadcast - ${new Date().toLocaleString('uz-UZ')}`,
      content: message,
      message_type: mediaType || 'text',
      file_id: mediaUrl || null,
      target_all_users: !userIds || userIds.length === 0,
      target_user_ids: userIds || [],
    };

    const backendResp = await fetch(`${API_BASE_URL}/broadcast/send`, {
      method: 'POST',
      headers,
      body: JSON.stringify(broadcastPayload),
    });

    const data = await backendResp.json();

    if (!backendResp.ok) {
      return NextResponse.json(
        { error: data.detail || 'Backend xatosi' },
        { status: backendResp.status }
      );
    }

    // Convert backend response { broadcast_id, total_users, status } → admin { broadcastId, total, status }
    return NextResponse.json(
      {
        broadcastId: data.broadcast_id,
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