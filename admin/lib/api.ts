import axios from 'axios';
import { toast } from 'sonner';

// Backend URL: environment'dan o'qiladi, fallback localhost:8002
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';

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