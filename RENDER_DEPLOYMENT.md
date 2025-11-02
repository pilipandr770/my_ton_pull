# 🚀 Deployment Guide - Render.com

Повний гайд по деплою TON Staking Pool на Render.com з PostgreSQL.

## 📋 Що підготовлено

✅ **Backend:**
- `render.yaml` - конфігурація для Render
- `backend/requirements.txt` - всі залежності (Flask, SQLAlchemy, PostgreSQL)
- `backend/Procfile` - процеси (web + release для міграцій)
- `backend/build.sh` - автоматичне створення схеми + міграції
- `backend/models.py` - моделі БД із схемою `ton_pool`
- `backend/app.py` - оновлено для production

✅ **Frontend:**
- `frontend/next.config.ts` - статичний експорт
- Автоматична збірка через `npm run build`

---

## 🗄️ PostgreSQL Database

### Ваша база даних:
```
Host: dpg-d0visga4d50c73ekmu4g-a.frankfurt-postgres.render.com
Database: ittoken_db
User: ittoken_db_user
Password: Xm98VVSZv7cMJkopkdWRkgvZzC7Aly42
Schema: ton_pool (автоматично створюється)
```

### Схема `ton_pool` включає:
- `users` - користувачі (wallet_address)
- `transactions` - історія депозитів/виводів
- `pool_stats` - статистика пулу
- `subscriptions` - Stripe підписки

---

## 🚀 Крок 1: Підготовка репозиторію

### 1.1. Закомітьте зміни:
```powershell
cd c:\Users\ПК\my_ton_pull
git add .
git commit -m "Add Render deployment configuration with PostgreSQL"
git push
```

---

## 🌐 Крок 2: Deploy Backend на Render

