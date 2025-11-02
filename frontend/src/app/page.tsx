'use client';
import { useAuth } from '@/contexts/AuthContext';
import Link from 'next/link';

export default function LandingPage() {
  const { isAuthenticated } = useAuth();
  
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      <header className="container mx-auto px-4 py-6 flex justify-between items-center">
        <div className="text-2xl font-bold text-blue-600">TON Pool</div>
        <nav className="flex gap-4">
          {isAuthenticated ? (
            <Link href="/dashboard" className="bg-blue-600 text-white px-6 py-2 rounded-lg">Dashboard</Link>
          ) : (
            <>
              <Link href="/login">Sign In</Link>
              <Link href="/register" className="bg-blue-600 text-white px-6 py-2 rounded-lg">Get Started</Link>
            </>
          )}
        </nav>
      </header>
      
      <section className="container mx-auto px-4 py-20 text-center">
        <h1 className="text-6xl font-bold mb-6">Stake TON, Earn Rewards</h1>
        <p className="text-xl text-gray-600 mb-8">Start from 1 TON. Earn up to 9.7% APY.</p>
        <Link href="/register" className="bg-blue-600 text-white px-8 py-4 rounded-lg text-lg">
          Start Staking
        </Link>
      </section>
    </div>
  );
}
