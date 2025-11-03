// frontend/src/app/page.tsx
'use client';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';

export default function LandingPage() {
  const { isAuthenticated, loading } = useAuth();
  
  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6">
      <h1 className="text-3xl font-bold mb-4">TON Pool</h1>
      <p className="mb-6 text-gray-600">Immutable pool based on official TON contracts. Analytics by subscription.</p>
      <div className="flex gap-4">
        {loading ? (
          <div className="px-4 py-2">Loading...</div>
        ) : isAuthenticated ? (
          <Link className="px-4 py-2 rounded bg-blue-600 text-white" href="/dashboard">Dashboard</Link>
        ) : (
          <>
            <Link className="px-4 py-2 rounded border" href="/login">Sign In</Link>
            <Link className="px-4 py-2 rounded border" href="/register">Register</Link>
          </>
        )}
      </div>
    </div>
  );
}
