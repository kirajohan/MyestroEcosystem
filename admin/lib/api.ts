import axios from 'axios';
import { toast } from 'sonner';

// Eski holati: const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';

// Yangi holati (Aynan backend public domeningiz bo'lishi shart):
const API_BASE_URL = 'https://myestro-backend-production.up.railway.app/api';export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
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