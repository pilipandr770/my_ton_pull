# Stop TON Staking Pool servers
# Зупиняє всі процеси Flask та Next.js

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🛑 Stopping TON Staking Pool servers..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Зупинити Python (Flask)
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*my_ton_pull*" }
if ($pythonProcesses) {
    Write-Host "Stopping Backend (Flask)..." -ForegroundColor Yellow
    $pythonProcesses | Stop-Process -Force
    Write-Host "✅ Backend stopped" -ForegroundColor Green
} else {
    Write-Host "⚠️  No Backend processes found" -ForegroundColor Gray
}

# Зупинити Node (Next.js)
$nodeProcesses = Get-Process node -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*node*" }
if ($nodeProcesses) {
    Write-Host "Stopping Frontend (Next.js)..." -ForegroundColor Yellow
    $nodeProcesses | Stop-Process -Force
    Write-Host "✅ Frontend stopped" -ForegroundColor Green
} else {
    Write-Host "⚠️  No Frontend processes found" -ForegroundColor Gray
}

Write-Host ""
Write-Host "✅ All servers stopped!" -ForegroundColor Green
Write-Host ""
