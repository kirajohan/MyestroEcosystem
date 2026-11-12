import { headers } from 'next/headers';

/**
 * Next.js proxy route'lari uchun: kiruvchi so'rovdagi `Authorization` sarlavhasini backend'ga uzatadi.
 * Backend endi admin endpointlarida JWT talab qiladi, shuning uchun proxy tokenni yo'qotmasligi kerak.
 */
export async function backendFetch(url: string | URL, init: RequestInit = {}): Promise<Response> {
  const merged = new Headers(init.headers);
  if (!merged.has('Authorization')) {
    const incoming = headers().get('authorization');
    if (incoming) merged.set('Authorization', incoming);
  }
  return fetch(url, { ...init, headers: merged });
}
