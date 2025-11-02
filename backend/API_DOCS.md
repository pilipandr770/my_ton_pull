# Backend API Documentation

## Base URL
```
Local: http://localhost:8000
Production: https://your-domain.com
```

---

## 🔗 TON Pool API Endpoints

### 1. Get Pool Statistics

**Endpoint:** `GET /api/pool/stats`

**Description:** Отримати загальну статистику пулу

**Response:**
```json
{
  "total_staked": 12345.67,
  "total_staked_usd": 30864.18,
  "participants_count": 342,
  "apy": 9.7,
  "pool_address": "EQDk2VTvn04SUKJrW7rXahzdF8_Qi6utb0wj43InCu9vdjrR",
  "status": "active",
  "min_stake": 10,
  "testnet": true
}
```

**Example:**
```bash
curl http://localhost:8000/api/pool/stats
```

---

### 2. Get User Balance

**Endpoint:** `GET /api/user/:address/balance`

**Description:** Отримати баланс користувача (wallet + staked + rewards)

**Parameters:**
- `address` (path) - TON адреса користувача

**Response:**
```json
{
  "user_address": "EQD...xyz",
  "wallet_balance": 100.5,
  "staked_amount": 50.0,
  "jettons_balance": 50.0,
  "accumulated_rewards": 2.35,
  "share_percentage": 2.5
}
```

**Example:**
```bash
curl http://localhost:8000/api/user/EQD...xyz/balance
```

---

### 3. Get User Transactions

**Endpoint:** `GET /api/user/:address/transactions?limit=10`

**Description:** Історія транзакцій користувача з пулом

**Parameters:**
- `address` (path) - TON адреса користувача
- `limit` (query, optional) - Кількість транзакцій (default: 10)

**Response:**
```json
{
  "transactions": [
    {
      "hash": "abc123...",
      "timestamp": 1730563200,
      "type": "deposit",
      "amount": 50.0,
      "status": "completed"
    },
    {
      "hash": "def456...",
      "timestamp": 1730476800,
      "type": "reward",
      "amount": 0.5,
      "status": "completed"
    }
  ]
}
```

**Example:**
```bash
curl "http://localhost:8000/api/user/EQD...xyz/transactions?limit=20"
```

---

### 4. Prepare Transaction

**Endpoint:** `POST /api/transaction/prepare`

**Description:** Підготувати дані транзакції для підпису в гаманці

**Request Body:**
```json
{
  "type": "deposit",
  "address": "EQD...xyz",
  "amount": 50.0
}
```

**Types:**
- `deposit` - Стейкнути TON в пул
- `withdraw` - Вивести TON з пулу

**Response (Deposit):**
```json
{
  "to": "EQDk2VTvn04SUKJrW7rXahzdF8_Qi6utb0wj43InCu9vdjrR",
  "amount": "50000000000",
  "payload": "",
  "from": "EQD...xyz",
  "valid_until": null,
  "type": "deposit"
}
```

**Response (Withdraw):**
```json
{
  "to": "EQDk2VTvn04SUKJrW7rXahzdF8_Qi6utb0wj43InCu9vdjrR",
  "amount": "50000000",
  "payload": "",
  "from": "EQD...xyz",
  "valid_until": null,
  "type": "withdraw",
  "withdraw_amount": "50000000000"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/transaction/prepare \
  -H "Content-Type: application/json" \
  -d '{
    "type": "deposit",
    "address": "EQD...xyz",
    "amount": 50.0
  }'
```

---

## 🔐 Admin Endpoints

### 5. Admin Login

**Endpoint:** `POST /login`

**Description:** Аутентифікація адміністратора

**Form Data:**
- `password` - Admin пароль (з .env)

**Response:** Redirect to `/dashboard`

---

### 6. Admin Dashboard

**Endpoint:** `GET /dashboard`

**Description:** Панель адміністратора

**Authentication:** Потрібен login

**Shows:**
- Активні Stripe підписки
- Customer IDs та Subscription IDs

---

## 💳 Stripe Webhooks

### 7. Stripe Webhook

**Endpoint:** `POST /stripe/webhook`

**Description:** Обробка подій від Stripe

**Events:**
- `invoice.payment_succeeded` - Успішна оплата підписки
- `customer.subscription.deleted` - Скасування підписки

**Security:** Перевіряється Stripe-Signature header

---

## 📊 Response Format

### Success Response
```json
{
  "data_field": "value",
  ...
}
```

### Error Response
```json
{
  "error": "Error message description"
}
```

**HTTP Status Codes:**
- `200 OK` - Успішний запит
- `400 Bad Request` - Невалідні параметри
- `403 Forbidden` - Немає доступу
- `404 Not Found` - Endpoint не знайдено
- `500 Internal Server Error` - Помилка сервера

---

## 🧪 Testing

### Test Pool Stats:
```bash
curl http://localhost:8000/api/pool/stats
```

### Test User Balance:
```bash
curl http://localhost:8000/api/user/EQDk2VTvn04SUKJrW7rXahzdF8_Qi6utb0wj43InCu9vdjrR/balance
```

### Test Transaction Prepare:
```bash
curl -X POST http://localhost:8000/api/transaction/prepare \
  -H "Content-Type: application/json" \
  -d '{
    "type": "deposit",
    "address": "EQDk2VTvn04SUKJrW7rXahzdF8_Qi6utb0wj43InCu9vdjrR",
    "amount": 10.0
  }'
```

---

## 🔧 Configuration

Налаштування в `.env`:

```env
# TON Configuration
TON_TESTNET=true                                    # true = testnet, false = mainnet
TON_POOL_ADDRESS=EQDk2VTvn04SUKJrW7rXahzdF8_Qi6... # Адреса pool контракту
TONCENTER_API_KEY=                                  # Опційно для rate limits
```

---

## 📝 Notes

### Current Implementation:
- ✅ Pool stats з реальним балансом контракту
- ✅ User wallet balance через TonCenter API
- ⏳ Staked amount, jettons, rewards - TODO (потребує get-методів контракту)
- ⏳ Transaction payload - TODO (потребує правильного формату BOC)

### TODO:
1. Додати get-методи контракту (nominators_count, user_stake, etc.)
2. Реалізувати правильний payload для deposit/withdraw
3. Додати розрахунок APY на основі validator rewards
4. WebSocket для real-time updates
5. Кешування даних для performance

---

**Last Updated:** 2025-11-02  
**Version:** 1.0 (MVP)  
**Status:** 🟡 In Development
