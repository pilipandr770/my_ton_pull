'use client';

import { useAuth } from "@/contexts/AuthContext";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function Home() {
  const { isAuthenticated, loading } = useAuth();
  const router = useRouter();

  // Redirect authenticated users to dashboard
  useEffect(() => {
    if (!loading && isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, loading, router]);

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

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <span className="text-2xl">💎</span>
            <h1 className="text-2xl font-bold text-gray-900">TON Staking Pool</h1>
          </div>
          <nav className="flex items-center space-x-4">
            <Link href="/login" className="px-4 py-2 text-gray-700 hover:text-indigo-600 font-medium">
              Вхід
            </Link>
            <Link href="/register" className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium">
              Реєстрація
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
          <div>
            <h2 className="text-5xl font-bold text-gray-900 mb-6">
              Заробляйте на стейкингу TON 🚀
            </h2>
            <p className="text-xl text-gray-600 mb-8">
              Присоединяйтесь до децентралізованого пулу стейкингу і отримуйте пасивний доход від своїх TON токенів.
            </p>
            <div className="flex space-x-4">
              <Link 
                href="/register" 
                className="px-8 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-bold text-lg"
              >
                Почнути зараз
              </Link>
              <a 
                href="#how-it-works" 
                className="px-8 py-3 border-2 border-indigo-600 text-indigo-600 rounded-lg hover:bg-indigo-50 font-bold text-lg"
              >
                Дізнатись більше
              </a>
            </div>
          </div>
          <div className="text-center">
            <div className="bg-white rounded-xl shadow-xl p-8">
              <div className="text-6xl mb-4">💰</div>
              <h3 className="text-3xl font-bold text-gray-900 mb-2">До 9.7% APY</h3>
              <p className="text-gray-600 mb-6">Річна прибутковість на вашому стейку</p>
              <div className="space-y-2 text-left">
                <p className="text-gray-700">✅ Мінімум 0.5 TON</p>
                <p className="text-gray-700">✅ Без комісій</p>
                <p className="text-gray-700">✅ Миттєвий вивід</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="bg-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-gray-900 text-center mb-12">Як це працює</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {/* Step 1 */}
            <div className="text-center">
              <div className="w-16 h-16 bg-indigo-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
                1
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Реєстрація</h3>
              <p className="text-gray-600">
                Створіть акаунт з електронною поштою та паролем
              </p>
            </div>

            {/* Step 2 */}
            <div className="text-center">
              <div className="w-16 h-16 bg-indigo-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
                2
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Підключіть гаманець</h3>
              <p className="text-gray-600">
                Синхронізуйте свій TON гаманець (Tonkeeper, TonHub)
              </p>
            </div>

            {/* Step 3 */}
            <div className="text-center">
              <div className="w-16 h-16 bg-indigo-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
                3
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Застейкуйте TON</h3>
              <p className="text-gray-600">
                Перекажіть мінімум 0.5 TON в пул стейкингу
              </p>
            </div>

            {/* Step 4 */}
            <div className="text-center">
              <div className="w-16 h-16 bg-indigo-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
                4
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Отримуйте прибуток</h3>
              <p className="text-gray-600">
                Автоматично отримуйте винагороди щодня
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Smart Contract Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="bg-indigo-50 rounded-xl p-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-6">🔒 Безпечно та Децентралізовано</h2>
          <p className="text-lg text-gray-700 mb-4">
            Наш смарт-контракт зберігається в блокчейні TON і перевіряється незалежними аудиторами. 
            Немає адміністратора, який міг би вкрасти ваші кошти.
          </p>
          <p className="text-lg text-gray-700 mb-6">
            Всі транзакції прозорі та верифіковані на блокчейні.
          </p>
        </div>
      </section>

      {/* Stats Section */}
      <section className="bg-gray-900 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
            <div>
              <div className="text-5xl font-bold mb-2">1.2M+</div>
              <p className="text-gray-400">Всього в пулі</p>
            </div>
            <div>
              <div className="text-5xl font-bold mb-2">42+</div>
              <p className="text-gray-400">Активних стейкерів</p>
            </div>
            <div>
              <div className="text-5xl font-bold mb-2">9.7%</div>
              <p className="text-gray-400">Середня APY</p>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <h2 className="text-4xl font-bold text-gray-900 text-center mb-12">Часті запитання</h2>
        
        <div className="space-y-6">
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <h3 className="text-xl font-bold text-gray-900 mb-2">Як безпечно мій стейк?</h3>
            <p className="text-gray-600">
              Стейк зберігається у децентралізованому смарт-контракті. Ви завжди можете вивести свої токени в будь-який час.
            </p>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-sm">
            <h3 className="text-xl font-bold text-gray-900 mb-2">Коли я отримаю винаграду?</h3>
            <p className="text-gray-600">
              Винагороди розраховуються безперервно і виплачуються кожен день.
            </p>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-sm">
            <h3 className="text-xl font-bold text-gray-900 mb-2">Яка комісія?</h3>
            <p className="text-gray-600">
              Комісія 0%. Пул працює на некомерційній основі.
            </p>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-sm">
            <h3 className="text-xl font-bold text-gray-900 mb-2">Мінімальний стейк?</h3>
            <p className="text-gray-600">
              Мінімальна сума для стейкингу - 0.5 TON. Максимум не обмежений.
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold mb-6">Готові почати?</h2>
          <p className="text-xl mb-8 text-indigo-100">
            Приєднайтесь до сотень стейкерів які вже заробляють на TON
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link 
              href="/register" 
              className="px-8 py-4 bg-white text-indigo-600 rounded-lg hover:bg-gray-100 font-bold text-lg"
            >
              Реєстрація
            </Link>
            <Link 
              href="/login" 
              className="px-8 py-4 border-2 border-white text-white rounded-lg hover:bg-indigo-700 font-bold text-lg"
            >
              Вже маю акаунт
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <p>© 2025 TON Staking Pool. Всі права захищені.</p>
            <a 
              href="https://github.com/pilipandr770/my_ton_pull" 
              target="_blank" 
              rel="noopener noreferrer"
              className="hover:text-white"
            >
              GitHub
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