### 2.1. Створіть Web Service:
1. Відкрийте [Render Dashboard](https://dashboard.render.com/)
2. **New** → **Web Service**
3. **Connect Repository**: `pilipandr770/my_ton_pull`
4. **Settings**:
   - Name: `ton-pool-backend`
   - Region: **Frankfurt**
   - Branch: `master`
   - Root Directory: `backend`
   - Runtime: **Python 3**
   - Build Command: `./build.sh`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app`

### 2.2. Налаштуйте Environment Variables:

**⚠️ ВАЖЛИВО - додайте ці змінні в Render:**

```bash
# Database
DATABASE_URL=postgresql://ittoken_db_user:Xm98VVSZv7cMJkopkdWRkgvZzC7Aly42@dpg-d0visga4d50c73ekmu4g-a.frankfurt-postgres.render.com/ittoken_db
DB_SCHEMA=ton_pool

# Flask
FLASK_ENV=production
SECRET_KEY=<generate-in-render>  # Render може згенерувати
PORT=10000

# TON
TON_API_KEY=2e5fc57e96c8d25f8a1cae2e6b2e7c8f3d4e5f6a7b8c9d0e1f2a3b4c5d6e7384ea
TON_POOL_ADDRESS=EQDrjaLahLkMB-hMCmkzOyBuHJ139ZUYmPHu6RRBKnbdLIYI

# Stripe (отримайте з https://dashboard.stripe.com/)
STRIPE_SECRET_KEY=sk_live_... або sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# CORS
FRONTEND_URL=https://ton-pool-frontend.onrender.com

# Admin
ADMIN_PASSWORD=<ваш-безпечний-пароль>
```

### 2.3. Deploy:
- Натисніть **Create Web Service**
- Render автоматично:
  1. Запустить `build.sh`
  2. Створить схему `ton_pool`
  3. Виконає міграції
  4. Запустить gunicorn

### 2.4. Перевірте логи:
- Має бути: `✅ Schema 'ton_pool' created/verified`
- Має бути: `⬆️  Running database migrations...`

---

## 🎨 Крок 3: Deploy Frontend на Render

### 3.1. Створіть Static Site:
1. **New** → **Static Site**
2. **Connect Repository**: `pilipandr770/my_ton_pull`
3. **Settings**:
   - Name: `ton-pool-frontend`
   - Region: **Frankfurt**
   - Branch: `master`
   - Root Directory: `frontend`
   - Build Command: `npm install && npm run build`
   - Publish Directory: `out`

### 3.2. Environment Variables:
```bash
NEXT_PUBLIC_API_URL=https://ton-pool-backend.onrender.com
NEXT_PUBLIC_TON_MANIFEST_URL=https://ton-connect.github.io/demo-dapp-with-wallet/tonconnect-manifest.json
```

### 3.3. Deploy:
- Натисніть **Create Static Site**
- Чекайте завершення збірки (~2-3 хв)

---

## 🔗 Крок 4: Оновіть URL

### 4.1. Після деплою отримаєте URL:
- Backend: `https://ton-pool-backend.onrender.com`
- Frontend: `https://ton-pool-frontend.onrender.com`

### 4.2. Оновіть FRONTEND_URL в Backend:
1. Render Dashboard → `ton-pool-backend` → Environment
2. Змініть `FRONTEND_URL` на реальний URL frontend
3. **Save Changes** → автоматичний редеплой

---

## ✅ Крок 5: Перевірка

### 5.1. Перевірте Backend API:
```bash
curl https://ton-pool-backend.onrender.com/api/pool/stats
```

Має повернути:
```json
{
  "total_staked": 0,
  "apy": 9.7,
  "participants": 0,
  "min_stake": 1,
  "max_participants": 100000
}
```

### 5.2. Відкрийте Frontend:
```
https://ton-pool-frontend.onrender.com
```

Має працювати:
- ✅ Підключення TON Connect
- ✅ Відображення статистики
- ✅ Форма депозиту/виводу

---

## 🗄️ Крок 6: Перевірка БД

### 6.1. Підключіться до PostgreSQL:
```bash
psql postgresql://ittoken_db_user:Xm98VVSZv7cMJkopkdWRkgvZzC7Aly42@dpg-d0visga4d50c73ekmu4g-a.frankfurt-postgres.render.com/ittoken_db
```

### 6.2. Перевірте схему:
```sql
\dn  -- Список схем (має бути ton_pool)
\dt ton_pool.*  -- Таблиці в схемі
SELECT * FROM ton_pool.users;  -- Користувачі
```

---

## 🔄 Автоматичні міграції

### Як це працює:
1. Ви змінюєте `models.py`
2. Комітите і пушите на GitHub
3. Render автоматично:
   - Запускає `build.sh`
   - Генерує міграцію (`flask db migrate`)
   - Застосовує її (`flask db upgrade`)

### Ручні міграції (якщо потрібно):
```bash
# В Render Shell (Dashboard → Shell)
cd backend
flask db migrate -m "Add new field"
flask db upgrade
```

---

## 🐛 Troubleshooting

### Помилка: "Schema ton_pool does not exist"
**Рішення:**
```bash
# В Render Shell
python -c "from app import db; db.engine.execute('CREATE SCHEMA IF NOT EXISTS ton_pool')"
flask db upgrade
```

### Помилка CORS
**Перевірте:**
- `FRONTEND_URL` в backend environment variables
- Має співпадати з реальним URL frontend

### Build fails
**Перевірте:**
- `backend/build.sh` має виконуватись (`chmod +x build.sh` не потрібно на Render)
- Всі залежності в `requirements.txt`

---

## 📊 Моніторинг

### Render Dashboard:
- **Logs**: Перегляд логів у реальному часі
- **Metrics**: CPU, Memory, Response Time
- **Events**: Історія деплоїв

### Health Check:
Backend автоматично відповідає на:
```
GET https://ton-pool-backend.onrender.com/
```

---

## 💰 Stripe Webhooks (опціонально)

Якщо використовуєте підписки:

1. **Stripe Dashboard** → Developers → Webhooks
2. **Add endpoint**: `https://ton-pool-backend.onrender.com/stripe/webhook`
3. **Events**: `invoice.payment_succeeded`, `customer.subscription.deleted`
4. **Скопіюйте Signing Secret** → додайте як `STRIPE_WEBHOOK_SECRET`

---

## 🎉 Готово!

Ваш TON Staking Pool тепер працює на:
- 🌐 **Frontend**: https://ton-pool-frontend.onrender.com
- 🔧 **Backend API**: https://ton-pool-backend.onrender.com
- 🗄️ **Database**: PostgreSQL з автоматичними міграціями
- 📈 **Schema**: `ton_pool` (ізольована від інших проектів)

---

## 📝 Наступні кроки

1. ✅ Перевірте роботу на production URL
2. ✅ Налаштуйте Stripe webhooks (якщо потрібно)
3. ✅ Скомпілюйте і задеплойте TON smart contract
4. ✅ Оновіть `TON_POOL_ADDRESS` після деплою контракту
5. ✅ Створіть custom domain (опціонально)

---

**Питання?** Перевірте логи в Render Dashboard або напишіть! 🚀
