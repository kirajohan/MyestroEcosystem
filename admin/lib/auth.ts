// ══════════════════════════════════════════════════════════════
// AUTH — yagona token boshqaruvi (single-flight refresh + authFetch)
// ══════════════════════════════════════════════════════════════

export const TOKEN_KEY = 'myestro_admin_token';
export const REFRESH_TOKEN_KEY = 'myestro_admin_refresh_token';
export const USER_KEY = 'myestro_admin_user';

export const TOKEN_REFRESHED_EVENT = 'auth:token-refreshed';
export const AUTH_CLEARED_EVENT = 'auth:cleared';

const isBrowser = () => typeof window !== 'undefined';

export function getAccessToken(): string | null {
  return isBrowser() ? localStorage.getItem(TOKEN_KEY) : null;
}

export function getRefreshToken(): string | null {
  return isBrowser() ? localStorage.getItem(REFRESH_TOKEN_KEY) : null;
}

export function setTokens(accessToken: string, refreshToken?: string | null) {
  if (!isBrowser()) return;
  localStorage.setItem(TOKEN_KEY, accessToken);
  if (refreshToken) localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
}

export function clearAuth() {
  if (!isBrowser()) return;
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  window.dispatchEvent(new Event(AUTH_CLEARED_EVENT));
}

function redirectToLogin() {
  if (isBrowser() && !window.location.pathname.startsWith('/login')) {
    window.location.href = '/login';
  }
}

/** JWT `exp` (sekundlarda) ni qaytaradi, o'qib bo'lmasa null. */
export function getTokenExp(token: string | null): number | null {
  if (!token) return null;
  try {
    const part = token.split('.')[1];
    const json = atob(part.replace(/-/g, '+').replace(/_/g, '/'));
    const exp = JSON.parse(json).exp;
    return typeof exp === 'number' ? exp : null;
  } catch {
    return null;
  }
}

/** Token tugagan yoki `skewSec` soniya ichida tugaydigan bo'lsa true. */
export function isTokenExpiring(token: string | null, skewSec = 60): boolean {
  const exp = getTokenExp(token);
  if (exp === null) return !token;
  return exp * 1000 - Date.now() <= skewSec * 1000;
}

// ─── Single-flight refresh ──────────────────────────────────
let refreshPromise: Promise<string | null> | null = null;

/**
 * Yangi access token oladi. Parallel chaqiruvlar bitta so'rovni kutadi.
 * Refresh token yaroqsiz (400/401) bo'lsa sessiya tozalanadi;
 * tarmoq xatosi yoki 5xx da sessiya SAQLANADI (null qaytadi).
 */
export function refreshAccessToken(): Promise<string | null> {
  if (refreshPromise) return refreshPromise;

  refreshPromise = (async () => {
    const refreshToken = getRefreshToken();
    if (!refreshToken) {
      clearAuth();
      return null;
    }

    try {
      const res = await fetch('/api/auth/refresh', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (res.status === 400 || res.status === 401) {
        clearAuth();
        return null;
      }
      if (!res.ok) return null;

      const data = await res.json();
      if (!data.access_token) return null;

      setTokens(data.access_token, data.refresh_token);
      window.dispatchEvent(new Event(TOKEN_REFRESHED_EVENT));
      return data.access_token as string;
    } catch (err) {
      console.error('Token refresh failed:', err);
      return null;
    } finally {
      refreshPromise = null;
    }
  })();

  return refreshPromise;
}

/**
 * fetch + Authorization header. 401 bo'lsa bir marta refresh qilib qayta urinadi.
 * Refresh muvaffaqiyatsiz bo'lsa va sessiya tozalangan bo'lsa — /login ga yo'naltiradi.
 */
export async function authFetch(input: RequestInfo | URL, init: RequestInit = {}): Promise<Response> {
  const send = (token: string | null) => {
    const headers = new Headers(init.headers);
    if (token) headers.set('Authorization', `Bearer ${token}`);
    return fetch(input, { ...init, headers });
  };

  let token = getAccessToken();
  if (token && isTokenExpiring(token, 10)) {
    token = (await refreshAccessToken()) ?? token;
  }

  const res = await send(token);
  if (res.status !== 401) return res;

  const newToken = await refreshAccessToken();
  if (newToken) return send(newToken);

  if (!getRefreshToken()) redirectToLogin();
  return res;
}
