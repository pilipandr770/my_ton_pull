# TON Pool Immutable Patch - Simplified Version
# Застосовує зміни для створення immutable pool

Param(
    [string]$RepoPath = "C:\Users\ПК\my_ton_pull\contracts\repo"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TON Pool Immutable Patch (Zero Address)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $RepoPath)) {
    Write-Host "Error: Repository not found at $RepoPath" -ForegroundColor Red
    exit 1
}

# Backup
$backupPath = "$RepoPath`_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
Write-Host "Creating backup..." -ForegroundColor Yellow
Copy-Item -Path $RepoPath -Destination $backupPath -Recurse -Force
Write-Host "Backup created: $backupPath" -ForegroundColor Green
Write-Host ""

# Patch new-pool.fif
$newPoolFile = Join-Path $RepoPath "func\new-pool.fif"
Write-Host "Patching: $newPoolFile" -ForegroundColor Cyan

$content = Get-Content $newPoolFile -Raw -Encoding UTF8

# Замінюємо рядок з validator_address
$oldPattern = '(\$1 true parse-load-address[^\n]+\n)constant validator_address'
$newPattern = "// PATCHED: validator_address set to ZERO (immutable pool)`n// Original: `$1 true parse-load-address ...`n0 constant validator_address  // ZERO = No owner"

$content = $content -replace $oldPattern, $newPattern

Set-Content -Path $newPoolFile -Value $content -Encoding UTF8 -NoNewline
Write-Host "  Done: validator_address = 0" -ForegroundColor Green
Write-Host ""

# Patch pool.fc - add warning
$poolFile = Join-Path $RepoPath "func\pool.fc"
Write-Host "Patching: $poolFile" -ForegroundColor Cyan

$content = Get-Content $poolFile -Raw -Encoding UTF8

$warningComment = @"
;; ========================================
;; IMMUTABLE POOL PATCH APPLIED
;; ========================================
;; validator_address = 0 (ZERO ADDRESS)
;; WARNING: This makes certain operations impossible
;; Use for demonstration/testing only
;; ========================================

"@

$content = $warningComment + $content
Set-Content -Path $poolFile -Value $content -Encoding UTF8 -NoNewline
Write-Host "  Done: Warning comment added" -ForegroundColor Green
Write-Host ""

# Show diff
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Changes Applied" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Push-Location $RepoPath
Write-Host "Git diff:" -ForegroundColor Yellow
git diff --stat
Write-Host ""
git diff func/new-pool.fif
Write-Host ""
Pop-Location

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "1. Review changes: cd $RepoPath; git diff" -ForegroundColor White
Write-Host "2. Test compilation (if you have TON tools)" -ForegroundColor White
Write-Host "3. Commit: cd $RepoPath; git add -A; git commit -m 'Set validator_address to zero'" -ForegroundColor White
Write-Host ""
Write-Host "BACKUP: $backupPath" -ForegroundColor Green
