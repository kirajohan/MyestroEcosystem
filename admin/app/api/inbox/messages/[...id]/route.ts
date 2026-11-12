import { backendFetch } from '@/lib/proxy';
import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.BACKEND_INTERNAL_URL || process.env.NEXT_PUBLIC_API_URL || 'https://myestroeco-backend-production.up.railway.app';

function getAuthHeader(request: NextRequest): Record<string, string> {
  const authHeader = request.headers.get('authorization');
  return authHeader ? { Authorization: authHeader } : {};
}

export async function GET(
  _request: NextRequest,
  { params }: { params: { id: string[] } }
) {
  try {
    const [messageId, subPath] = params.id;

    if (!subPath) {
      // GET /api/inbox/messages/{id} — get single message
      const backendResp = await backendFetch(`${API_BASE_URL}/admin-messages/${messageId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeader(_request),
        },
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
    }

    return NextResponse.json({ detail: 'Not found' }, { status: 404 });
  } catch (error: any) {
    console.error('Inbox thread GET error:', error);
    return NextResponse.json(
      { detail: error?.message || "Noma'lum xato" },
      { status: 500 }
    );
  }
}

export async function POST(
  request: NextRequest,
  { params }: { params: { id: string[] } }
) {
  try {
    const [messageId, subPath] = params.id;

    if (subPath === 'reply') {
      // POST /api/inbox/messages/{id}/reply — send reply
      const body = await request.json();
      const { reply } = body;

      if (!reply || typeof reply !== 'string' || reply.trim().length === 0) {
        return NextResponse.json(
          { detail: 'Reply matni majburiy' },
          { status: 400 }
        );
      }

      const backendResp = await backendFetch(`${API_BASE_URL}/admin-messages/${messageId}/reply`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeader(request),
        },
        body: JSON.stringify({ reply: reply.trim() }),
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
    }

    if (subPath === 'read') {
      // POST /api/inbox/messages/{id}/read — mark as read
      const backendResp = await backendFetch(`${API_BASE_URL}/admin-messages/${messageId}/read`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeader(request),
        },
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
    }

    return NextResponse.json({ detail: 'Not found' }, { status: 404 });
  } catch (error: any) {
    console.error('Inbox POST error:', error);
    return NextResponse.json(
      { detail: error?.message || "Noma'lum xato" },
      { status: 500 }
    );
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string[] } }
) {
  try {
    const [messageId, subPath] = params.id;

    if (!subPath) {
      // DELETE /api/inbox/messages/{id} — delete message
      const backendResp = await backendFetch(`${API_BASE_URL}/admin-messages/${messageId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeader(request),
        },
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
    }

    return NextResponse.json({ detail: 'Not found' }, { status: 404 });
  } catch (error: any) {
    console.error('Inbox DELETE error:', error);
    return NextResponse.json(
      { detail: error?.message || "Noma'lum xato" },
      { status: 500 }
    );
  }
}