'use client';

import React, { createContext, useContext, useState, ReactNode, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import {
  TOKEN_KEY,
  REFRESH_TOKEN_KEY,
  USER_KEY,
  TOKEN_REFRESHED_EVENT,
  AUTH_CLEARED_EVENT,
  getAccessToken,
  getRefreshToken,
  getTokenExp,
  isTokenExpiring,
  refreshAccessToken,
} from '@/lib/auth';

interface AuthUser {
  id: number;
  email: string;
  full_name: string;
  role: string;
}

interface AuthContextType {
  isLoggedIn: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  loginWithPhone: (phone: string, password: string) => Promise<void>; 
  logout: () => void;
  refreshToken: () => Promise<string | null>;
  error: string | null;
  user: AuthUser | null;
  token: string | null;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<AuthUser | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [refreshTokenValue, setRefreshTokenValue] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const resetState = useCallback(() => {
    setToken(null);
    setRefreshTokenValue(null);
    setUser(null);
    setIsLoggedIn(false);
  }, []);

  // Check localStorage on mount (eskirgan access token bo'lsa avval refresh qilinadi)
  useEffect(() => {
    let cancelled = false;

    (async () => {
      try {
        const storedUser = localStorage.getItem(USER_KEY);
        let storedToken = getAccessToken();

        if (storedToken && storedUser && isTokenExpiring(storedToken)) {
          storedToken = (await refreshAccessToken()) ?? getAccessToken();
        }

        if (cancelled) return;

        if (storedToken && storedUser) {
          setToken(storedToken);
          setRefreshTokenValue(getRefreshToken());
          setUser(JSON.parse(storedUser));
          setIsLoggedIn(true);
        }
      } catch {
        // Ignore parse errors
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, []);

  // Token yangilanganda / boshqa tabda o'zgarganda / sessiya tozalanganda state'ni sinxronlash
  useEffect(() => {
    const onRefreshed = () => {
      setToken(getAccessToken());
      setRefreshTokenValue(getRefreshToken());
    };
    const onCleared = () => {
      resetState();
      router.push('/login');
    };
    const onStorage = (e: StorageEvent) => {
      if (e.key === TOKEN_KEY || e.key === REFRESH_TOKEN_KEY) {
        const t = getAccessToken();
        if (!t) onCleared();
        else onRefreshed();
      }
    };

    window.addEventListener(TOKEN_REFRESHED_EVENT, onRefreshed);
    window.addEventListener(AUTH_CLEARED_EVENT, onCleared);
    window.addEventListener('storage', onStorage);
    return () => {
      window.removeEventListener(TOKEN_REFRESHED_EVENT, onRefreshed);
      window.removeEventListener(AUTH_CLEARED_EVENT, onCleared);
      window.removeEventListener('storage', onStorage);
    };
  }, [resetState, router]);

  // Proaktiv refresh: access token tugashidan 60s oldin; tab qaytganda ham tekshiriladi
  useEffect(() => {
    if (!isLoggedIn || !token) return;

    const exp = getTokenExp(token);
    const delay = exp ? Math.max(exp * 1000 - Date.now() - 60_000, 5_000) : 10 * 60_000;
    const timer = setTimeout(() => {
      refreshAccessToken();
    }, delay);

    const onVisible = () => {
      if (document.visibilityState === 'visible' && isTokenExpiring(getAccessToken())) {
        refreshAccessToken();
      }
    };
    document.addEventListener('visibilitychange', onVisible);

    return () => {
      clearTimeout(timer);
      document.removeEventListener('visibilitychange', onVisible);
    };
  }, [isLoggedIn, token]);

  const login = async (email: string, password: string) => {
    setError(null);
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || 'Login xatosi');
      }

      const adminToken = data.token;
      const adminRefreshToken = data.refresh_token;
      
      if (!adminToken || !adminToken.startsWith('eyJ')) {
        throw new Error("Backend haqiqiy token qaytarmadi");
      }
      
      const adminUser: AuthUser = {
        id: data.user?.id ?? 0,
        email: data.user?.email ?? email,
        full_name: data.user?.full_name ?? 'Admin',
        role: data.user?.role ?? 'admin',
      };

      localStorage.setItem(TOKEN_KEY, adminToken);
      if (adminRefreshToken) {
        localStorage.setItem(REFRESH_TOKEN_KEY, adminRefreshToken);
      }
      localStorage.setItem(USER_KEY, JSON.stringify(adminUser));

      setToken(adminToken);
      setRefreshTokenValue(adminRefreshToken);
      setUser(adminUser);
      setIsLoggedIn(true);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Login xatosi');
      throw err;
    }
  };

const loginWithPhone = async (phone: string, password: string) => {
  setError(null);
  try {
    const res = await fetch('/api/auth/phone-login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone, password }),
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || 'Telefon yoki parol notogri');
    }

    const adminToken = data.access_token || data.token;
    const adminRefreshToken = data.refresh_token;

    if (!adminToken) {
      throw new Error('Backend token qaytarmadi');
    }

    const adminUser: AuthUser = {
      id: data.user?.id ?? 0,
      email: data.user?.email ?? '',
      full_name: data.user?.full_name ?? 'Admin',
      role: data.user?.role ?? 'admin',
    };

    // Admin role tekshiruvi
    if (adminUser.role !== 'admin' && adminUser.role !== 'superadmin') {
      throw new Error('Bu tizimga faqat adminlar kira oladi');
    }

    localStorage.setItem(TOKEN_KEY, adminToken);
    if (adminRefreshToken) {
      localStorage.setItem(REFRESH_TOKEN_KEY, adminRefreshToken);
    }
    localStorage.setItem(USER_KEY, JSON.stringify(adminUser));

    setToken(adminToken);
    setRefreshTokenValue(adminRefreshToken);
    setUser(adminUser);
    setIsLoggedIn(true);
    router.push('/dashboard');
  } catch (err: any) {
    setError(err.message || 'Telefon orqali kirishda xatolik');
    throw err;
  }
};

  const refreshToken = useCallback(() => refreshAccessToken(), []);

  const logout = () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    setToken(null);
    setRefreshTokenValue(null);
    setUser(null);
    setIsLoggedIn(false);
    router.push('/login');
  };

  const value: AuthContextType = {
    isLoggedIn,
    isLoading,
    login,
    logout,
    refreshToken,
    loginWithPhone,
    error,
    user,
    token,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}