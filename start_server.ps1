Write-Host "Starting PCheck (self-hosted - Daphne)..." -ForegroundColor Green
Set-Location $PSScriptRoot
if (Test-Path ".\venv\Scripts\Activate.ps1") { .\venv\Scripts\Activate.ps1 }
$env:DJANGO_SETTINGS_MODULE = "PCheckMain.settings"
python -m daphne -b 0.0.0.0 -p 8000 PCheckMain.asgi:application

