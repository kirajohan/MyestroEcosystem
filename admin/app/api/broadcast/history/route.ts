// C:\Projects\MyestroEco\MyestroEco\admin\app\api\broadcast\history\route.ts
import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.BACKEND_INTERNAL_URL || 'http://backend:8000';

export async function GET(request: NextRequest) {
  try {
    const authHeader = request.headers.get('Authorization');
    if (!authHeader) {
      return NextResponse.json({ error: 'Unauthorized: Token topilmadi' }, { status: 401 });
    }

    const backendResp = await fetch(`${API_BASE_URL}/broadcast/history`, {
      method: 'GET',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`, // ⬅️ Shu qatorni qo'shing
      },
      next: { revalidate: 0 },
    });

    const data = await backendResp.json();

    if (!backendResp.ok) {
      return NextResponse.json(
        { error: data.detail || 'Backend xatosi' },
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