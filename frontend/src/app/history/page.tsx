"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import TransactionList from "@/components/TransactionList";

export default function HistoryPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [apiUrl, setApiUrl] = useState<string>("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check authentication on component mount
    const checkAuth = () => {
      const storedToken = localStorage.getItem("token");
      const storedApiUrl = localStorage.getItem("apiUrl") || process.env.NEXT_PUBLIC_API_URL || "https://my-ton-pull.onrender.com";

      if (!storedToken) {
        router.push("/login");
        return;
      }

      setToken(storedToken);
      setApiUrl(storedApiUrl);
      setIsLoading(false);
    };

    checkAuth();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">⏳ Loading...</p>
        </div>
      </div>
    );
  }

  if (!token) {
    return null; // Router will redirect
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-4xl font-bold text-gray-900">
                📜 Transaction History
              </h1>
              <p className="text-gray-600 mt-2">
                View all your staking transactions and their status
              </p>
            </div>
            <button
              onClick={() => router.push("/dashboard")}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold"
            >
              ← Back to Dashboard
            </button>
          </div>
        </div>

        {/* Transaction List */}
        <TransactionList apiUrl={apiUrl} token={token} />

        {/* Info Section */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              📥 Stake
            </h3>
            <p className="text-gray-600 text-sm">
              Deposit TON into the staking pool. Your coins will be locked and
              earn rewards.
            </p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              📤 Unstake
            </h3>
            <p className="text-gray-600 text-sm">
              Request withdrawal from the pool. Coins will be sent after the
              current epoch ends (up to 36h).
            </p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              ✅ Status
            </h3>
            <p className="text-gray-600 text-sm">
              <span className="inline-block mr-2">⏳ Pending:</span> Waiting for
              blockchain confirmation
              <br />
              <span className="inline-block mr-2">✅ Confirmed:</span> Successfully
              recorded on blockchain
            </p>
          </div>
        </div>

        {/* TonScan Info */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">
            🔍 About Transaction Hashes
          </h3>
          <p className="text-blue-800 text-sm">
            Each transaction has a unique hash (transaction ID) that you can
            view on{" "}
            <a
              href="https://tonscan.org"
              target="_blank"
              rel="noopener noreferrer"
              className="underline hover:no-underline font-semibold"
            >
              TonScan
            </a>
            . Click on any transaction hash above to see the full details on the
            blockchain explorer. This proves your transaction was recorded on
            the TON blockchain.
          </p>
        </div>
      </div>
    </div>
  );
}
