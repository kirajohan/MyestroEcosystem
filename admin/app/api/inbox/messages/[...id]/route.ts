import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.BACKEND_INTERNAL_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';

export async function GET(
  _request: NextRequest,
  { params }: { params: { id: string[] } }
) {
  try {
    const [messageId, subPath] = params.id;

    if (!subPath) {
      // GET /api/inbox/messages/{id} — get thread
      const backendResp = await fetch(`${API_BASE_URL}/inbox/messages/${messageId}`, {
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

      const backendResp = await fetch(`${API_BASE_URL}/inbox/messages/${messageId}/reply`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
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

    return NextResponse.json({ detail: 'Not found' }, { status: 404 });
  } catch (error: any) {
    console.error('Inbox reply POST error:', error);
    return NextResponse.json(
      { detail: error?.message || "Noma'lum xato" },
      { status: 500 }
    );
  }
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: { id: string[] } }
) {
  try {
    const [messageId, subPath] = params.id;

    if (subPath === 'status') {
      // PATCH /api/inbox/messages/{id}/status — update status
      const body = await request.json();
      const { status: newStatus } = body;

      if (!newStatus || !['new', 'read', 'replied', 'closed'].includes(newStatus)) {
        return NextResponse.json(
          { detail: 'Noto\'g\'ri status qiymati' },
          { status: 400 }
        );
      }

      const backendResp = await fetch(`${API_BASE_URL}/inbox/messages/${messageId}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus }),
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
    console.error('Inbox status PATCH error:', error);
    return NextResponse.json(
      { detail: error?.message || "Noma'lum xato" },
      { status: 500 }
    );
  }
}

export async function DELETE(
  _request: NextRequest,
  { params }: { params: { id: string[] } }
) {
  try {
    const [messageId, subPath] = params.id;

    if (!subPath) {
      // DELETE /api/inbox/messages/{id} — delete message
      const backendResp = await fetch(`${API_BASE_URL}/inbox/messages/${messageId}`, {
        method: 'DELETE',
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