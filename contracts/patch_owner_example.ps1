# contracts/patch_owner_example.ps1
# Автоматичний патч для заміни owner/admin адрес на нульові

Param(
  [string]$RepoPath = "C:\Users\ПК\my_ton_pull\contracts\repo"
)

$zero = "0:0000000000000000000000000000000000000000000000000000000000000000"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TON Pool Owner/Admin Patch Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Patching repository at: $RepoPath" -ForegroundColor Yellow
Write-Host "Replacing OWNER_ADDRESS with: $zero" -ForegroundColor Yellow
Write-Host ""

if (-not (Test-Path $RepoPath)) {
    Write-Host "❌ Error: Repository path does not exist!" -ForegroundColor Red
    Write-Host "Please clone the TON pool repository first:" -ForegroundColor Red
    Write-Host "  cd C:\Users\ПК\my_ton_pull\contracts" -ForegroundColor White
    Write-Host "  git clone <repository-url> repo" -ForegroundColor White
    exit 1
}

$fileCount = 0
Get-ChildItem -Path $RepoPath -Recurse -Include *.fc,*.tact,*.sol,*.js,*.ts,*.py | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    if ($content -match "OWNER_ADDRESS") {
        $newContent = $content -replace "OWNER_ADDRESS", $zero
        Set-Content -Path $_.FullName -Value $newContent -NoNewline
        Write-Host "✓ Patched: $($_.FullName)" -ForegroundColor Green
        $fileCount++
    }
}

Write-Host ""
if ($fileCount -eq 0) {
    Write-Host "⚠️  No files were patched. Make sure OWNER_ADDRESS pattern is correct." -ForegroundColor Yellow
    Write-Host "   You may need to manually search and replace owner/admin addresses." -ForegroundColor Yellow
} else {
    Write-Host "✓ Successfully patched $fileCount file(s)" -ForegroundColor Green
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Review changes: cd $RepoPath; git status; git diff" -ForegroundColor White
Write-Host "2. Manually verify all owner/admin references are set to zero" -ForegroundColor White
Write-Host "3. Remove or disable any upgrade/setOwner/setAdmin functions" -ForegroundColor White
Write-Host "4. Run tests to ensure contract still works" -ForegroundColor White
Write-Host "5. Commit changes: git add -A; git commit -m 'Set owner/admin to zero'" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  IMPORTANT: Manual review required!" -ForegroundColor Red
Write-Host "   This script only replaces OWNER_ADDRESS placeholder." -ForegroundColor Red
Write-Host "   You must manually verify all owner/admin logic is removed." -ForegroundColor Red
