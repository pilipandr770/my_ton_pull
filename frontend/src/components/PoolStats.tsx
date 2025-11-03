"use client";

import { useEffect, useState } from "react";

interface PoolStatsData {
  total_staked: number;
  total_staked_usd: number;
  participants_count: number;
  apy: number;
  min_stake: number;
  status: string;
  testnet: boolean;
}

interface PoolStatsProps {
  apiUrl: string;
}

export default function PoolStats({ apiUrl }: PoolStatsProps) {
  const [stats, setStats] = useState<PoolStatsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchStats();
    // Оновлюємо кожні 30 секунд
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch(`${apiUrl}/api/pool/stats`);
      if (!response.ok) throw new Error("Failed to fetch pool stats");
      const data = await response.json();
      
      // Ensure all required fields exist with defaults
      const validatedData: PoolStatsData = {
        total_staked: data.total_staked ?? 0,
        total_staked_usd: data.total_staked_usd ?? 0,
        participants_count: data.participants_count ?? 0,
        apy: data.apy ?? 0,
        min_stake: data.min_stake ?? 0,
        status: data.status ?? 'active',
        testnet: data.testnet ?? false,
      };
      
      setStats(validatedData);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-6"></div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map((i) => (
              <div key={i}>
                <div className="h-4 bg-gray-200 rounded w-2/3 mb-2"></div>
                <div className="h-8 bg-gray-200 rounded w-full"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error || !stats) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-6">
        <p className="text-red-800">❌ Помилка завантаження: {error}</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-8">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">📊 Статистика пулу</h2>
        {stats.testnet && (
          <span className="bg-yellow-100 text-yellow-800 text-xs font-semibold px-3 py-1 rounded-full">
            TESTNET
          </span>
        )}
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        {/* Total Staked */}
        <div>
          <p className="text-sm text-gray-500 mb-1">Всього застейкано</p>
          <p className="text-2xl font-bold text-gray-900">
            {(stats.total_staked ?? 0).toLocaleString()} TON
          </p>
          <p className="text-sm text-gray-400">
            ${(stats.total_staked_usd ?? 0).toLocaleString()}
          </p>
        </div>

        {/* APY */}
        <div>
          <p className="text-sm text-gray-500 mb-1">APY</p>
          <p className="text-2xl font-bold text-green-600">{stats.apy}%</p>
          <p className="text-sm text-gray-400">Річна прибутковість</p>
        </div>

        {/* Participants */}
        <div>
          <p className="text-sm text-gray-500 mb-1">Учасників</p>
          <p className="text-2xl font-bold text-gray-900">
            {stats.participants_count}
          </p>
          <p className="text-sm text-gray-400">Активних стейкерів</p>
        </div>

        {/* Min Stake */}
        <div>
          <p className="text-sm text-gray-500 mb-1">Мін. ставка</p>
          <p className="text-2xl font-bold text-gray-900">
            {stats.min_stake} TON
          </p>
          <p className="text-sm text-gray-400">Мінімальна сума</p>
        </div>
      </div>

      {/* Status Indicator */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Статус пулу:</span>
          <span
            className={`flex items-center text-sm font-semibold ${
              stats.status === "active"
                ? "text-green-600"
                : "text-yellow-600"
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-current mr-2 animate-pulse"></span>
            {stats.status === "active" ? "Активний" : "Очікування"}
          </span>
        </div>
      </div>
    </div>
  );
}
