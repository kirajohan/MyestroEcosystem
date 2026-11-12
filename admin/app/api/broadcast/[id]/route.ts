// C:\Projects\MyestroEco\MyestroEco\admin\app\api\broadcast\[id]\route.ts
import { backendFetch } from '@/lib/proxy';
import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.BACKEND_INTERNAL_URL || 'http://backend:8000';

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const authHeader = request.headers.get('Authorization');
    if (!authHeader) {
      return NextResponse.json({ error: 'Unauthorized: Token topilmadi' }, { status: 401 });
    }

    const { id } = params;
    if (!id) {
      return NextResponse.json({ error: 'id majburiy' }, { status: 400 });
    }

    const backendResp = await backendFetch(`${API_BASE_URL}/broadcast/status/${id}`, {
      method: 'GET',
      headers: {
        'Authorization': authHeader,
      },
    });

    if (!backendResp.ok) {
      const errText = await backendResp.text();
      return NextResponse.json(
        { error: errText || 'Backend xatosi' },
        { status: backendResp.status }
      );
    }

    const data = await backendResp.json();

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

export async function POST(request: NextRequest) {
  try {
    const authHeader = request.headers.get('Authorization');
    if (!authHeader) {
      return NextResponse.json({ error: 'Unauthorized: Token topilmadi' }, { status: 401 });
    }

    const formData = await request.formData();
    const file = formData.get('file');

    if (!file || !(file instanceof Blob)) {
      return NextResponse.json(
        { error: 'Fayl talab qilinadi' },
        { status: 400 }
      );
    }

    const backendFormData = new FormData();
    backendFormData.append('file', file);

    const backendResp = await backendFetch(`${API_BASE_URL}/broadcast/upload-media`, {
      method: 'POST',
      headers: {
        'Authorization': authHeader,
      },
      body: backendFormData,
    });

    const data = await backendResp.json();

    if (!backendResp.ok) {
      return NextResponse.json(
        { error: data.detail || 'Upload xatosi' },
        { status: backendResp.status }
      );
    }

    return NextResponse.json(data, { status: 200 });
  } catch (error: any) {
    return NextResponse.json(
      { error: error?.message || "Noma'lum xato" },
      { status: 500 }
    );
  }
}