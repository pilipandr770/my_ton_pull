"use client";

import { useState } from "react";
import { useTonConnectUI } from "@tonconnect/ui-react";

interface StakeFormProps {
  apiUrl: string;
  userAddress: string;
}

type ActionType = "deposit" | "withdraw";

export default function StakeForm({ apiUrl, userAddress }: StakeFormProps) {
  const [tonConnectUI] = useTonConnectUI();
  const [action, setAction] = useState<ActionType>("deposit");
  const [amount, setAmount] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      const amountNum = parseFloat(amount);
      if (isNaN(amountNum) || amountNum <= 0) {
        throw new Error("Невірна сума");
      }

      // Вибираємо потрібний endpoint
      const endpoint = action === "deposit" 
        ? "/api/transaction/prepare-stake"
        : "/api/transaction/prepare-unstake";

      // Отримуємо дані для транзакції з бекенду
      const response = await fetch(`${apiUrl}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_address: userAddress,
          amount: amountNum,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || "Failed to prepare transaction");
      }

      const txData = await response.json();
      const tx = txData.transaction;

      // Будуємо транзакцію для TON Connect
      const transaction = {
        validUntil: Math.floor(Date.now() / 1000) + 600, // 10 хвилин
        messages: [
          {
            address: tx.to,
            amount: tx.amount.toString(),
            payload: tx.payload || undefined,
          },
        ],
      };

      console.log("Sending transaction:", transaction);

      // Відправляємо транзакцію через TON Connect
      const result = await tonConnectUI.sendTransaction(transaction);

      // Отримуємо tx_hash (залежить від реалізації TonConnect)
      const txHash = result.boc || result.hash || "pending";

      // Записуємо транзакцію на бекенді
      const recordResponse = await fetch(`${apiUrl}/api/transaction/${action}`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${localStorage.getItem("token")}`
        },
        body: JSON.stringify({
          tx_hash: txHash,
          amount: amountNum,
          user_address: userAddress,
        }),
      });

      if (!recordResponse.ok) {
        const error = await recordResponse.json();
        throw new Error(error.error || "Failed to record transaction");
      }

      setMessage({
        type: "success",
        text: `✅ Транзакція відправлена! ${action === "deposit" ? "Депозит" : "Вивід"} ${amount} TON (${txHash.substring(0, 10)}...)`,
      });
      setAmount("");

      console.log("Transaction result:", result);
    } catch (err) {
      setMessage({
        type: "error",
        text: err instanceof Error ? err.message : "Помилка відправки транзакції",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h3 className="text-xl font-bold text-gray-900 mb-4">
        {action === "deposit" ? "📥 Внести TON" : "📤 Вивести TON"}
      </h3>

      {/* Action Tabs */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setAction("deposit")}
          className={`flex-1 py-2 px-4 rounded-lg font-semibold transition-colors ${
            action === "deposit"
              ? "bg-blue-600 text-white"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200"
          }`}
        >
          Внести
        </button>
        <button
          onClick={() => setAction("withdraw")}
          className={`flex-1 py-2 px-4 rounded-lg font-semibold transition-colors ${
            action === "withdraw"
              ? "bg-blue-600 text-white"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200"
          }`}
        >
          Вивести
        </button>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="amount" className="block text-sm font-medium text-gray-700 mb-2">
            Сума (TON)
          </label>
          <input
            type="number"
            id="amount"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            step="0.1"
            min="1"
            placeholder={action === "deposit" ? "Мінімум 1 TON" : "Введіть суму"}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
            disabled={loading}
          />
          <p className="text-xs text-gray-500 mt-1">
            {action === "deposit"
              ? "💡 Мінімальна ставка: 1 TON (доступно для всіх!)"
              : "💡 Виведення може зайняти до 36 годин"}
          </p>
        </div>

        {/* Quick Amount Buttons */}
        {action === "deposit" && (
          <div className="flex gap-2">
            {[1, 5, 10, 50].map((val) => (
              <button
                key={val}
                type="button"
                onClick={() => setAmount(val.toString())}
                className="flex-1 py-2 text-sm font-semibold text-blue-600 border border-blue-300 rounded-lg hover:bg-blue-50 transition-colors"
                disabled={loading}
              >
                {val} TON
              </button>
            ))}
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading || !amount}
          className={`w-full py-3 px-4 rounded-lg font-semibold text-white transition-colors ${
            loading || !amount
              ? "bg-gray-400 cursor-not-allowed"
              : action === "deposit"
              ? "bg-blue-600 hover:bg-blue-700"
              : "bg-green-600 hover:bg-green-700"
          }`}
        >
          {loading
            ? "⏳ Обробка..."
            : action === "deposit"
            ? "💎 Внести в пул"
            : "💰 Вивести з пулу"}
        </button>
      </form>

      {/* Message */}
      {message && (
        <div
          className={`mt-4 p-4 rounded-lg ${
            message.type === "success"
              ? "bg-green-50 text-green-800 border border-green-200"
              : "bg-red-50 text-red-800 border border-red-200"
          }`}
        >
          {message.text}
        </div>
      )}

      {/* Info */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <p className="text-xs text-gray-600">
          {action === "deposit" ? (
            <>
              ℹ️ <strong>Як це працює:</strong> Ваші TON будуть застейкані в
              immutable контракт. Винагороди нараховуються автоматично кожну епоху
              (~36 годин).
            </>
          ) : (
            <>
              ℹ️ <strong>Процес виведення:</strong> Запит на вивід буде
              оброблений після завершення поточної епохи стейкінгу (до 36 годин).
            </>
          )}
        </p>
      </div>
    </div>
  );
}
