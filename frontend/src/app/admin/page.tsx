"use client";

import { useAuth } from "@/contexts/AuthContext";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import Link from "next/link";
import AdminStatsCard from "@/components/AdminStatsCard";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "";

interface AdminStats {
  users: {
    total: number;
    active_subscriptions: number;
    inactive: number;
  };
  transactions: {
    total: number;
    pending: number;
    confirmed: number;
    failed: number;
  };
  transaction_types: {
    stakes: number;
    unstakes: number;
  };
  volume: {
    total_staked_ton: number;
    total_unstaked_ton: number;
  };
  withdrawal_locks: {
    locked_count: number;
    unlocked_available: number;
  };
  pool: {
    total_pool_ton: number;
    total_jettons: number;
    apy: number;
    updated_at: string;
  };
  recent_transactions: Array<{
    id: number;
    user_id: number;
    type: string;
    amount: number;
    status: string;
    tx_hash: string;
    created_at: string;
    is_locked: boolean;
  }>;
  timestamp: string;
}

interface User {
  id: number;
  email: string;
  role: string;
  subscription_status: string;
  transaction_count: number;
  created_at: string;
}

export default function AdminPage() {
  const { isAuthenticated, loading, user, logout } = useAuth();
  const router = useRouter();
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [statsLoading, setStatsLoading] = useState(false);
  const [users, setUsers] = useState<User[]>([]);
  const [usersLoading, setUsersLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Redirect if not admin
  useEffect(() => {
    if (!loading && (!isAuthenticated || user?.role !== "admin")) {
      router.push("/dashboard");
    }
  }, [isAuthenticated, loading, user, router]);

  // Fetch admin stats
  useEffect(() => {
    if (!isAuthenticated || user?.role !== "admin") return;

    const fetchStats = async () => {
      setStatsLoading(true);
      setError(null);

      try {
        const token = localStorage.getItem("token");
        const response = await fetch(`${API_URL}/api/admin/stats`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          const data = await response.json();
          throw new Error(data.error || "Failed to fetch stats");
        }

        const data = await response.json();
        setStats(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setStatsLoading(false);
      }
    };

    fetchStats();
  }, [isAuthenticated, user?.role]);

  // Fetch users
  useEffect(() => {
    if (!isAuthenticated || user?.role !== "admin") return;

    const fetchUsers = async () => {
      setUsersLoading(true);

      try {
        const token = localStorage.getItem("token");
        const response = await fetch(`${API_URL}/api/admin/users?page=1&limit=10`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          const data = await response.json();
          throw new Error(data.error || "Failed to fetch users");
        }

        const data = await response.json();
        setUsers(data.users || []);
      } catch (err) {
        console.error("Error fetching users:", err);
      } finally {
        setUsersLoading(false);
      }
    };

    fetchUsers();
  }, [isAuthenticated, user?.role]);

  const handleLogout = () => {
    logout();
    router.push("/");
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Завантаження...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated || user?.role !== "admin") {
    return null;
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div>
            <Link href="/dashboard" className="flex items-center space-x-2">
              <h1 className="text-2xl font-bold text-gray-900">
                ⚙️ Admin Dashboard
              </h1>
            </Link>
            <p className="text-sm text-gray-500">Системна статистика та управління</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <p className="text-sm text-gray-600">{user?.email}</p>
              <p className="text-xs text-purple-600 font-semibold">👑 Адміністратор</p>
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
            <Link
              href="/dashboard"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
            >
              📊 До дашборду
            </Link>
            <Link
              href="/history"
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium"
            >
              📜 Історія транзакцій
            </Link>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800">❌ {error}</p>
          </div>
        )}

        {/* Statistics Cards */}
        {statsLoading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Завантаження статистики...</p>
          </div>
        ) : stats ? (
          <>
            {/* Users Section */}
            <div className="mb-8">
              <h2 className="text-xl font-bold text-gray-900 mb-4">👥 Користувачі</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <AdminStatsCard
                  icon="👤"
                  label="Всього користувачів"
                  value={stats.users.total}
                  subtext={`${stats.users.active_subscriptions} з активною підпискою`}
                  color="blue"
                />
                <AdminStatsCard
                  icon="✅"
                  label="Активні підписки"
                  value={stats.users.active_subscriptions}
                  color="green"
                />
                <AdminStatsCard
                  icon="⏸️"
                  label="Неактивні"
                  value={stats.users.inactive}
                  color="orange"
                />
              </div>
            </div>

            {/* Transactions Section */}
            <div className="mb-8">
              <h2 className="text-xl font-bold text-gray-900 mb-4">
                📜 Транзакції
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <AdminStatsCard
                  icon="📊"
                  label="Всього транзакцій"
                  value={stats.transactions.total}
                  color="blue"
                />
                <AdminStatsCard
                  icon="⏳"
                  label="В очікуванні"
                  value={stats.transactions.pending}
                  color="orange"
                />
                <AdminStatsCard
                  icon="✅"
                  label="Підтверджено"
                  value={stats.transactions.confirmed}
                  color="green"
                />
                <AdminStatsCard
                  icon="❌"
                  label="Помилки"
                  value={stats.transactions.failed}
                  color="red"
                />
              </div>
            </div>

            {/* Transaction Types and Volume */}
            <div className="mb-8">
              <h2 className="text-xl font-bold text-gray-900 mb-4">
                💰 Обсяги операцій
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <AdminStatsCard
                  icon="📥"
                  label="Операції Stake"
                  value={stats.transaction_types.stakes}
                  color="green"
                />
                <AdminStatsCard
                  icon="📤"
                  label="Операції Unstake"
                  value={stats.transaction_types.unstakes}
                  color="orange"
                />
                <AdminStatsCard
                  icon="💎"
                  label="Обсяг stake (TON)"
                  value={stats.volume.total_staked_ton.toFixed(2)}
                  color="blue"
                />
                <AdminStatsCard
                  icon="💸"
                  label="Обсяг unstake (TON)"
                  value={stats.volume.total_unstaked_ton.toFixed(2)}
                  color="red"
                />
              </div>
            </div>

            {/* Withdrawal Locks */}
            <div className="mb-8">
              <h2 className="text-xl font-bold text-gray-900 mb-4">
                🔒 Блокування виводу
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <AdminStatsCard
                  icon="🔒"
                  label="Заблокованих транзакцій"
                  value={stats.withdrawal_locks.locked_count}
                  color="orange"
                />
                <AdminStatsCard
                  icon="🔓"
                  label="Доступних для виводу"
                  value={stats.withdrawal_locks.unlocked_available}
                  color="green"
                />
              </div>
            </div>

            {/* Pool Statistics */}
            <div className="mb-8">
              <h2 className="text-xl font-bold text-gray-900 mb-4">
                🏊 Статистика пулу
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <AdminStatsCard
                  icon="💰"
                  label="Всього в пулу (TON)"
                  value={stats.pool.total_pool_ton.toFixed(2)}
                  color="blue"
                />
                <AdminStatsCard
                  icon="🪙"
                  label="Jettons видано"
                  value={stats.pool.total_jettons.toFixed(2)}
                  color="green"
                />
                <AdminStatsCard
                  icon="📈"
                  label="APY (%)"
                  value={stats.pool.apy.toFixed(2)}
                  color="purple"
                />
              </div>
            </div>

            {/* Recent Transactions Table */}
            <div className="mb-8">
              <h2 className="text-xl font-bold text-gray-900 mb-4">
                🔄 Останні транзакції
              </h2>
              {stats.recent_transactions.length > 0 ? (
                <div className="bg-white rounded-lg shadow overflow-hidden">
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-gray-50 border-b border-gray-200">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase">
                            ID
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase">
                            Тип
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase">
                            Статус
                          </th>
                          <th className="px-6 py-3 text-right text-xs font-semibold text-gray-700 uppercase">
                            Сума (TON)
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase">
                            TX Hash
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase">
                            Час
                          </th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {stats.recent_transactions.map((tx) => (
                          <tr key={tx.id} className="hover:bg-gray-50">
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-mono">
                              {tx.id}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold">
                              {tx.type === "stake" ? "📥 Stake" : "📤 Unstake"}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span
                                className={`px-3 py-1 rounded-full text-xs font-semibold ${
                                  tx.status === "pending"
                                    ? "bg-yellow-100 text-yellow-800"
                                    : tx.status === "confirmed"
                                    ? "bg-green-100 text-green-800"
                                    : "bg-red-100 text-red-800"
                                }`}
                              >
                                {tx.status === "pending"
                                  ? "⏳ Pending"
                                  : tx.status === "confirmed"
                                  ? "✅ Confirmed"
                                  : "❌ Failed"}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-semibold">
                              {tx.amount > 0 ? `${tx.amount} TON` : "—"}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-blue-600">
                              {tx.tx_hash}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-xs text-gray-500">
                              {new Date(tx.created_at).toLocaleDateString("uk-UA")}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ) : (
                <div className="bg-white rounded-lg shadow p-6 text-center">
                  <p className="text-gray-600">Нема транзакцій</p>
                </div>
              )}
            </div>
          </>
        ) : null}
      </div>

      {/* Footer */}
      <footer className="bg-white border-t mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-sm text-gray-500">
            ⚙️ Адмін-панель TON Staking Pool
          </p>
        </div>
      </footer>
    </main>
  );
}
