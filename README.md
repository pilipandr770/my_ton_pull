# TON Pool Project

Immutable TON staking pool з підпискою через Stripe (5 €/міс для доступу до аналітики).

## Огляд проєкту

Цей проєкт реалізує **повністю децентралізований TON стейкінг пул** з наступними характеристиками:

- ✅ **Immutable контракти**: Owner/Admin = нульові адреси, неможливо змінити після деплою
- ✅ **Без комісій власника**: весь дохід розподіляється між учасниками пропорційно
- ✅ **Підписка офчейн**: 5 €/міс через Stripe — доступ до веб-інтерфейсу та аналітики
- ✅ **Повний контроль користувачів**: тільки deposit → share tokens і withdraw
- ✅ **Безпека**: без приватних ключів у бекенді, без backdoor функцій

## Структура проєкту

```
my_ton_pull/
├── contracts/                # TON смарт-контракти
│   ├── README.md            # Інструкції з патчу контрактів
│   ├── patch_owner_example.ps1
│   └── repo/                # Форк офіційного TON пулу (клонувати окремо)
├── backend/                 # Flask веб-сервер
│   ├── app.py              # Основний додаток
│   ├── requirements.txt    # Python залежності
│   └── .env.example        # Шаблон змінних оточення
├── scripts/                 # Скрипти деплою
│   └── deploy.ps1          # PowerShell скрипт для деплою контрактів
├── COPILOT_INSTRUCTIONS.md # Детальна документація для розробки
└── README.md               # Цей файл
```

## Швидкий старт (Windows PowerShell)

### 1. Клонування та налаштування проєкту

```powershell
# Перейдіть до папки проєкту
cd C:\Users\ПК\my_ton_pull

# Створіть віртуальне оточення Python
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Встановіть залежності
pip install -r requirements.txt
```

### 2. Налаштування змінних оточення

```powershell
# Створіть .env файл з .env.example
cd C:\Users\ПК\my_ton_pull\backend
copy .env.example .env

# Відредагуйте .env файл у VS Code або будь-якому редакторі
code .env
```

Додайте ваші реальні значення:
```env
FLASK_SECRET_KEY=your_random_secret_key_here
ADMIN_PASSWORD=your_strong_password
STRIPE_SECRET_KEY=sk_test_your_stripe_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
```

### 3. Запуск Flask бекенду

```powershell
cd C:\Users\ПК\my_ton_pull\backend
.\.venv\Scripts\Activate.ps1
$env:FLASK_APP="app.py"
flask run --host=0.0.0.0 --port=8000
```

Відкрийте браузер: http://localhost:8000

### 4. Робота з контрактами

#### Крок 1: Форк офіційного TON пулу

```powershell
# Створіть форк на GitHub офіційного репозиторію:
# https://github.com/ton-blockchain/nominator-pool
# або
# https://github.com/ton-blockchain/liquid-staking-contract

# Клонуйте ваш форк
cd C:\Users\ПК\my_ton_pull\contracts
git clone https://github.com/<your-username>/<your-ton-fork>.git repo
```

#### Крок 2: Патч owner/admin на нульові адреси

```powershell
cd C:\Users\ПК\my_ton_pull\contracts
.\patch_owner_example.ps1 -RepoPath "C:\Users\ПК\my_ton_pull\contracts\repo"
```

#### Крок 3: Перевірка змін

```powershell
cd C:\Users\ПК\my_ton_pull\contracts\repo
git status
git diff

# Якщо все правильно
git add -A
git commit -m "Set owner/admin to zero address; remove upgrade functions"
git push origin main
```

#### Крок 4: Деплой у testnet

```powershell
cd C:\Users\ПК\my_ton_pull\scripts
.\deploy.ps1 -NETWORK testnet
```

**Примітка**: Перед запуском `deploy.ps1` потрібно додати реальні команди компіляції та деплою для вашого TON toolchain.

## Налаштування Stripe

### 1. Створення продукту в Stripe Dashboard

