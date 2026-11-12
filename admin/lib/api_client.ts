import {
  Test,
  TestCreate,
  TestUpdate,
  TestQuestion,
  QuestionCreate,
  QuestionUpdate,
  TestWithQuestions,
} from '@/types/test';
import { authFetch } from '@/lib/auth';

// ══════════════════════════════════════════════════════════════
// API CLIENT — authFetch (token + single-flight refresh) ustida
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
    const response = await authFetch(endpoint, {
      ...options,
      headers: { 'Content-Type': 'application/json', ...(options.headers as Record<string, string>) },
    });

    if (response.status === 401) {
      throw new ApiError('Sessiya tugadi. Qayta tizimga kiring.', 401);
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
