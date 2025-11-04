"use client";

import { useTonAddress } from "@tonconnect/ui-react";
import { useAuth } from "@/contexts/AuthContext";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import PoolStats from "@/components/PoolStats";
import UserBalance from "@/components/UserBalance";
import StakeForm from "@/components/StakeForm";
import TonConnectButtonWrapper from "@/components/TonConnectButtonWrapper";
import WithdrawalTimer from "@/components/WithdrawalTimer";
import Link from "next/link";

// Use relative URLs for API calls (same server)
const API_URL = process.env.NEXT_PUBLIC_API_URL || "";

export default function Dashboard() {
  const userAddress = useTonAddress();
  const { isAuthenticated, loading, logout, user } = useAuth();
  const router = useRouter();

  // Redirect unauthenticated users to login
  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, loading, router]);

  // Log address changes for debugging
  useEffect(() => {
    console.log('📍 Dashboard - userAddress changed:', userAddress);
  }, [userAddress]);

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Завантаження...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null; // Will redirect via useEffect
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div>
            <Link href="/" className="flex items-center space-x-2">
              <h1 className="text-2xl font-bold text-gray-900">
                💎 TON Staking Pool
              </h1>
            </Link>
            <p className="text-sm text-gray-500">
              Ваш персональний кабінет
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <p className="text-sm text-gray-600">{user?.email}</p>
              <p className="text-xs text-gray-500">{user?.role === 'admin' ? '👑 Адмін' : '👤 Користувач'}</p>
            </div>
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm font-medium"
            >
              Вихід
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Quick Actions */}
        <div className="mb-8 bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Швидкі дії</h2>
          <div className="flex flex-wrap gap-3">
            <TonConnectButtonWrapper />
            <Link 
              href="/history" 
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
            >
              📜 История транзакций
            </Link>
            <Link 
              href="/analytics" 
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium"
            >
              📊 Аналітика
            </Link>
            {user?.role === 'admin' && (
              <Link 
                href="/admin" 
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-medium"
              >
                ⚙️ Админ-панель
              </Link>
            )}
          </div>
        </div>

        {/* Pool Statistics */}
        <div className="mb-8">
          <PoolStats apiUrl={API_URL} />
        </div>

        {/* Withdrawal Locks */}
        <div className="mb-8">
          <WithdrawalTimer apiUrl={API_URL} token={localStorage.getItem("token")} />
        </div>

        {/* User Section - показуємо тільки якщо гаманець підключено */}
        {userAddress && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* User Balance */}
            <UserBalance apiUrl={API_URL} userAddress={userAddress} />

            {/* Stake/Unstake Form */}
            <StakeForm apiUrl={API_URL} userAddress={userAddress} />
          </div>
        )}

        {/* Call to Action - якщо гаманець не підключено */}
        {!userAddress && (
          <div className="bg-white rounded-xl shadow-lg p-8 text-center">
            <div className="text-6xl mb-4">🔗</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Підключіть гаманець
            </h2>
            <p className="text-gray-600 mb-6">
              Для початку роботи з пулом підключіть TON гаманець
            </p>
            <div className="flex justify-center">
              <TonConnectButtonWrapper />
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="bg-white border-t mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <p className="text-sm text-gray-500">
              🔒 Immutable контракт - без адміністратора
            </p>
            <a
              href="https://github.com/pilipandr770/my_ton_pull"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              GitHub
            </a>
          </div>
        </div>
      </footer>
    </main>
  );
}
