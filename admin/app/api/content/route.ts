import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.BACKEND_INTERNAL_URL || 'http://backend:8002';

export async function GET() {
  try {
    const backendResp = await fetch(`${API_BASE_URL}/content`, {
      method: 'GET',
    });

    if (!backendResp.ok) {
      const errText = await backendResp.text();
      return NextResponse.json(
        { detail: errText || 'Backend xatosi' },
        { status: backendResp.status }
      );
    }

    const data = await backendResp.json();
    return NextResponse.json(data, { status: 200 });
  } catch (error: any) {
    return NextResponse.json(
      { detail: error?.message || 'Nomatʼlum xato' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();

    // Forward to backend content endpoint
    const backendResp = await fetch(`${API_BASE_URL}/content`, {
      method: 'POST',
      body: formData,
    });

    if (!backendResp.ok) {
      const errText = await backendResp.text();
      return NextResponse.json(
        { detail: errText || 'Backend xatosi' },
        { status: backendResp.status }
      );
    }

    const data = await backendResp.json();
    return NextResponse.json(data, { status: 200 });
  } catch (error: any) {
    return NextResponse.json(
      { detail: error?.message || 'Nomatʼlum xato' },
      { status: 500 }
    );
  }
}
