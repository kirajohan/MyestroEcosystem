'use client';

import React, { createContext, useContext, useState, ReactNode, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';

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
  logout: () => void;
  refreshToken: () => Promise<string | null>;
  error: string | null;
  user: AuthUser | null;
  token: string | null;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

const TOKEN_KEY = 'myestro_admin_token';
const REFRESH_TOKEN_KEY = 'myestro_admin_refresh_token';
const USER_KEY = 'myestro_admin_user';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<AuthUser | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [refreshTokenValue, setRefreshTokenValue] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  // Check localStorage on mount
  useEffect(() => {
    try {
      const storedToken = localStorage.getItem(TOKEN_KEY);
      const storedRefreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
      const storedUser = localStorage.getItem(USER_KEY);
      
      if (storedToken && storedUser) {
        setToken(storedToken);
        setRefreshTokenValue(storedRefreshToken);
        setUser(JSON.parse(storedUser));
        setIsLoggedIn(true);
      }
    } catch {
      // Ignore parse errors
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Auto-refresh token before expiry (every 14 minutes for 15min token)
  // useEffect(() => {
  //   if (!isLoggedIn || !refreshTokenValue) return;

  //   const refreshInterval = setInterval(async () => {
  //     try {
  //       const newToken = await refreshToken();
  //       if (!newToken) {
  //         logout();
  //       }
  //     } catch (err) {
  //       console.error('Auto-refresh failed:', err);
  //       logout();
  //     }
  //   }, 14 * 60 * 1000); // 14 minutes

  //   return () => clearInterval(refreshInterval);
  // }, [isLoggedIn, refreshTokenValue]);

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

  const refreshToken = useCallback(async (): Promise<string | null> => {
    try {
      const currentRefreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
      if (!currentRefreshToken) {
        return null;
      }

      const res = await fetch('/api/auth/refresh', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: currentRefreshToken }),
      });

      if (!res.ok) {
        return null;
      }

      const data = await res.json();
      const newAccessToken = data.access_token;
      const newRefreshToken = data.refresh_token;

      if (newAccessToken) {
        localStorage.setItem(TOKEN_KEY, newAccessToken);
        if (newRefreshToken) {
          localStorage.setItem(REFRESH_TOKEN_KEY, newRefreshToken);
        }
        setToken(newAccessToken);
        if (newRefreshToken) {
          setRefreshTokenValue(newRefreshToken);
        }
        return newAccessToken;
      }

      return null;
    } catch (error) {
      console.error('Token refresh failed:', error);
      return null;
    }
  }, []);

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