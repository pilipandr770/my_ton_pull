// frontend/src/contexts/AuthContext.tsx
'use client';

import React, { createContext, useContext, useState } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || '';

interface User {
  id: number;
  email?: string;
  role: string;
  subscription_status: string;
  subscription_expires_at?: string | null;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isAdmin: boolean;
  hasActiveSubscription: boolean;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Initialize user from localStorage if available
function initializeUser(): User | null {
  if (typeof window === 'undefined') return null;
  const saved = localStorage.getItem('auth_user');
  if (saved) {
    try {
      return JSON.parse(saved);
    } catch (e) {
      console.error('Failed to parse saved user:', e);
      localStorage.removeItem('auth_user');
    }
  }
  return null;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(() => initializeUser());
  // Since we initialize in useState callback, loading is always false after render
  const loading = false;

  function saveAuth(u: User, access: string, refresh: string) {
    setUser(u);
    localStorage.setItem('auth_user', JSON.stringify(u));
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
  }

  async function register(email: string, password: string) {
    const r = await fetch(`${API_URL}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    if (!r.ok) throw new Error('Registration failed');
    const data = await r.json();
    saveAuth(data.user, data.access_token, data.refresh_token);
  }

  async function login(email: string, password: string) {
    const r = await fetch(`${API_URL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    if (!r.ok) throw new Error('Login failed');
    const data = await r.json();
    saveAuth(data.user, data.access_token, data.refresh_token);
  }

  function logout() {
    setUser(null);
    localStorage.removeItem('auth_user');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isAdmin: user?.role === 'admin',
    hasActiveSubscription: user?.subscription_status === 'active',
    loading,
    login, register, logout
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
