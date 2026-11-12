import { backendFetch } from '@/lib/proxy';
import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'https://myestroeco-backend-production.up.railway.app';

// GET /api/bot-texts/[id] - Get single bot text
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const backendUrl = `${BACKEND_URL}/api/bot-texts/${params.id}`;
    
    const res = await backendFetch(backendUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({ detail: 'Not found' }));
      return NextResponse.json(
        { error: errorData.detail || 'Bot text not found' },
        { status: res.status }
      );
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error(`[API] GET /api/bot-texts/${params.id} error:`, error);
    return NextResponse.json(
      { error: 'Failed to connect to backend' },
      { status: 500 }
    );
  }
}

// PUT /api/bot-texts/[id] - Update bot text
export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const body = await request.json();
    const backendUrl = `${BACKEND_URL}/api/bot-texts/${params.id}`;
    
    const res = await backendFetch(backendUrl, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({ detail: 'Update failed' }));
      return NextResponse.json(
        { error: errorData.detail || 'Failed to update bot text' },
        { status: res.status }
      );
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error(`[API] PUT /api/bot-texts/${params.id} error:`, error);
    return NextResponse.json(
      { error: 'Failed to connect to backend' },
      { status: 500 }
    );
  }
}

// DELETE /api/bot-texts/[id] - Delete bot text
export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const backendUrl = `${BACKEND_URL}/api/bot-texts/${params.id}`;
    
    const res = await backendFetch(backendUrl, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({ detail: 'Delete failed' }));
      return NextResponse.json(
        { error: errorData.detail || 'Failed to delete bot text' },
        { status: res.status }
      );
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error(`[API] DELETE /api/bot-texts/${params.id} error:`, error);
    return NextResponse.json(
      { error: 'Failed to connect to backend' },
      { status: 500 }
    );
  }
}