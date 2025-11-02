"use client";

import { useEffect, useState } from "react";

interface UserBalanceData {
  user_address: string;
  wallet_balance: number;
  staked_amount: number;
  accumulated_rewards: number;
  jettons_balance: number;
  share_percentage: number;
}

interface UserBalanceProps {
  apiUrl: string;
  userAddress: string;
}

export default function UserBalance({ apiUrl, userAddress }: UserBalanceProps) {
  const [balance, setBalance] = useState<UserBalanceData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (userAddress) {
      fetchBalance();
      // Оновлюємо кожні 10 секунд
      const interval = setInterval(fetchBalance, 10000);
      return () => clearInterval(interval);
    }
  }, [userAddress]);

  const fetchBalance = async () => {
    try {
      const response = await fetch(`${apiUrl}/api/user/${userAddress}/balance`);
      if (!response.ok) throw new Error("Failed to fetch balance");
      const data = await response.json();
      setBalance(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/2 mb-4"></div>
          <div className="space-y-3">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-12 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error || !balance) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-6">
        <p className="text-red-800">❌ Помилка завантаження балансу</p>
      </div>
    );
  }

  const totalValue = balance.wallet_balance + balance.staked_amount + balance.accumulated_rewards;

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h3 className="text-xl font-bold text-gray-900 mb-4">💰 Ваш баланс</h3>

      <div className="space-y-4">
        {/* Wallet Balance */}
        <div className="flex justify-between items-center p-4 bg-blue-50 rounded-lg">
          <div>
            <p className="text-sm text-gray-600">Баланс гаманця</p>
            <p className="text-2xl font-bold text-gray-900">
              {balance.wallet_balance.toLocaleString()} TON
            </p>
          </div>
          <div className="text-4xl">💳</div>
        </div>

        {/* Staked Amount */}
        <div className="flex justify-between items-center p-4 bg-green-50 rounded-lg">
          <div>
            <p className="text-sm text-gray-600">Застейкано</p>
            <p className="text-2xl font-bold text-green-700">
              {balance.staked_amount.toLocaleString()} TON
            </p>
          </div>
          <div className="text-4xl">🔒</div>
        </div>

        {/* Rewards */}
        <div className="flex justify-between items-center p-4 bg-yellow-50 rounded-lg">
          <div>
            <p className="text-sm text-gray-600">Накопичені винагороди</p>
            <p className="text-2xl font-bold text-yellow-700">
              {balance.accumulated_rewards.toLocaleString()} TON
            </p>
          </div>
          <div className="text-4xl">⭐</div>
        </div>

        {/* Share Percentage */}
        {balance.share_percentage > 0 && (
          <div className="flex justify-between items-center p-4 bg-purple-50 rounded-lg">
            <div>
              <p className="text-sm text-gray-600">Ваша частка в пулі</p>
              <p className="text-2xl font-bold text-purple-700">
                {balance.share_percentage.toFixed(2)}%
              </p>
            </div>
            <div className="text-4xl">📊</div>
          </div>
        )}

        {/* Total Value */}
        <div className="pt-4 border-t border-gray-200">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Загальна вартість:</span>
            <span className="text-xl font-bold text-gray-900">
              {totalValue.toLocaleString()} TON
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
