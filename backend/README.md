# TON Pool Backend

Flask веб-додаток для керування підписками та відображення даних TON Pool.

## Функціональність

- ✅ **Admin Dashboard** - Панель адміністратора
- ✅ **Stripe Integration** - Підписка 5 €/міс
- ✅ **Webhook Handler** - Обробка подій Stripe
- ✅ **Mock API** - Тестові дані пулу (буде замінено на real TON indexer)
- ✅ **Session Management** - Безпечна аутентифікація

## Швидкий старт

### 1. Встановлення залежностей

```powershell
cd C:\Users\ПК\my_ton_pull\backend

# Створіть віртуальне оточення (якщо не створено)
python -m venv .venv

# Активуйте
.\.venv\Scripts\Activate.ps1

# Встановіть пакети
pip install -r requirements.txt
```

### 2. Налаштування змінних оточення

```powershell
# Створіть .env файл
copy .env.example .env

# Відредагуйте у VS Code
code .env
```

**Необхідні змінні (.env):**

```env
# Flask
FLASK_SECRET_KEY=your_random_secret_here_use_secrets_token_hex_32
ADMIN_PASSWORD=your_strong_admin_password

# Stripe (отримайте з https://dashboard.stripe.com/)
STRIPE_SECRET_KEY=sk_test_your_test_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

**Генерація секретного ключа:**

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Запуск dev сервера

```powershell
# Переконайтеся, що .venv активовано
.\.venv\Scripts\Activate.ps1

# Встановіть Flask app
$env:FLASK_APP="app.py"

# Запустіть dev сервер
flask run --host=0.0.0.0 --port=8000 --debug
```

**Або безпосередньо:**

```powershell
python app.py
```

Відкрийте: http://localhost:8000

### 4. Production запуск

```powershell
# Використовуйте gunicorn (Linux/Mac) або waitress (Windows)
pip install waitress

# Запуск
waitress-serve --host=0.0.0.0 --port=8000 app:app
```

## API Endpoints

### Публічні

#### `GET /`
Головна сторінка з інформацією про пул

**Відповідь:**
```html
<h2>TON Pool — Демо</h2>
<p>Поточний APY (mock): 9.7%</p>
```

#### `GET /api/pool`
Статистика пулу (mock дані)

**Відповідь:**
```json
{
  "total_pool_ton": 12345.678,
  "total_jettons": 98765.432,
  "apy": 0.097
}
```

#### `GET /api/position/<address>`
Позиція користувача

**Приклад:** `/api/position/EQD...xyz`

**Відповідь:**
```json
{
  "address": "EQD...xyz",
  "ton": 10.0,
  "jettons": 100.0
}
```

### Адміністративні

#### `GET /login`
Сторінка входу адміністратора

#### `POST /login`
Аутентифікація

**Body:**
```
password=your_admin_password
```

#### `GET /dashboard`
Панель адміністратора (потрібна аутентифікація)

**Показує:**
- Кількість активних підписок
- Список customer_id та subscription_id
- Статус підписок

### Webhook

#### `POST /stripe/webhook`
Обробка подій Stripe

**Підтримувані події:**
- `invoice.payment_succeeded` - Успішна оплата
- `customer.subscription.deleted` - Скасування підписки

**Безпека:**
- Перевірка Stripe-Signature
- Валідація через `STRIPE_WEBHOOK_SECRET`

## Stripe Налаштування

### 1. Створення продукту

1. Відкрийте [Stripe Dashboard](https://dashboard.stripe.com/)
2. **Products** → **Add Product**
3. Налаштування:
   - Name: `TON Pool Access`
   - Description: `Monthly subscription for TON Pool analytics and automation`
   - Pricing: `€5.00 / month` (recurring)
   - Tax: За потреби
4. **Save product**

### 2. Налаштування Webhook

1. **Developers** → **Webhooks** → **Add endpoint**
2. Endpoint URL:
   ```
   https://your-domain.com/stripe/webhook
   ```
   Для локального тестування використовуйте **Stripe CLI** або **ngrok**

3. **Select events:**
   - ✅ `invoice.payment_succeeded`
   - ✅ `customer.subscription.deleted`
   - ✅ `customer.subscription.updated`

4. **Add endpoint**

5. **Скопіюйте Signing secret** → додайте в `.env` як `STRIPE_WEBHOOK_SECRET`

### 3. API Ключі

1. **Developers** → **API keys**
2. **Test mode:**
   - Secret key: `sk_test_...` → `.env` як `STRIPE_SECRET_KEY`
   - Publishable key: `pk_test_...` (для frontend)

### 4. Локальне тестування webhook

**Використовуйте Stripe CLI:**

```powershell
# Встановіть Stripe CLI
# https://stripe.com/docs/stripe-cli

