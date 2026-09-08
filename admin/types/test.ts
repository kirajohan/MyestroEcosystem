export type CefrLevel = 'A1' | 'A2' | 'B1' | 'B2' | 'C1' | 'C2';

export const CEFR_LEVELS: CefrLevel[] = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'];

// ═══════════════════════════════════════════════════════════
// TestOption — Javob varianti
// ═══════════════════════════════════════════════════════════
export interface TestOption {
  id?: number;
  text: string;
  is_correct: boolean;
  order?: number;
}

export interface AITestGenerateRequest {
  title: string;
  cefr_level: CefrLevel;
  num_questions: number;
  topic: string;
}
// ═══════════════════════════════════════════════════════════
// TestQuestion — Alohida savol (test ichidagi)
// ═══════════════════════════════════════════════════════════
export interface TestQuestion {
  id: number;
  test_id: number;
  question_text: string;
  options: string[];
  correct_option_index: number;
  explanation?: string | null;
  order_index?: number;
  created_at?: string;
  updated_at?: string;
}

// ═══════════════════════════════════════════════════════════
// Test — To'liq test (title, description, questions bilan)
// ═══════════════════════════════════════════════════════════
export interface Test {
  id: number;
  title: string;
  description?: string | null;
  cefr_level: CefrLevel;
  passing_score: number;
  time_limit_sec?: number;
  is_active: boolean;
  is_published?: boolean;
  questions?: TestQuestion[];
  created_at: string;
  updated_at?: string;
}

// ═══════════════════════════════════════════════════════════
// Payloads — API so'rovlari uchun
// ═══════════════════════════════════════════════════════════
export interface TestCreate {
  title: string;
  description?: string | null;
  cefr_level: CefrLevel;
  passing_score: number;
  is_active: boolean;
}

export interface TestUpdate {
  title: string;
  description?: string | null;
  cefr_level: CefrLevel;
  passing_score: number;
  is_active: boolean;
}

export interface QuestionCreate {
  question_text: string;
  options: string[];
  correct_option_index: number;
  explanation?: string | null;
  order_index?: number;
}

export interface QuestionUpdate {
  question_text: string;
  options: string[];
  correct_option_index: number;
  explanation?: string | null;
}

// ═══════════════════════════════════════════════════════════
// Form States — Komponentlar uchun
// ═══════════════════════════════════════════════════════════
export interface TestFormState {
  title: string;
  description: string;
  cefr_level: CefrLevel;
  passing_score: number;
  is_active: boolean;
}

export const DEFAULT_TEST_FORM: TestFormState = {
  title: '',
  description: '',
  cefr_level: 'A1',
  passing_score: 70,
  is_active: true,
};

export interface QuestionFormState {
  question_text: string;
  options: string[];
  correct_option_index: number;
  explanation: string;
}

export const DEFAULT_QUESTION_FORM: QuestionFormState = {
  question_text: '',
  options: ['', ''],
  correct_option_index: 0,
  explanation: '',
};

// ═══════════════════════════════════════════════════════════
// API Response types
// ═══════════════════════════════════════════════════════════
export interface TestWithQuestions extends Test {
  questions: TestQuestion[];
}

export interface TestListResponse {
  items: Test[];
  total: number;
  page?: number;
  per_page?: number;
}