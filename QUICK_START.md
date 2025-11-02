# 🚀 Quick Start Guide - TON Staking Pool

**Останнє оновлення:** 2 листопада 2025

Швидкий старт для TON Pool проєкту.

## ✅ Що вже готово

Проєкт **повністю налаштовано** і готовий до використання:

1. ✅ Git репозиторій: https://github.com/pilipandr770/my_ton_pull
2. ✅ Backend (Flask) працює
3. ✅ Контракти проаналізовано та пропатчено
4. ✅ Документація повна
5. ✅ PowerShell скрипти готові

## 🎯 Перевірка роботи (30 секунд)

### Backend працює?

```powershell
cd C:\Users\ПК\my_ton_pull\backend
.\.venv\Scripts\Activate.ps1
python app.py
```

Відкрийте браузер: **http://localhost:8000**

**Очікується:**
- Головна сторінка з "TON Pool — Демо"
- Посилання "Admin login"
- APY: 9.7% (mock)

### API працює?

Відкрийте:
- http://localhost:8000/api/pool
- http://localhost:8000/api/position/test

**Очікується:** JSON відповідь з даними

### Контракти пропатчено?

```powershell
cd C:\Users\ПК\my_ton_pull\contracts\repo
git log --oneline -1
git diff HEAD~1 func/new-pool.fif
```

**Очікується:** Коміт "IMMUTABLE PATCH: Set validator_address to zero"

---

## 📋 Наступні кроки (в порядку пріоритету)

### 1️⃣ Створити форк TON Pool (5 хвилин)

**Чому:** Щоб мати власну версію контракту на GitHub

**Як:**
1. Відкрийте: https://github.com/ton-blockchain/nominator-pool
2. Натисніть "Fork" (верхній правий кут)
3. Виберіть свій акаунт
4. Дочекайтеся завершення

**Потім:**
```powershell
cd C:\Users\ПК\my_ton_pull\contracts\repo
git remote set-url origin https://github.com/pilipandr770/nominator-pool.git
git push origin main
```

**Документація:** `contracts/FORK_GUIDE.md`

### 2️⃣ Налаштувати Stripe (10 хвилин)

**Чому:** Щоб приймати підписки 5 €/міс

**Як:**
1. Створіть обліковий запис: https://dashboard.stripe.com/register
2. Створіть продукт:
   - Products → Add Product
   - Name: "TON Pool Access"
   - Price: €5.00/month
3. Налаштуйте webhook:
   - Developers → Webhooks → Add endpoint
   - URL: `https://your-domain.com/stripe/webhook` (поки що локально - див. нижче)
   - Events: `invoice.payment_succeeded`, `customer.subscription.deleted`
4. Скопіюйте ключі в `.env`:
   ```env
   STRIPE_SECRET_KEY=sk_test_your_key_here
   STRIPE_WEBHOOK_SECRET=whsec_your_secret_here
   ```

**Локальне тестування webhook:**
```powershell
# Варіант 1: Stripe CLI
stripe listen --forward-to localhost:8000/stripe/webhook

# Варіант 2: ngrok
ngrok http 8000
# Використайте ngrok URL у Stripe webhook settings
```

**Документація:** `backend/README.md` розділ "Stripe Налаштування"

### 3️⃣ Встановити TON Dev Tools (20 хвилин)

**Чому:** Щоб компілювати та деплоїти контракти

**Варіанти:**

#### A. Blueprint (рекомендовано для початківців)
```powershell
npm install -g @ton-community/blueprint
```

#### B. TON Compiler
```powershell
npm install -g ton-compiler
```

#### C. func (низькорівнева робота)
Завантажити з: https://ton.org/docs/develop/func/

**Тест компіляції:**
```powershell
cd C:\Users\ПК\my_ton_pull\contracts\repo\func
func -o output.fif pool.fc stdlib.fc
```

**Документація:** `contracts/README.md`

### 4️⃣ Testnet Deploy (30 хвилин)

**Передумови:**
- ✅ TON tools встановлено
- ✅ Контракт скомпільовано
- ⏳ TON wallet (testnet)
- ⏳ Test TON токени

**Кроки:**

1. **Створіть testnet wallet:**
   - Використайте Tonkeeper або TON Wallet
   - Переключіться на testnet
   - Запишіть адресу

2. **Отримайте тестові токени:**
   - Testnet faucet: https://t.me/testgiver_ton_bot

3. **Оновіть deploy скрипт:**
   ```powershell
   code C:\Users\ПК\my_ton_pull\scripts\deploy.ps1
   ```
   Додайте реальні команди компіляції та деплою

4. **Запустіть деплой:**
   ```powershell
   cd C:\Users\ПК\my_ton_pull\scripts
   .\deploy.ps1 -NETWORK testnet
   ```