# Логін
stripe login

# Forward webhook до локального сервера
stripe listen --forward-to localhost:8000/stripe/webhook

# Тестовий webhook
stripe trigger invoice.payment_succeeded
```

**Або ngrok:**

```powershell
# Встановіть ngrok
# https://ngrok.com/download

# Запустіть tunnel
ngrok http 8000

# Використовуйте ngrok URL у Stripe webhook settings
# Приклад: https://abc123.ngrok.io/stripe/webhook
```

## Storage

### subscriptions.json

Локальне зберігання підписок (буде створено автоматично).

**Структура:**

```json
{
  "customers": {
    "cus_ABC123xyz": {
      "subscription_id": "sub_123456",
      "status": "active",
      "last_invoice": "in_789xyz"
    },
    "cus_DEF456abc": {
      "subscription_id": "sub_654321",
      "status": "canceled",
      "last_invoice": "in_xyz789"
    }
  }
}
```

**Статуси:**
- `active` - Активна підписка
- `canceled` - Скасована
- `past_due` - Прострочена оплата

### Міграція на БД (майбутнє)

Для production рекомендується використовувати:
- **PostgreSQL**
- **SQLite** (для малих проєктів)
- **MongoDB**

## TODO: Інтеграція з TON Indexer

Поточні endpoints `/api/pool` та `/api/position/:address` повертають mock дані.

**Плани:**

1. Підключити **TON API:**
   - https://toncenter.com/api/v2/
   - https://tonapi.io/

2. Читати on-chain дані:
   - Баланс пулу
   - Кількість учасників
   - APY (середній за 30 днів)
   - Позиції користувачів

3. Приклад інтеграції:

```python
import requests

def get_pool_data(pool_address):
    url = f"https://toncenter.com/api/v2/getAddressInformation?address={pool_address}"
    response = requests.get(url)
    data = response.json()
    
    # Парсинг state, balance, etc.
    return {
        "total_pool_ton": data["result"]["balance"],
        # ...
    }
```

## Безпека

### Поточні міри:

✅ Session-based auth для адміна  
✅ Stripe signature verification  
✅ Environment variables для секретів  
✅ `.env` в `.gitignore`  

### TODO:

⏳ Rate limiting (Flask-Limiter)  
⏳ CORS налаштування  
⏳ HTTPS (Let's Encrypt)  
⏳ CSRF protection  
⏳ Logging та monitoring  

## Розробка

### Структура коду

```
backend/
├── app.py                 # Основний Flask додаток
├── requirements.txt       # Python залежності
├── .env.example          # Шаблон змінних
├── .env                  # Ваші секрети (не в git!)
├── subscriptions.json    # Storage (буде створено)
└── README.md            # Ця документація
```

### Додавання нових endpoints

```python
@app.route("/api/new-endpoint")
def new_endpoint():
    # Ваша логіка
    return jsonify({"status": "ok"})
```

### Middleware для перевірки підписки

```python
from functools import wraps

def subscription_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Перевірка підписки
        if not has_active_subscription():
            return redirect("/payment-required")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/premium-feature")
@subscription_required
def premium_feature():
    return "Premium content"
```

## Тестування

```powershell
# Встановіть pytest
pip install pytest pytest-flask

# Запустіть тести (коли додамо)
pytest
```

## Логи

```powershell
# Додайте в app.py для детальних логів
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'flask'"

```powershell
# Активуйте venv
.\.venv\Scripts\Activate.ps1

# Встановіть залежності
pip install -r requirements.txt
```

### "Invalid Stripe signature"

Переконайтеся, що `STRIPE_WEBHOOK_SECRET` в `.env` правильний і відповідає webhook endpoint в Stripe Dashboard.

### "Address already in use"

```powershell
# Змініть порт
flask run --port=8001
```

## Production Checklist

- [ ] `FLASK_SECRET_KEY` - випадковий, довгий
- [ ] `ADMIN_PASSWORD` - сильний пароль
- [ ] Stripe - production keys (не test)
- [ ] HTTPS налаштовано
- [ ] Firewall rules
- [ ] Monitoring (Sentry, Datadog)
- [ ] Backup для subscriptions.json
- [ ] Rate limiting
- [ ] CORS налаштовано для вашого домену

## Корисні команди

```powershell
# Активувати venv
.\.venv\Scripts\Activate.ps1

# Деактивувати
deactivate

# Оновити залежності
pip freeze > requirements.txt

# Запуск
flask run --debug

# Перевірка синтаксису
python -m py_compile app.py
```

---

**Статус:** ✅ Готово до використання  
**Версія:** 1.0.0  
**Дата:** 2025-11-02
