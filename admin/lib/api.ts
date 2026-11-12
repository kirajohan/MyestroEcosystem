import axios from 'axios';
import { toast } from 'sonner';
import { authFetch, getAccessToken, getRefreshToken, refreshAccessToken } from '@/lib/auth';

// ✅ YAGONA konstanta — barcha fetch va axios uchun
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://myestroeco-backend-production.up.railway.app';

// ─────────────────────────────────────────────────────────────
// TYPES
// ─────────────────────────────────────────────────────────────
export interface BotText {
  id: number;
  key: string;
  lang: string;
  text: string;
  updated_at?: string;
}

export interface BotTextCreate {
  key: string;
  lang: string;
  text: string;
}

export interface BotTextStats {
  total: number;
  by_lang: { uz: number; ru: number; en: number };
  unique_keys: number;
}

// ─────────────────────────────────────────────────────────────
// BOT TEXTS
// ─────────────────────────────────────────────────────────────
export async function getBotTexts(lang?: string): Promise<BotText[]> {
  const params = new URLSearchParams();
  if (lang) params.append('lang', lang);
  const url = `${API_BASE_URL}/api/bot-texts${params.toString() ? `?${params}` : ''}`;
  const res = await authFetch(url, { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch bot texts');
  return res.json();
}

export async function getBotTextsBulk(lang?: string): Promise<BotText[]> {
  const params = new URLSearchParams();
  if (lang) params.append('lang', lang);
  const url = `${API_BASE_URL}/api/bot-texts/bulk${params.toString() ? `?${params}` : ''}`;
  const res = await authFetch(url, { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch bot texts bulk');
  return res.json();
}

export async function getBotTextStats(): Promise<BotTextStats> {
  const res = await authFetch(`${API_BASE_URL}/api/bot-texts/stats`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch stats');
  return res.json();
}

export async function getBotTextKeys(): Promise<string[]> {
  const res = await authFetch(`${API_BASE_URL}/api/bot-texts/keys`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch keys');
  return res.json();
}

export async function upsertBotText(data: BotTextCreate): Promise<BotText> {
  const res = await authFetch(`${API_BASE_URL}/api/bot-texts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to upsert bot text');
  return res.json();
}

export async function bulkUpsertBotTexts(texts: BotTextCreate[]): Promise<BotText[]> {
  const res = await authFetch(`${API_BASE_URL}/api/bot-texts/bulk-upsert`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(texts),
  });
  if (!res.ok) throw new Error('Failed to bulk upsert');
  return res.json();
}

export async function updateBotText(id: number, text: string): Promise<BotText> {
  const res = await authFetch(`${API_BASE_URL}/api/bot-texts/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) throw new Error('Failed to update bot text');
  return res.json();
}

export async function deleteBotText(id: number): Promise<void> {
  const res = await authFetch(`${API_BASE_URL}/api/bot-texts/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Failed to delete bot text');
}

// ─────────────────────────────────────────────────────────────
// MEDIA UPLOAD (audio / image)
// ─────────────────────────────────────────────────────────────
export async function uploadMedia(
  file: File,
  fileType: 'audio' | 'image' = 'audio'
): Promise<{ url: string; file_name: string; size_bytes: number; content_type: string }> {
  if (!getAccessToken()) throw new Error('Token topilmadi. Qayta login qiling.');

  const formData = new FormData();
  formData.append('file', file);

  const res = await authFetch(
    `${API_BASE_URL}/api/v2/exam/admin/media/upload?file_type=${fileType}`,
    { method: 'POST', body: formData }
  );

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Upload xatosi: ${res.status} - ${errText}`);
  }
  return res.json();
}

export async function uploadAudioToTelegram(
  file: File
): Promise<{ file_id: string; file_name: string; duration: number; size_bytes: number }> {
  if (!getAccessToken()) throw new Error('Token topilmadi. Qayta login qiling.');

  const formData = new FormData();
  formData.append('file', file);

  const res = await authFetch(
    `${API_BASE_URL}/api/v2/exam/admin/media/upload-audio`,
    { method: 'POST', body: formData }
  );

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Telegram upload xatosi: ${res.status} - ${errText}`);
  }
  return res.json();
}


// ─────────────────────────────────────────────────────────────
// AXIOS INSTANCE
// ─────────────────────────────────────────────────────────────
export const api = axios.create({
  baseURL: API_BASE_URL,
});

// ✅ 1. Request interceptor — token'ni avtomatik qo'shish
api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token && !config.headers.Authorization) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ✅ 2. 401 → yagona single-flight refresh (lib/auth.ts), so'ng BIR marta qayta urinish
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;

    if (
      error.response?.status === 401 &&
      original &&
      !original._retry &&
      !original.url?.includes('/auth/')   // refresh/login'ni o'zi loop bo'lmasin
    ) {
      original._retry = true;
      const newToken = await refreshAccessToken();

      if (newToken) {
        original.headers.Authorization = `Bearer ${newToken}`;
        return api(original);
      }

      // Refresh token yaroqsiz bo'lib sessiya tozalangan bo'lsa — login'ga
      if (typeof window !== 'undefined' && !getRefreshToken()) {
        window.location.href = '/login';
      }
      return Promise.reject(error);
    }

    // Qolgan xatolar — toast (eski logika o'zgarmadi)
    if (!error.response) {
      toast.error('Server bilan aloqa yo‘q');
      return Promise.reject(error);
    }

    const status = error.response.status;
    const data = error.response.data;

    switch (status) {
      case 404:
        toast.error('Topilmadi');
        break;
      case 500:
        toast.error('Server xatosi');
        break;
      default: {
        const errorMsg = data?.detail || data?.message || 'Xatolik yuz berdi';
        toast.error(errorMsg);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
