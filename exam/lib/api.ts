// lib/api.ts
// Backend API bilan ishlash uchun markaziy client.
// Session-based auth: cookie avtomatik yuboriladi (credentials: "include").

export const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002";

interface ApiOptions extends Omit<RequestInit, 'body'> {
  body?: unknown;
}

export async function apiFetch<T = unknown>(
  path: string,
  options: ApiOptions = {}
): Promise<{ ok: boolean; status: number; data: T | null }> {
  const { body, headers, ...rest } = options;

  const res = await fetch(`${API_URL}${path}`, {
    ...rest,
    credentials: "include", // ✅ cookie yuborish uchun SHART
    headers: {
      "Content-Type": "application/json",
      ...(headers as Record<string, string>),
    },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  let data: T | null = null;
  try {
    data = await res.json();
  } catch {
    data = null;
  }

  return { ok: res.ok, status: res.status, data };
}

// ── Auth ──────────────────────────────────────────────
export function login(phone: string, password: string) {
  return apiFetch("/api/v2/exam/auth/login", {
    method: "POST",
    body: { phone, password },
  });
}

export function logout() {
  return apiFetch("/api/v2/exam/auth/logout", { method: "POST" });
}

export function getMe() {
  return apiFetch("/api/v2/exam/auth/me", { method: "GET" });
}
