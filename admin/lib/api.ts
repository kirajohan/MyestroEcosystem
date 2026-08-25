import axios from 'axios';
import { toast } from 'sonner';

// Backend URL: environment'dan o'qiladi, fallback localhost:8002
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';


// lib/api.ts
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

// ─── GET ALL ────────────────────────────────────────────
export async function getBotTexts(lang?: string): Promise<BotText[]> {
  const params = new URLSearchParams();
  if (lang) params.append('lang', lang);

  const url = `${API_BASE_URL}/api/bot-texts${params.toString() ? `?${params}` : ''}`;
  const res = await fetch(url, { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch bot texts');
  return res.json();
}

// ─── GET BULK (all for caching) ─────────────────────────
export async function getBotTextsBulk(lang?: string): Promise<BotText[]> {
  const params = new URLSearchParams();
  if (lang) params.append('lang', lang);

  const url = `${API_BASE_URL}/api/bot-texts/bulk${params.toString() ? `?${params}` : ''}`;
  const res = await fetch(url, { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch bot texts bulk');
  return res.json();
}

// ─── GET STATS ──────────────────────────────────────────
export async function getBotTextStats(): Promise<BotTextStats> {
  const res = await fetch(`${API_BASE_URL}/api/bot-texts/stats`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch stats');
  return res.json();
}

// ─── GET KEYS ───────────────────────────────────────────
export async function getBotTextKeys(): Promise<string[]> {
  const res = await fetch(`${API_BASE_URL}/api/bot-texts/keys`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch keys');
  return res.json();
}

// ─── UPSERT (create or update) ──────────────────────────
export async function upsertBotText(data: BotTextCreate): Promise<BotText> {
  const res = await fetch(`${API_BASE_URL}/api/bot-texts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to upsert bot text');
  return res.json();
}

// ─── BULK UPSERT ────────────────────────────────────────
export async function bulkUpsertBotTexts(texts: BotTextCreate[]): Promise<BotText[]> {
  const res = await fetch(`${API_BASE_URL}/api/bot-texts/bulk-upsert`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(texts),
  });
  if (!res.ok) throw new Error('Failed to bulk upsert');
  return res.json();
}

// ─── UPDATE ─────────────────────────────────────────────
export async function updateBotText(id: number, text: string): Promise<BotText> {
  const res = await fetch(`${API_BASE_URL}/api/bot-texts/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) throw new Error('Failed to update bot text');
  return res.json();
}

// ─── DELETE ─────────────────────────────────────────────
export async function deleteBotText(id: number): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/api/bot-texts/${id}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Failed to delete bot text');
}


export const api = axios.create({
  baseURL: API_BASE_URL,
  // Content-Type default qo'yilmaydi — Axios avtomatik aniqlaydi:
  // - Plain object yuborilsa → application/json
  // - FormData yuborilsa → multipart/form-data; boundary=...
  // Agar default Content-Type: application/json qo'yilsa, FormData
  // multipart/form-dataga o'tmaydi va backend 422 qaytaradi.
});

// Faqat xatoliklarni ko'rsatish, token bilan bog'liq kod YO'Q
api.interceptors.response.use(
  (response) => response,
  (error) => {
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
      default:
        const errorMsg = data?.detail || data?.message || 'Xatolik yuz berdi';
        toast.error(errorMsg);
    }

    return Promise.reject(error);
  }
);

export default api;