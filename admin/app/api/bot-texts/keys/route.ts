import { backendFetch } from '@/lib/proxy';
import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// GET /api/bot-texts/keys - Get all unique keys
export async function GET(request: NextRequest) {
  try {
    const backendUrl = `${BACKEND_URL}/api/bot-texts/keys`;
    
    const res = await backendFetch(backendUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!res.ok) {
      return NextResponse.json(
        { error: 'Failed to fetch keys' },
        { status: res.status }
      );
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('[API] GET /api/bot-texts/keys error:', error);
    return NextResponse.json(
      { error: 'Failed to connect to backend' },
      { status: 500 }
    );
  }
}