1. Увійдіть у [Stripe Dashboard](https://dashboard.stripe.com/)
2. Перейдіть до **Products** → **Add Product**
3. Створіть продукт:
   - Name: "TON Pool Access"
   - Pricing: €5.00 / month (recurring)
4. Збережіть Product ID

### 2. Налаштування Webhook

1. Перейдіть до **Developers** → **Webhooks**
2. Додайте endpoint: `https://your-domain.com/stripe/webhook`
3. Виберіть події:
   - `invoice.payment_succeeded`
   - `customer.subscription.deleted`
   - `customer.subscription.updated`
4. Скопіюйте **Signing secret** у `.env` як `STRIPE_WEBHOOK_SECRET`

### 3. Отримання API ключів

1. **Developers** → **API keys**
2. Скопіюйте **Secret key** (sk_test_... для тесту)
3. Додайте у `.env` як `STRIPE_SECRET_KEY`

## API Endpoints

### Публічні

- `GET /` - Головна сторінка (інформація про пул)
- `GET /api/pool` - Статистика пулу (mock дані)
- `GET /api/position/:address` - Позиція користувача (mock дані)

### Адміністративні

- `GET /login` - Сторінка логіну адміна
- `POST /login` - Аутентифікація адміна
- `GET /dashboard` - Панель адміністратора (потрібна аутентифікація)

### Stripe Webhooks

- `POST /stripe/webhook` - Обробка подій від Stripe

## Безпека

### Чек-ліст перед mainnet деплоєм

- [ ] **Контракти перевірені**: Owner/Admin = нульові адреси
- [ ] **Код аудований**: Незалежний аудит безпеки виконано
- [ ] **Тести пройдені**: Всі unit та integration тести успішні
- [ ] **Testnet перевірка**: Контракти протестовані на testnet
- [ ] **Немає upgrade функцій**: setOwner/setAdmin видалені або заблоковані
- [ ] **Немає backdoors**: Код перевірено на приховані функції
- [ ] **Приватні ключі безпечні**: Ніколи не коммітяться в Git
- [ ] **Stripe налаштовано**: Webhook працює коректно
- [ ] **Secrets захищені**: `.env` файл не в репозиторії
- [ ] **Rate limiting**: Захист від DDoS на webhook
- [ ] **Monitoring**: Логування та моніторинг налаштовані

## Розробка

### TODO для GitHub Copilot

Детальні інструкції для Copilot знаходяться у файлі `COPILOT_INSTRUCTIONS.md`.

**Основні завдання:**

1. ✅ Створити структуру проєкту
2. ✅ Налаштувати Flask бекенд
3. ✅ Інтегрувати Stripe підписки
4. ⏳ Патч TON контрактів (owner → zero)
5. ⏳ Деплой контрактів у testnet
6. ⏳ Інтеграція з TON indexer API
7. ⏳ Додати фронтенд UI
8. ⏳ Безпековий аудит

### Корисні команди

```powershell
# Активація віртуального оточення
cd C:\Users\ПК\my_ton_pull\backend
.\.venv\Scripts\Activate.ps1

# Запуск dev сервера
flask run --host=0.0.0.0 --port=8000 --debug

# Встановлення нових залежностей
pip install <package-name>
pip freeze > requirements.txt

# Перевірка git статусу
git status
git diff

# Деплой контрактів (тестова мережа)
cd C:\Users\ПК\my_ton_pull\scripts
.\deploy.ps1 -NETWORK testnet
```

## Архітектура

### Смарт-контракти (TON)

- **Базис**: Форк офіційного nominator-pool або liquid-staking
- **Модифікації**: 
  - Owner/Admin → `0:0000...0000` (нульові адреси)
  - Видалені функції upgrade/setOwner/setAdmin
  - Мінімальний стейк настроюється через константу
- **Логіка**: Стандартний розподіл винагород між учасниками

### Backend (Flask)

- **Аутентифікація**: Локальний адмін (session-based)
- **Stripe**: Обробка підписок через webhooks
- **Storage**: JSON файл для збереження підписок (можна замінити на БД)
- **API**: Mock endpoints для on-chain даних (підключити TON indexer)

### Офчейн підписка (Stripe)

- **Продукт**: 5 €/міс recurring
- **Доступ**: Захист веб-інтерфейсу middleware перевіркою підписки
- **Незалежність**: Смарт-контракт працює незалежно від підписки

## Питання та підтримка

Для детальної інформації дивіться:
- `COPILOT_INSTRUCTIONS.md` - Повна документація для розробників
- `contracts/README.md` - Інструкції з роботи з контрактами
- `backend/app.py` - Коментарі в коді бекенду

## Ліцензія

MIT License (або вкажіть вашу ліцензію)

---

**⚠️ ВАЖЛИВО**: Цей проєкт знаходиться в розробці. Перед використанням на mainnet обов'язково проведіть повний аудит безпеки!
