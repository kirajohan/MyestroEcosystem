'use client';

import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
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
  error: string | null;
  user: AuthUser | null;
  token: string | null;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

const TOKEN_KEY = 'myestro_admin_token';
const USER_KEY = 'myestro_admin_user';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<AuthUser | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  // Check localStorage on mount
  useEffect(() => {
    try {
      const storedToken = localStorage.getItem(TOKEN_KEY);
      const storedUser = localStorage.getItem(USER_KEY);
      if (storedToken && storedUser) {
        setToken(storedToken);
        setUser(JSON.parse(storedUser));
        setIsLoggedIn(true);
      }
    } catch {
      // Ignore parse errors
    } finally {
      setIsLoading(false);
    }
  }, []);

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
      localStorage.setItem(USER_KEY, JSON.stringify(adminUser));

      setToken(adminToken);
      setUser(adminUser);
      setIsLoggedIn(true);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Login xatosi');
      throw err;
    }
  };

  const logout = () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    setToken(null);
    setUser(null);
    setIsLoggedIn(false);
    router.push('/login');
  };

  const value: AuthContextType = {
    isLoggedIn,
    isLoading,
    login,
    logout,
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