export const SESSION_COOKIE = "maestro_session";
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002";

export function getSessionToken(): string | null {
  if (typeof document === "undefined") return null;
  const m = document.cookie.match(
    new RegExp(`(?:^|;\\s*)${SESSION_COOKIE}=([^;]*)`)
  );
  return m ? decodeURIComponent(m[1]) : null;
}

export function setSessionToken(token: string) {
  const secure = window.location.protocol === "https:" ? "; Secure" : "";
  document.cookie =
    `${SESSION_COOKIE}=${encodeURIComponent(token)}; path=/; max-age=604800; SameSite=Lax${secure}`;
}

export function clearSessionToken() {
  // Barcha variantlarni o'chirish (Secure bilan/holda)
  document.cookie = `${SESSION_COOKIE}=; path=/; max-age=0`;
  document.cookie = `${SESSION_COOKIE}=; path=/; max-age=0; Secure`;
}

/** Backend'ga HAR DOIM Bearer header bilan so'rov yuboradi */
export async function apiFetch(path: string, options: RequestInit = {}) {
  const token = getSessionToken();
  const headers = new Headers(options.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (options.body && typeof options.body === "string") {
    headers.set("Content-Type", "application/json");
  }
  return fetch(`${API_URL}${path}`, { ...options, headers });
}