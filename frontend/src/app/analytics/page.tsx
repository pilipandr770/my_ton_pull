"use client";

import { useAuth } from "@/contexts/AuthContext";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import Link from "next/link";
import {
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "";

interface TrendData {
  date: string;
  stakes: {
    count: number;
    volume: number;
  };
  unstakes: {
    count: number;
  };
}

interface AnalyticsData {
  stakingTrends?: TrendData[];
  userActivity?: any;
  distribution?: any;
}

export default function AnalyticsPage() {
  const { isAuthenticated, loading } = useAuth();
  const router = useRouter();
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData>({});
  const [analyticsLoading, setAnalyticsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Redirect if not authenticated
  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, loading, router]);

  // Fetch analytics data
  useEffect(() => {
    if (!isAuthenticated) return;

    const fetchAnalytics = async () => {
      setAnalyticsLoading(true);
      setError(null);

      try {
        const token = localStorage.getItem("token");
        const headers = {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        };

        // Fetch staking trends
        const trendsResponse = await fetch(`${API_URL}/api/analytics/staking-trends`, {
          method: "GET",
          headers,
        });

        if (!trendsResponse.ok) throw new Error("Failed to fetch trends");
        const trendsData = await trendsResponse.json();

        // Fetch user activity
        const activityResponse = await fetch(`${API_URL}/api/analytics/user-activity`, {
          method: "GET",
          headers,
        });

        if (!activityResponse.ok) throw new Error("Failed to fetch activity");
        const activityData = await activityResponse.json();

        // Fetch distribution
        const distributionResponse = await fetch(`${API_URL}/api/analytics/distribution`, {
          method: "GET",
          headers,
        });

        if (!distributionResponse.ok) throw new Error("Failed to fetch distribution");
        const distributionData = await distributionResponse.json();

        setAnalyticsData({
          stakingTrends: trendsData.trends,
          userActivity: activityData,
          distribution: distributionData,
        });
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setAnalyticsLoading(false);
      }
    };

    fetchAnalytics();
  }, [isAuthenticated]);

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
    return null;
  }

  const pieData = analyticsData.distribution
    ? [
        {
          name: "Stakes",
          value: analyticsData.distribution.transaction_types?.stakes?.count || 0,
        },
        {
          name: "Unstakes",
          value: analyticsData.distribution.transaction_types?.unstakes?.count || 0,
        },
      ]
    : [];

  const statusData = analyticsData.distribution
    ? [
        {
          name: "Pending",
          value: analyticsData.distribution.status_distribution?.pending?.count || 0,
        },
        {
          name: "Confirmed",
          value: analyticsData.distribution.status_distribution?.confirmed?.count || 0,
        },
        {
          name: "Failed",
          value: analyticsData.distribution.status_distribution?.failed?.count || 0,
        },
      ]
    : [];

  const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"];

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div>
            <Link href="/dashboard" className="flex items-center space-x-2">
              <h1 className="text-2xl font-bold text-gray-900">📊 Analytics</h1>
            </Link>
            <p className="text-sm text-gray-500">Система статистики та аналізи</p>
          </div>
          <div className="flex items-center space-x-4">
            <Link
              href="/dashboard"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium"
            >
              ← Назад до дашборду
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800">❌ {error}</p>
          </div>
        )}

        {analyticsLoading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Завантаження аналітики...</p>
          </div>
        ) : (
          <>
            {/* Staking Trends Chart */}
            <div className="mb-8 bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">📈 Стейкінг тренди (30 днів)</h2>
              {analyticsData.stakingTrends && analyticsData.stakingTrends.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={analyticsData.stakingTrends}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="date"
                      stroke="#9ca3af"
                      style={{ fontSize: "12px" }}
                    />
                    <YAxis stroke="#9ca3af" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#f9fafb",
                        border: "1px solid #e5e7eb",
                        borderRadius: "8px",
                      }}
                    />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="stakes.count"
                      stroke="#3b82f6"
                      name="Stake Транзакції"
                      dot={false}
                      strokeWidth={2}
                    />
                    <Line
                      type="monotone"
                      dataKey="unstakes.count"
                      stroke="#f59e0b"
                      name="Unstake Транзакції"
                      dot={false}
                      strokeWidth={2}
                    />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <p className="text-gray-600">Немає даних</p>
              )}
            </div>

            {/* Distribution Charts Row */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
              {/* Transaction Types Pie Chart */}
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">
                  💎 Розподіл за типами
                </h2>
                {pieData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={pieData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, value }: any) =>
                          `${name}: ${value}`
                        }
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {pieData.map((entry, index) => (
                          <Cell
                            key={`cell-${index}`}
                            fill={COLORS[index % COLORS.length]}
                          />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <p className="text-gray-600">Немає даних</p>
                )}
              </div>

              {/* Status Distribution Pie Chart */}
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">
                  ✅ Розподіл за статусом
                </h2>
                {statusData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={statusData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, value }) =>
                          `${name}: ${value}`
                        }
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {statusData.map((entry, index) => (
                          <Cell
                            key={`cell-${index}`}
                            fill={COLORS[index % COLORS.length]}
                          />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <p className="text-gray-600">Немає даних</p>
                )}
              </div>
            </div>

            {/* Statistics Cards */}
            {analyticsData.distribution && (
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-500">
                  <p className="text-sm text-gray-600">Всього Stake</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {analyticsData.distribution.transaction_types?.stakes?.count || 0}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {analyticsData.distribution.transaction_types?.stakes?.volume.toFixed(2) ||
                      0}{" "}
                    TON
                  </p>
                </div>

                <div className="bg-white rounded-lg shadow p-4 border-l-4 border-orange-500">
                  <p className="text-sm text-gray-600">Всього Unstake</p>
                  <p className="text-2xl font-bold text-orange-600">
                    {analyticsData.distribution.transaction_types?.unstakes?.count || 0}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {analyticsData.distribution.transaction_types?.unstakes?.volume.toFixed(2) ||
                      0}{" "}
                    TON
                  </p>
                </div>

                <div className="bg-white rounded-lg shadow p-4 border-l-4 border-green-500">
                  <p className="text-sm text-gray-600">Підтверджено</p>
                  <p className="text-2xl font-bold text-green-600">
                    {analyticsData.distribution.status_distribution?.confirmed?.count || 0}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {analyticsData.distribution.status_distribution?.confirmed?.percentage.toFixed(
                      1
                    ) || 0}
                    %
                  </p>
                </div>

                <div className="bg-white rounded-lg shadow p-4 border-l-4 border-gray-500">
                  <p className="text-sm text-gray-600">В очікуванні</p>
                  <p className="text-2xl font-bold text-gray-600">
                    {analyticsData.distribution.status_distribution?.pending?.count || 0}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {analyticsData.distribution.status_distribution?.pending?.percentage.toFixed(1) ||
                      0}
                    %
                  </p>
                </div>
              </div>
            )}

            {/* User Activity */}
            {analyticsData.userActivity && (
              <div className="mt-8 bg-white rounded-lg shadow-lg p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">
                  👥 Активність користувачів
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  <div className="bg-blue-50 rounded-lg p-4 border-l-4 border-blue-500">
                    <p className="text-sm text-gray-600">Активні користувачі (30 днів)</p>
                    <p className="text-3xl font-bold text-blue-600">
                      {analyticsData.userActivity.active_users_last_30_days || 0}
                    </p>
                  </div>
                  <div className="bg-green-50 rounded-lg p-4 border-l-4 border-green-500">
                    <p className="text-sm text-gray-600">Топ користувачів</p>
                    <p className="text-3xl font-bold text-green-600">
                      {analyticsData.userActivity.top_users?.length || 0}
                    </p>
                  </div>
                </div>

                {analyticsData.userActivity.top_users &&
                  analyticsData.userActivity.top_users.length > 0 && (
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-4 py-2 text-left text-gray-700 font-semibold">
                              Email
                            </th>
                            <th className="px-4 py-2 text-right text-gray-700 font-semibold">
                              Транзакції
                            </th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                          {analyticsData.userActivity.top_users.map(
                            (user: any, index: number) => (
                              <tr key={index} className="hover:bg-gray-50">
                                <td className="px-4 py-2 text-gray-900 font-mono text-xs">
                                  {user.email}
                                </td>
                                <td className="px-4 py-2 text-right text-gray-600 font-semibold">
                                  {user.transaction_count}
                                </td>
                              </tr>
                            )
                          )}
                        </tbody>
                      </table>
                    </div>
                  )}
              </div>
            )}
          </>
        )}
      </div>

      {/* Footer */}
      <footer className="bg-white border-t mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-sm text-gray-500">📊 TON Staking Pool Analytics</p>
        </div>
      </footer>
    </main>
  );
}