**Документація:** `scripts/deploy.ps1` (TODO коментарі)

### 5️⃣ Інтеграція TON Indexer (1 година)

**Чому:** Замінити mock API на реальні on-chain дані

**Файл для редагування:** `backend/app.py`

**Endpoints:**
- `/api/pool` - дані пулу з blockchain
- `/api/position/:address` - баланс користувача

**API опції:**
1. **TON Center API** (безкоштовний)
   ```python
   import requests
   
   def get_pool_balance(pool_address):
       url = f"https://testnet.toncenter.com/api/v2/getAddressInformation?address={pool_address}"
       response = requests.get(url)
       return response.json()
   ```

2. **TON API** (більше функцій)
   ```python
   import requests
   
   def get_pool_info(pool_address):
       url = f"https://tonapi.io/v2/accounts/{pool_address}"
       response = requests.get(url)
       return response.json()
   ```

**Документація:** `backend/README.md` розділ "TODO: Інтеграція з TON Indexer"

---

## 🆘 Troubleshooting

### Backend не запускається

**Помилка:** "No module named 'flask'"

**Рішення:**
```powershell
cd C:\Users\ПК\my_ton_pull\backend
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Git push не працює

**Помилка:** "Permission denied"

**Рішення:**
```powershell
# Налаштуйте Git credentials
git config --global user.name "Your Name"
git config --global user.email "your@email.com"

# Або використайте SSH
ssh-keygen -t ed25519 -C "your@email.com"
# Додайте ~/.ssh/id_ed25519.pub до GitHub Settings → SSH Keys
```

### Stripe webhook не працює локально

**Рішення 1: Stripe CLI**
```powershell
stripe listen --forward-to localhost:8000/stripe/webhook
```

**Рішення 2: ngrok**
```powershell
ngrok http 8000
# Використайте ngrok URL: https://abc123.ngrok.io/stripe/webhook
```

### Контракт не компілюється

**Проблема:** Немає TON tools

**Рішення:**
```powershell
# Встановіть Blueprint
npm install -g @ton-community/blueprint

# Або завантажте func binary
# https://ton.org/docs/develop/func/
```

---

## 📚 Корисні команди

### Backend
```powershell
# Активувати venv
cd C:\Users\ПК\my_ton_pull\backend
.\.venv\Scripts\Activate.ps1

# Запустити сервер
python app.py

# Оновити залежності
pip freeze > requirements.txt
```

### Git
```powershell
# Статус
git status

# Додати зміни
git add .
git commit -m "Your message"
git push origin master

# Переглянути історію
git log --oneline
```

### Контракти
```powershell
# Застосувати патч
cd C:\Users\ПК\my_ton_pull\contracts
.\patch_simple.ps1 -RepoPath ".\repo"

# Переглянути зміни
cd repo
git diff
```

---

## 🎓 Навчальні ресурси

### TON Development
- **Офіційні Docs:** https://docs.ton.org/
- **TON Community:** https://t.me/tondev
- **Tutorials:** https://ton.org/dev

### Flask
- **Офіційна документація:** https://flask.palletsprojects.com/
- **Quickstart:** https://flask.palletsprojects.com/en/latest/quickstart/

### Stripe
- **API Docs:** https://stripe.com/docs/api
- **Testing:** https://stripe.com/docs/testing

---

## ✅ Checklist

Використовуйте цей checklist для відстеження прогресу:

- [x] Git репозиторій ініціалізовано
- [x] Backend запускається локально
- [x] Контракти проаналізовано
- [x] Патч застосовано
- [ ] Форк створено на GitHub
- [ ] Stripe налаштовано
- [ ] TON tools встановлено
- [ ] Testnet deploy виконано
- [ ] TON indexer інтегровано
- [ ] Frontend створено (опційно)
- [ ] Security audit пройдено
- [ ] Mainnet deploy (остаточний крок)

---

## 🚀 Готові до старту?

**Рекомендований порядок:**

1. ✅ Перевірте що все працює (30 сек)
2. ⏳ Створіть форк на GitHub (5 хв)
3. ⏳ Налаштуйте Stripe (10 хв)
4. ⏳ Встановіть TON tools (20 хв)
5. ⏳ Deploy у testnet (30 хв)

**Загальний час:** ~1 година

**Повна документація:**
- `README.md` - Головна документація
- `PROJECT_STATUS.md` - Детальний звіт
- `COPILOT_INSTRUCTIONS.md` - План розробки
- `backend/README.md` - Backend документація
- `contracts/README.md` - Контракти документація

**Готові?** Виберіть наступний крок і вперед! 🎯

---

**Останнє оновлення:** 2 листопада 2025  
**Репозиторій:** https://github.com/pilipandr770/my_ton_pull  
**Status:** 🟢 Ready to go!
