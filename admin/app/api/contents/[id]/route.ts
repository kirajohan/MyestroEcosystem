import { backendFetch } from '@/lib/proxy';
import { NextRequest, NextResponse } from 'next/server';
const API_BASE_URL = process.env.BACKEND_INTERNAL_URL || process.env.NEXT_PUBLIC_API_URL || 'https://myestroeco-backend-production.up.railway.app';

// PATCH — tahrirlash (matn + ixtiyoriy fayl almashtirish)
export async function PATCH(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params;
    const formData = await request.formData();

    // Validate content type if file is being uploaded
    const file = formData.get('file') as File | null;
    const contentType = formData.get('content_type') as string | null;
    
    if (file && !contentType) {
      return NextResponse.json(
        { detail: 'content_type maydoni to\'ldirilishi shart' },
        { status: 400 }
      );
    }

    // Forward to backend PATCH endpoint with timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 120000); // 2 minute timeout for file uploads

    try {
      const backendResp = await backendFetch(`${API_BASE_URL}/content/${id}`, {
        method: 'PATCH',
        body: formData,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!backendResp.ok) {
        let errorDetail = 'Backend xatosi';
        try {
          const errData = await backendResp.json();
          errorDetail = errData.detail || errData.message || errorDetail;
        } catch {
          const errText = await backendResp.text();
          errorDetail = errText || errorDetail;
        }
        
        return NextResponse.json(
          { detail: errorDetail },
          { status: backendResp.status }
        );
      }

      const data = await backendResp.json();
      
      // Validate response has required fields
      if (!data.id || !data.telegram_file_id) {
        return NextResponse.json(
          { detail: 'Backend noto\'g\'ri javob qaytardi' },
          { status: 500 }
        );
      }

      return NextResponse.json(data, { status: 200 });
    } catch (fetchError: any) {
      clearTimeout(timeoutId);
      
      if (fetchError.name === 'AbortError') {
        return NextResponse.json(
          { detail: 'So\'rov vaqti tugadi. Kattaroq fayl yuklash uchun biroz kuting.' },
          { status: 408 }
        );
      }
      
      throw fetchError;
    }
  } catch (error: any) {
    console.error('Content PATCH error:', error);
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

    const backendResp = await backendFetch(`${API_BASE_URL}/content/${id}`, {
      method: 'DELETE',
    });

    if (!backendResp.ok) {
      let errorDetail = 'Backend xatosi';
      try {
        const errData = await backendResp.json();
        errorDetail = errData.detail || errData.message || errorDetail;
      } catch {
        const errText = await backendResp.text();
        errorDetail = errText || errorDetail;
      }
      
      return NextResponse.json(
        { detail: errorDetail },
        { status: backendResp.status }
      );
    }

    const data = await backendResp.json().catch(() => ({ message: 'Deleted' }));
    return NextResponse.json(data, { status: 200 });
  } catch (error: any) {
    console.error('Content DELETE error:', error);
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
