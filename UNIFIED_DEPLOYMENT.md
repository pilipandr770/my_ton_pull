# 🚀 TON Pool - Unified Deployment

**Один сервіс = Backend + Frontend разом!**

## 📦 Що входить

- **Backend**: Flask + PostgreSQL (API на `/api/*`)
- **Frontend**: Next.js static files (UI на `/`)
- **Database**: PostgreSQL зі схемою `ton_pool`
- **Deploy**: Один Web Service на Render.com

---

## 🎯 Як це працює

1. **Build**: 
   - `build-unified.sh` встановлює Python залежності
   - Створює PostgreSQL схему `ton_pool`
   - Встановлює Node.js залежності
   - Будує Next.js в статичні файли (`frontend/out`)

2. **Runtime**:
   - Gunicorn запускає Flask app
   - Flask віддає API на `/api/*`
   - Flask віддає статичні файли Next.js на `/`

3. **Роутинг**:
   ```
   /api/pool/stats          → Flask API
   /api/user/:address       → Flask API  
   /stripe/webhook          → Flask API
   /                        → Next.js (index.html)
   /_next/static/*          → Next.js static files
   ```

---

## 🚀 Деплой на Render.com

### Варіант 1: Blueprint (рекомендовано)

1. **Render Dashboard** → **New** → **Blueprint**
2. Підключіть репозиторій: `pilipandr770/my_ton_pull`
3. Render прочитає `render.yaml` і створить сервіс `ton-pool-unified`

### Варіант 2: Ручне створення Web Service

**Settings:**
- Name: `ton-pool-unified`
- Runtime: Python
- Branch: `master`
- Build Command: `chmod +x build-unified.sh && ./build-unified.sh`
- Start Command: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --chdir /opt/render/project/src/backend app:app`

**Environment Variables:**
```bash
PYTHON_VERSION=3.11.0
NODE_VERSION=18.17.0
DATABASE_URL=postgresql://ittoken_db_user:...
DB_SCHEMA=ton_pool
FLASK_ENV=production
SECRET_KEY=<generate>
TON_API_KEY=2e5fc57e96c8d25f8a1cae2e6b2e7c8f3d4e5f6a7b8c9d0e1f2a3b4c5d6e7384ea
STRIPE_SECRET_KEY=sk_...
STRIPE_WEBHOOK_SECRET=whsec_...
TON_POOL_ADDRESS=EQDrjaLahLkMB-hMCmkzOyBuHJ139ZUYmPHu6RRBKnbdLIYI
NEXT_PUBLIC_TON_MANIFEST_URL=https://ton-connect.github.io/demo-dapp-with-wallet/tonconnect-manifest.json
```

---

## ✅ Перевірка

### 1. Backend API
```bash
curl https://your-service.onrender.com/api/pool/stats
```

Має повернути JSON:
```json
{
  "total_staked": 0,
  "apy": 9.7,
  "participants": 0
}
```

### 2. Frontend
Відкрийте в браузері: `https://your-service.onrender.com`

Має показати:
- ✅ UI TON Staking Pool
- ✅ Кнопка "Connect Wallet" (TON Connect)
- ✅ Форма депозиту/виводу
- ✅ Статистика пулу

### 3. Database
```sql
psql postgresql://ittoken_db_user:...@dpg-.../ittoken_db

\dt ton_pool.*
```

Має показати таблиці: `users`, `transactions`, `pool_stats`, `subscriptions`

---

## 🔧 Локальна розробка

### Backend (Flask API)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

→ API доступне на http://localhost:8000/api/

### Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev
```

→ UI доступний на http://localhost:3000

### Unified (обидва разом)
```powershell
.\start.ps1  # Запускає backend + frontend в окремих терміналах
```

---

## 📊 Переваги Unified Deployment

✅ **Один сервіс** = простіше керувати  
✅ **Один URL** = немає CORS проблем  
✅ **Один порт** = менше конфігурації  
✅ **Free tier** = 750 год/міс (достатньо!)  
✅ **Швидше** = немає додаткових HTTP запитів між сервісами  

---

## 🆚 Порівняння з окремими сервісами

| Параметр | Unified | Separate |
|----------|---------|----------|
| Кількість сервісів | 1 | 2 |
| Free tier години | 750/міс | 375/міс кожен |
| CORS налаштування | Не потрібні | Обов'язкові |
| URL | Один | Два різних |
| Складність | Низька | Середня |
| Build час | ~3-5 хв | ~2-3 хв кожен |

---

## 🐛 Troubleshooting

### Frontend не показується
**Перевірте build logs**: має бути `npm run build` і створитись `frontend/out/`

### API не працює
**Перевірте роути**: `/api/*` мають бути зареєстровані ДО catch-all роуту `/`

### CORS помилки
**Не потрібні!** Frontend і backend на одному домені.

### Database connection error
**Перевірте** `DATABASE_URL` в Environment Variables

---

**Готово! Один сервіс, повний стек! 🎉**
