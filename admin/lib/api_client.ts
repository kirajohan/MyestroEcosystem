// admin/lib/api-client.ts

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
// API CLIENT — Next.js API route'lariga so'rov yuborish uchun
// Frontend komponentlar shu client orqali ishlaydi
// ══════════════════════════════════════════════════════════════

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  try {
    const response = await fetch(endpoint, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Noma\'lum xato' }));
      throw new ApiError(errorData.detail || `HTTP ${response.status}`, response.status);
    }

    // DELETE 204 No Content qaytarishi mumkin
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

// ─── TESTS API ─────────────────────────────────────────────────

export const testsApi = {
  // Testlar ro'yxatini olish
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

  // Bitta testni olish
  get: async (id: number): Promise<Test> => {
    return request<Test>(`/api/tests/${id}`);
  },

  // Yangi test yaratish
  create: async (data: TestCreate): Promise<Test> => {
    return request<Test>('/api/tests', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  // Testni yangilash
  update: async (id: number, data: TestUpdate): Promise<Test> => {
    return request<Test>(`/api/tests/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  // Testni o'chirish
  delete: async (id: number): Promise<void> => {
    return request<void>(`/api/tests/${id}`, {
      method: 'DELETE',
    });
  },

  // Test savollarini olish
  getQuestions: async (testId: number): Promise<TestWithQuestions> => {
    return request<TestWithQuestions>(`/api/tests/${testId}/questions`);
  },

  // Savol qo'shish
  addQuestion: async (testId: number, data: QuestionCreate): Promise<TestQuestion> => {
    return request<TestQuestion>(`/api/tests/${testId}/questions`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  // Savolni yangilash
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

  // Savolni o'chirish
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
