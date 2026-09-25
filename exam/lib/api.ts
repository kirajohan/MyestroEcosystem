// exam/lib/api.ts
export const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://myestroeco-backend-production.up.railway.app";
export const SESSION_COOKIE = "maestro_session";

// 1. Tokenni o'qish (Middleware va Client uchun)
export function getSessionToken(): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie.match(new RegExp(`(?:^|;\\s*)${SESSION_COOKIE}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

// 2. Tokenni saqlash (Frontend domeniga cookie sifatida yozadi)
export function setSessionToken(token: string) {
  if (typeof window === "undefined") return;
  const secure = window.location.protocol === "https:" ? "; Secure" : "";
  // SameSite=Lax bu yerda to'g'ri, chunki cookie endi frontend domenida saqlanmoqda
  document.cookie = `${SESSION_COOKIE}=${encodeURIComponent(token)}; path=/; max-age=604800; SameSite=Lax${secure}`;
}

export function clearSessionToken() {
  if (typeof window === "undefined") return;
  document.cookie = `${SESSION_COOKIE}=; path=/; max-age=0`;
  document.cookie = `${SESSION_COOKIE}=; path=/; max-age=0; Secure`;
}

interface ApiOptions extends Omit<RequestInit, 'body'> {
  body?: unknown;
}

// 3. Yagona, to'g'ri apiFetch funksiyasi
export async function apiFetch<T = unknown>(
  path: string,
  options: ApiOptions = {}
): Promise<{ ok: boolean; status: number; data: T | null }> {
  const { body, headers, ...rest } = options;
  const token = getSessionToken();

  const res = await fetch(`${API_URL}${path}`, {
    ...rest,
    headers: {
      "Content-Type": "application/json",
      // Agar token bo'lsa, Bearer sifatida yuboramiz
      ...(token ? { "Authorization": `Bearer ${token}` } : {}),
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

// 4. Auth funksiyalari
export async function login(phone: string, password: string) {
  const res = await apiFetch<{ access_token: string }>("/api/v2/exam/auth/login", {
    method: "POST",
    body: { phone, password },
  });
  
  // MUHIM: Backend JSON javobida access_token qaytarishi kerak!
  if (res.ok && res.data && "access_token" in res.data) {
    setSessionToken(res.data.access_token);
  }
  
  return res;
}

export function logout() {
  clearSessionToken();
  return apiFetch("/api/v2/exam/auth/logout", { method: "POST" });
}

export function getMe() {
  return apiFetch("/api/v2/exam/auth/me", { method: "GET" });
}