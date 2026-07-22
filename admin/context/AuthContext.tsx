'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import api from '@/lib/api';

interface AdminUser {
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
  user: AdminUser | null;
  token: string | null;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [user, setUser] = useState<AdminUser | null>(null);
  const [token, setToken] = useState<string | null>(null);

  // Restore login state + token from localStorage
  useEffect(() => {
    const loggedInFlag = localStorage.getItem('isAdminLoggedIn');
    const savedUser = localStorage.getItem('admin_user');
    const savedToken = localStorage.getItem('admin_token');
    if (loggedInFlag === 'true' && savedUser) {
      try {
        setUser(JSON.parse(savedUser));
        setIsLoggedIn(true);
        if (savedToken) setToken(savedToken);
      } catch (e) {
        console.error('Failed to restore user:', e);
        localStorage.removeItem('isAdminLoggedIn');
        localStorage.removeItem('admin_user');
        localStorage.removeItem('admin_token');
      }
    }
  }, []);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await api.post('/auth/admin-login', { email, password });
      const data = response.data;

      if (data.success && data.user) {
        setIsLoggedIn(true);
        setUser(data.user);
        if (data.access_token) {
          setToken(data.access_token);
          localStorage.setItem('admin_token', data.access_token);
        }
        localStorage.setItem('isAdminLoggedIn', 'true');
        localStorage.setItem('admin_user', JSON.stringify(data.user));
      } else {
        setError('Login failed');
        throw new Error('Login failed');
      }
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Parol notogri yoki admin huquqi yoq';
      setError(msg);
      throw new Error(msg);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setIsLoggedIn(false);
    setUser(null);
    setToken(null);
    setError(null);
    localStorage.removeItem('isAdminLoggedIn');
    localStorage.removeItem('admin_user');
    localStorage.removeItem('admin_token');
  };

  return (
    <AuthContext.Provider value={{ isLoggedIn, isLoading, login, logout, error, user, token }}>
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