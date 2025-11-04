"use client";

import { useState, useEffect, useCallback } from "react";

interface WithdrawalLock {
  is_locked: boolean;
  seconds_remaining: number;
  available_at: string | null;
  is_available: boolean;
}

interface LockedTransaction {
  tx_hash: string;
  type: "stake" | "unstake";
  amount: number;
  status: string;
  withdrawal: WithdrawalLock;
  lock_duration: number;
  created_at: string;
}

interface WithdrawalTimerProps {
  apiUrl: string;
  token: string | null;
}

export default function WithdrawalTimer({
  apiUrl,
  token,
}: WithdrawalTimerProps) {
  const [lockedTransactions, setLockedTransactions] = useState<
    LockedTransaction[]
  >([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [timers, setTimers] = useState<Map<string, number>>(new Map());

  const fetchLockedTransactions = useCallback(async () => {
    if (!token) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${apiUrl}/api/withdrawal/locked-transactions`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || "Failed to fetch locked transactions");
      }

      const data = await response.json();
      setLockedTransactions(data.locked_transactions || []);

      // Initialize timers
      const newTimers = new Map<string, number>();
      for (const tx of data.locked_transactions || []) {
        if (tx.withdrawal.is_locked) {
          newTimers.set(tx.tx_hash, tx.withdrawal.seconds_remaining);
        }
      }
      setTimers(newTimers);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }, [token, apiUrl]);

  useEffect(() => {
    fetchLockedTransactions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  // Update timers every second
  useEffect(() => {
    if (timers.size === 0) return;

    const interval = setInterval(() => {
      setTimers((prevTimers) => {
        const newTimers = new Map(prevTimers);
        let hasActive = false;

        for (const [hash, seconds] of newTimers) {
          if (seconds > 0) {
            newTimers.set(hash, seconds - 1);
            hasActive = true;
          }
        }

        // If no more active timers, refresh the list
        if (!hasActive) {
          fetchLockedTransactions();
        }

        return newTimers;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [timers, fetchLockedTransactions]);

  const formatTime = (seconds: number): string => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (days > 0) {
      return `${days}д ${hours}ч ${minutes}м`;
    }
    if (hours > 0) {
      return `${hours}ч ${minutes}м ${secs}с`;
    }
    if (minutes > 0) {
      return `${minutes}м ${secs}с`;
    }
    return `${secs}с`;
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString("uk-UA", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getProgressPercentage = (tx: LockedTransaction): number => {
    if (!tx.withdrawal.is_locked || tx.lock_duration === 0) return 100;
    const elapsed = tx.lock_duration - tx.withdrawal.seconds_remaining;
    return Math.max(0, Math.min(100, (elapsed / tx.lock_duration) * 100));
  };

  const getTonScanUrl = (txHash: string) => {
    return `https://tonscan.org/tx/${txHash}`;
  };

  if (loading && lockedTransactions.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Loading locked transactions...</span>
        </div>
      </div>
    );
  }

  if (!lockedTransactions || lockedTransactions.length === 0) {
    return (
      <div className="bg-gradient-to-r from-green-50 to-emerald-50 border-l-4 border-green-500 rounded-lg shadow p-4">
        <div className="flex items-center">
          <span className="text-2xl mr-3">✅</span>
          <div>
            <h3 className="font-semibold text-green-900">No Locked Transactions</h3>
            <p className="text-green-700 text-sm">
              All your transactions are available for withdrawal
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold text-gray-900">⏱️ Withdrawal Locks</h2>

      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 rounded-lg shadow p-4">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {lockedTransactions.map((tx) => {
          const timer = timers.get(tx.tx_hash) ?? tx.withdrawal.seconds_remaining;
          const isAvailable = timer <= 0;
          const progress = getProgressPercentage(tx);

          return (
            <div
              key={tx.tx_hash}
              className={`rounded-lg shadow-md p-4 border-l-4 transition-all ${
                isAvailable
                  ? "bg-green-50 border-green-500"
                  : "bg-orange-50 border-orange-500"
              }`}
            >
              {/* Header */}
              <div className="flex justify-between items-start mb-3">
                <div>
                  <span className="text-sm font-semibold text-gray-600">
                    {tx.type === "stake" ? "📥 Staked" : "📤 Unstaked"}
                  </span>
                  <p className="text-2xl font-bold text-gray-900 mt-1">
                    {tx.amount.toFixed(2)} TON
                  </p>
                </div>
                <span
                  className={`px-3 py-1 rounded-full text-xs font-semibold ${
                    isAvailable
                      ? "bg-green-100 text-green-800"
                      : "bg-orange-100 text-orange-800"
                  }`}
                >
                  {isAvailable ? "✅ Ready" : "🔒 Locked"}
                </span>
              </div>

              {/* Timer */}
              <div className="mb-4">
                {!isAvailable && (
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium text-gray-700">
                        Available in:
                      </span>
                      <span className="text-lg font-bold text-orange-600">
                        {formatTime(timer)}
                      </span>
                    </div>
                    {/* Progress bar */}
                    <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                      <div
                        className="bg-gradient-to-r from-orange-400 to-orange-600 h-full transition-all duration-1000 ease-linear"
                        style={{ width: `${progress}%` }}
                      ></div>
                    </div>
                  </div>
                )}
                {isAvailable && (
                  <div className="flex items-center text-green-700">
                    <span className="text-xl mr-2">✅</span>
                    <span className="font-semibold">Ready for withdrawal</span>
                  </div>
                )}
              </div>

              {/* Available at */}
              {tx.withdrawal.available_at && (
                <p className="text-xs text-gray-500 mb-3">
                  Available: {formatDate(tx.withdrawal.available_at)}
                </p>
              )}

              {/* Transaction hash link */}
              <a
                href={getTonScanUrl(tx.tx_hash)}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center text-xs text-blue-600 hover:text-blue-800 break-all"
              >
                <span className="mr-1">🔗</span>
                {tx.tx_hash.slice(0, 12)}...{tx.tx_hash.slice(-8)}
              </a>
            </div>
          );
        })}
      </div>
    </div>
  );
}
