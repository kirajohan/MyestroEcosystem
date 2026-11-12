import { backendFetch } from '@/lib/proxy';
import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.BACKEND_INTERNAL_URL || 'http://backend:8002';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const params = new URLSearchParams();
    
    const skip = searchParams.get('skip');
    const limit = searchParams.get('limit');
    const search = searchParams.get('search');
    const role = searchParams.get('role');
    const cefr_level = searchParams.get('cefr_level');
    const lang = searchParams.get('lang');
    const is_active = searchParams.get('is_active');
    
    if (skip) params.set('skip', skip);
    if (limit) params.set('limit', limit);
    if (search) params.set('search', search);
    if (role) params.set('role', role);
    if (cefr_level) params.set('cefr_level', cefr_level);
    if (lang) params.set('lang', lang);
    if (is_active) params.set('is_active', is_active);

    const backendResp = await backendFetch(`${API_BASE_URL}/users?${params.toString()}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
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