// admin/types/test.ts

// ══════════════════════════════════════════════════════════════
// TEST MODULE TYPES
// ══════════════════════════════════════════════════════════════

// CEFR darajalar
export type CefrLevel = 'A1' | 'A2' | 'B1' | 'B2' | 'C1' | 'C2';

export const CEFR_LEVELS: CefrLevel[] = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'];

// ─── TEST (asosiy ma'lumotlar) ─────────────────────────────────

export interface Test {
  id: number;
  title: string;
  description: string | null;
  cefr_level: CefrLevel;
  passing_score: number; // 0-100 foiz
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Test yaratish payload
export interface TestCreate {
  title: string;
  description?: string | null;
  cefr_level: CefrLevel;
  passing_score?: number; // default: 60
  is_active?: boolean; // default: true
}

// Test yangilash payload
export interface TestUpdate {
  title?: string;
  description?: string | null;
  cefr_level?: CefrLevel;
  passing_score?: number;
  is_active?: boolean;
}

// ─── TEST QUESTION (savol) ─────────────────────────────────────

export interface TestQuestion {
  id: number;
  test_id: number;
  question_text: string;
  options: string[]; // ["variant1", "variant2", "variant3", "variant4"]
  correct_option_index: number; // 0, 1, 2, 3
  explanation: string | null;
  order_index: number;
  created_at: string;
}

// Savol yaratish payload
export interface QuestionCreate {
  question_text: string;
  options: string[]; // Kamida 2 ta, maksimal 10 ta variant
  correct_option_index: number; // 0-based index
  explanation?: string | null;
  order_index?: number;
}

// Savol yangilash payload
export interface QuestionUpdate {
  question_text?: string;
  options?: string[];
  correct_option_index?: number;
  explanation?: string | null;
  order_index?: number;
}

// ─── TEST WITH QUESTIONS (batafsil) ────────────────────────────

export interface TestWithQuestions extends Test {
  questions: TestQuestion[];
}

// ─── API RESPONSE TYPES ────────────────────────────────────────

export interface ApiErrorResponse {
  detail: string;
}

export interface TestListResponse {
  tests: Test[];
  total: number;
}

// ─── FORM STATE (frontend uchun) ───────────────────────────────

export interface TestFormState {
  title: string;
  description: string;
  cefr_level: CefrLevel;
  passing_score: number;
  is_active: boolean;
}

export interface QuestionFormState {
  question_text: string;
  options: string[];
  correct_option_index: number;
  explanation: string;
}

export const DEFAULT_TEST_FORM: TestFormState = {
  title: '',
  description: '',
  cefr_level: 'A1',
  passing_score: 60,
  is_active: true,
};

export const DEFAULT_QUESTION_FORM: QuestionFormState = {
  question_text: '',
  options: ['', '', '', ''],
  correct_option_index: 0,
  explanation: '',
};