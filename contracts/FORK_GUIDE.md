# Створення форку TON Nominator Pool

## Автоматичне створення форку (рекомендовано)

### Варіант 1: Через GitHub Web Interface

1. **Відкрийте офіційний репозиторій:**
   - https://github.com/ton-blockchain/nominator-pool

2. **Створіть форк:**
   - Натисніть кнопку "Fork" у правому верхньому куті
   - Виберіть ваш акаунт (@pilipandr770)
   - Дочекайтеся завершення форку

3. **Клонуйте ваш форк:**
   ```powershell
   cd C:\Users\ПК\my_ton_pull\contracts
   
   # Видаліть існуючий repo (якщо є)
   Remove-Item -Path repo -Recurse -Force
   
   # Клонуйте ваш форк
   git clone https://github.com/pilipandr770/nominator-pool.git repo
   cd repo
   
   # Додайте upstream для синхронізації
   git remote add upstream https://github.com/ton-blockchain/nominator-pool.git
   ```

4. **Застосуйте immutable патч:**
   ```powershell
   cd C:\Users\ПК\my_ton_pull\contracts
   .\patch_simple.ps1 -RepoPath ".\repo"
   ```

5. **Push патч у ваш форк:**
   ```powershell
   cd repo
   git add -A
   git commit -m "IMMUTABLE PATCH: Set validator_address to zero"
   git push origin main
   ```

### Варіант 2: Через GitHub CLI (якщо встановлено)

```powershell
# Встановіть GitHub CLI (якщо немає)
# winget install --id GitHub.cli

# Авторизуйтеся
gh auth login

# Створіть форк
gh repo fork ton-blockchain/nominator-pool --clone=true

# Перемістіть до contracts/repo
cd C:\Users\ПК\my_ton_pull\contracts
Remove-Item -Path repo -Recurse -Force -ErrorAction SilentlyContinue
Move-Item -Path nominator-pool -Destination repo

# Застосуйте патч
.\patch_simple.ps1 -RepoPath ".\repo"

# Push
cd repo
git add -A
git commit -m "IMMUTABLE PATCH: Set validator_address to zero"
git push origin main
```

## Що вже зроблено

✅ Склоновано офіційний `ton-blockchain/nominator-pool`  
✅ Застосовано патч (validator_address = 0)  
✅ Створено backup оригінального коду  
✅ Закоммічено зміни локально  
✅ Створено форк на GitHub: https://github.com/pilipandr770/nominator-pool  
✅ Push патчу у форк виконано  
✅ Remote налаштовано (origin → ваш форк, upstream → офіційний)  

## Готово! ✅

Ваш форк з immutable патчем доступний:
**https://github.com/pilipandr770/nominator-pool**

Коміт з патчем: `acb0e7c` - "IMMUTABLE PATCH: Set validator_address to zero (0)"  

## Структура після форку

```
my_ton_pull/
├── contracts/
│   ├── repo/                        # Ваш форк з патчем
│   │   ├── .git/                   # Git від вашого форку
│   │   ├── func/
│   │   │   ├── pool.fc            # ✓ Патч застосовано
│   │   │   ├── new-pool.fif       # ✓ Патч застосовано
│   │   │   └── ...
│   │   └── README.md              # Оригінальний README
│   ├── repo_backup_*/             # Backup оригіналу (ignored)
│   ├── ANALYSIS.md                # Аналіз контракту
│   ├── patch_simple.ps1           # Скрипт патчу
│   └── README.md                  # Інструкції
└── ...
```

## Синхронізація з upstream (опційно)

Щоб отримувати оновлення з офіційного репозиторію:

```powershell
cd C:\Users\ПК\my_ton_pull\contracts\repo

# Додайте upstream (якщо не додано)
git remote add upstream https://github.com/ton-blockchain/nominator-pool.git

# Отримайте зміни
git fetch upstream

# Переглянути відмінності
git diff upstream/main

# Змерджити (якщо потрібно)
git merge upstream/main

# Push оновлення
git push origin main
```

## Поширені проблеми

### 1. "repo already exists"

```powershell
cd C:\Users\ПК\my_ton_pull\contracts
Remove-Item -Path repo -Recurse -Force
# Потім клонуйте знову
```

### 2. "Permission denied" при push

Переконайтеся, що ви авторизовані:
```powershell
# Через SSH
ssh -T git@github.com

# Або використовуйте HTTPS з токеном
# Settings → Developer settings → Personal access tokens → Generate new token
```

### 3. Патч не застосувався

Перевірте, що файли існують:
```powershell
Test-Path ".\repo\func\pool.fc"
Test-Path ".\repo\func\new-pool.fif"
```

## Наступні кроки

1. ✅ Форк створено на GitHub
2. ⏳ Компіляція контрактів (потрібні TON dev tools)
3. ⏳ Тести на TON testnet
4. ⏳ Деплой у testnet
5. ⏳ Безпековий аудит
6. ⏳ Документація використання

## Корисні посилання

- **Офіційний репозиторій:** https://github.com/ton-blockchain/nominator-pool
- **Ваш форк (з патчем):** https://github.com/pilipandr770/nominator-pool ✅
- **TON Docs:** https://docs.ton.org/
- **TON Dev Tools:** https://github.com/ton-community/ton-compiler
