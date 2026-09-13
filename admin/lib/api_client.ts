import {
  Test,
  TestCreate,
  TestUpdate,
  TestQuestion,
  QuestionCreate,
  QuestionUpdate,
  TestWithQuestions,
} from '@/types/test';

// ══════════════════════════════════════════════════════════════
// API CLIENT — Token bilan + Auto-refresh interceptor
// ══════════════════════════════════════════════════════════════

const TOKEN_KEY = 'myestro_admin_token';
const REFRESH_TOKEN_KEY = 'myestro_admin_refresh_token';

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

// ─── Token Refresh Logikasi ─────────────────────────────────
let isRefreshing = false;
let refreshPromise: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  // Agar boshqa joyda refresh bo'layotgan bo'lsa, uni kutamiz
  if (isRefreshing && refreshPromise) {
    return refreshPromise;
  }

  isRefreshing = true;
  refreshPromise = (async () => {
    try {
      const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
      if (!refreshToken) return null;

      const res = await fetch('/api/auth/refresh', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!res.ok) {
        console.error('❌ Refresh failed:', res.status);
        return null;
      }

      const data = await res.json();
      const newAccessToken = data.access_token;
      const newRefreshToken = data.refresh_token;

      if (newAccessToken) {
        localStorage.setItem(TOKEN_KEY, newAccessToken);
        if (newRefreshToken) {
          localStorage.setItem(REFRESH_TOKEN_KEY, newRefreshToken);
        }
        console.log('✅ Token refreshed successfully');
        return newAccessToken;
      }

      return null;
    } catch (error) {
      console.error('❌ Refresh token error:', error);
      return null;
    } finally {
      isRefreshing = false;
      refreshPromise = null;
    }
  })();

  return refreshPromise;
}

// ─── Asosiy request funksiyasi ──────────────────────────────
async function request<T>(
  endpoint: string,
  options: RequestInit = {},
  isRetry = false
): Promise<T> {
  try {
    // ✅ Token'ni qo'shish
    const token = localStorage.getItem(TOKEN_KEY);
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(endpoint, {
      ...options,
      headers,
    });

    // ✅ 401 Unauthorized — token eskirgan, refresh qilishga urinish
    if (response.status === 401 && !isRetry) {
      console.log('🔄 401 received, attempting to refresh token...');
      const newToken = await refreshAccessToken();
      
      if (newToken) {
        // Yangi token bilan qayta urinish
        console.log('🔄 Retrying request with new token...');
        return request<T>(endpoint, options, true);
      } else {
        // Refresh muvaffaqiyatsiz — login sahifaga yo'naltirish
        console.error('❌ Refresh failed, redirecting to login');
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(REFRESH_TOKEN_KEY);
        localStorage.removeItem('myestro_admin_user');
        
        // Login sahifaga redirect (faqat browser'da)
        if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
          window.location.href = '/login';
        }
        
        throw new ApiError('Sessiya tugadi. Qayta tizimga kiring.', 401);
      }
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Noma\'lum xato' }));
      throw new ApiError(errorData.detail || `HTTP ${response.status}`, response.status);
    }

    // DELETE 204 No Content
    if (response.status === 204) {
      return undefined as T;
    }

    return response.json();
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError(
      error instanceof Error ? error.message : 'Tarmoq xatosi',
      0
    );
  }
}

// ─── TESTS API ─────────────────────────────────────────────

export const testsApi = {
  list: async (params?: {
    level?: string;
    active_only?: boolean;
    limit?: number;
    offset?: number;
  }): Promise<Test[]> => {
    const searchParams = new URLSearchParams();
    if (params?.level) searchParams.set('level', params.level);
    if (params?.active_only !== undefined) searchParams.set('active_only', String(params.active_only));
    if (params?.limit) searchParams.set('limit', String(params.limit));
    if (params?.offset) searchParams.set('offset', String(params.offset));

    const query = searchParams.toString();
    return request<Test[]>(`/api/tests${query ? `?${query}` : ''}`);
  },

  get: async (id: number): Promise<Test> => {
    return request<Test>(`/api/tests/${id}`);
  },

  create: async (data: TestCreate): Promise<Test> => {
    return request<Test>('/api/tests', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  update: async (id: number, data: TestUpdate): Promise<Test> => {
    return request<Test>(`/api/tests/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  delete: async (id: number): Promise<void> => {
    return request<void>(`/api/tests/${id}`, {
      method: 'DELETE',
    });
  },

  getQuestions: async (testId: number): Promise<TestWithQuestions> => {
    return request<TestWithQuestions>(`/api/tests/${testId}/questions`);
  },

  addQuestion: async (testId: number, data: QuestionCreate): Promise<TestQuestion> => {
    return request<TestQuestion>(`/api/tests/${testId}/questions`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  updateQuestion: async (
    testId: number,
    questionId: number,
    data: QuestionUpdate
  ): Promise<TestQuestion> => {
    return request<TestQuestion>(`/api/tests/${testId}/questions/${questionId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  deleteQuestion: async (testId: number, questionId: number): Promise<void> => {
    return request<void>(`/api/tests/${testId}/questions/${questionId}`, {
      method: 'DELETE',
    });
  },

  generateWithAI: async (data: import('@/types/test').AITestGenerateRequest): Promise<Test> => {
    return request<Test>('/api/tests/ai-generate', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
};