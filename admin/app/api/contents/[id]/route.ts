import { NextRequest, NextResponse } from 'next/server';
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';

// PATCH — tahrirlash (matn + ixtiyoriy fayl almashtirish)
export async function PATCH(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params;
    const formData = await request.formData();

    // Forward to backend PATCH endpoint
    const backendResp = await fetch(`${API_BASE_URL}/content/${id}`, {
      method: 'PATCH',
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
      { detail: error?.message || "Noma'lum xato" },
      { status: 500 }
    );
  }
}

// DELETE — o'chirish
export async function DELETE(
  _request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params;

    const backendResp = await fetch(`${API_BASE_URL}/content/${id}`, {
      method: 'DELETE',
    });

    if (!backendResp.ok) {
      const errText = await backendResp.text();
      return NextResponse.json(
        { detail: errText || 'Backend xatosi' },
        { status: backendResp.status }
      );
    }

    const data = await backendResp.json().catch(() => ({ message: 'Deleted' }));
    return NextResponse.json(data, { status: 200 });
  } catch (error: any) {
    return NextResponse.json(
      { detail: error?.message || "Noma'lum xato" },
      { status: 500 }
    );
  }
}

// GET — progress endpoint placeholder
export async function GET(
  _req: NextRequest,
  { params }: { params: { id: string } }
) {
  const { id } = params;
  if (!id) {
    return NextResponse.json({ error: "id majburiy" }, { status: 400 });
  }

  // Placeholder response until Redis is properly set up
  return NextResponse.json(
    { error: "Broadcast progress endpoint not yet implemented" },
    { status: 501 }
  );
}
