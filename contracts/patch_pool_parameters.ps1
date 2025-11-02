# PowerShell script to patch pool parameters
# Changes:
# - max_nominators_count: 40 -> 1000
# - min_validator_stake: 1000 TON -> 10 TON  
# - min_nominator_stake: 100 TON -> 10 TON

$ErrorActionPreference = "Stop"

Write-Host "`n=== TON Pool Parameters Patch ===" -ForegroundColor Cyan
Write-Host "Changing pool parameters to be more accessible`n" -ForegroundColor Yellow

$poolFile = ".\repo\func\new-pool.fif"

if (-not (Test-Path $poolFile)) {
    Write-Host "ERROR: File not found: $poolFile" -ForegroundColor Red
    Write-Host "Make sure you're in the contracts directory" -ForegroundColor Red
    exit 1
}

# Backup
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = ".\repo\func\new-pool.fif.backup_$timestamp"
Copy-Item $poolFile $backupFile
Write-Host "✅ Backup created: $backupFile" -ForegroundColor Green

# Read file
$content = Get-Content $poolFile -Raw

# Apply patches
Write-Host "`nApplying patches..." -ForegroundColor Cyan

# 1. Max nominators count: 40 -> 1000
Write-Host "  Patching max_nominators_count..." -ForegroundColor Gray
$content = $content -replace 'max_nominators_count 40 >', 'max_nominators_count 1000 >'
Write-Host "  √ max_nominators_count: 40 -> 1000" -ForegroundColor Green

# 2. Min validator stake: 1000 TON -> 10 TON (1000000000000 -> 10000000000)
Write-Host "  Patching min_validator_stake..." -ForegroundColor Gray
$content = $content -replace 'min_validator_stake 1000000000000 <', 'min_validator_stake 10000000000 <'
Write-Host "  √ min_validator_stake: 1000 TON -> 10 TON" -ForegroundColor Green

# 3. Min nominator stake: 100 TON -> 10 TON (100000000000 -> 10000000000)
Write-Host "  Patching min_nominator_stake..." -ForegroundColor Gray
$content = $content -replace 'min_nominator_stake 100000000000 <', 'min_nominator_stake 10000000000 <'
Write-Host "  √ min_nominator_stake: 100 TON -> 10 TON" -ForegroundColor Green

# 4. Update error messages
$content = $content -replace 'we do not recommend max_nominators_count higher than 40', 'max_nominators_count cannot be higher than 1000'
$content = $content -replace 'we do not recommend min_validator_stake less than at least 1000', 'min_validator_stake cannot be less than 10 TON'
$content = $content -replace 'we do not recommend min_nominator_stake less than at least 100', 'min_nominator_stake cannot be less than 10 TON'

# Save
$content | Set-Content $poolFile -NoNewline
Write-Host "`n✅ Patches applied successfully!" -ForegroundColor Green

# Summary
Write-Host "`n=== Summary ===" -ForegroundColor Cyan
Write-Host "File: $poolFile" -ForegroundColor White
Write-Host "Backup: $backupFile" -ForegroundColor Gray
Write-Host "`nChanges:" -ForegroundColor Yellow
Write-Host "  • Max nominators: 40 -> 1000" -ForegroundColor White
Write-Host "  • Min validator stake: 1000 TON -> 10 TON" -ForegroundColor White  
Write-Host "  • Min nominator stake: 100 TON -> 10 TON" -ForegroundColor White

Write-Host "" -ForegroundColor Cyan
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Commit changes to Git" -ForegroundColor White
Write-Host "  2. Compile contract" -ForegroundColor White
Write-Host "  3. Deploy to testnet" -ForegroundColor White
Write-Host "  4. Test through frontend" -ForegroundColor White

Write-Host "" -ForegroundColor Yellow
Write-Host "Remember:" -ForegroundColor Yellow
Write-Host "  - These parameters are SET AT DEPLOY TIME" -ForegroundColor White
Write-Host "  - Cannot be changed after deployment (immutable)" -ForegroundColor White
Write-Host "  - Test on testnet first!" -ForegroundColor White

Write-Host ""
