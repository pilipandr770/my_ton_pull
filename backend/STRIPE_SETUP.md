# ✅ Stripe налаштовано!

## Ваші дані Stripe (Test Mode):

### Продукт створено:
- **Назва:** Абонемент на вытягивание тонн (TON Pool Access)
- **Product ID:** `prod_TLkgHv5mD74dii`
- **Price ID:** `price_1SP3AxHpsuFkjt3p8J5ZPUnE`
- **Ціна:** 5 EUR/місяць (recurring)

### API Ключі (додано в .env):
- ✅ **Secret Key:** `sk_test_51PhccQ...` 
- ✅ **Publishable Key:** `pk_test_51PhccQ...`
- ⏳ **Webhook Secret:** Потрібно налаштувати endpoint

---

## 🔧 Наступний крок: Налаштувати Webhook

### Варіант 1: Локальне тестування (Stripe CLI)

**Встановіть Stripe CLI:**
```powershell
# Windows (через Scoop)
scoop bucket add stripe https://github.com/stripe/scoop-stripe-cli.git
scoop install stripe

# Або завантажте з: https://github.com/stripe/stripe-cli/releases/latest
```

**Використання:**
```powershell
# 1. Логін
stripe login

# 2. Forward webhook до локального сервера
stripe listen --forward-to localhost:8000/stripe/webhook

# Stripe CLI покаже webhook secret - скопіюйте його в .env
# whsec_xxxxxxxxxxxxx

# 3. Тест webhook (в іншому терміналі)
stripe trigger invoice.payment_succeeded
```

### Варіант 2: Локальне тестування (ngrok)

**Встановіть ngrok:**
```powershell
# Завантажте з: https://ngrok.com/download
# Або через Chocolatey:
choco install ngrok
```

**Використання:**
```powershell
# 1. Запустіть ngrok tunnel
ngrok http 8000

# 2. Скопіюйте публічний URL (наприклад: https://abc123.ngrok.io)

# 3. Додайте webhook в Stripe Dashboard:
#    https://dashboard.stripe.com/test/webhooks
#    Endpoint URL: https://abc123.ngrok.io/stripe/webhook
#    Events: invoice.payment_succeeded, customer.subscription.deleted

# 4. Скопіюйте Webhook Signing Secret в .env
```

### Варіант 3: Production (після deploy)

Коли задеплоїте на реальний домен:

1. **Додайте endpoint в Stripe:**
   - URL: `https://your-domain.com/stripe/webhook`
   - Events: 
     - `invoice.payment_succeeded`
     - `customer.subscription.deleted`
     - `customer.subscription.updated`

2. **Скопіюйте Signing Secret** → `.env` як `STRIPE_WEBHOOK_SECRET`

---

## 🧪 Тестування

### 1. Запустіть Flask server (якщо не запущено)

```powershell
cd C:\Users\ПК\my_ton_pull\backend
.\.venv\Scripts\Activate.ps1
python app.py
```

### 2. Перевірте endpoints

**Головна сторінка:**
```
http://localhost:8000/
```

**API pool:**
```
http://localhost:8000/api/pool
```

**Admin login:**
```
http://localhost:8000/login
```

### 3. Тестові картки Stripe

Для тестування підписок використовуйте:

**Успішна оплата:**
- Номер: `4242 4242 4242 4242`
- Термін: Будь-який майбутній (наприклад: 12/25)
- CVC: Будь-які 3 цифри
- ZIP: Будь-який

**Помилка оплати:**
- Номер: `4000 0000 0000 0002`

**3D Secure (потребує підтвердження):**
- Номер: `4000 0027 6000 3184`

**Більше тестових карток:**
https://stripe.com/docs/testing#cards

---

## 📝 Що додано в .env:

```env
# Flask Configuration
FLASK_SECRET_KEY=ab7dd9fe3456a77c2145c1c1295d13668368f63ea82edb823ccc5533553378c7
ADMIN_PASSWORD=strongpassword_change_me_2024

# Stripe Configuration (Test Mode)
STRIPE_SECRET_KEY=sk_test_51PhccQ...
STRIPE_PUBLISHABLE_KEY=pk_test_51PhccQ...
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here ⚠️ ПОТРІБНО ОНОВИТИ

# Stripe Product Details
STRIPE_PRODUCT_ID=prod_TLkgHv5mD74dii
STRIPE_PRICE_ID=price_1SP3AxHpsuFkjt3p8J5ZPUnE
```

**⚠️ Важливо:** Оновіть `STRIPE_WEBHOOK_SECRET` після налаштування webhook endpoint!

---

## 🔐 Безпека

### ✅ Зроблено:
- Secret keys в `.env` (не в Git)
- `.gitignore` налаштовано
- Flask secret key згенеровано

### ⚠️ TODO:
- Змініть `ADMIN_PASSWORD` на сильний пароль
- Налаштуйте webhook та оновіть `STRIPE_WEBHOOK_SECRET`
- Для production використовуйте live keys (не test)

---

## 📊 Stripe Dashboard

**Переглянути ваш продукт:**
https://dashboard.stripe.com/test/products/prod_TLkgHv5mD74dii

**Всі продукти:**
https://dashboard.stripe.com/test/products

**Webhooks:**
https://dashboard.stripe.com/test/webhooks

**API ключі:**
https://dashboard.stripe.com/test/apikeys

**Логи:**
https://dashboard.stripe.com/test/logs

---

## 🎯 Наступні кроки:

1. ✅ Stripe продукт створено
2. ✅ API ключі додано в .env
3. ⏳ **Налаштуйте webhook** (Варіант 1 або 2)
4. ⏳ Оновіть `STRIPE_WEBHOOK_SECRET` в .env
5. ⏳ Перезапустіть Flask server
6. ⏳ Протестуйте підписку

**Після налаштування webhook - все готово для прийняття платежів!** 💳

---

**Дата:** 2 листопада 2025  
**Режим:** Test Mode (безпечно для розробки)  
**Продукт:** prod_TLkgHv5mD74dii  
**Ціна:** 5 EUR/місяць
