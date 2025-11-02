# 🔧 Виправлення деплою - Python 3.13 несумісність

## ❌ Проблема
```
ImportError: неопределенный символ: _PyInterpreterState_Get
```

**Причина**: Python 3.13.4 несумісний з `psycopg2-binary==2.9.9`

## ✅ Виправлення (вже застосовано)

### 1. Зафіксовано Python 3.11.0
- Додано `backend/runtime.txt` з версією `python-3.11.0`
- Оновлено `render.yaml` → `PYTHON_VERSION: 3.11.0`

### 2. Оновлено psycopg2-binary
- `requirements.txt`: `psycopg2-binary==2.9.10`

### 3. Спрощено деплой
- Видалено `build.sh` (проблеми з виконанням)
- Автоматичне створення схеми при запуску app
- Build Command: `pip install --upgrade pip && pip install -r requirements.txt`

---

## 🚀 Redeploy на Render

### Варіант 1: Автоматичний (рекомендовано)
Render автоматично виявить новий коміт і перезапустить деплой.

**Перевірте в Dashboard:**
1. Build logs → має використовувати Python 3.11.0
2. Deploy logs → має показати `✅ Database schema 'ton_pool' ready`

### Варіант 2: Ручний
1. Render Dashboard → `ton-pool-backend`
2. **Manual Deploy** → **Clear build cache & deploy**

---

## ✅ Очікуваний результат

```
==> Установка Python версии 3.11.0...
==> Использование Python версии 3.11.0
==> pip install --upgrade pip && pip install -r requirements.txt
Successfully installed Flask-3.1.0 ... psycopg2-binary-2.9.10 ...
==> Запускаем gunicorn...
✅ Database schema 'ton_pool' ready
[INFO] Listening at: http://0.0.0.0:10000
```

---

## 📊 Перевірка після деплою

### 1. Backend API
```bash
curl https://ton-pool-backend.onrender.com/
# Має повернути HTML з "TON Pool — Демо"
```

### 2. Pool Stats
```bash
curl https://ton-pool-backend.onrender.com/api/pool/stats
# Має повернути JSON
```

### 3. Database Schema
```bash
psql postgresql://ittoken_db_user:...@dpg-d0visga4d50c73ekmu4g-a.frankfurt-postgres.render.com/ittoken_db -c "\dt ton_pool.*"
```

Має показати таблиці:
- `ton_pool.users`
- `ton_pool.transactions`
- `ton_pool.pool_stats`
- `ton_pool.subscriptions`

---

## 🐛 Якщо все ще не працює

### Database connection error
**Перевірте Environment Variables в Render:**
```
DATABASE_URL=postgresql://ittoken_db_user:Xm98VVSZv7cMJkopkdWRkgvZzC7Aly42@dpg-d0visga4d50c73ekmu4g-a.frankfurt-postgres.render.com/ittoken_db
```

### Module not found
**Clear build cache:**
1. Dashboard → Settings → "Clear build cache"
2. Manual Deploy

### Schema не створюється
**Ручна команда через Render Shell:**
```python
python
>>> from app import app, db
>>> with app.app_context():
...     with db.engine.connect() as conn:
...         conn.execute(db.text("CREATE SCHEMA IF NOT EXISTS ton_pool"))
...         conn.commit()
...     db.create_all()
```

---

**Всі виправлення вже в репозиторії (коміт 29ba05f)!** 🎉
