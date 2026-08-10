// UserResponse (backend schema)
export interface UserResponse {
  id: number;
  email: string | null;
  full_name: string;
  role: 'user' | 'admin';
  cefr_level: string;
  target_level: string;
  is_active: boolean;
  is_verified: boolean;
  profile_completed: boolean;
  telegram_id: number | null;
  telegram_username: string | null;
  ai_enabled: boolean;
  phone: string | null;
  last_login_at: string | null;
  created_at: string;
  updated_at: string;
}

// LoginRequest
export interface LoginRequest {
  email: string;
  password: string;
}

// LoginResponse
export interface LoginResponse {
  user: UserResponse;
}

// StatsResponse
export interface StatsResponse {
  total_users: number;
  active_users_7d: number;
  today_messages: number;
  error_count: number;
}

// ActivityPoint
export interface ActivityPoint {
  date: string;
  count: number;
}

// CEFRDistribution
export interface CEFRDistribution {
  A1: number;
  A2: number;
  B1: number;
  B2: number;
  C1: number;
  C2: number;
}

// UserUpdate
export interface UserUpdate {
  full_name?: string;
  email?: string;
  role?: 'user' | 'admin';
  cefr_level?: string;
  target_level?: string;
  is_active?: boolean;
  ai_enabled?: boolean;
  telegram_id?: number | null;
  phone?: string;
  password?: string;
}

// SendMessageRequest
export interface SendMessageRequest {
  telegram_id: number;
  text: string;
}

// SendMessageResponse
export interface SendMessageResponse {
  success: boolean;
  message: string;
}

// ContentItem
export interface ContentItem {
  id: number;
  title: string;
  description: string | null;
  content_type: 'video' | 'file';
  file_path: string | null;
  telegram_file_id: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ContentUpdateForm {
  title: string;
  description: string;
  file?: File | null;
}

