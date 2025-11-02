# Start TON Staking Pool - Backend + Frontend
# Запускає обидва сервери одночасно в окремих вікнах PowerShell

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 TON Staking Pool - Starting..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Перевірка чи існують директорії
if (-not (Test-Path "backend")) {
    Write-Host "❌ Error: backend folder not found" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path "frontend")) {
    Write-Host "❌ Error: frontend folder not found" -ForegroundColor Red
    exit 1
}

# Перевірка Python virtual environment
if (-not (Test-Path "backend\.venv")) {
    Write-Host "❌ Error: Python virtual environment not found" -ForegroundColor Red
    Write-Host "Run: cd backend && python -m venv .venv" -ForegroundColor Yellow
    exit 1
}

# Перевірка Node modules
if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "❌ Error: Node modules not found" -ForegroundColor Red
    Write-Host "Run: cd frontend && npm install" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Backend folder: OK" -ForegroundColor Green
Write-Host "✅ Frontend folder: OK" -ForegroundColor Green
Write-Host "✅ Python venv: OK" -ForegroundColor Green
Write-Host "✅ Node modules: OK" -ForegroundColor Green
Write-Host ""

# Запуск Backend в новому вікні
Write-Host "Starting Backend (Flask)..." -ForegroundColor Yellow
$backendScript = @"
cd '$PWD\backend'
.\.venv\Scripts\Activate.ps1
Write-Host '🐍 Flask Backend Started' -ForegroundColor Green
Write-Host 'URL: http://localhost:8000' -ForegroundColor Cyan
Write-Host 'Press Ctrl+C to stop' -ForegroundColor Gray
Write-Host ''
python app.py
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript

Write-Host "✅ Backend started in new window" -ForegroundColor Green
Start-Sleep -Seconds 2

# Запуск Frontend в новому вікні
Write-Host "Starting Frontend (Next.js)..." -ForegroundColor Yellow
$frontendScript = @"
cd '$PWD\frontend'
Write-Host '⚡ Next.js Frontend Started' -ForegroundColor Green
Write-Host 'URL: http://localhost:3000' -ForegroundColor Cyan
Write-Host 'Press Ctrl+C to stop' -ForegroundColor Gray
Write-Host ''
npm run dev
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript

Write-Host "✅ Frontend started in new window" -ForegroundColor Green
Write-Host ""

# Фінальні інструкції
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🎉 Both servers starting!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Wait ~5 seconds, then open:" -ForegroundColor Yellow
Write-Host "http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "To stop: Close both PowerShell windows" -ForegroundColor Gray
Write-Host "Or press Ctrl+C in each window" -ForegroundColor Gray
Write-Host ""

# Відкрити браузер через 5 секунд
Write-Host "Opening browser in 5 seconds..." -ForegroundColor Gray
Start-Sleep -Seconds 5
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "✅ Done! Browser opened." -ForegroundColor Green
Write-Host ""
