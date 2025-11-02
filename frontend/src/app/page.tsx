"use client";

import { TonConnectButton, useTonAddress } from "@tonconnect/ui-react";
import { useEffect, useState } from "react";
import PoolStats from "@/components/PoolStats";
import UserBalance from "@/components/UserBalance";
import StakeForm from "@/components/StakeForm";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Home() {
  const userAddress = useTonAddress();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return null; // Avoid hydration mismatch
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              💎 TON Staking Pool
            </h1>
            <p className="text-sm text-gray-500">
              Децентралізований immutable пул
            </p>
          </div>
          <TonConnectButton />
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Pool Statistics */}
        <div className="mb-8">
          <PoolStats apiUrl={API_URL} />
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
              <TonConnectButton />
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
              GitHub →
            </a>
          </div>
        </div>
      </footer>
    </main>
  );
}
