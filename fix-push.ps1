# Fix Git Push Protection Issue

cd "C:\Users\marka\Desktop\PCHECK PROJECT\PCheck"

# First, check current status
Write-Host "Current git status:"
git status

Write-Host "`nCurrent log:"
git log --oneline -5

Write-Host "`n=== SOLUTION ===" 
Write-Host "1. Visit: https://github.com/briant118/PCheck/security/secret-scanning"
Write-Host "2. Click 'Push protection' tab"
Write-Host "3. Unblock the secrets or dismiss them"
Write-Host "4. Then run: git push origin deployment"
Write-Host ""
Write-Host "OR alternatively:"
Write-Host "1. Reset to clean commit: git reset --hard ae824cd"
Write-Host "2. Re-apply your changes manually"
Write-Host "3. Commit with: git commit -m 'Apply changes without hardcoded secrets'"
Write-Host "4. Force push: git push --force-with-lease origin deployment"
