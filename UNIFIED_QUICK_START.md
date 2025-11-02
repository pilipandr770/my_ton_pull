# ✅ Unified Deployment - Quick Start

## 🎯 Що змінилось

**БУЛО**: 2 окремих сервіси (backend + frontend)  
**СТАЛО**: 1 сервіс (все разом!)

---

## 🚀 Деплой (3 кроки)

### 1. Видаліть старі сервіси (якщо створювали)
Render Dashboard → видаліть `ton-pool-backend` і `ton-pool-frontend` (якщо є)

### 2. Створіть новий unified сервіс

**Render Dashboard** → **New** → **Web Service**

**Налаштування:**
```
Repository: pilipandr770/my_ton_pull
Name: ton-pool
Runtime: Python
Branch: master
Build Command: chmod +x build-unified.sh && ./build-unified.sh
Start Command: gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --chdir /opt/render/project/src/backend app:app
```

**Environment Variables:**
```bash
PYTHON_VERSION=3.11.0
NODE_VERSION=18.17.0
DATABASE_URL=postgresql://ittoken_db_user:Xm98VVSZv7cMJkopkdWRkgvZzC7Aly42@dpg-d0visga4d50c73ekmu4g-a.frankfurt-postgres.render.com/ittoken_db
DB_SCHEMA=ton_pool
FLASK_ENV=production
SECRET_KEY=<auto-generate>
TON_API_KEY=2e5fc57e96c8d25f8a1cae2e6b2e7c8f3d4e5f6a7b8c9d0e1f2a3b4c5d6e7384ea
TON_POOL_ADDRESS=EQDrjaLahLkMB-hMCmkzOyBuHJ139ZUYmPHu6RRBKnbdLIYI
NEXT_PUBLIC_TON_MANIFEST_URL=https://ton-connect.github.io/demo-dapp-with-wallet/tonconnect-manifest.json
STRIPE_SECRET_KEY=sk_...  (опціонально)
STRIPE_WEBHOOK_SECRET=whsec_...  (опціонально)
```

### 3. Почекайте ~5 хвилин

Build process:
- ✅ Встановлює Python 3.11.0
- ✅ Встановлює Python залежності
- ✅ Створює PostgreSQL схему `ton_pool`
- ✅ Встановлює Node.js 18.17.0
- ✅ Будує Next.js frontend
- ✅ Запускає Gunicorn

---

## ✅ Перевірка

Після деплою отримаєте URL: `https://ton-pool.onrender.com`

### Backend API:
```bash
curl https://ton-pool.onrender.com/api/pool/stats
```

### Frontend UI:
Відкрийте в браузері: `https://ton-pool.onrender.com`

Має працювати:
- ✅ React UI з Tailwind
- ✅ TON Connect кнопка
- ✅ Статистика пулу
- ✅ Форма депозиту/виводу

---

## 🎉 Готово!

**Один URL, весь стек:**
- 🎨 Frontend: React + Next.js + TON Connect
- 🔧 Backend: Flask + PostgreSQL
- 🗄️ Database: Схема `ton_pool`
- 💰 Stripe: Webhooks готові

**Free tier**: 750 год/міс = 24/7 роботи! ✨

---

## 📝 Додатково

- **Full guide**: `UNIFIED_DEPLOYMENT.md`
- **Fixes**: `DEPLOY_FIX.md`
- **Ukrainian**: `DEPLOY_UA.md`

**Питання?** Всі інструкції в репозиторії! 🚀
