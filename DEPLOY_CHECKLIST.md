# ✅ Render.com Deployment Checklist

## 📦 Що готово

- ✅ `render.yaml` - Blueprint конфігурація
- ✅ `backend/requirements.txt` - Python залежності з PostgreSQL
- ✅ `backend/build.sh` - автоматичні міграції
- ✅ `backend/models.py` - моделі БД зі схемою `ton_pool`
- ✅ `backend/app.py` - production ready
- ✅ `backend/Procfile` - gunicorn + release phase
- ✅ `frontend/next.config.ts` - static export
- ✅ `frontend/package.json` - додано `serve`

## 🚀 Швидкий старт

### 1. Закомітьте все
```powershell
git add .
git commit -m "Add Render deployment with PostgreSQL schema"
git push
```

### 2. Render Dashboard
1. Відкрийте https://dashboard.render.com/
2. **New** → **Blueprint** → підключіть репозиторій `pilipandr770/my_ton_pull`
3. Render автоматично прочитає `render.yaml` і створить 2 сервіси

### 3. Налаштуйте секретні змінні
В Dashboard для `ton-pool-backend` додайте:
- `STRIPE_SECRET_KEY` (з Stripe Dashboard)
- `STRIPE_WEBHOOK_SECRET` (після створення webhook)
- `TON_API_KEY` (вже є: 2e5fc57e96c8d25f...)
- `ADMIN_PASSWORD` (ваш безпечний пароль)

### 4. Оновіть URL
Після деплою:
1. Скопіюйте URL backend: `https://ton-pool-backend.onrender.com`
2. Скопіюйте URL frontend: `https://ton-pool-frontend.onrender.com`
3. Оновіть `FRONTEND_URL` в backend environment variables
4. Оновіть `NEXT_PUBLIC_API_URL` в frontend (якщо відрізняється)

## ✅ Перевірка

```bash
# Backend API
curl https://ton-pool-backend.onrender.com/api/pool/stats

# PostgreSQL схема
psql postgresql://ittoken_db_user:Xm98VVSZv7cMJkopkdWRkgvZzC7Aly42@dpg-d0visga4d50c73ekmu4g-a.frankfurt-postgres.render.com/ittoken_db -c "\dn"
```

Має показати схему `ton_pool` ✅

## 📊 Що станеться при deploy

1. **Backend:**
   - Встановить Python 3.10
   - Запустить `build.sh`:
     - Створить схему `ton_pool`
     - Виконає `flask db migrate`
     - Виконає `flask db upgrade`
   - Запустить gunicorn на порту 10000

2. **Frontend:**
   - Встановить Node.js 18
   - Запустить `npm run build` (статичний експорт)
   - Запустить `serve` для роздачі файлів

3. **Database:**
   - Використає вашу існуючу БД
   - Створить окрему схему `ton_pool` (не вплине на інші проекти)
   - Таблиці: users, transactions, pool_stats, subscriptions

## 🔥 Free tier limits

- Backend: 750 годин/міс (достатньо для 1 сервісу 24/7)
- Frontend: Необмежено (static hosting)
- Database: Ваша власна БД (вже оплачена)

## 📝 Детальна інструкція

Дивіться `RENDER_DEPLOYMENT.md` для повного гайду!
